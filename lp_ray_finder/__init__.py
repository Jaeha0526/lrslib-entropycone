"""
LP-Based Ray Finder for Holographic Entropy Cones

This package contains implementations for finding extreme rays in large-scale
convex cones using Linear Programming with active-set methods.

Core modules:
- core.lp_ray_finder_phase3: Main GPU-accelerated implementation
- core.ray_finder_random_violations_fixed: Fixed random violation selection
- verification.quick_s7_verification: S7 permutation verification
- utils: Utility functions for ray processing

Data:
- UNIQUE_RAYS_CONSOLIDATED/: All discovered unique rays (4300 total)
"""

__version__ = "1.0.0"
__author__ = "Jaeha Lee"

# Import main classes for easy access
try:
    from .core.lp_ray_finder_phase3 import HybridLPRayFinder, GPUConstraintManager
except ImportError:
    # Fallback if imports fail
    pass