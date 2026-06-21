#!/usr/bin/env bash
set -o pipefail

EMI_FILE=${EMI_FILE:-small_emi.c}
ORION_PY=${ORION_PY:-/tmp/WeightDD/hdd-mt-example/gcc-66186/orion_ast.py}
if [ ! -f "$ORION_PY" ] ; then
  ORION_PY=/home/ubuntu/mtdd/WeightDD/hdd-mt-example/gcc-66186/orion_ast.py
fi

# Coverage compiler used by orion_ast.py.
# Default: system gcc.  Set to BADCC base command (e.g. "gcc-4.8.0 -m32 -lm")
# to run the experiment without any system-gcc dependency.
EMI_COV_CMD=${EMI_COV_CMD:-"gcc -lm"}
# gcov binary matching the coverage compiler.
# Use versioned gcov when EMI_COV_CMD uses an older gcc, e.g.
# EMI_GCOV=/compilers/gcc/4.8.0/bin/gcov
EMI_GCOV=${EMI_GCOV:-"gcov"}

# Set EMI_CRASH_FALLBACK=0 to use pure MT divergence only (approach A):
#   oracle passes only when BADCC behaves differently on P vs P'.
# Set EMI_CRASH_FALLBACK=1 (default) to also accept a crash on P as evidence
# of a real bug when EMI was generated (approach A+B):
#   useful for BADCC2/BADCC1 where both P and P' often crash the same way.
EMI_CRASH_FALLBACK=${EMI_CRASH_FALLBACK:-1}

# Install libclang once if needed (orion_ast.py requires it)
python3 -c 'import clang.cindex' 2>/dev/null || \
  pip3 install --quiet 'libclang==11.0' 2>/dev/null || true

collect_from_var() {
  local src_var="$1"
  local dst_var="$2"
  if ! declare -p "$src_var" >/dev/null 2>&1; then
    return 0
  fi

  local -n src_ref="$src_var"
  local -n dst_ref="$dst_var"
  local decl
  decl=$(declare -p "$src_var" 2>/dev/null || true)
  if [[ "$decl" == declare\ -a* ]]; then
    local v
    for v in "${src_ref[@]}"; do
      if [[ -n "$v" ]]; then
        dst_ref+=("$v")
      fi
    done
  else
    if [[ -n "${src_ref-}" ]]; then
      dst_ref+=("${src_ref}")
    fi
  fi
}


run_sig() {
  local cc="$1"
  local src="$2"
  local tag="$3"
  local mode="${4-}"

  rm -f ./t "${tag}.cc.out" "${tag}.run.out"

  local cret=0
  if [[ -n "$mode" ]]; then
    timeout -s 9 "$TIMEOUTCC" $cc $CFLAG $mode "$src" > "${tag}.cc.out" 2>&1
    cret=$?
  else
    timeout -s 9 "$TIMEOUTCC" $cc $CFLAG "$src" > "${tag}.cc.out" 2>&1
    cret=$?
  fi

  if grep -Eiq 'internal compiler error|please attach the following files to the bug report' "${tag}.cc.out" ; then
    echo "ICE"
    return 0
  fi

  if [[ $cret -ne 0 ]]; then
    echo "CFAIL:${cret}"
    return 0
  fi

  if [[ ! -x ./t ]]; then
    echo "COMPILE_OK_NO_BIN"
    return 0
  fi

  timeout -s 9 "$TIMEOUTEXE" ./t > "${tag}.run.out" 2>&1
  local rret=$?
  if [[ $rret -ne 0 ]]; then
    echo "RUNFAIL:${rret}"
    return 0
  fi

  local h
  h=$(sha256sum "${tag}.run.out" | awk '{print $1}')
  echo "OK:${h}"
}

if [[ ! -f "$CFILE" ]] ; then
  exit 1
fi

declare -a BAD_CMDS=()
collect_from_var BADCC BAD_CMDS
collect_from_var BADCC1 BAD_CMDS
collect_from_var BADCC2 BAD_CMDS
collect_from_var BADCC3 BAD_CMDS
if [[ ${#BAD_CMDS[@]} -eq 0 ]] ; then
  exit 1
fi

declare -a MODE_LIST=()
collect_from_var MODE MODE_LIST
if [[ ${#MODE_LIST[@]} -eq 0 ]] ; then
  MODE_LIST=("")
fi

# orion_ast.py removes only provably dead code (AST-exact + gcov).
# Two ways the oracle can pass:
#
# (A) MT divergence (BADCC3 / wrong-result bugs):
#     BADCC(P) output != BADCC(P') output — compiler treats equivalent
#     programs differently, which is the bug.
#
# (B) Crash + valid EMI (BADCC2 / execution-crash bugs, BADCC1 / ICE bugs):
#     EMI generation requires system gcc to compile and *run* P successfully
#     for coverage, proving P is well-defined.  If BADCC then crashes on P,
#     that is a genuine compiler bug, not UB.  Signals:
#       RUNFAIL:<N>  — binary crash / timeout (BADCC2)
#       ICE          — internal compiler error (BADCC1)
#       CFAIL:<N>    — compiler non-zero exit without ICE (BADCC1 hangs, etc.)
#
# For BADCC3 only (A) fires; B_ORIG is always "OK:<hash>" (wrong but non-zero-exit).
# For BADCC1/2 (B) fires even when both P and P' crash the same way.

EMI_MAX_ATTEMPTS=${EMI_MAX_ATTEMPTS:-5}
ORACLE_PASS=0

# Infer whether condition A requires B_ORIG to still be a crash/ICE signal.
# BADCC1/BADCC2 bugs: crash must persist — prevents drift to spurious hash
#   divergence after the crash disappears during reduction.
# BADCC3 bugs (wrong result): any hash divergence is the bug signal.
# Override with EMI_A_REQUIRE_CRASH=0/1 if needed.
declare -a _crash_type_cmds=()
collect_from_var BADCC1 _crash_type_cmds
collect_from_var BADCC2 _crash_type_cmds
_a_require_crash_default=0
[[ ${#_crash_type_cmds[@]} -gt 0 ]] && _a_require_crash_default=1
_a_require_crash=${EMI_A_REQUIRE_CRASH:-$_a_require_crash_default}

for _attempt in $(seq 1 "$EMI_MAX_ATTEMPTS") ; do
  rm -f "$EMI_FILE"
  python3 "$ORION_PY" --prog_file "$CFILE" \
    --cov-cmd "$EMI_COV_CMD" --gcov "$EMI_GCOV" > /dev/null 2>&1 || true
  # If no EMI generated, system gcc couldn't run CFILE — skip this attempt.
  [[ ! -s "$EMI_FILE" ]] && continue

  for bad in "${BAD_CMDS[@]}" ; do
    for mode in "${MODE_LIST[@]}" ; do
      B_ORIG=$(run_sig "$bad" "$CFILE" bad_orig "$mode")

      # (B) Crash/ICE on original + valid EMI proves bug is real.
      # Skipped when EMI_CRASH_FALLBACK=0 (pure MT divergence, approach A).
      if [[ $EMI_CRASH_FALLBACK -eq 1 ]] && \
         [[ "$B_ORIG" =~ ^(RUNFAIL:|ICE|CFAIL:) ]] ; then
        ORACLE_PASS=1
        break 2
      fi

      # (A) MT divergence signal.
      # For BADCC3 (wrong result): any hash divergence is the bug — the compiler
      #   treats equivalent programs differently, which is the miscompilation.
      # For BADCC2/BADCC1 (crash/ICE): require B_ORIG still crashes so reduction
      #   cannot drift to spurious hash divergence after the crash disappears.
      B_EMI=$(run_sig "$bad" "$EMI_FILE" bad_emi "$mode")
      if [[ "$B_ORIG" != "$B_EMI" ]] ; then
        if [[ $_a_require_crash -eq 0 ]] || \
           [[ "$B_ORIG" =~ ^(RUNFAIL:|ICE|CFAIL:) ]] ; then
          ORACLE_PASS=1
          break 2
        fi
      fi
    done
  done

  [[ $ORACLE_PASS -eq 1 ]] && break
done

if [[ $ORACLE_PASS -ne 1 ]] ; then
  exit 1
fi

exit 0