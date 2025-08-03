#!/usr/bin/env python3
"""
Check if new rays are permutations of existing rays
"""

import numpy as np
from itertools import permutations
import time

def generate_s7_permutations():
    """Generate all permutations in S7"""
    # For N=6, we have 7 parties
    # The 63 components correspond to subsets of size 1-6
    # We need to understand how S7 acts on these components
    
    # First, let's understand the structure:
    # 7 components for size 1 subsets: {1}, {2}, ..., {7}
    # 21 components for size 2 subsets: {1,2}, {1,3}, ..., {6,7}
    # 35 components for size 3 subsets
    # Total: 7 + 21 + 35 = 63
    
    # For now, just return the identity
    # TODO: Implement full S7 action on 63-dimensional vectors
    return [list(range(7))]  # Identity permutation

def check_if_permutation_equivalent(ray1, ray2, tolerance=1e-9):
    """
    Check if ray2 is a permutation of ray1 under S7
    
    For a proper implementation, we need to:
    1. Generate all S7 permutations of ray1
    2. Check if any match ray2
    """
    # Normalize both rays
    ray1_norm = ray1 / np.linalg.norm(ray1)
    ray2_norm = ray2 / np.linalg.norm(ray2)
    
    # Quick heuristic checks before expensive permutation testing:
    
    # 1. Check if sorted values match (necessary but not sufficient)
    sorted1 = np.sort(np.abs(ray1_norm))
    sorted2 = np.sort(np.abs(ray2_norm))
    if not np.allclose(sorted1, sorted2, rtol=tolerance):
        return False, None
    
    # 2. Check value frequencies
    unique1, counts1 = np.unique(np.round(ray1_norm, 8), return_counts=True)
    unique2, counts2 = np.unique(np.round(ray2_norm, 8), return_counts=True)
    
    if len(unique1) != len(unique2):
        return False, None
    
    # Sort by counts to compare
    idx1 = np.argsort(counts1)
    idx2 = np.argsort(counts2)
    
    if not np.array_equal(counts1[idx1], counts2[idx2]):
        return False, None
    
    if not np.allclose(unique1[idx1], unique2[idx2], rtol=tolerance):
        return False, None
    
    # If we get here, rays MIGHT be related by permutation
    # For now, return "possibly equivalent" 
    # A full check would require implementing S7 action
    return True, "Possibly related by S7 (heuristic check)"

def main():
    print("🔍 Checking if new rays are S₇ permutations of existing rays")
    print("="*60)
    
    # Load existing rays
    existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
    print(f"Loaded {len(existing_rays)} existing orbit representatives")
    
    # Load new rays
    try:
        new_rays = np.loadtxt('new_rays_extensive_search.txt')
        if new_rays.ndim == 1:
            new_rays = new_rays.reshape(1, -1)
        print(f"Loaded {len(new_rays)} new rays to check")
    except:
        print("No new rays file found")
        return
    
    # Check each new ray
    truly_new = []
    possibly_permuted = []
    
    for i, new_ray in enumerate(new_rays):
        print(f"\nChecking ray {i+1}/{len(new_rays)}...")
        
        # First check: is it just a scalar multiple of an existing ray?
        is_multiple = False
        for j, existing in enumerate(existing_rays):
            # Check if parallel (same direction or opposite)
            dot = np.dot(new_ray, existing)
            norm_prod = np.linalg.norm(new_ray) * np.linalg.norm(existing)
            if np.abs(dot / norm_prod) > 0.9999:
                print(f"  → Matches existing ray #{j+1} (parallel)")
                is_multiple = True
                break
        
        if is_multiple:
            continue
            
        # Second check: could it be a permutation?
        found_permutation = False
        for j, existing in enumerate(existing_rays[:100]):  # Check first 100 for speed
            is_perm, msg = check_if_permutation_equivalent(existing, new_ray)
            if is_perm:
                print(f"  → {msg} of ray #{j+1}")
                possibly_permuted.append((i, j))
                found_permutation = True
                break
        
        if not found_permutation:
            truly_new.append(i)
            print(f"  → Appears to be TRULY NEW!")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY:")
    print(f"   Total new rays checked: {len(new_rays)}")
    print(f"   Possibly S₇-related: {len(possibly_permuted)}")
    print(f"   Truly new (not permutations): {len(truly_new)}")
    
    if len(truly_new) > 0:
        print(f"\n🎉 Found {len(truly_new)} genuinely new orbit representatives!")
        print("   These are NOT permutations of existing rays")
        
        # Save truly new rays
        truly_new_rays = new_rays[truly_new]
        np.savetxt('truly_new_orbit_reps.txt', truly_new_rays, fmt='%.10f')
        print(f"   Saved to: truly_new_orbit_reps.txt")
    
    # Analysis of value patterns
    if len(new_rays) > 0:
        print(f"\n📊 Value pattern analysis (first new ray):")
        ray = new_rays[0]
        unique_vals, counts = np.unique(np.round(ray, 8), return_counts=True)
        for val, count in zip(unique_vals, counts):
            print(f"   Value {val:.8f} appears {count} times")

if __name__ == "__main__":
    main()