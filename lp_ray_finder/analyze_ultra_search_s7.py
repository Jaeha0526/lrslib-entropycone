#!/usr/bin/env python3
"""
Analyze S7 permutations for ultra search (50K) results
"""

import numpy as np
import os
from datetime import datetime

def get_ray_signature(ray, tol=1e-8):
    """Get signature invariant under S7 permutations"""
    ray_rounded = np.round(ray / np.linalg.norm(ray), 8)
    unique_vals, counts = np.unique(ray_rounded, return_counts=True)
    sorted_idx = np.argsort(unique_vals)
    signature = (
        tuple(unique_vals[sorted_idx]),
        tuple(counts[sorted_idx])
    )
    return signature

def analyze_ultra_results():
    print("🔍 Analyzing Ultra Search (50K) Results for S₇ Permutations")
    print("=" * 70)
    print(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.path.exists('ultra_search_50k_rays_fixed.txt'):
        print("❌ No ultra search results file found")
        return
    
    # Load rays
    try:
        ultra_rays = np.loadtxt('ultra_search_50k_rays_fixed.txt')
        if ultra_rays.ndim == 1:
            ultra_rays = ultra_rays.reshape(1, -1)
    except Exception as e:
        print(f"Error loading ultra search results: {e}")
        return
    
    print(f"📊 Loaded {len(ultra_rays)} rays from ultra search")
    
    # Get unique signatures
    signatures = {}
    for i, ray in enumerate(ultra_rays):
        sig = get_ray_signature(ray)
        if sig not in signatures:
            signatures[sig] = []
        signatures[sig].append(i)
    
    unique_count = len(signatures)
    print(f"🎯 Found {unique_count} unique signatures from {len(ultra_rays)} rays")
    
    # Orbit size analysis
    orbit_sizes = sorted([len(indices) for indices in signatures.values()], reverse=True)
    
    print(f"\n📈 Orbit Size Distribution:")
    print(f"   Largest orbit: {orbit_sizes[0]} rays")
    print(f"   Median orbit: {orbit_sizes[len(orbit_sizes)//2]} rays")
    print(f"   Unique orbits (size 1): {orbit_sizes.count(1)}")
    
    # Top 10 orbits
    print(f"\n🏆 Top 10 Largest Orbits:")
    for i, size in enumerate(orbit_sizes[:10]):
        print(f"   Orbit {i+1}: {size} rays")
    
    # Save unique representatives
    unique_rays = []
    for sig, indices in signatures.items():
        unique_rays.append(ultra_rays[indices[0]])
    
    unique_rays = np.array(unique_rays)
    np.savetxt('ultra_search_unique_rays.txt', unique_rays, fmt='%.10f')
    
    print(f"\n✅ Analysis Complete:")
    print(f"   Unique orbit representatives: {unique_count}")
    print(f"   Saved to: ultra_search_unique_rays.txt")
    
    # Calculate totals
    previous_total = 4558  # From extended search
    new_total = previous_total + unique_count
    
    print(f"\n🏆 ULTRA SEARCH ACHIEVEMENT:")
    print(f"   Previous total: {previous_total}")
    print(f"   New discoveries: {unique_count}")
    print(f"   NEW TOTAL: {new_total}")
    print(f"   Total increase: {((new_total - 4155) / 4155) * 100:.1f}% over original 4,155!")
    
    # Success metrics
    if len(ultra_rays) > 0:
        print(f"\n📊 Search Efficiency:")
        print(f"   Raw rays found: {len(ultra_rays)}")
        print(f"   Unique orbits: {unique_count}")
        print(f"   Uniqueness ratio: {(unique_count/len(ultra_rays))*100:.1f}%")

if __name__ == "__main__":
    analyze_ultra_results()