#!/usr/bin/env python3
"""
Verify rays against S₇ constraints with correct understanding:
All facets pass through origin, so constraint is: facet · ray >= 0
"""

import numpy as np

def verify_rays_sample():
    """Quick verification of a few rays against S₇ constraints"""
    
    # Load first few new rays
    print("Loading sample of new rays...")
    rays = []
    with open('new_positive_rays.txt', 'r') as f:
        for line in f:
            if not line.startswith('#') and line.strip():
                ray = np.array([float(x) for x in line.split()])
                if len(ray) == 63:
                    rays.append(ray)
                    if len(rays) >= 5:  # Just test first 5
                        break
    
    print(f"Testing {len(rays)} rays")
    
    # Load sample of S₇ constraints
    print("\nLoading sample of S₇ constraints...")
    constraints = []
    with open('/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine', 'r') as f:
        in_data = False
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
                if len(values) == 63:  # Just 63 coefficients, no constant!
                    facet = np.array([float(x) for x in values])
                    constraints.append(facet)
                    
                    if len(constraints) >= 10000:  # Test with 10K constraints
                        break
    
    print(f"Loaded {len(constraints)} S₇ constraints")
    
    # Test each ray
    print("\nVerifying rays...")
    for i, ray in enumerate(rays):
        violations = 0
        for facet in constraints:
            # Constraint: facet · ray >= 0 (no constant term!)
            if np.dot(facet, ray) < -1e-10:
                violations += 1
        
        if violations == 0:
            print(f"Ray {i+1}: ✅ VALID (satisfies all {len(constraints)} constraints)")
        else:
            print(f"Ray {i+1}: ❌ {violations} violations out of {len(constraints)} constraints")

if __name__ == "__main__":
    verify_rays_sample()