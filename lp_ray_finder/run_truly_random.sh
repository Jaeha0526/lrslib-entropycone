#!/bin/bash
#SBATCH --job-name=ray_truly_random_v3
#SBATCH --output=results/ray_truly_random_v3_%j.out
#SBATCH --error=results/ray_truly_random_v3_%j.err
#SBATCH --time=10:00:00
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:1

# Load modules
module load cuda/11.8.0 2>/dev/null || true

# Print job info
echo "Starting MAXIMUM ENTROPY random ray finder (v3) at $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Key improvements:"
echo "  - Microsecond precision timing for seed generation"
echo "  - Multiple entropy sources: attempt + time + PID + hash"
echo "  - Fixed pseudo-random cycling issue"

# Change to the lp_ray_finder directory (absolute path)
cd /resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder

echo "Working directory: $(pwd)"
echo "Contents: $(ls -la core/ | wc -l) files in core/"

# Run the maximum entropy random violation finder
python core/ray_finder_random_violations_truly_random.py random 30

echo "Job completed at $(date)"
echo "Results saved in: lp_ray_finder/results/"