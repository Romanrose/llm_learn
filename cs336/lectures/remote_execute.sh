# Execute a particular lecture on remote

T=c-pliang@ad12a3ca-hn01.cloud.together.ai

echo "=== Copying to $T..."
rsync -arvz *.py gelu.cu slurm_run.sh slurm_script.sh var images trace-viewer/dist $T:spring2025-lectures || exit 1

for module in "$@"; do
  echo "=== Executing lecture $module..."
  ssh $T "(cd spring2025-lectures && ./slurm_run python execute.py -m $module)" || exit 1
done

echo "=== Copying from $T..."
rsync -arvz $T:spring2025-lectures/var/traces var || exit 1
