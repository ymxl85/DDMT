# Apply Perses-DDMT Patch to WeightDD

This patch adds **Metamorphic Testing (MT) oracle** support to Perses delta debugging.

## What the patch adds

- `ddmt/emi_predicate.sh` — MT oracle implementation
- `ddmt/orion_ast.py` — AST-based EMI generator  
- `run_perses_ddmt.sh` — Convenience wrapper script
- `benchmark_sets_example.txt` — 8 pre-configured test cases
- `perses_ddmt.md` — Full documentation

## How to apply

```bash
# 1. Clone WeightDD from GitHub
git clone https://github.com/weightdd/WeightDD.git
cd WeightDD

# 2. Apply the patch
git apply perses-ddmt.patch

# 3. Run the benchmark
bash run_perses_ddmt.sh \
  -sf benchmark_sets_example.txt \
  -r perses_ddmin \
  -i 1 -j 5 \
  -o result_ddmt
```

Or with Docker:

```bash
docker run --rm --cap-add SYS_PTRACE \
  -v $(pwd):/tmp/work \
  wddartifact/wdd:latest \
  bash -c "cd /tmp/work && \
    pip3 install -q libclang==11.0 && \
    bash run_perses_ddmt.sh \
      -sf benchmark_sets_example.txt \
      -r perses_ddmin \
      -i 1 -j 5 \
      -o result_ddmt"
```

## What it does

The MT oracle:
- ✅ Works without a reference "good" compiler (GOODCC)
- ✅ Uses only system `gcc` for coverage + the buggy compiler under test
- ✅ Generates equivalent program variants (EMI) to detect compiler bugs

## For more details

See `perses_ddmt.md` after applying the patch.
