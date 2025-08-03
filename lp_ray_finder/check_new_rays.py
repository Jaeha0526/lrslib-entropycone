#!/usr/bin/env python3
"""
Check if the "new" rays found by phase3_no_limit are actually new
"""

import numpy as np

# Load existing rays
existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
print(f"Loaded {len(existing_rays)} existing rays")

# Normalize all existing rays
existing_normalized = []
for ray in existing_rays:
    existing_normalized.append(ray / np.linalg.norm(ray))
existing_normalized = np.array(existing_normalized)

# Load "new" rays if saved
try:
    new_rays = np.loadtxt('new_rays_full_s7.txt')
    if new_rays.ndim == 1:
        new_rays = new_rays.reshape(1, -1)
    print(f"\nLoaded {len(new_rays)} 'new' rays")
    
    actually_new = 0
    for i, new_ray in enumerate(new_rays):
        new_norm = new_ray / np.linalg.norm(new_ray)
        
        # Check against all existing
        max_dot = np.max(np.abs(existing_normalized @ new_norm))
        
        if max_dot < 0.9999:
            actually_new += 1
            print(f"\nRay {i+1} is ACTUALLY NEW!")
            print(f"  Max dot product: {max_dot:.6f}")
            print(f"  Ray: {new_ray[:10]}...")
        else:
            match_idx = np.argmax(np.abs(existing_normalized @ new_norm))
            print(f"\nRay {i+1} matches existing ray #{match_idx+1}")
            print(f"  Dot product: {max_dot:.6f}")
    
    print(f"\n\nSUMMARY: {actually_new} out of {len(new_rays)} are actually new")
    
except FileNotFoundError:
    print("No new_rays_full_s7.txt file found")
    print("\nLet's check the phase3_no_limit implementation...")
    
    # Quick check of the algorithm
    print("\nThe issue might be:")
    print("1. The dot product threshold 0.9999 might be too strict")
    print("2. The rays might need integer scaling to match")
    print("3. The constraint violations might not be checked properly")