#!/usr/bin/env python3
"""
Analyze integer representations of extended search rays
"""

import numpy as np
from fractions import Fraction
import math

def to_integer_ray(ray, tolerance=1e-9):
    """Convert a ray to minimal integer coordinates"""
    ray_norm = ray / np.linalg.norm(ray)
    fractions = []
    for val in ray_norm:
        frac = Fraction(val).limit_denominator(10000)
        fractions.append(frac)
    
    denominators = [f.denominator for f in fractions]
    lcm = denominators[0]
    for d in denominators[1:]:
        lcm = lcm * d // math.gcd(lcm, d)
    
    integer_ray = []
    for f in fractions:
        integer_ray.append(int(f * lcm))
    
    nonzero_vals = [abs(x) for x in integer_ray if x != 0]
    if nonzero_vals:
        gcd = math.gcd(*nonzero_vals)
        if gcd > 1:
            integer_ray = [x // gcd for x in integer_ray]
    
    return integer_ray

def main():
    print("🔢 Converting Extended Search Rays to Integer Form")
    print("="*70)
    
    # Load extended unique rays
    rays = np.loadtxt('extended_unique_rays.txt')
    print(f"Loaded {len(rays)} unique orbit representatives from extended search")
    
    for i, ray in enumerate(rays):
        int_ray = to_integer_ray(ray)
        unique_vals = sorted(set(int_ray))
        
        print(f"\n📌 Extended Ray {i+1}:")
        print(f"   First 10 integer values: {int_ray[:10]}")
        print(f"   Unique integer values: {unique_vals}")
        print(f"   Max value: {max(int_ray)}")
        print(f"   Min value: {min(int_ray)}")
    
    print(f"\n🎯 Summary:")
    print(f"   Total new orbit representatives: {len(rays)}")
    print(f"   Previous known: 4,155")
    print(f"   New total: {4155 + len(rays)}")

if __name__ == "__main__":
    main()