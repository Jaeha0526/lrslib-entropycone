#\!/usr/bin/env python3
"""
Verify if there really are new rays beyond the 4,145
"""

import numpy as np
from phase3_no_limit import FullConstraintRayFinder

# Load existing rays
existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
print(f"Loaded {len(existing_rays)} existing rays")

# Create finder - but this time we'll be smarter about constraints
finder = FullConstraintRayFinder(verbose=True)

# Load S7 constraints 
print("\nLoading S₇ constraints...")
s7_file = '/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine'
finder.load_all_s7_constraints(s7_file)

# Use a very specific objective that might find a gap
print("\n🎯 Searching with specific objective...")

# Try objective that's orthogonal to many existing rays
objective = np.ones(63) / np.sqrt(63)  # Uniform vector

ray, converged = finder.find_ray_active_set(objective, initial_size=1000, max_iter=10)

if ray is not None and converged:
    print(f"\n✅ Found ray that satisfies all {len(finder.constraints):,} constraints\!")
    print(f"   Ray (first 15): {ray[:15]}")
    
    # Detailed check against existing rays
    print("\n📊 Checking against existing rays...")
    
    # Normalize all existing rays
    existing_normalized = []
    for r in existing_rays:
        existing_normalized.append(r / np.linalg.norm(r))
    existing_normalized = np.array(existing_normalized)
    
    # Check dot products
    dots = np.abs(existing_normalized @ ray)
    max_dot = np.max(dots)
    match_idx = np.argmax(dots)
    
    print(f"   Best match: ray #{match_idx+1}")
    print(f"   Dot product: {max_dot:.8f}")
    
    if max_dot < 0.9999:
        print("\n🎉 This appears to be a GENUINELY NEW ray\!")
        print("   Saving to: potential_new_ray.txt")
        
        # Save it
        np.savetxt('potential_new_ray.txt', ray, fmt='%.10f')
        
        # Also save integer form
        scale = 10000
        ray_int = np.round(ray * scale).astype(int)
        gcd = np.gcd.reduce(ray_int)
        if gcd > 1:
            ray_int = ray_int // gcd
        
        print(f"   Integer form (first 15): {ray_int[:15]}")
        np.savetxt('potential_new_ray_int.txt', ray_int, fmt='%d')
        
        # Triple-check violations
        violations = finder.constraints @ ray
        num_violations = np.sum(violations < -1e-10)
        print(f"\n   Final violation check: {num_violations} violations (should be 0)")
        
        if num_violations > 0:
            print("   ❌ ERROR: Ray has violations\!")
        else:
            print("   ✅ Ray satisfies ALL S₇ constraints")
    else:
        print("   This is an existing ray")
        print(f"   Existing ray #{match_idx+1} (first 15): {existing_rays[match_idx][:15]}")
else:
    print("❌ Failed to find ray")
EOF < /dev/null
