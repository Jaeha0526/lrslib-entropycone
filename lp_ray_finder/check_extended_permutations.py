#!/usr/bin/env python3
"""
Check S7 permutations for extended search results
"""

import numpy as np
import os

def get_ray_signature(ray, tol=1e-8):
    """Get signature of a ray"""
    ray_rounded = np.round(ray / np.linalg.norm(ray), 8)
    unique_vals, counts = np.unique(ray_rounded, return_counts=True)
    sorted_idx = np.argsort(unique_vals)
    signature = (
        tuple(unique_vals[sorted_idx]),
        tuple(counts[sorted_idx])
    )
    return signature

def main():
    if not os.path.exists('extended_search_new_rays.txt'):
        print("No extended search results to analyze")
        return
    
    # Load new rays from extended search
    try:
        new_rays = np.loadtxt('extended_search_valid.txt')
        if new_rays.ndim == 1:
            new_rays = new_rays.reshape(1, -1)
    except Exception as e:
        print(f"Error loading rays: {e}")
        return
    
    print(f"Analyzing {len(new_rays)} rays from extended search...")
    
    # Get signatures
    signatures = {}
    for i, ray in enumerate(new_rays):
        sig = get_ray_signature(ray)
        if sig not in signatures:
            signatures[sig] = []
        signatures[sig].append(i)
    
    print(f"Found {len(signatures)} unique signatures")
    
    # Save unique representatives
    unique_rays = []
    for sig, indices in signatures.items():
        unique_rays.append(new_rays[indices[0]])
        if len(indices) > 1:
            print(f"  Signature group: {len(indices)} rays (indices {indices})")
    
    unique_rays = np.array(unique_rays)
    np.savetxt('extended_unique_rays.txt', unique_rays, fmt='%.10f')
    
    print(f"\n✅ {len(unique_rays)} unique orbit representatives from extended search")
    print(f"💾 Saved to: extended_unique_rays.txt")

if __name__ == "__main__":
    main()