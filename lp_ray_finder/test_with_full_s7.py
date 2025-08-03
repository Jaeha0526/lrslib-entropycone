#!/usr/bin/env python3
"""
Test new rays against the FULL S₇-expanded constraint file
"""

import numpy as np

def load_s7_constraints_sample(filename, max_constraints=100000):
    """Load a sample of S₇-expanded constraints"""
    print(f"Loading sample of S₇ constraints from {filename}...")
    
    constraints = []
    with open(filename, 'r') as f:
        in_data = False
        for i, line in enumerate(f):
            line = line.strip()
            
            if line == 'begin':
                in_data = True
                continue
            elif line == 'end':
                break
            elif in_data and line and line[0].isdigit():
                # Skip the dimension line
                if 'integer' in line:
                    continue
                
                try:
                    # Parse constraint
                    values = [float(x) for x in line.split()]
                    if len(values) == 64:  # constant + 63 variables
                        constraints.append(values)
                        
                        if len(constraints) >= max_constraints:
                            break
                except:
                    continue
    
    return np.array(constraints)

def test_rays_with_s7():
    """Test our new rays against S₇-expanded constraints"""
    print("🔍 Testing new rays against FULL S₇-expanded constraints")
    print("=" * 60)
    
    # Load sample of S₇ constraints
    s7_constraints = load_s7_constraints_sample(
        '/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine',
        max_constraints=100000  # Test with 100K constraints first
    )
    
    print(f"Loaded {len(s7_constraints)} S₇-expanded constraints")
    
    # Load a few of our best new rays
    with open('new_positive_rays.txt', 'r') as f:
        lines = f.readlines()
    
    test_rays = []
    for i, line in enumerate(lines[4:20]):  # Test first few rays
        if not line.startswith('#') and line.strip():
            try:
                ray = np.array([float(x) for x in line.split()])
                if len(ray) == 63:
                    test_rays.append((i+1, ray))
            except:
                continue
    
    print(f"\nTesting {len(test_rays)} rays against S₇ constraints...")
    
    valid_rays = []
    invalid_rays = []
    
    for ray_id, ray in test_rays:
        # Check: constraint * ray >= 0
        # S₇ file format: constant first, then 63 variables
        # So we compute: sum(constraint[1:] * ray) + constraint[0] >= 0
        
        violations = 0
        for constraint in s7_constraints:
            value = np.dot(constraint[1:], ray) + constraint[0]
            if value < -1e-10:
                violations += 1
        
        if violations == 0:
            valid_rays.append(ray_id)
            print(f"✅ Ray {ray_id}: VALID (no violations in {len(s7_constraints)} constraints)")
        else:
            invalid_rays.append((ray_id, violations))
            print(f"❌ Ray {ray_id}: {violations} violations out of {len(s7_constraints)} constraints")
    
    print(f"\n📊 RESULTS:")
    print(f"   Valid rays: {len(valid_rays)}/{len(test_rays)}")
    print(f"   Invalid rays: {len(invalid_rays)}/{len(test_rays)}")
    
    if invalid_rays:
        print("\n⚠️  CRITICAL FINDING:")
        print("Some rays that satisfy orbit representatives do NOT")
        print("satisfy the full S₇-expanded constraints!")
        print("\nThis means we need to use the FULL constraint set")
        print("in our LP optimization to find truly valid rays.")
    
    if valid_rays:
        print("\n🎉 GOOD NEWS:")
        print(f"{len(valid_rays)} rays ARE valid under S₇ expansion!")
        print("This suggests there may indeed be new rays to discover!")
    
    return valid_rays, invalid_rays

if __name__ == "__main__":
    valid, invalid = test_rays_with_s7()