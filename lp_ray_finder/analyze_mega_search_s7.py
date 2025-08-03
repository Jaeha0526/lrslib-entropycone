#!/usr/bin/env python3
"""
Analyze S7 permutations for mega search results
"""

import numpy as np
import os

def get_ray_signature(ray, tol=1e-8):
    """Get signature of a ray invariant under S7 permutations"""
    ray_rounded = np.round(ray / np.linalg.norm(ray), 8)
    unique_vals, counts = np.unique(ray_rounded, return_counts=True)
    sorted_idx = np.argsort(unique_vals)
    signature = (
        tuple(unique_vals[sorted_idx]),
        tuple(counts[sorted_idx])
    )
    return signature

def analyze_mega_results():
    print("🔍 Analyzing Mega Search Results for S₇ Permutations")
    print("=" * 60)
    
    if not os.path.exists('mega_search_10k_rays_fixed.txt'):
        print("❌ No mega search results file found")
        return
    
    # Load mega search rays
    try:
        mega_rays = np.loadtxt('mega_search_10k_rays_fixed.txt')
        if mega_rays.ndim == 1:
            mega_rays = mega_rays.reshape(1, -1)
    except Exception as e:
        print(f"Error loading mega search results: {e}")
        return
    
    print(f"📊 Loaded {len(mega_rays)} rays from mega search")
    
    # Get signatures for S7 uniqueness
    signatures = {}
    for i, ray in enumerate(mega_rays):
        sig = get_ray_signature(ray)
        if sig not in signatures:
            signatures[sig] = []
        signatures[sig].append(i)
    
    unique_count = len(signatures)
    print(f"🎯 Found {unique_count} unique signatures from {len(mega_rays)} rays")
    
    # Show orbit size distribution
    orbit_sizes = [len(indices) for indices in signatures.values()]
    orbit_sizes.sort(reverse=True)
    
    print(f"\\n📈 Orbit Size Distribution:")
    for i, size in enumerate(orbit_sizes[:10]):  # Top 10
        print(f"   Orbit {i+1}: {size} rays")
    
    if len(orbit_sizes) > 10:
        print(f"   ... and {len(orbit_sizes)-10} more orbits")
    
    # Save unique representatives
    unique_rays = []
    for sig, indices in signatures.items():
        unique_rays.append(mega_rays[indices[0]])  # First representative
    
    unique_rays = np.array(unique_rays)
    np.savetxt('mega_search_unique_rays.txt', unique_rays, fmt='%.10f')
    
    print(f"\\n✅ Analysis Complete:")
    print(f"   Unique orbit representatives: {unique_count}")
    print(f"   Saved to: mega_search_unique_rays.txt")
    
    # Compare with previous discoveries
    total_previous = 4171  # 4155 original + 16 from extended search
    new_total = total_previous + unique_count
    
    print(f"\\n🏆 Grand Total Discovery:")
    print(f"   Previous known: {total_previous}")
    print(f"   New from mega search: {unique_count}")
    print(f"   New grand total: {new_total}")
    print(f"   Total increase: {((new_total - 4155) / 4155) * 100:.2f}%")

if __name__ == "__main__":
    analyze_mega_results()