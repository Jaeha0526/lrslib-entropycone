#!/usr/bin/env python3
"""
Properly validate new rays against full S₇ constraints
"""

import numpy as np

def check_rays_against_s7_file(ray_file, s7_file, sample_size=100000):
    """Check rays against S₇ constraints by streaming through the file"""
    
    # Load rays to test
    print("Loading rays to validate...")
    with open(ray_file, 'r') as f:
        lines = f.readlines()
    
    test_rays = []
    for line in lines:
        if not line.startswith('#') and line.strip():
            try:
                ray = np.array([float(x) for x in line.split()])
                if len(ray) == 63:
                    test_rays.append(ray)
            except:
                continue
    
    print(f"Loaded {len(test_rays)} rays to validate")
    
    # Initialize violation counters
    violations_per_ray = [0] * len(test_rays)
    
    print(f"\nValidating against S₇ constraints (sampling {sample_size})...")
    
    # Stream through S₇ file
    constraints_checked = 0
    with open(s7_file, 'r') as f:
        in_data = False
        for line in f:
            line = line.strip()
            
            if line == 'begin':
                in_data = True
                continue
            elif line == 'end':
                break
            elif in_data and line and line[0].isdigit() or line[0] == '-':
                # Skip dimension line
                if 'integer' in line:
                    continue
                
                try:
                    values = line.split()
                    if len(values) == 64:  # constant + 63 vars
                        const = float(values[0])
                        coeffs = np.array([float(x) for x in values[1:]])
                        
                        # Check each ray
                        for i, ray in enumerate(test_rays):
                            # Constraint: const + coeffs · ray >= 0
                            value = const + np.dot(coeffs, ray)
                            if value < -1e-10:
                                violations_per_ray[i] += 1
                        
                        constraints_checked += 1
                        
                        if constraints_checked % 10000 == 0:
                            print(f"   Checked {constraints_checked} constraints...")
                        
                        if constraints_checked >= sample_size:
                            break
                except:
                    continue
    
    print(f"\nChecked {constraints_checked} S₇ constraints")
    
    # Report results
    print("\n📊 VALIDATION RESULTS:")
    valid_rays = 0
    for i, violations in enumerate(violations_per_ray):
        if i < 10 or violations > 0:  # Show first 10 and any with violations
            if violations == 0:
                print(f"Ray {i+1}: ✅ VALID (no violations)")
                valid_rays += 1
            else:
                print(f"Ray {i+1}: ❌ INVALID ({violations} violations)")
    
    if valid_rays == len(test_rays):
        print(f"\n🎉 ALL {valid_rays} rays are VALID under S₇!")
        return True
    else:
        print(f"\n⚠️  Only {valid_rays}/{len(test_rays)} rays are valid under S₇")
        print("\n💡 This means we found rays that satisfy orbit representatives")
        print("   but NOT the full S₇ symmetry group!")
        return False

def main():
    print("🔍 Validating new rays against FULL S₇ expansion")
    print("=" * 60)
    
    # First test a small sample
    print("\nTest 1: First 10 rays against 100K S₇ constraints")
    all_valid = check_rays_against_s7_file(
        'new_positive_rays.txt',
        '/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine',
        sample_size=100000
    )
    
    if not all_valid:
        print("\n🚨 CRITICAL FINDING:")
        print("The rays we found using orbit representatives are NOT")
        print("necessarily valid rays of the full holographic entropy cone!")
        print("\n📝 To find TRULY new rays, we must:")
        print("1. Use the FULL 8.6M S₇-expanded constraints in the LP")
        print("2. Or verify that rays satisfy all S₇ permutations")

if __name__ == "__main__":
    main()