#!/usr/bin/env python3
"""
Carefully analyze what happens when we find a "new" ray
"""

import numpy as np
from phase3_no_limit import FullConstraintRayFinder

# Load existing rays
existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
print(f"Loaded {len(existing_rays)} existing rays")

# Quick test - use first existing ray as objective
print("\n🧪 Using existing ray #1 as objective to see if we recover it")
test_ray = existing_rays[0]
print(f"Target ray (first 10): {test_ray[:10]}")

# Normalize for objective
objective = test_ray / np.linalg.norm(test_ray)

# Create simple LP test
print("\n📊 Testing LP with subset of constraints")
finder = FullConstraintRayFinder(verbose=False)

# Load just first 10000 constraints for quick test
constraints = []
with open('/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine', 'r') as f:
    in_data = False
    count = 0
    for line in f:
        line = line.strip()
        if line == 'begin':
            in_data = True
            continue
        elif line == 'end':
            break
        elif in_data and line and (line[0].isdigit() or line[0] == '-'):
            if 'integer' in line:
                continue
            values = line.split()
            if len(values) == 63:
                constraints.append([float(x) for x in values])
                count += 1
                if count >= 10000:
                    break

finder.constraints = np.array(constraints)
finder.d = 63
print(f"Loaded {len(finder.constraints)} constraints for testing")

# Try to find ray
ray, converged = finder.find_ray_active_set(objective, initial_size=500, max_iter=5)

if ray is not None:
    print(f"\n✅ Found ray!")
    print(f"   Ray (first 10): {ray[:10]}")
    
    # Compare with target
    dot = np.dot(ray, objective)
    print(f"   Dot product with target: {dot:.6f}")
    
    # Check if it matches any existing ray
    max_dot = 0
    best_match = -1
    for i, existing in enumerate(existing_rays):
        existing_norm = existing / np.linalg.norm(existing)
        d = np.abs(np.dot(ray, existing_norm))
        if d > max_dot:
            max_dot = d
            best_match = i
    
    print(f"   Best match: ray #{best_match+1}, dot={max_dot:.6f}")
    
    if max_dot > 0.9999:
        print("   ✅ This is an existing ray")
    else:
        print("   ❓ This appears to be a NEW ray?")
        print("   Let's check scaling...")
        
        # Try integer scaling
        for scale in [1, 10, 100, 1000, 10000]:
            ray_scaled = ray * scale
            ray_int = np.round(ray_scaled).astype(int)
            
            # Check if close to any existing ray
            for i, existing in enumerate(existing_rays[:100]):  # Check first 100
                if np.allclose(ray_int, existing, rtol=0.01):
                    print(f"   ✅ Matches ray #{i+1} with scale={scale}")
                    break