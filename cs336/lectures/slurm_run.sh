sbatch --wait `dirname $0`/slurm_script.sh uv run "$@"
