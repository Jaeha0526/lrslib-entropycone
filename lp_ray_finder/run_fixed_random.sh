#!/bin/bash
#SBATCH --job-name=ray_fixed_random_v2
#SBATCH --output=results/ray_fixed_random_v2_%j.out
#SBATCH --error=results/ray_fixed_random_v2_%j.err
#SBATCH --time=10:00:00
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:1

# Load modules
module load cuda/11.8.0 2>/dev/null || true

# Print job info
echo "Starting FIXED random ray finder (v2 - results in lp_ray_finder) at $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Output directory: lp_ray_finder/results/"
echo "Key improvements:"
echo "  - Results stored inside lp_ray_finder for future repo separation"
echo "  - Relative paths for cross-platform compatibility"
echo "  - Fixed random seed synchronization"

# Change to the lp_ray_finder directory (absolute path)
cd /resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder

echo "Working directory: $(pwd)"
echo "Contents: $(ls -la core/ | wc -l) files in core/"

# Run the fixed random violation finder
python core/ray_finder_random_violations_fixed.py random 30

echo "Job completed at $(date)"
echo "Results saved in: lp_ray_finder/results/"