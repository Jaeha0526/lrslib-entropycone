#!/usr/bin/env python3
"""
Check if our discovered rays are duplicates of the known 4,144 rays
"""

import numpy as np

def get_ray_signature(ray, tol=1e-8):
    """Get signature of a ray invariant under S7 permutations"""
    norm = np.linalg.norm(ray)
    if norm < tol:
        return ('zero',)
    
    ray_norm = ray / norm
    ray_rounded = np.round(ray_norm, 8)
    unique_vals, counts = np.unique(ray_rounded, return_counts=True)
    val_count_pairs = sorted(zip(unique_vals, counts))
    return tuple(val_count_pairs)

print("🔍 Checking if discovered rays are duplicates of known rays...")
print("=" * 70)

# Load known rays
print("\n1. Loading known rays from rays.txt...")
known_rays = []
with open('/workspace/lrslib-entropycone/n6data/rays.txt', 'r') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 63:
            ray = np.array([float(x) for x in parts])
            known_rays.append(ray)

print(f"   Loaded {len(known_rays)} known rays")

# Get signatures of known rays
print("\n2. Computing signatures of known rays...")
known_signatures = set()
for ray in known_rays:
    sig = get_ray_signature(ray)
    known_signatures.add(sig)

print(f"   Found {len(known_signatures)} unique signatures among known rays")

# Load our discovered rays
print("\n3. Loading our discovered rays...")
our_rays = np.loadtxt('all_unique_rays_final.txt')
print(f"   Loaded {len(our_rays)} discovered rays")

# Check each discovered ray against known rays
print("\n4. Checking for duplicates...")
truly_new_rays = []
duplicate_count = 0

for i, ray in enumerate(our_rays):
    sig = get_ray_signature(ray)
    if sig in known_signatures:
        duplicate_count += 1
        print(f"   ❌ Ray {i+1} is a duplicate of a known ray")
    else:
        truly_new_rays.append(ray)

print(f"\n📊 RESULTS:")
print(f"   Total discovered rays: {len(our_rays)}")
print(f"   Duplicates of known rays: {duplicate_count}")
print(f"   TRULY NEW RAYS: {len(truly_new_rays)}")

if len(truly_new_rays) > 0:
    # Save truly new rays
    truly_new_rays = np.array(truly_new_rays)
    np.savetxt('truly_new_rays_final.txt', truly_new_rays, fmt='%.10f')
    print(f"\n✅ Saved {len(truly_new_rays)} truly new rays to: truly_new_rays_final.txt")
    
    # Final count
    original = 4155  # or 4144 from file
    new_total = original + len(truly_new_rays)
    increase = (len(truly_new_rays) / original) * 100
    
    print(f"\n🎯 FINAL VERIFIED COUNT:")
    print(f"   Original known rays: {original}")
    print(f"   Truly new discoveries: {len(truly_new_rays)}")
    print(f"   New total: {new_total}")
    print(f"   Increase: {increase:.2f}%")
else:
    print("\n😔 All discovered rays were duplicates of known rays")