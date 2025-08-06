#!/usr/bin/env python3
"""
Flexible S7 verification using invariant signatures
Verifies new rays against known rays and checks internal S7 duplicates
"""

import numpy as np
import os
import argparse
from collections import Counter

def get_s7_invariant_signature(ray, tolerance=1e-10):
    """
    Get S₇-invariant signature of a ray.
    This includes properties that don't change under S₇ permutations.
    """
    # Absolute values sorted (invariant under S₇)
    abs_vals = np.abs(ray)
    
    # Count of different value types
    n_zeros = np.sum(abs_vals < tolerance)
    n_ones = np.sum(np.abs(abs_vals - 1.0) < tolerance)
    n_halves = np.sum(np.abs(abs_vals - 0.5) < tolerance)
    n_1_32 = np.sum(np.abs(abs_vals - 1/32) < tolerance)
    n_1_16 = np.sum(np.abs(abs_vals - 1/16) < tolerance)
    
    # Sum of absolute values (invariant)
    sum_abs = np.sum(abs_vals)
    
    # Sorted absolute values hash
    sorted_hash = hash(tuple(np.round(np.sort(abs_vals), 10)))
    
    return {
        'n_zeros': n_zeros,
        'n_1_32': n_1_32,
        'n_1_16': n_1_16,
        'sum_abs': round(sum_abs, 10),
        'min_nonzero': round(np.min(abs_vals[abs_vals > tolerance]), 10) if n_zeros < 63 else 0,
        'max_val': round(np.max(abs_vals), 10),
        'sorted_hash': sorted_hash
    }

def rays_potentially_s7_equivalent(ray1, ray2):
    """
    Quick check if two rays could be S₇ equivalent based on invariants.
    """
    sig1 = get_s7_invariant_signature(ray1)
    sig2 = get_s7_invariant_signature(ray2)
    
    # These must match exactly for S₇ equivalence
    if sig1['n_zeros'] != sig2['n_zeros']:
        return False
    if sig1['n_1_32'] != sig2['n_1_32']:
        return False
    if abs(sig1['sum_abs'] - sig2['sum_abs']) > 1e-8:
        return False
    if sig1['sorted_hash'] != sig2['sorted_hash']:
        return False
    
    return True

def load_rays_from_file(filepath, max_rays=None):
    """Load rays from file, optionally limiting number"""
    rays = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                try:
                    # Remove comment part if present
                    ray_data = line.split('#')[0].strip()
                    ray = np.fromstring(ray_data, sep=' ')
                    if len(ray) == 63:
                        rays.append(ray)
                        if max_rays and len(rays) >= max_rays:
                            break
                except:
                    pass
    return np.array(rays)

def find_internal_s7_duplicates(rays):
    """
    Find S7 duplicates within a set of newly discovered rays.
    Returns groups of potentially equivalent rays.
    """
    print(f"🔍 Checking {len(rays)} new rays for internal S₇ duplicates...")
    
    s7_groups = {}  # signature -> list of ray indices
    potential_duplicates = []
    
    for i, ray in enumerate(rays):
        sig = get_s7_invariant_signature(ray)
        sig_key = (sig['n_zeros'], sig['n_1_32'], sig['sum_abs'], sig['sorted_hash'])
        
        if sig_key in s7_groups:
            # Found potential duplicate
            s7_groups[sig_key].append(i)
            print(f"  ⚠️ Ray {i+1} shares S₇ signature with ray(s): {[x+1 for x in s7_groups[sig_key][:-1]]}")
        else:
            s7_groups[sig_key] = [i]
    
    # Identify groups with multiple rays
    for sig_key, ray_indices in s7_groups.items():
        if len(ray_indices) > 1:
            potential_duplicates.append(ray_indices)
    
    return potential_duplicates

def select_orbit_representatives(rays, duplicate_groups):
    """
    From groups of potentially S7-equivalent rays, select one representative from each group.
    """
    if not duplicate_groups:
        print("✅ No internal S₇ duplicates found - all rays have unique signatures")
        return list(range(len(rays))), []
    
    print(f"\n📋 Found {len(duplicate_groups)} groups of potentially S₇-equivalent rays:")
    
    representatives = set(range(len(rays)))  # Start with all rays
    removed_rays = []
    
    for group_idx, ray_indices in enumerate(duplicate_groups):
        print(f"  Group {group_idx + 1}: Rays {[i+1 for i in ray_indices]} (keeping ray {ray_indices[0]+1})")
        
        # Keep first ray from each group, remove others
        for ray_idx in ray_indices[1:]:
            representatives.discard(ray_idx)
            removed_rays.append(ray_idx)
    
    return sorted(list(representatives)), removed_rays

def main():
    parser = argparse.ArgumentParser(description='S7 verification of newly discovered rays')
    parser.add_argument('--new', required=True, help='Path to new rays file')
    parser.add_argument('--known', help='Path to known rays file (optional)')
    parser.add_argument('--internal-only', action='store_true', 
                       help='Only check for internal duplicates among new rays')
    
    args = parser.parse_args()
    
    print("🔍 S₇ Permutation Verification")
    print("=" * 60)
    
    # Load new rays
    print(f"Loading new rays from: {args.new}")
    new_rays = load_rays_from_file(args.new)
    print(f"Loaded {len(new_rays)} new rays")
    
    # Step 1: Internal S7 verification
    print("\n" + "=" * 60)
    print("STEP 1: Internal S₇ Verification")
    print("-" * 40)
    
    duplicate_groups = find_internal_s7_duplicates(new_rays)
    representatives, removed = select_orbit_representatives(new_rays, duplicate_groups)
    
    print(f"\n📊 Internal verification results:")
    print(f"  • Total new rays: {len(new_rays)}")
    print(f"  • Unique orbit representatives: {len(representatives)}")
    print(f"  • S₇ duplicates removed: {len(removed)}")
    
    if args.internal_only:
        print("\n✅ Internal-only verification complete!")
        return
    
    # Step 2: External verification (if known rays provided)
    if args.known:
        print("\n" + "=" * 60)
        print("STEP 2: External S₇ Verification")
        print("-" * 40)
        
        print(f"Loading known rays from: {args.known}")
        known_rays = load_rays_from_file(args.known)
        print(f"Loaded {len(known_rays)} known rays")
        
        external_matches = 0
        final_representatives = []
        
        for rep_idx in representatives:
            new_ray = new_rays[rep_idx]
            has_match = False
            
            for known_ray in known_rays:
                if rays_potentially_s7_equivalent(new_ray, known_ray):
                    external_matches += 1
                    print(f"  ⚠️ New ray {rep_idx+1} might be S₇ equivalent to existing ray")
                    has_match = True
                    break
            
            if not has_match:
                final_representatives.append(rep_idx)
                print(f"  ✅ New ray {rep_idx+1} has unique S₇ signature vs known rays")
        
        print(f"\n📊 Final verification results:")
        print(f"  • After internal filtering: {len(representatives)} unique rays")
        print(f"  • Matches with known rays: {external_matches}")
        print(f"  • Genuinely new orbit representatives: {len(final_representatives)}")
        
        if final_representatives:
            print(f"\n🎉 Final unique rays: {[i+1 for i in final_representatives]}")
    
    else:
        print(f"\n🎉 Internal verification complete - {len(representatives)} unique orbit representatives")

if __name__ == "__main__":
    main()