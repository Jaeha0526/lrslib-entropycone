#!/usr/bin/env python3
"""
Analyze S7 permutations for giga search (100K) results
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

def analyze_giga_results():
    print("🌟 Analyzing Giga Search (100K) Results for S₇ Permutations")
    print("=" * 70)
    print(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.path.exists('giga_search_100k_rays.txt'):
        print("❌ No giga search results file found")
        return
    
    # Load rays
    try:
        giga_rays = np.loadtxt('giga_search_100k_rays_fixed.txt')
        if giga_rays.ndim == 1:
            giga_rays = giga_rays.reshape(1, -1)
    except Exception as e:
        print(f"Error loading giga search results: {e}")
        return
    
    print(f"📊 Loaded {len(giga_rays)} rays from giga search")
    
    # Get unique signatures
    signatures = {}
    for i, ray in enumerate(giga_rays):
        sig = get_ray_signature(ray)
        if sig not in signatures:
            signatures[sig] = []
        signatures[sig].append(i)
    
    unique_count = len(signatures)
    print(f"🎯 Found {unique_count} unique signatures from {len(giga_rays)} rays")
    
    # Detailed analysis
    orbit_sizes = sorted([len(indices) for indices in signatures.values()], reverse=True)
    
    print(f"\n📈 Comprehensive Orbit Analysis:")
    print(f"   Total orbits: {len(orbit_sizes)}")
    print(f"   Largest orbit: {orbit_sizes[0]} rays")
    print(f"   Average orbit size: {np.mean(orbit_sizes):.1f}")
    print(f"   Median orbit size: {orbit_sizes[len(orbit_sizes)//2]}")
    
    # Distribution
    print(f"\n📊 Orbit Size Distribution:")
    size_counts = {}
    for size in orbit_sizes:
        if size not in size_counts:
            size_counts[size] = 0
        size_counts[size] += 1
    
    for size in sorted(size_counts.keys())[:10]:
        print(f"   Size {size}: {size_counts[size]} orbits")
    
    # Save unique representatives
    unique_rays = []
    for sig, indices in signatures.items():
        unique_rays.append(giga_rays[indices[0]])
    
    unique_rays = np.array(unique_rays)
    np.savetxt('giga_search_unique_rays.txt', unique_rays, fmt='%.10f')
    
    print(f"\n✅ Analysis Complete:")
    print(f"   Unique orbit representatives: {unique_count}")
    print(f"   Saved to: giga_search_unique_rays.txt")
    
    # Grand totals (assuming ultra search also completed)
    base_total = 4155  # Original
    extended_unique = 16 + 403  # From previous searches
    
    # Check if ultra search completed
    ultra_unique = 0
    if os.path.exists('ultra_search_unique_rays.txt'):
        try:
            ultra_data = np.loadtxt('ultra_search_unique_rays.txt')
            ultra_unique = len(ultra_data) if ultra_data.ndim > 1 else 1
        except:
            pass
    
    grand_total = base_total + extended_unique + ultra_unique + unique_count
    
    print(f"\n🏆 GIGA SEARCH ULTIMATE ACHIEVEMENT:")
    print(f"   Original base: 4,155")
    print(f"   Extended searches: +{extended_unique}")
    print(f"   Ultra search: +{ultra_unique}")
    print(f"   Giga search: +{unique_count}")
    print(f"   GRAND TOTAL: {grand_total} orbit representatives!")
    print(f"   Total increase: {((grand_total - 4155) / 4155) * 100:.1f}% over original!")
    
    if grand_total > 5000:
        print(f"\n🎊 HISTORIC MILESTONE: OVER 5,000 EXTREME RAYS DISCOVERED!")

if __name__ == "__main__":
    analyze_giga_results()