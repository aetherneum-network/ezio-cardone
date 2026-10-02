#!/bin/bash
# Runner probe, round 2: one measurement on this machine, its time, and the entries it left in its temporary folder.
# usage: bash probe/round2.sh suite13|suite14|scenarios|eval|rebuild TAG system|work
#   suite13 = the suite of v2.0.13 (main 7dde2ff, exported to a folder of its own), suite14 = the suite of this commit
#   system  = the job's default temporary folder; work = a new folder under the runner's temporary folder of the job
set -u
kind=$1 tag=$2 where=$3
W="$GITHUB_WORKSPACE"
if [ "$where" = work ]; then
  if [ "$RUNNER_OS" = Windows ]; then d="$RUNNER_TEMP\t_$tag"; else d="$RUNNER_TEMP/t_$tag"; fi
  mkdir -p "$d"
  export TEMP="$d" TMP="$d" TMPDIR="$d"
fi
count() { python -c "import os, sys; print(len(os.listdir(sys.argv[1])))" "$1"; }
tmpdir=$(python -c "import tempfile; print(tempfile.gettempdir())")
before=$(count "$tmpdir")
if [ "$kind" = suite13 ]; then cd "$RUNNER_TEMP/v2013"; else cd "$W"; fi
start=$(date +%s.%N)
case $kind in
  suite13|suite14) python "$W/probe/tim.py" "$RUNNER_TEMP/$tag.json" - ;;
  scenarios) python scenarios/run_all.py --json "$RUNNER_TEMP/$tag.json" > "$RUNNER_TEMP/$tag.out" 2>&1 ;;
  eval) python -m eval.score --suite dev --json "$RUNNER_TEMP/$tag.json" > "$RUNNER_TEMP/$tag.out" 2>&1 ;;
  rebuild) python tools/rebuild.py > "$RUNNER_TEMP/$tag.out" 2>&1 ;;
esac
rc=$?
end=$(date +%s.%N)
after=$(count "$tmpdir")
[ -f "$RUNNER_TEMP/$tag.out" ] && grep -a -E "sha256|REBUILD|never_events|Scenarios:" "$RUNNER_TEMP/$tag.out" | cut -c1-160
echo "PROBE2 $tag rc=$rc seconds=$(python -c "print(round($end - $start, 1))") temp=$tmpdir left=$((after - before))"
exit $rc
