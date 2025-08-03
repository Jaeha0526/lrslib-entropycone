#!/usr/bin/env python3
"""Quick progress check"""
import numpy as np

# Count new rays
try:
    new_rays = np.loadtxt('new_rays_extensive_search.txt')
    if new_rays.ndim == 1:
        new_rays = new_rays.reshape(1, -1)
    new_count = len(new_rays)
    
    print(f"🎉 Progress Update:")
    print(f"   New rays found: {new_count}")
    print(f"   Total rays now: {4145 + new_count}")
    print(f"\n📊 Sample of new rays (first 5 components):")
    for i in range(min(3, new_count)):
        print(f"   Ray {i+1}: {new_rays[i][:5]}...")
    
    # Check for uniqueness among new rays
    print(f"\n🔍 Checking uniqueness among new rays...")
    unique = True
    for i in range(new_count):
        for j in range(i+1, new_count):
            dot = np.dot(new_rays[i], new_rays[j]) / (np.linalg.norm(new_rays[i]) * np.linalg.norm(new_rays[j]))
            if dot > 0.9999:
                print(f"   ⚠️  Rays {i+1} and {j+1} might be duplicates (dot={dot:.6f})")
                unique = False
    
    if unique and new_count > 1:
        print(f"   ✅ All {new_count} new rays are unique!")
    
except Exception as e:
    print(f"Error: {e}")