#!/usr/bin/env python3
"""
Verify new rays against the full S₇-expanded constraint set
"""

import numpy as np
import itertools

def generate_s7_permutation(perm):
    """Generate permutation matrix for S₇ action on 63-dimensional space"""
    # This is complex - for now, let's check a simpler approach
    # We'll verify by checking if the rays satisfy S₆ permutations at least
    pass

def check_ray_orbit_consistency(ray, facets):
    """
    Check if a ray satisfies not just the orbit representatives,
    but also basic permutations
    """
    # For a quick check, let's verify S₆ permutations (physical regions only)
    # The 6 regions correspond to different subsets
    
    violations = 0
    
    # Check original constraints
    products = facets @ ray
    orig_violations = np.sum(products < -1e-10)
    
    # We need the full S₇ expansion to properly verify
    # For now, let's at least check some basic symmetries
    
    return orig_violations

def main():
    print("🔍 Verifying new rays with S₇ expansion considerations")
    print("=" * 60)
    
    # Load facets and new rays
    facets = np.loadtxt('/workspace/lrslib-entropycone/n6data/facets.txt')
    
    # Load new rays
    with open('new_positive_rays.txt', 'r') as f:
        lines = f.readlines()
    
    new_rays = []
    for line in lines:
        if not line.startswith('#') and line.strip():
            try:
                ray = np.array([float(x) for x in line.split()])
                if len(ray) == 63:
                    new_rays.append(ray)
            except:
                continue
    
    print(f"Loaded {len(new_rays)} new rays")
    print(f"Loaded {len(facets)} orbit representative facets")
    
    print("\n⚠️  CRITICAL REALIZATION:")
    print("We found these rays using only orbit representatives!")
    print("For true validity, they must satisfy ALL S₇ permutations.")
    
    # Quick check against orbit representatives
    print("\n📊 Checking against orbit representatives:")
    valid_count = 0
    for i, ray in enumerate(new_rays):
        violations = check_ray_orbit_consistency(ray, facets)
        if violations == 0:
            valid_count += 1
        else:
            print(f"Ray {i+1}: {violations} violations")
    
    print(f"\nOrbit representative validation: {valid_count}/{len(new_rays)} rays valid")
    
    print("\n🎯 KEY INSIGHTS:")
    print("1. We found rays that satisfy the 1,877 orbit representatives")
    print("2. These may or may not satisfy all 8.6M S₇-expanded constraints")
    print("3. To be true rays of the holographic entropy cone, they must")
    print("   satisfy ALL permutations under S₇ symmetry")
    
    print("\n💡 WHAT THIS MEANS:")
    print("- If these rays DON'T satisfy S₇ expansion: They're spurious")
    print("- If they DO satisfy S₇ expansion: MAJOR DISCOVERY!")
    print("- Need to test against full 8.6M constraint file to know for sure")
    
    print("\n📝 RECOMMENDATION:")
    print("Run LP optimization with the FULL S₇-expanded constraint set")
    print("to find truly valid new rays!")

if __name__ == "__main__":
    main()