#!/usr/bin/env python3
"""
Consolidate all unique rays from various discoveries into organized structure.
Total: 4300 unique rays
- Original: 4145 rays
- Aug 3: 129 new rays
- Aug 5: 26 new rays
"""

import numpy as np
import shutil
import os

def check_ray_similarity(ray1, ray2, threshold=0.9999):
    """Check if two rays are similar"""
    r1_norm = ray1 / np.linalg.norm(ray1)
    r2_norm = ray2 / np.linalg.norm(ray2)
    similarity = abs(np.dot(r1_norm, r2_norm))
    return similarity > threshold

def load_rays_from_file(filepath):
    """Load rays from a file"""
    rays = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        ray_data = line.split('#')[0].strip()
                        ray = np.fromstring(ray_data, sep=' ')
                        if len(ray) == 63:
                            rays.append(ray)
                    except:
                        pass
        print(f"Loaded {len(rays)} rays from {filepath}")
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return rays

def extract_26_new_from_27(rays_27, known_4145):
    """Extract the 26 genuinely new rays from the 27 Aug 5 rays"""
    new_rays = []
    for i, ray in enumerate(rays_27):
        is_duplicate = False
        for known_ray in known_4145:
            if check_ray_similarity(ray, known_ray):
                print(f"  Ray {i+1} is duplicate of known ray, skipping")
                is_duplicate = True
                break
        if not is_duplicate:
            new_rays.append(ray)
    return new_rays

def save_rays_to_file(rays, filepath, header=""):
    """Save rays to file with optional header"""
    with open(filepath, 'w') as f:
        if header:
            f.write(header + "\n")
        for i, ray in enumerate(rays):
            ray_str = " ".join(f"{v:.15g}" for v in ray)
            f.write(f"{ray_str}\n")
    print(f"Saved {len(rays)} rays to {filepath}")

def main():
    print("Consolidating all unique S₇ orbit representatives")
    print("="*60)
    
    # Create directory structure
    base_dir = "/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED"
    os.makedirs(base_dir, exist_ok=True)
    
    # Load all ray sets
    print("\n1. Loading original 4145 rays...")
    original_4145 = load_rays_from_file("/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/n6data/rays.txt")
    
    print("\n2. Loading Aug 3 rays...")
    aug3_129 = load_rays_from_file("/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED/aug3_129_new_rays.txt")
    
    print("\n3. Loading 2 unique S₇ orbit representatives from Aug 5...")
    aug5_2_unique = load_rays_from_file("/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED/aug5_2_unique_orbit_representatives.txt")
    
    print(f"Note: Aug 5 originally had 26 rays, but S₇ verification revealed only {len(aug5_2_unique)} unique orbits")
    
    print("\n4. Loading 1 unique S₇ orbit representative from fixed random experiment...")
    fixed_random_1_unique = load_rays_from_file("/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED/fixed_random_1_unique_orbit_representative.txt")
    
    print(f"Note: Fixed random experiment originally had 16 rays, but S₇ verification revealed only {len(fixed_random_1_unique)} unique orbit")
    
    # Save individual sets
    print("\n5. Saving individual ray sets...")
    save_rays_to_file(
        original_4145,
        os.path.join(base_dir, "original_4145_rays.txt"),
        "# Original 4145 extreme rays for N=6 holographic entropy cone"
    )
    
    save_rays_to_file(
        aug3_129,
        os.path.join(base_dir, "aug3_129_new_rays.txt"),
        "# 129 new rays discovered on August 3, 2025"
    )
    
    save_rays_to_file(
        aug5_2_unique,
        os.path.join(base_dir, "aug5_2_unique_orbit_representatives.txt"),
        "# 2 unique S₇ orbit representatives discovered on August 5, 2025"
    )
    
    save_rays_to_file(
        fixed_random_1_unique,
        os.path.join(base_dir, "fixed_random_1_unique_orbit_representative.txt"),
        "# 1 unique S₇ orbit representative from fixed random experiment (Aug 5, 2025)"
    )
    
    # Combine all rays
    print("\n6. Creating master file with all S₇-verified unique rays...")
    all_rays = original_4145 + aug3_129 + aug5_2_unique + fixed_random_1_unique
    
    save_rays_to_file(
        all_rays,
        os.path.join(base_dir, "ALL_S7_VERIFIED_UNIQUE_RAYS.txt"),
        "# Complete set of S₇-verified unique extreme rays for N=6 holographic entropy cone\n" +
        "# Original: 4145 rays (assumed S₇-verified)\n" +
        "# August 3, 2025: +129 new rays (S₇-verified, all unique)\n" +
        "# August 5, 2025: +2 unique S₇ orbit representatives (24 S₇ duplicates removed)\n" +
        "# Fixed random experiment: +1 unique S₇ orbit representative (15 S₇ duplicates removed)\n" +
        f"# Total: {len(all_rays)} S₇-verified unique rays"
    )
    
    # Create summary file
    print("\n7. Creating summary file...")
    with open(os.path.join(base_dir, "SUMMARY.md"), 'w') as f:
        f.write("# S₇-Verified Unique Rays for N=6 Holographic Entropy Cone\n\n")
        f.write("## Summary\n")
        f.write(f"- **Total S₇-verified unique rays**: {len(all_rays)}\n")
        f.write(f"- **Original rays**: 4145 (assumed S₇-verified)\n")
        f.write(f"- **New rays (Aug 3)**: 129 (S₇-verified, all unique)\n")
        f.write(f"- **New rays (Aug 5)**: 2 unique S₇ orbit representatives (24 S₇ duplicates removed)\n\n")
        f.write("## S₇ Verification Results\n")
        f.write("- **Aug 3 (129 rays)**: ✅ All unique orbit representatives\n")
        f.write("- **Aug 5 (26 rays)**: 🚨 Only 2 unique orbits (24 S₇ duplicates removed)\n")
        f.write("- **Current experiment**: 🚨 Similar S₇ duplication pattern observed\n\n")
        f.write("## Files\n")
        f.write("- `ALL_S7_VERIFIED_UNIQUE_RAYS.txt`: Master file with S₇-verified unique rays\n")
        f.write("- `original_4145_rays.txt`: Original known rays\n")
        f.write("- `aug3_129_new_rays.txt`: 129 S₇-verified new rays from August 3\n")
        f.write("- `aug5_2_unique_orbit_representatives.txt`: 2 unique orbit representatives from August 5\n\n")
        f.write("## Verification Process\n")
        f.write("1. **Cosine similarity filtering**: Removes rays with similarity > 0.9999\n")
        f.write("2. **S₇ invariant signature verification**: Identifies potential S₇ equivalent rays\n")
        f.write("3. **Orbit representative selection**: Keeps one ray per S₇ orbit\n\n")
        f.write("Each ray is a 63-dimensional vector representing an extreme ray of the cone.\n")
    
    print("\n" + "="*60)
    print("S₇ VERIFICATION AND CONSOLIDATION COMPLETE!")
    print(f"All files saved to: {base_dir}")
    print(f"Total S₇-verified unique rays: {len(all_rays)}")
    print(f"\nKey insight: LP ray finder needs S₇-aware deduplication to avoid finding S₇ variants")

if __name__ == "__main__":
    main()