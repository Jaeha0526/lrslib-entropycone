#!/bin/bash
#SBATCH --job-name=ray_large_10k
#SBATCH --output=ray_large_%j.out
#SBATCH --error=ray_large_%j.err
#SBATCH --time=10:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --partition=expansion

# Load Python module if needed
module load python/3.9

# Run the large subset ray finder with 10,000 initial constraints
cd /resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder

echo "Starting large subset ray finder with 10,000 initial constraints"
echo "Time: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"

# Run with mixed selection method (50% random, 50% greedy) for better exploration
python core/ray_finder_large_subset.py mixed 30 10000

echo "Job completed at: $(date)"