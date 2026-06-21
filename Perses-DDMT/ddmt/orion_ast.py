#!/usr/bin/env python3
"""
orion_ast.py - AST-based EMI variant generator for C programs.

Uses libclang for exact function/block boundaries + gcov coverage data.
Removals are at precise AST node boundaries, so output is guaranteed
syntactically valid C.

Since only provably dead code (never-executed per gcov) is removed, the
EMI is semantically equivalent by construction for the tested input.
No reference compiler (GOODCC) is needed to validate the output.

Dependencies (no docker patching required):
  pip3 install 'libclang==11.0'
  libclang.so: /compilers/clang/trunk/lib/libclang.so (clang 10, in wdd docker)
"""

import os
import re
import random
import argparse

PRUNE_PROB = float(os.environ.get("EMI_PRUNE_PROB", "0.5"))
LIBCLANG_SO = os.environ.get(
    "LIBCLANG_SO", "/compilers/clang/trunk/lib/libclang.so"
)

# Initialize libclang once at import time so set_library_file is never
# called twice in the same process (it raises on the second call).
try:
    import clang.cindex as _cx
except ImportError:
    import subprocess, sys
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet", "libclang==11.0"]
    )
    import clang.cindex as _cx

_cx.Config.set_library_file(LIBCLANG_SO)


def collect_coverage(prog_file, cov_cmd="gcc -lm", gcov_bin="gcov"):
    """Compile with gcov instrumentation, run, parse .gcov output."""
    os.system(
        cov_cmd + " -fprofile-arcs -ftest-coverage "
        + prog_file
        + " -o a.out 2>/dev/null"
    )
    ret = os.system("./a.out > /dev/null 2>&1")
    if ret != 0:
        return set(), set()
    os.system(gcov_bin + " " + prog_file + " > /dev/null 2>&1")

    covered, uncovered = set(), set()
    gcov_file = prog_file + ".gcov"
    try:
        with open(gcov_file) as f:
            for line in f:
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                count_str = parts[0].strip()
                try:
                    lineno = int(parts[1].strip())
                except ValueError:
                    continue
                if count_str == "#####":
                    uncovered.add(lineno)
                elif count_str not in ("-", "=====", "$$$$$", ""):
                    covered.add(lineno)
    except FileNotFoundError:
        pass

    return covered, uncovered


def _all_dead(start_line, end_line, covered, uncovered):
    """True if range has executable lines and all are uncovered."""
    interior = set(range(start_line, end_line + 1))
    exec_lines = interior & (covered | uncovered)
    return bool(exec_lines) and not (exec_lines & covered)


def _collect_candidates(cursor, abs_path, covered, uncovered, cx):
    """
    Walk AST depth-first and return candidate removals as list of dicts:
      kind='function': remove entire node extent (signature + body)
      kind='block':    blank interior of COMPOUND_STMT (keep braces)
    Sorted innermost-first so outer removal check can skip contained nodes.
    """
    COMPOUND = cx.CursorKind.COMPOUND_STMT
    FUNC     = cx.CursorKind.FUNCTION_DECL

    candidates = []

    def visit(node, inside_func):
        if node.location.file and node.location.file.name != abs_path:
            return

        if node.kind == FUNC and node.is_definition():
            body = next(
                (c for c in node.get_children() if c.kind == COMPOUND), None
            )
            if body:
                interior_start = body.extent.start.line + 1
                interior_end   = body.extent.end.line   - 1
                if interior_start <= interior_end and _all_dead(
                    interior_start, interior_end, covered, uncovered
                ):
                    candidates.append({
                        "kind":  "function",
                        "start": node.extent.start.line,
                        "end":   node.extent.end.line,
                        "name":  node.spelling,
                    })
                    return  # don't recurse: whole function is a candidate
            # recurse into function body for nested block candidates
            for child in node.get_children():
                visit(child, inside_func=True)
            return

        if node.kind == COMPOUND and inside_func:
            start = node.extent.start.line + 1  # first interior line
            end   = node.extent.end.line   - 1  # last interior line
            if start <= end and _all_dead(start, end, covered, uncovered):
                candidates.append({
                    "kind":  "block",
                    "start": start,
                    "end":   end,
                    "name":  None,
                })
                return  # don't recurse: block interior is a candidate

        for child in node.get_children():
            visit(child, inside_func=inside_func)

    visit(cursor, inside_func=False)

    # innermost first: shorter ranges before longer ones
    candidates.sort(key=lambda c: c["end"] - c["start"])
    return candidates


def _still_referenced(func_name, lines, removed_lines):
    """Return True if func_name is called in any non-removed line."""
    pattern = re.compile(r"\b" + re.escape(func_name) + r"\s*\(")
    for i, line in enumerate(lines):
        if (i + 1) not in removed_lines and pattern.search(line):
            return True
    return False


def gen_variant(prog_file, lines, covered, uncovered, prune_prob):
    """Return modified line list with dead-code regions removed."""
    abs_path = os.path.abspath(prog_file)
    index = _cx.Index.create()
    tu = index.parse(abs_path, args=["-x", "c"])

    candidates = _collect_candidates(tu.cursor, abs_path, covered, uncovered, _cx)

    removed_lines  = set()   # lines to drop entirely (function removals)
    emptied_ranges = []      # (start, end) interiors to blank (block removals)

    for cand in candidates:
        start, end = cand["start"], cand["end"]

        # skip if already covered by a previously accepted removal
        if any(r[0] <= start and end <= r[1] for r in emptied_ranges):
            continue
        if start in removed_lines or end in removed_lines:
            continue

        if random.random() >= prune_prob:
            continue

        if cand["kind"] == "function":
            tentative = set(range(start, end + 1))
            if cand["name"] and _still_referenced(
                cand["name"], lines, removed_lines | tentative
            ):
                continue
            removed_lines |= tentative
        else:
            emptied_ranges.append((start, end))

    def _in_emptied(lineno):
        return any(s <= lineno <= e for s, e in emptied_ranges)

    return [
        line
        for i, line in enumerate(lines)
        if (i + 1) not in removed_lines and not _in_emptied(i + 1)
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate an AST-based EMI variant of a C program."
    )
    parser.add_argument("--prog_file", required=True, help="Source C file")
    parser.add_argument(
        "--compiler",
        default="gcc",
        help="Unused; kept for drop-in compatibility with orion.py",
    )
    parser.add_argument(
        "--cov-cmd",
        default=os.environ.get("EMI_COV_CMD", "gcc -lm"),
        help="Compiler command for gcov coverage (default: 'gcc -lm'). "
             "Use BADCC base compiler to avoid system-gcc dependency, e.g. "
             "'gcc-4.8.0 -m32 -lm'. Optimization flags are NOT added here.",
    )
    parser.add_argument(
        "--gcov",
        default=os.environ.get("EMI_GCOV", "gcov"),
        help="gcov binary matching the coverage compiler (default: 'gcov'). "
             "Use versioned gcov for older compilers, e.g. "
             "'/compilers/gcc/4.8.0/bin/gcov'.",
    )
    args = parser.parse_args()

    with open(args.prog_file) as f:
        lines = f.readlines()

    covered, uncovered = collect_coverage(args.prog_file, args.cov_cmd, args.gcov)
    if not covered and not uncovered:
        raise SystemExit(1)

    MAX_TRIES = 10
    for _ in range(MAX_TRIES):
        variant = gen_variant(args.prog_file, lines, covered, uncovered, PRUNE_PROB)
        with open("small_emi.c", "w") as f:
            f.writelines(variant)
        if os.system(args.cov_cmd + " -o /dev/null small_emi.c 2>/dev/null") == 0:
            raise SystemExit(0)

    if os.path.exists("small_emi.c"):
        os.remove("small_emi.c")
    raise SystemExit(1)
