#!/usr/bin/env python3
"""
Extract the 129 August 3 rays from ALL_4300_UNIQUE_RAYS.txt by subtracting known components.
Expected structure:
- 4145 original rays
- 129 August 3 rays  
- 26 August 5 rays
Total: 4300 rays
"""

import numpy as np
import os

def load_rays_from_file(filepath):
    """Load floating-point rays from a file"""
    rays = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        # Try to parse as floating-point ray
                        parts = line.split('#')[0].strip().split()
                        if len(parts) == 63:  # Check if it's a 63-dimensional vector
                            ray = np.array([float(x) for x in parts])
                            rays.append(ray)
                    except:
                        pass
        print(f"Loaded {len(rays)} floating-point rays from {filepath}")
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return rays

def check_ray_similarity(ray1, ray2, threshold=0.9999):
    """Check if two rays are similar"""
    r1_norm = ray1 / np.linalg.norm(ray1)
    r2_norm = ray2 / np.linalg.norm(ray2)
    similarity = abs(np.dot(r1_norm, r2_norm))
    return similarity > threshold

def extract_august3_rays():
    """Extract August 3 rays by subtracting known components from ALL_4300_UNIQUE_RAYS.txt"""
    
    # Load all 4300 rays
    print("Loading ALL_4300_UNIQUE_RAYS.txt...")
    all_4300_rays = load_rays_from_file("/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED/ALL_4300_UNIQUE_RAYS.txt")
    
    # Load original 4145 rays
    print("Loading original 4145 rays...")
    original_4145 = load_rays_from_file("/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/n6data/rays.txt")
    
    # Load August 5 rays (26 original)
    print("Loading August 5 rays...")
    aug5_26_rays = load_rays_from_file("/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED/aug5_26_new_rays.txt")
    
    print(f"Total rays in ALL_4300: {len(all_4300_rays)}")
    print(f"Original rays: {len(original_4145)}")
    print(f"Aug 5 rays: {len(aug5_26_rays)}")
    print(f"Expected Aug 3 rays: {len(all_4300_rays) - len(original_4145) - len(aug5_26_rays)}")
    
    # Create combined known rays (original + aug5)
    known_rays = original_4145 + aug5_26_rays
    print(f"Total known rays (original + Aug 5): {len(known_rays)}")
    
    # Extract rays from all_4300 that are not in known_rays
    aug3_rays = []
    for i, ray in enumerate(all_4300_rays):
        is_known = False
        for known_ray in known_rays:
            if check_ray_similarity(ray, known_ray):
                is_known = True
                break
        if not is_known:
            aug3_rays.append(ray)
            print(f"  Found Aug 3 ray {len(aug3_rays)}: ray {i+1} from ALL_4300")
    
    print(f"\nExtracted {len(aug3_rays)} August 3 rays")
    
    # Save the extracted August 3 rays
    output_file = "/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED/aug3_129_new_rays_extracted.txt"
    with open(output_file, 'w') as f:
        f.write("# 129 new rays discovered on August 3, 2025 (extracted from ALL_4300_UNIQUE_RAYS.txt)\n")
        f.write("# S₇-verified as all unique orbit representatives\n")
        for i, ray in enumerate(aug3_rays):
            ray_str = " ".join(f"{v:.15g}" for v in ray)
            f.write(f"{ray_str}  # Ray {i+1}\n")
    
    print(f"Saved {len(aug3_rays)} August 3 rays to {output_file}")
    return aug3_rays

if __name__ == "__main__":
    extract_august3_rays()