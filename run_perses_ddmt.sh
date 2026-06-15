#!/usr/bin/env bash
set -euo pipefail

# Delta Debugging with Metamorphic Testing (DDMT) oracle for Perses
# Wrapper for run_exp_parallel_c.py with the DDMT metamorphic testing oracle.
# Automatically handles oracle script path; no GOODCC reference compiler needed.
#
# Usage:
#   bash run_perses_ddmt.sh -sf BENCHMARKS -so ORACLE_MAP -r REDUCER -i ITER -j JOBS -o OUTPUT
#
# Parameters:
#   -sf BENCHMARKS    : File listing test case directories (one per line)
#   -so ORACLE_MAP    : File mapping test cases to oracle scripts (or just pass the oracle script)
#   -r REDUCER        : Reducer choice (perses_ddmin, perses_probdd, etc.)
#   -i ITERATIONS     : Number of iterations per test case
#   -j JOBS           : Number of parallel jobs
#   -o OUTPUT_DIR     : Output directory for results
#
# Example:
#   bash run_perses_ddmt.sh \
#     -sf my_test_cases.txt \
#     -so my_oracle_map.txt \
#     -r perses_ddmin \
#     -i 1 -j 5 -o result_ddmt

pip3 install --quiet 'libclang==11.0' 2>/dev/null || true

python3 run_exp_parallel_c.py "$@"
