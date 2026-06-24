# Perses-DDMT: Delta Debugging with Metamorphic Testing

This patch adds **Metamorphic Testing (MT) oracle** support to Perses delta debugging.

## What's New

- **`ddmt/emi_predicate.sh`** — MT oracle implementation using EMI (Equivalent Mutant Insertion)
- **`ddmt/orion_ast.py`** — AST-based EMI generator (provably correct dead code removal)
- **`run_perses_ddmt.sh`** — Convenience wrapper script

## No More GOODCC Required

Unlike differential testing oracles, the MT oracle:
- ✅ Works without a reference "good" compiler (GOODCC)
- ✅ Uses only the buggy compiler (BADCC) + system `gcc` for coverage
- ✅ Applies to compiler bugs with wrong results, crashes, or ICE

## How It Works

The oracle takes a program P and generates an equivalent variant P' using EMI:

1. **EMI Generation**: `orion_ast.py` removes provably dead code (AST-exact + gcov coverage)
2. **Metamorphic Testing**: Runs both P and P' on the compiler (BADCC)
3. **Oracle Decision**:
   - **Approach A (MT divergence)**: BADCC(P) ≠ BADCC(P') → bug confirmed
   - **Approach B (Crash persistence)**: BADCC crashes on P with valid EMI → bug confirmed

## Quick Start

### Run with provided benchmark list

An example benchmark list with 8 test cases is included as `benchmark_sets_example.txt`:

```bash
bash run_perses_ddmt.sh \
  -sf benchmark_sets_example.txt \
  -r perses_ddmin \
  -i 1 -j 5 \
  -o result_ddmt
```

Or create your own test case list:

```bash
cat > my_test_cases.txt << 'EOF'
c_benchmarks/gcc-66186
c_benchmarks/clang-21582
EOF

bash run_perses_ddmt.sh \
  -sf my_test_cases.txt \
  -r perses_ddmin \
  -i 1 -j 5 \
  -o result_ddmt
```

Each test case already has compiler specs in its `r.sh` script (BADCC3, BADCC2, BADCC1).

### Run with Docker (recommended)

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

### Analyze results

```bash
# Convert to CSV
python3 convert_result_to_csv.py -d result_ddmt/perses_ddmin_0/* -o results.csv

# Or compare with baseline
python3 compare_results.py \
  --baseline result_baseline \
  --treatment result_ddmt \
  --label-base "Perses (Differential Test)" \
  --label-treat "Perses-DDMT (MT Oracle)"
```

## Configuration

### Environment Variables

Set these before running to customize oracle behavior:

| Variable | Default | Purpose |
|----------|---------|---------|
| `EMI_MAX_ATTEMPTS` | 5 | Retries for EMI generation per oracle call |
| `EMI_CRASH_FALLBACK` | 1 | Enable crash+valid-EMI condition (Approach B) |
| `EMI_A_REQUIRE_CRASH` | auto | Force (A) to require B_ORIG to still be a crash |
| `EMI_COV_CMD` | `gcc -lm` | Coverage compiler command |
| `EMI_GCOV` | `gcov` | gcov binary matching coverage compiler |

### Examples

**Pure MT divergence (Approach A only, no crash fallback):**
```bash
EMI_CRASH_FALLBACK=0 bash run_perses_ddmt.sh ...
```

**Aggressive EMI pruning (smaller EMIs, less stable):**
```bash
EMI_PRUNE_PROB=0.8 bash run_perses_ddmt.sh ...
```

**More retries for hard-to-trigger divergence:**
```bash
EMI_MAX_ATTEMPTS=10 bash run_perses_ddmt.sh ...
```

## Oracle Mechanism

### Condition A: Metamorphic Divergence

The compiler's behavior differs on equivalent programs:
- BADCC(P) output ≠ BADCC(P') output → miscompilation detected

**When it fires:** Wrong-result compiler bugs (always), crash/ICE bugs (if behavior persists)

**Why it's correct:** Equivalent programs must produce identical output; divergence proves the compiler is wrong.

### Condition B: Crash + Valid EMI

The compiler crashes, but we proved P is valid via EMI generation:
- System `gcc` compiles and runs P successfully → P is well-defined
- BADCC crashes (ICE, segfault, timeout) on P → genuine bug, not undefined behavior

**When it fires:** Crash/ICE bugs (when BADCC(P) is a crash signal)

**Why it's correct:** Crash on a valid, well-defined program is a compiler bug.

## Requirements

- **Python 3** with `libclang` (auto-installed by script)
- **System `gcc`** (for coverage collection via gcov)
- **Test cases** in WeightDD with compiler specs already in each `c_benchmarks/[case]/r.sh`

## Troubleshooting

**"EMI generation failed; all attempts skipped"**
- System `gcc` cannot compile/run your test case
- Check for undefined behavior or missing dependencies

**"Oracle always returns 0 (fails on all variants)"**
- EMI generation is failing silently
- Try increasing `EMI_MAX_ATTEMPTS=20` or set `EMI_PRUNE_PROB=0.3` (less aggressive)

**"Reduction stops early (not reaching fixpoint)"**
- Normal behavior — may indicate the reduced code is correct
- Run multiple iterations (`-i 5`) to reduce randomness

## References

- **Paper**: "Delta Debugging with Metamorphic Testing" (pending publication)
- **EMI**: Orion-style equivalent mutant insertion for compiler testing
- **Coverage**: gcov-based dead code analysis for provably correct EMI

## Citation

If you use this oracle in your research, please cite:

```
[Pending publication details]
```
