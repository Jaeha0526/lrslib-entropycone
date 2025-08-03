#!/usr/bin/env python3
"""
More detailed check for S7 permutations among the 37 new rays
"""

import numpy as np
from itertools import combinations

def analyze_ray_structure(ray):
    """Analyze the structure of a ray to understand permutation patterns"""
    # Round to avoid floating point issues
    ray_rounded = np.round(ray, 8)
    
    # Get unique values and their counts
    unique_vals, counts = np.unique(ray_rounded, return_counts=True)
    
    # Sort by count for comparison
    sorted_counts = sorted(counts)
    
    return unique_vals, counts, sorted_counts

def check_permutation_candidates(rays):
    """Check which rays might be permutations of each other"""
    n = len(rays)
    
    # Group rays by their value patterns
    patterns = {}
    
    for i, ray in enumerate(rays):
        unique_vals, counts, sorted_counts = analyze_ray_structure(ray)
        
        # Create a pattern key from sorted counts and sorted unique values
        pattern_key = (
            tuple(sorted_counts),
            tuple(sorted(np.round(unique_vals, 8)))
        )
        
        if pattern_key not in patterns:
            patterns[pattern_key] = []
        patterns[pattern_key].append(i)
    
    return patterns

def main():
    print("🔍 Detailed S₇ Permutation Check for New Rays")
    print("="*60)
    
    # Load the 37 new rays
    new_rays = np.loadtxt('new_rays_extensive_search.txt')
    print(f"Loaded {len(new_rays)} new rays")
    
    # Analyze patterns
    print("\n📊 Analyzing value patterns...")
    patterns = check_permutation_candidates(new_rays)
    
    print(f"\nFound {len(patterns)} distinct value patterns")
    
    # Show groups that might be permutations
    permutation_groups = []
    for pattern_key, indices in patterns.items():
        if len(indices) > 1:
            permutation_groups.append(indices)
            print(f"\n⚠️  Rays that might be S₇-related: {indices}")
            print(f"   Pattern: {pattern_key[0]}")
            
            # Show the rays
            for idx in indices[:3]:  # Show first 3
                ray = new_rays[idx]
                print(f"   Ray {idx+1} (first 10): {ray[:10]}")
    
    # Check within each group more carefully
    truly_new = set(range(len(new_rays)))
    
    print("\n🔍 Checking within potential permutation groups...")
    for group in permutation_groups:
        print(f"\nChecking group: {group}")
        
        # Keep first ray in group, mark others as potential permutations
        for i in range(1, len(group)):
            ray1 = new_rays[group[0]]
            ray2 = new_rays[group[i]]
            
            # Check if ray2 is a permutation of ray1
            # This is still heuristic - proper check needs S7 action
            
            # Check if multisets of values match exactly
            if np.array_equal(sorted(np.round(ray1, 8)), 
                            sorted(np.round(ray2, 8))):
                print(f"   Ray {group[i]+1} might be permutation of Ray {group[0]+1}")
                truly_new.discard(group[i])
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 PERMUTATION CHECK SUMMARY:")
    print(f"   Total new rays: {len(new_rays)}")
    print(f"   Potential permutation groups: {len(permutation_groups)}")
    print(f"   Possibly unique orbit reps: {len(truly_new)}")
    
    if len(truly_new) < len(new_rays):
        print(f"\n⚠️  Some rays might be S₇ permutations of each other!")
        print(f"   Recommended: Implement full S₇ action to verify")
    
    # Save potentially unique rays
    unique_rays = new_rays[sorted(list(truly_new))]
    np.savetxt('potentially_unique_orbit_reps.txt', unique_rays, fmt='%.10f')
    print(f"\n💾 Saved {len(unique_rays)} potentially unique rays to:")
    print("   potentially_unique_orbit_reps.txt")
    
    # Also check against existing rays
    print("\n🔍 Checking against existing 4,145 rays...")
    existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
    
    # Get patterns for existing rays (check first 100 for speed)
    existing_patterns = check_permutation_candidates(existing_rays[:100])
    
    # Check if any new ray patterns match existing patterns
    matches_existing = 0
    for pattern_key, new_indices in patterns.items():
        if pattern_key in existing_patterns:
            matches_existing += len(new_indices)
            print(f"\n⚠️  Pattern {pattern_key[0]} matches existing rays!")
            print(f"   New ray indices: {new_indices}")
    
    if matches_existing > 0:
        print(f"\n⚠️  {matches_existing} new rays have patterns matching existing rays")
        print("   These might be S₇ permutations of existing rays!")

if __name__ == "__main__":
    main()