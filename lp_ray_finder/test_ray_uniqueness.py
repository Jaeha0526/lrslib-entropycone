#!/usr/bin/env python3
"""
Test why we're finding "new" rays
"""

import numpy as np
from phase3_no_limit import FullConstraintRayFinder

# Load existing rays
existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
print(f"Loaded {len(existing_rays)} existing rays")

# Normalize all existing rays for comparison
existing_normalized = []
for ray in existing_rays:
    existing_normalized.append(ray / np.linalg.norm(ray))
existing_normalized = np.array(existing_normalized)

# Create finder and load constraints
finder = FullConstraintRayFinder(verbose=False)
s7_file = '/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine'
finder.load_all_s7_constraints(s7_file)
print(f"Loaded {len(finder.constraints):,} S₇ constraints")

# Test 1: Use an existing ray as objective
print("\n🧪 Test 1: Using existing ray #100 as objective")
test_ray = existing_rays[100]
objective = test_ray / np.linalg.norm(test_ray)

ray, converged = finder.find_ray_active_set(objective, initial_size=500, max_iter=10)

if ray is not None and converged:
    # Check if it's the same ray
    dot_product = np.dot(ray, objective)
    print(f"✅ Found ray, dot product with objective: {dot_product:.6f}")
    
    # Check against all existing rays
    max_dot = np.max(np.abs(existing_normalized @ ray))
    match_idx = np.argmax(np.abs(existing_normalized @ ray))
    print(f"   Best match: ray #{match_idx+1}, dot product: {max_dot:.6f}")
    
    if max_dot < 0.9999:
        print("   ❌ PROBLEM: Ray appears NEW but shouldn't be!")
    else:
        print("   ✅ Correctly identified as existing ray")

# Test 2: Random objective
print("\n🧪 Test 2: Random objective")
objective = np.random.rand(63)
objective = objective / np.linalg.norm(objective)

ray, converged = finder.find_ray_active_set(objective, initial_size=500, max_iter=10)

if ray is not None and converged:
    # Check violations
    violations = finder.constraints @ ray
    num_violations = np.sum(violations < -1e-10)
    print(f"✅ Found ray, violations: {num_violations} (should be 0)")
    
    # Check if new
    max_dot = np.max(np.abs(existing_normalized @ ray))
    match_idx = np.argmax(np.abs(existing_normalized @ ray))
    
    print(f"   Best match: ray #{match_idx+1}, dot product: {max_dot:.6f}")
    
    if max_dot < 0.9999:
        print("   🎉 This appears to be a NEW ray!")
        print(f"   Ray (first 10): {ray[:10]}")
        
        # Double-check by scaling to integers
        scale = 1000
        ray_int = np.round(ray * scale).astype(int)
        gcd = np.gcd.reduce(ray_int)
        if gcd > 1:
            ray_int = ray_int // gcd
            print(f"   Integer form (first 10): {ray_int[:10]}")
    else:
        print("   This is an existing ray")