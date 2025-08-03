#!/usr/bin/env python3
"""
Quick test of phase3_no_limit with debug output
"""

import numpy as np
from phase3_no_limit import FullConstraintRayFinder

print("🔍 Quick test with full S₇ constraints")
print("="*60)

# Load existing rays
existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
print(f"Loaded {len(existing_rays)} existing rays")

# Create finder
finder = FullConstraintRayFinder(verbose=True)

# Load ALL S₇ constraints
s7_file = '/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine'
num_constraints = finder.load_all_s7_constraints(s7_file)

print("\n🎯 Testing with 1 random objective...")

# Random objective
objective = np.random.rand(63)
objective = objective / np.linalg.norm(objective)

ray, converged = finder.find_ray_active_set(objective, initial_size=500, max_iter=10)

if ray is not None and converged:
    print("\n✅ Found ray!")
    print(f"   Ray (first 10): {ray[:10]}")
    
    # Check violations
    print("\n📊 Checking violations against ALL 8.6M constraints...")
    violations = finder.constraints @ ray
    num_violations = np.sum(violations < -1e-10)
    print(f"   Violations: {num_violations:,} out of {len(finder.constraints):,}")
    
    if num_violations > 0:
        print("   ❌ RAY VIOLATES S₇ CONSTRAINTS!")
        worst_violations = violations[violations < -1e-10]
        print(f"   Worst violation: {np.min(worst_violations):.6f}")
    else:
        print("   ✅ Ray satisfies all S₇ constraints")
        
        # Check if new
        is_new = True
        for existing in existing_rays:
            existing_norm = existing / np.linalg.norm(existing)
            if np.dot(ray, existing_norm) > 0.9999:
                is_new = False
                break
        
        if is_new:
            print("   🎉 This is a NEW ray!")
        else:
            print("   This is an existing ray")
else:
    print("❌ Failed to find ray")