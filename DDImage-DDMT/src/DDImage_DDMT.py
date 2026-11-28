"""Shared implementation for the six model/stage entry points.

find: C(I) != C(MR(I)), without DD or ground-truth labels.
dd:   C(I') == C(I) and C(MR(I')) != C(I').
Images/MRs/masks are constructed in RGB uint8 before model preprocessing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
IMAGE_SIZE = (224, 224)
MR_NAMES = ("flip", "rotate_plus5", "rotate_minus5")
ROTATIONS = {"rotate_plus5": 5, "rotate_minus5": -5}
MODEL_IDS = {"resnet": "resnet_v2_50_classification_5",
             "mobilenet": "mobilenet_v2_imagenet", "vgg": "vgg16_imagenet"}
RESNET_URL = "https://tfhub.dev/google/imagenet/resnet_v2_50/classification/5"
RESAMPLING = getattr(Image, "Resampling", Image)
FIND_FIELDS = (
    "model", "image", "source_path", "source_sha256", "status", "source_pred",
    "flip_pred", "rotate_plus5_pred", "rotate_minus5_pred",
    "flip_violation", "rotate_plus5_violation", "rotate_minus5_violation",
    "any_violation", "original_width", "original_height", "I_size_pixels",
    "flip_copy_path", "rotate_plus5_copy_path", "rotate_minus5_copy_path",
    "inference_calls", "execution_time_seconds", "error",
)
FAILURE_FIELDS = ("model", "image", "source_path", "source_sha256", "mr",
                  "source_pred", "followup_pred", "copied_path")
DD_FIELDS = (
    "model", "image", "mr", "source_path", "input_path", "source_sha256", "status",
    "source_pred", "screen_followup_pred", "seed_pred", "seed_followup_pred",
    "I_prime_pred", "I_prime_followup_pred", "original_width", "original_height",
    "I_size_pixels", "I_prime_size_pixels", "pixel_ratio", "n_segments",
    "selected_segments", "is_reduced", "one_minimal", "final_pass",
    "test_calls", "dd_test_calls", "minimality_test_calls", "inference_calls",
    "dd_time_seconds", "minimality_time_seconds", "execution_time_seconds",
    "original_copy_path", "I_path", "I_prime_path", "MR_I_prime_path", "mask_path", "error",
)


def read_image(path):
    data = Path(path).read_bytes()
    with Image.open(io.BytesIO(data)) as opened:
        size = opened.size
        image = np.asarray(opened.convert("RGB").resize(IMAGE_SIZE), dtype=np.uint8)
    return image, size, hashlib.sha256(data).hexdigest()


def apply_mr(image, mr):
    if mr == "flip":
        return np.ascontiguousarray(np.fliplr(image))
    if mr not in ROTATIONS:
        raise ValueError(f"Unsupported MR: {mr}")
    return np.asarray(Image.fromarray(image).rotate(
        ROTATIONS[mr], resample=RESAMPLING.BICUBIC, expand=False, fillcolor=(0, 0, 0)))


def segment_image(image):
    from skimage.segmentation import quickshift

    return quickshift(image.astype(np.float64) / 255.0,
                      kernel_size=4, max_dist=200, ratio=0.2, rng=42)


def black_background(image):
    """Fill removed components with RGB black before model preprocessing."""
    return np.zeros_like(image)


def keep_segments(image, segments, components, background):
    return np.where(np.isin(segments, components)[..., None], image, background)


def image_paths(directory):
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise FileNotFoundError(f"Image directory not found: {directory}")
    paths = [p for p in directory.iterdir()
             if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}]
    paths.sort(key=lambda p: [int(s) if s.isdigit() else s.lower()
                             for s in re.split(r"(\d+)", p.name)])
    if not paths:
        raise ValueError(f"No supported images: {directory}")
    return paths


def class_ids(output, batch_size):
    if isinstance(output, dict):
        key = next((k for k in ("logits", "predictions", "outputs", "default") if k in output), None)
        if key is None:
            if len(output) != 1:
                raise ValueError(f"Ambiguous model outputs: {list(output)}")
            key = next(iter(output))
        output = output[key]
    scores = np.asarray(output.numpy() if hasattr(output, "numpy") else output)
    if scores.ndim != 2 or scores.shape[0] != batch_size or scores.shape[1] < 2:
        raise ValueError(f"Expected [batch, classes], got {scores.shape}")
    if not np.isfinite(scores).all():
        raise ValueError("Model output contains NaN or infinity")
    return np.argmax(scores, axis=1).astype(int)


def load_model(model_name, local_model=None):
    """Load the original TF Hub ResNet or a Keras ImageNet MobileNetV2/VGG16."""
    if model_name not in MODEL_IDS:
        raise ValueError(f"Unknown model: {model_name}")
    if model_name != "resnet":
        if local_model:
            raise ValueError("--local-model applies only to the ResNet SavedModel")
        os.environ.setdefault("KERAS_HOME", str(ROOT / "keras_cache"))
        from tensorflow.keras.applications import MobileNetV2, VGG16
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobile_preprocess
        from tensorflow.keras.applications.vgg16 import preprocess_input as vgg_preprocess

        constructor, preprocess = ((MobileNetV2, mobile_preprocess) if model_name == "mobilenet"
                                   else (VGG16, vgg_preprocess))
        model = constructor(include_top=True, weights="imagenet", input_shape=(224, 224, 3))

        def predict(images):
            # VGG preprocessing mutates arrays: never pass the source/candidate itself.
            inputs = preprocess(np.asarray(images, dtype=np.float32).copy())
            return class_ids(model(inputs, training=False), len(images))

        return predict

    os.environ["TFHUB_CACHE_DIR"] = str(ROOT / "tfhub_cache")
    import tensorflow as tf
    import tensorflow_hub as hub

    model = hub.load(str(local_model) if local_model else RESNET_URL)
    serving = getattr(model, "signatures", {}).get("serving_default")
    selected_call = None

    def signature_call(tensor):
        if serving is None:
            raise TypeError("No serving_default signature")
        _, keywords = serving.structured_input_signature
        if len(keywords) == 1:
            return serving(**{next(iter(keywords)): tensor})
        return serving(tensor)

    def predict(images):
        nonlocal selected_call
        tensor = tf.convert_to_tensor(np.asarray(images, dtype=np.float32) / 255.0)
        if selected_call is not None:
            return class_ids(selected_call(tensor), len(images))
        calls = ([lambda x: model(x, False, False, 0.99), lambda x: model(x, training=False),
                  lambda x: model(x)] if callable(model) else []) + [signature_call]
        errors = []
        for call in calls:
            try:
                result = class_ids(call(tensor), len(images))
            except (TypeError, ValueError) as exc:
                errors.append(str(exc))
            else:
                selected_call = call
                return result
        raise RuntimeError("Cannot call ResNet: " + " | ".join(errors))

    return predict


class PredictionMeter:
    def __init__(self, predict):
        self.predict = predict
        self.inference_calls = 0
        self.model_batch_calls = 0

    def __call__(self, images):
        ids = np.asarray(self.predict(images))
        if ids.shape != (len(images),) or not np.issubdtype(ids.dtype, np.integer):
            raise ValueError("Predictor must return one integer class ID per image")
        self.inference_calls += len(images)
        self.model_batch_calls += 1
        return ids

    def one(self, image):
        return int(self(image[None, ...])[0])


def ddmin(components, predicate):
    """Subset/complement DD from a seed already known to satisfy predicate."""
    result, n = list(components), 2
    while len(result) >= 2:
        n = min(n, len(result))
        subsets = [part.tolist() for part in np.array_split(result, n)]
        for subset in subsets:
            if predicate(subset):
                result, n = subset, 2
                break
        else:
            for subset in subsets:
                removed = set(subset)
                complement = [item for item in result if item not in removed]
                if predicate(complement):
                    result, n = complement, max(2, n - 1)
                    break
            else:
                if n == len(result):
                    break
                n = min(len(result), n * 2)
    return result


def enforce_one_minimal(components, predicate):
    result = list(components)
    if not predicate(result):
        return result, False
    if predicate([]):
        result = []
    else:
        while True:
            for component in result:
                candidate = [item for item in result if item != component]
                if predicate(candidate):
                    result = candidate
                    break
            else:
                break
    final_pass = predicate(result)
    removable = any(predicate([item for item in result if item != component]) for component in result)
    return result, bool(final_pass and not removable)


def reduce_for_mr(image, segments, background, mr, label, meter):
    components = [int(x) for x in np.unique(segments)]
    if segments.shape != image.shape[:2]:
        raise ValueError("Segment map shape differs from input image")
    started = last_progress = time.perf_counter()
    before = meter.inference_calls
    tests = {"dd": 0, "minimality": 0}
    phase = "dd"
    last_passing = None
    seed_predictions = []

    def predicate(selected):
        nonlocal last_passing, last_progress
        tests[phase] += 1
        prime = keep_segments(image, segments, selected, background)
        a = meter.one(prime)
        b = meter.one(apply_mr(prime, mr)) if a == label else None
        if sum(tests.values()) == 1:
            seed_predictions.extend([a, b])
        passed = a == label and b != a
        if passed:
            last_passing = (tuple(selected), a, b)
        if time.perf_counter() - last_progress >= 15:
            print(f"  {mr}: {sum(tests.values())} tests, {len(selected)} candidate components", flush=True)
            last_progress = time.perf_counter()
        return passed

    seed_pass = predicate(components)
    selected = ddmin(components, predicate) if seed_pass else components
    dd_seconds = time.perf_counter() - started
    phase = "minimality"
    minimality_started = time.perf_counter()
    selected, minimal = enforce_one_minimal(selected, predicate) if seed_pass else (selected, False)
    minimality_seconds = time.perf_counter() - minimality_started
    final_pass = bool(minimal and last_passing and last_passing[0] == tuple(selected))
    row = {"seed_pred": seed_predictions[0], "seed_followup_pred": seed_predictions[1],
           "status": "selected" if final_pass else "verification_failed",
           "test_calls": sum(tests.values()), "dd_test_calls": tests["dd"],
           "minimality_test_calls": tests["minimality"],
           "inference_calls": meter.inference_calls - before,
           "dd_time_seconds": round(dd_seconds, 6),
           "minimality_time_seconds": round(minimality_seconds, 6),
           "one_minimal": final_pass, "final_pass": final_pass, "n_segments": len(components)}
    if not seed_pass:
        row["status"] = "source_label_changed" if seed_predictions[0] != label else "seed_no_longer_fails"
    if not final_pass:
        return row
    mask = np.isin(segments, selected)
    prime = keep_segments(image, segments, selected, background)
    row.update(I_prime_pred=last_passing[1], I_prime_followup_pred=last_passing[2],
               I_prime_size_pixels=int(mask.sum()), pixel_ratio=float(mask.mean()),
               selected_segments=" ".join(map(str, selected)), is_reduced=len(selected) < len(components),
               prime=prime, followup=apply_mr(prime, mr), mask=mask)
    return row


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def read_csv(path, fields=None):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if fields is not None and reader.fieldnames != list(fields):
            raise ValueError(f"Incompatible CSV header: {path}")
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Incomplete CSV record; inspect the last line before resuming: {path}")
    return rows


class RunLog:
    """Durable per-image/per-pair journal; model predictions never depend on exports."""
    def __init__(self, output_root, resume, config, fields):
        self.fields = fields
        if resume:
            self.directory = Path(resume).resolve()
            previous = json.loads((self.directory / "metadata.json").read_text(encoding="utf-8"))
            if previous["config"] != config:
                raise ValueError("Resume configuration/input changed; use a new run directory")
        else:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
            self.directory = Path(output_root).resolve() / stamp
            self.directory.mkdir(parents=True, exist_ok=False)
            write_json(self.directory / "metadata.json", {"created_utc": datetime.now(timezone.utc).isoformat(),
                                                          "config": config})
        path = self.directory / "results.csv"
        self.rows = read_csv(path, fields) if path.exists() else []
        if not path.exists():
            with path.open("w", encoding="utf-8-sig", newline="") as stream:
                csv.DictWriter(stream, fieldnames=fields).writeheader()
        self.stream = path.open("a", encoding="utf-8", newline="")
        self.writer = csv.DictWriter(self.stream, fieldnames=fields)

    def append(self, row):
        clean = {field: str(row[field]) if row.get(field) is not None else "" for field in self.fields}
        self.writer.writerow(clean)
        self.stream.flush()
        os.fsync(self.stream.fileno())
        self.rows.append(clean)

    def close(self):
        self.stream.close()


def experiment_config(model_name, stage, local_model):
    return {"schema": 1, "stage": stage, "model": MODEL_IDS[model_name],
            "local_model": str(Path(local_model).resolve()) if local_model else None,
            "image_size": list(IMAGE_SIZE), "mrs": {"flip": "horizontal", **ROTATIONS},
            "rotation": {"interpolation": "bicubic", "expand": False, "fill_rgb": [0, 0, 0]},
            "pixels": "RGB uint8; model-specific preprocessing only at inference"}


def export_failures(log):
    path = log.directory / "failures.csv"
    temp = path.with_suffix(".csv.tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FAILURE_FIELDS)
        writer.writeheader()
        for row in log.rows:
            for mr in MR_NAMES:
                if row[mr + "_violation"] == "True":
                    writer.writerow({"model": row["model"], "image": row["image"],
                                     "source_path": row["source_path"], "source_sha256": row["source_sha256"],
                                     "mr": mr, "source_pred": row["source_pred"],
                                     "followup_pred": row[mr + "_pred"], "copied_path": row[mr + "_copy_path"]})
    os.replace(temp, path)


def run_find(model_name, data_dir, output_root, max_images=None, resume=None,
             local_model=None, progress_every=100, predict=None):
    all_paths = image_paths(data_dir)
    paths = all_paths[:max_images] if max_images is not None else all_paths
    config = experiment_config(model_name, "find", local_model)
    config.update(data_dir=str(Path(data_dir).resolve()), max_images=max_images,
                  available_images=len(all_paths),
                  files=[(p.name, p.stat().st_size, p.stat().st_mtime_ns) for p in paths])
    # JSON arrays use lists; normalize tuples for exact resume comparisons.
    config = json.loads(json.dumps(config))
    log = RunLog(output_root, resume, config, FIND_FIELDS)
    done = {row["image"] for row in log.rows}
    if len(done) != len(log.rows) or not done.issubset({p.name for p in paths}):
        log.close()
        raise ValueError("Duplicate/unexpected images in existing find results")
    started = time.perf_counter()
    state, error, meter = "running", "", None
    print(f"{model_name} find: {len(paths)}/{len(all_paths)} images; output: {log.directory}", flush=True)
    try:
        if len(done) < len(paths):
            meter = PredictionMeter(predict if predict is not None else load_model(model_name, local_model))
        for index, path in enumerate(paths, 1):
            if path.name in done:
                continue
            item_started = time.perf_counter()
            row = {"model": MODEL_IDS[model_name], "image": path.name, "source_path": str(path.resolve()),
                   "status": "image_error", "inference_calls": 0}
            try:
                image, size, digest = read_image(path)
            except (OSError, ValueError) as exc:
                row["error"] = str(exc)
            else:
                ids = meter(np.stack([image] + [apply_mr(image, mr) for mr in MR_NAMES]))
                label = int(ids[0])
                row.update(source_sha256=digest, source_pred=label, original_width=size[0],
                           original_height=size[1], I_size_pixels=image.shape[0] * image.shape[1],
                           inference_calls=4)
                for mr, followup in zip(MR_NAMES, map(int, ids[1:])):
                    violation = label != followup
                    row[mr + "_pred"], row[mr + "_violation"] = followup, violation
                    if violation:
                        copied = log.directory / mr / path.name
                        copied.parent.mkdir(exist_ok=True)
                        shutil.copy2(path, copied)
                        if hashlib.sha256(copied.read_bytes()).hexdigest() != digest:
                            raise RuntimeError(f"Source changed while copying: {path}")
                        row[mr + "_copy_path"] = str(copied.resolve())
                row["any_violation"] = any(row[mr + "_violation"] for mr in MR_NAMES)
                row["status"] = "failure" if row["any_violation"] else "no_failure"
            row["execution_time_seconds"] = round(time.perf_counter() - item_started, 6)
            log.append(row)
            if index == 1 or index % progress_every == 0 or index == len(paths):
                export_failures(log)
                print(f"  {model_name} find: {len(log.rows)}/{len(paths)} images", flush=True)
        state = "complete" if all(r["status"] != "image_error" for r in log.rows) else "complete_with_image_errors"
    except KeyboardInterrupt:
        state = "interrupted"
        raise
    except Exception as exc:
        state, error = "failed", str(exc)
        raise
    finally:
        log.close()
        export_failures(log)
        counts = {mr: sum(r[mr + "_violation"] == "True" for r in log.rows) for mr in MR_NAMES}
        summary = {"status": state, "model": MODEL_IDS[model_name], "available_images": len(all_paths),
                   "planned_images": len(paths), "processed_images": len(log.rows),
                   "failed_unique_images": sum(r["any_violation"] == "True" for r in log.rows),
                   "failed_pairs": sum(counts.values()), "failures_by_mr": counts,
                   "image_errors": sum(r["status"] == "image_error" for r in log.rows),
                   "all_dataset_images_tested": state == "complete" and len(log.rows) == len(all_paths),
                   "inference_calls": sum(int(r["inference_calls"]) for r in log.rows),
                   "session_elapsed_seconds": round(time.perf_counter() - started, 6), "error": error}
        write_json(log.directory / "summary.json", summary)
    print(f"{model_name}: {summary['failed_unique_images']} failing images, {summary['failed_pairs']} MR pairs", flush=True)
    return log.directory


def load_failures(csv_path, model_name):
    rows = read_csv(csv_path)
    seen = set()
    for row in rows:
        if row.get("model") != MODEL_IDS[model_name]:
            raise ValueError(f"Failure list belongs to {row.get('model')}, expected {MODEL_IDS[model_name]}")
        name, mr = row.get("image", ""), row.get("mr")
        if not name or Path(name).name != name or mr not in MR_NAMES:
            raise ValueError("Failure list contains an invalid image name or MR")
        label, followup = int(row["source_pred"]), int(row["followup_pred"])
        max_classes = 1001 if model_name == "resnet" else 1000
        if not (0 <= label < max_classes and 0 <= followup < max_classes) or label == followup:
            raise ValueError("Failure list contains invalid labels or a non-failing pair")
        if (name, mr) in seen:
            raise ValueError(f"Duplicate failure pair: {name}/{mr}")
        seen.add((name, mr))
    # Header must still identify a failures file when there are zero failures.
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream), [])
    if not {"model", "image", "source_path", "mr", "source_pred", "followup_pred", "copied_path"}.issubset(header):
        raise ValueError("Input must be failures.csv, not results.csv")
    return rows


def latest_failures(model_name):
    candidates = []
    roots = [ROOT / "mr_failures" / model_name]
    if model_name == "resnet":
        roots.append(ROOT / "mr_failures")  # Existing find_mr_failures.py output.
    for root in roots:
        if not root.exists():
            continue
        for run in root.iterdir():
            if not run.is_dir() or not (run / "failures.csv").is_file():
                continue
            try:
                summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
                metadata = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            model = metadata.get("config", {}).get("model", metadata.get("model_name"))
            if summary.get("status") == "complete" and model == MODEL_IDS[model_name]:
                candidates.append((bool(summary.get("all_dataset_images_tested")), run.name, run / "failures.csv"))
    if not candidates:
        raise FileNotFoundError(f"No completed {model_name} screening run; run {model_name}_find_failures.py first")
    return max(candidates)[2]


def failure_image_path(row, csv_path):
    for key in ("copied_path", "source_path"):
        if row.get(key):
            path = Path(row[key])
            if not path.is_absolute():
                path = csv_path.parent / path
            if path.is_file():
                return path
    raise FileNotFoundError(f"Neither copied nor source image exists: {row['image']}")


def save_dd(run_dir, row, input_path, image, result):
    folder = run_dir / row["mr"]
    filename = row["image"] + ".png"
    paths = {"original_copy_path": folder / "originals" / row["image"],
             "I_path": folder / "I" / filename, "I_prime_path": folder / "I_prime" / filename,
             "MR_I_prime_path": folder / "MR_I_prime" / filename, "mask_path": folder / "masks" / filename}
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_path, paths["original_copy_path"])
    for key, array in (("I_path", image), ("I_prime_path", result["prime"]),
                       ("MR_I_prime_path", result["followup"]),
                       ("mask_path", result["mask"].astype(np.uint8) * 255)):
        Image.fromarray(array).save(paths[key])
    return {key: str(path.resolve()) for key, path in paths.items()}


def run_dd(model_name, failures_csv, output_root, max_pairs=None, resume=None,
           local_model=None, progress_every=10, predict=None):
    failures_csv = Path(failures_csv).resolve()
    all_failures = load_failures(failures_csv, model_name)
    failures = all_failures[:max_pairs] if max_pairs is not None else all_failures
    config = experiment_config(model_name, "dd", local_model)
    config.update(failures_csv=str(failures_csv), failures_sha256=hashlib.sha256(failures_csv.read_bytes()).hexdigest(),
                  max_pairs=max_pairs, mask_fill="black",
                  quickshift={"kernel_size": 4, "max_dist": 200, "ratio": 0.2, "rng": 42})
    log = RunLog(output_root, resume, config, DD_FIELDS)
    done = {(r["image"], r["mr"]) for r in log.rows}
    allowed = {(r["image"], r["mr"]) for r in failures}
    if len(done) != len(log.rows) or not done.issubset(allowed):
        log.close()
        raise ValueError("Duplicate/unexpected pairs in existing DD results")
    started = time.perf_counter()
    state, error, meter = "running", "", None
    print(f"{model_name} DD: {len(failures)}/{len(all_failures)} failure pairs from {failures_csv}", flush=True)
    print(f"Output: {log.directory}", flush=True)
    try:
        if len(done) < len(failures):
            meter = PredictionMeter(predict if predict is not None else load_model(model_name, local_model))
        for index, failure in enumerate(failures, 1):
            if (failure["image"], failure["mr"]) in done:
                continue
            item_started = time.perf_counter()
            row = {"model": MODEL_IDS[model_name], "image": failure["image"], "mr": failure["mr"],
                   "source_path": failure["source_path"], "source_pred": failure["source_pred"],
                   "screen_followup_pred": failure["followup_pred"], "status": "image_error",
                   "test_calls": 0, "inference_calls": 0}
            try:
                input_path = failure_image_path(failure, failures_csv)
                image, size, digest = read_image(input_path)
            except (OSError, ValueError) as exc:
                row["error"] = str(exc)
            else:
                row.update(input_path=str(input_path.resolve()), source_sha256=digest,
                           original_width=size[0], original_height=size[1], I_size_pixels=image.shape[0] * image.shape[1])
                if failure.get("source_sha256") and failure["source_sha256"] != digest:
                    row.update(status="input_changed", error="Input bytes differ from the screening record")
                else:
                    segments = segment_image(image)
                    result = reduce_for_mr(image, segments, black_background(image), failure["mr"],
                                           int(failure["source_pred"]), meter)
                    row.update({key: value for key, value in result.items() if key in DD_FIELDS})
                    if result["status"] == "selected":
                        row.update(save_dd(log.directory, row, input_path, image, result))
            # Per-pair wall time: input reading, segmentation, DD/audit and saving;
            # model initialization and the earlier find stage are excluded.
            row["execution_time_seconds"] = round(time.perf_counter() - item_started, 6)
            log.append(row)
            print(f"  {index}/{len(failures)} {failure['image']} {failure['mr']}: {row['status']}", flush=True)
        state = "complete" if all(r["status"] == "selected" for r in log.rows) else "complete_with_rejections"
    except KeyboardInterrupt:
        state = "interrupted"
        raise
    except Exception as exc:
        state, error = "failed", str(exc)
        raise
    finally:
        log.close()
        selected = [r for r in log.rows if r["status"] == "selected"]
        summary = {"model": MODEL_IDS[model_name], "status": state, "available_failure_pairs": len(all_failures),
                   "planned_pairs": len(failures), "processed_pairs": len(log.rows), "selected_pairs": len(selected),
                   "selected_unique_images": len({r["image"] for r in selected}),
                   "selected_by_mr": {mr: sum(r["mr"] == mr for r in selected) for mr in MR_NAMES},
                   "rejections_by_status": {s: sum(r["status"] == s for r in log.rows)
                       for s in sorted({r["status"] for r in log.rows} - {"selected"})},
                   "test_calls": sum(int(r["test_calls"]) for r in log.rows),
                   "inference_calls": sum(int(r["inference_calls"]) for r in log.rows),
                   "execution_time_seconds": round(sum(float(r["execution_time_seconds"]) for r in log.rows), 6),
                   "session_elapsed_seconds": round(time.perf_counter() - started, 6), "error": error}
        write_json(log.directory / "summary.json", summary)
    print(f"{model_name}: {len(selected)} DD results; CSV: {log.directory / 'results.csv'}", flush=True)
    return log.directory


def stage_main(model_name, stage, argv=None):
    parser = argparse.ArgumentParser(description=(
        f"{MODEL_IDS[model_name]}: " + ("find initial MR failures only" if stage == "find" else "DD only the recorded failure pairs")
        + ". MRs: horizontal flip, +5 and -5 degrees; no ground-truth labels."))
    parser.add_argument("--output-dir", type=Path, help="Parent directory for timestamped output runs")
    parser.add_argument("--resume", type=Path, metavar="RUN_DIR", help="Resume this stage's interrupted run")
    if model_name == "resnet":
        parser.add_argument("--local-model", type=Path, help="Local directory containing the same ResNet SavedModel")
    if stage == "find":
        parser.add_argument("--data-dir", "--input-dir", dest="data_dir", type=Path)
        parser.add_argument("--max-images", type=int, help="First N test images; omit for all")
        parser.add_argument("--progress-every", type=int, default=100)
    else:
        parser.add_argument("--failures", type=Path, help="failures.csv or its run directory; default: latest completed full screening")
        parser.add_argument("--max-pairs", type=int, help="First N failure pairs; omit for all")
    args = parser.parse_args(argv)
    try:
        previous = json.loads((args.resume / "metadata.json").read_text(encoding="utf-8"))["config"] if args.resume else {}
        local_model = getattr(args, "local_model", None) or previous.get("local_model")
        if local_model and not (Path(local_model) / "saved_model.pb").is_file():
            raise ValueError("--local-model must contain saved_model.pb")
        if stage == "find":
            limit = args.max_images if args.max_images is not None else previous.get("max_images")
            if (limit is not None and limit < 1) or args.progress_every < 1:
                raise ValueError("--max-images and --progress-every must be positive")
            data = args.data_dir or Path(previous.get("data_dir", ROOT / "tiny-imagenet-200" / "test" / "images"))
            output = args.output_dir or ROOT / "mr_failures" / model_name
            if output.resolve() == data.resolve() or data.resolve() in output.resolve().parents:
                raise ValueError("Output must be outside the input image directory")
            run_find(model_name, data, output, limit, args.resume, local_model, args.progress_every)
        else:
            limit = args.max_pairs if args.max_pairs is not None else previous.get("max_pairs")
            if limit is not None and limit < 1:
                raise ValueError("--max-pairs must be positive")
            failures = args.failures or previous.get("failures_csv") or latest_failures(model_name)
            failures = Path(failures)
            if failures.is_dir():
                failures = failures / "failures.csv"
            output = args.output_dir or ROOT / "dd_results_black" / model_name
            run_dd(model_name, failures, output, limit, args.resume, local_model)
        return 0
    except KeyboardInterrupt:
        print("Interrupted. Completed rows are preserved; use --resume RUN_DIR to continue.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


def find_main(model_name, argv=None):
    return stage_main(model_name, "find", argv)


def dd_main(model_name, argv=None):
    return stage_main(model_name, "dd", argv)
