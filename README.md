# lrslib-entropycone

Enhanced lrslib with critical bug fixes and LP-based ray finder for N=6 holographic entropy cone analysis.

## Key Achievements

- **Fixed critical startingcobasis bug** in lrslib enabling large-scale vertex enumeration
- **Discovered 155 new extreme rays** for N=6 holographic entropy cone (total: 4300 unique rays)
- **GPU-accelerated LP ray finder** with active-set methods for 8.6M constraint systems

## Repository Structure

### Core lrslib (Root Level)
- `lrslib.c`, `lrsgmp.c`, etc. - Enhanced lrslib with bug fixes
- `n6data/` - N=6 holographic entropy cone data and original 4145 rays
- `project_history.md` - Complete development history and bug fix documentation

### LP Ray Finder (`lp_ray_finder/`)
Modern Python implementation for large-scale ray discovery:

```
lp_ray_finder/
├── core/                          # Core ray finding algorithms
│   ├── lp_ray_finder_phase3.py    # GPU-accelerated main implementation
│   ├── ray_finder_random_violations_fixed.py  # Fixed random violation selection
│   └── ray_finder_enhanced_tracking.py        # Enhanced tracking version
├── demos/                         # Performance demos and comparisons
├── utils/                         # Ray processing utilities
├── verification/                  # S7 permutation verification tools
├── UNIQUE_RAYS_CONSOLIDATED/      # All 4300 discovered unique rays
│   ├── ALL_4300_UNIQUE_RAYS.txt   # Master file with all rays
│   ├── original_4145_rays.txt     # Original known rays
│   ├── aug3_129_new_rays.txt      # 129 rays discovered Aug 3
│   └── aug5_26_new_rays.txt       # 26 rays discovered Aug 5
└── README.md                      # Detailed usage guide
```

## Quick Start

### LP Ray Finder
```python
# Import main implementation
from lp_ray_finder.core.lp_ray_finder_phase3 import HybridLPRayFinder

# See lp_ray_finder/README.md for detailed usage
```

### lrslib with fixes
```bash
# Compile enhanced lrslib
make lrs

# Use with startingcobasis (now works reliably)
echo "startingcobasis 1 2 3" | ./lrs input.ine
```

## Major Discoveries

1. **lrslib startingcobasis bug**: Fixed array corruption in cobasis processing
2. **155 new extreme rays**: Verified unique S7 orbit representatives
3. **Algorithmic saturation**: Identified and fixed random seed synchronization issue
4. **Scale achievement**: Successful processing of 8.6M constraint systems

## Key Files

- `project_history.md` - Complete technical documentation of discoveries and fixes
- `lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED/` - All discovered rays with verification
- `n6data/n6_correct_s7_expansion.ine` - Full N=6 constraint system (8.6M constraints)

## Citation

If you use this enhanced lrslib or the ray discoveries, please cite:
- Original lrslib: Avis & Fukuda
- N=6 entropy cone work: [Your publications]
- Bug fixes and new rays: This repository

## Status

- ✅ lrslib bugs fixed and validated on large systems
- ✅ 155 new rays discovered and S7-verified 
- 🔄 Enhanced random ray finder testing in progress
- 📚 Ready for production use and further research