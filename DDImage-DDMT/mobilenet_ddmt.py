"""MobileNetV2 ImageNet: DD only MobileNet's recorded MR failures.

Defaults to its latest completed full screening. Use --failures RUN_DIR,
--max-pairs N, or --resume DD_RUN_DIR as needed. Run with --help for details.
"""

from mr_pipeline_black import dd_main


if __name__ == "__main__":
    raise SystemExit(dd_main("mobilenet"))
