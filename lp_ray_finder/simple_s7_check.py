#!/usr/bin/env python3
"""
Simple S7 permutation check by comparing ray patterns
"""

import numpy as np
from itertools import combinations
import time

def get_ray_signature(ray, tol=1e-8):
    """Get a signature of a ray that is invariant under S7 permutations"""
    # Round to avoid floating point issues
    ray_rounded = np.round(ray / np.linalg.norm(ray), 8)
    
    # Count occurrences of each unique value
    unique_vals, counts = np.unique(ray_rounded, return_counts=True)
    
    # Sort by value for consistent ordering
    sorted_idx = np.argsort(unique_vals)
    
    # Create signature: (sorted values, sorted counts)
    signature = (
        tuple(unique_vals[sorted_idx]),
        tuple(counts[sorted_idx])
    )
    
    return signature

def rays_potentially_equivalent(ray1, ray2):
    """Quick check if two rays could be S7 permutations of each other"""
    sig1 = get_ray_signature(ray1)
    sig2 = get_ray_signature(ray2)
    
    # Same signature means they could be permutations
    return sig1 == sig2

def analyze_new_rays():
    """Analyze the 37 new rays for S7 equivalences"""
    print("🔍 S₇ Permutation Analysis (Simple Method)")
    print("="*60)
    
    # Load new rays
    new_rays = np.loadtxt('new_rays_extensive_search.txt')
    print(f"Loaded {len(new_rays)} new rays")
    
    # Get signatures for all rays
    signatures = {}
    for i, ray in enumerate(new_rays):
        sig = get_ray_signature(ray)
        if sig not in signatures:
            signatures[sig] = []
        signatures[sig].append(i)
    
    print(f"\n📊 Found {len(signatures)} distinct signatures")
    
    # Show groups
    groups = []
    for sig, indices in signatures.items():
        if len(indices) > 1:
            groups.append(indices)
            print(f"\n📌 Signature group with {len(indices)} rays:")
            print(f"   Ray indices: {[i+1 for i in indices]}")
            print(f"   Value pattern: {len(sig[0])} unique values")
            print(f"   Count pattern: {sig[1]}")
    
    # Count unique representatives
    unique_count = len(signatures)
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY:")
    print(f"   Total rays: {len(new_rays)}")
    print(f"   Distinct signatures: {unique_count}")
    print(f"   Potential S₇ groups: {len(groups)}")
    
    # Save one representative from each signature
    representatives = []
    for sig, indices in signatures.items():
        representatives.append(new_rays[indices[0]])
    
    representatives = np.array(representatives)
    np.savetxt('signature_unique_rays.txt', representatives, fmt='%.10f')
    print(f"\n💾 Saved {len(representatives)} signature-unique rays")
    
    # Also check against existing rays
    print("\n🔍 Checking signatures against existing rays...")
    existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
    
    # Get signatures for first 100 existing rays
    existing_sigs = set()
    for i in range(min(100, len(existing_rays))):
        sig = get_ray_signature(existing_rays[i])
        existing_sigs.add(sig)
    
    # Check how many new signatures match existing ones
    matches = 0
    for sig in signatures:
        if sig in existing_sigs:
            matches += 1
            print(f"\n⚠️  Signature {sig[1]} matches existing rays!")
            print(f"   New ray indices: {[i+1 for i in signatures[sig]]}")
    
    if matches == 0:
        print("\n✅ No signature matches found with first 100 existing rays")
    else:
        print(f"\n⚠️  {matches} signatures match existing rays")
        print("   These might be S₇ permutations of existing rays")
    
    return unique_count

if __name__ == "__main__":
    unique_count = analyze_new_rays()
    
    print(f"\n🎯 FINAL RESULT: Found {unique_count} potentially unique orbit representatives")