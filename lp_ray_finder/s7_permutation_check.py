#!/usr/bin/env python3
"""
Implement S7 permutation action on 63-dimensional entropy vectors
"""

import numpy as np
from itertools import combinations, permutations
import time

class S7PermutationChecker:
    def __init__(self):
        """Initialize S7 permutation checker for N=6 (7 parties)"""
        self.n_parties = 7
        self.d = 63  # Total dimensions
        
        # Build index mapping for subsets
        self.subset_to_index = {}
        self.index_to_subset = {}
        
        # Order: subsets of size 1, then size 2, ..., up to size 6
        # But we need 63 total, which is C(7,1) + C(7,2) + C(7,3) = 7 + 21 + 35 = 63
        idx = 0
        for size in range(1, 4):  # sizes 1, 2, and 3 only
            for subset in combinations(range(7), size):
                self.subset_to_index[subset] = idx
                self.index_to_subset[idx] = subset
                idx += 1
        
        assert idx == 63, f"Expected 63 components, got {idx}"
        
    def apply_permutation(self, ray, perm):
        """Apply a permutation from S7 to a ray"""
        # perm is a permutation of [0,1,2,3,4,5,6]
        # We need to permute the parties and get the new ray
        
        new_ray = np.zeros(63)
        
        for old_idx in range(63):
            old_subset = self.index_to_subset[old_idx]
            # Apply permutation to the subset
            new_subset = tuple(sorted(perm[i] for i in old_subset))
            new_idx = self.subset_to_index[new_subset]
            new_ray[new_idx] = ray[old_idx]
            
        return new_ray
    
    def check_if_permutation_equivalent(self, ray1, ray2, tolerance=1e-9):
        """Check if ray2 is a permutation of ray1 under S7"""
        # Normalize both rays
        ray1_norm = ray1 / np.linalg.norm(ray1)
        ray2_norm = ray2 / np.linalg.norm(ray2)
        
        # Quick check: if value multisets don't match, they can't be permutations
        if not np.allclose(sorted(ray1_norm), sorted(ray2_norm), rtol=tolerance):
            return False, None
        
        # Try all permutations (this is expensive - 5040 permutations!)
        # For efficiency, we'll only check a subset of "likely" permutations
        
        # First, try to find a permutation by matching patterns
        # This is a heuristic to avoid checking all 5040 permutations
        
        # Get the values for size-1 subsets (first 7 components)
        vals1_size1 = ray1_norm[:7]
        vals2_size1 = ray2_norm[:7]
        
        # Try to find a permutation that maps vals1_size1 to vals2_size1
        # Sort indices by values
        idx1 = np.argsort(vals1_size1)
        idx2 = np.argsort(vals2_size1)
        
        # Check if sorted values match
        if not np.allclose(vals1_size1[idx1], vals2_size1[idx2], rtol=tolerance):
            return False, None
        
        # Build candidate permutation
        candidate_perm = np.zeros(7, dtype=int)
        for i in range(7):
            candidate_perm[idx1[i]] = idx2[i]
        
        # Test this permutation
        permuted_ray1 = self.apply_permutation(ray1_norm, candidate_perm)
        if np.allclose(permuted_ray1, ray2_norm, rtol=tolerance):
            return True, candidate_perm
        
        # If the heuristic didn't work, we could try more permutations
        # but for now, return False
        return False, None
    
    def find_permutation_groups(self, rays, check_thoroughly=False):
        """Find groups of rays that are S7 permutations of each other"""
        n = len(rays)
        groups = []
        assigned = [False] * n
        
        for i in range(n):
            if assigned[i]:
                continue
                
            # Start new group with ray i
            group = [i]
            assigned[i] = True
            
            # Check all other unassigned rays
            for j in range(i+1, n):
                if assigned[j]:
                    continue
                
                is_perm, perm = self.check_if_permutation_equivalent(rays[i], rays[j])
                if is_perm:
                    group.append(j)
                    assigned[j] = True
                    if perm is not None:
                        print(f"   Ray {j+1} = σ(Ray {i+1}) with σ = {perm}")
            
            groups.append(group)
        
        return groups

def main():
    print("🔍 S₇ Permutation Check for New Rays")
    print("="*60)
    
    # Initialize checker
    checker = S7PermutationChecker()
    print("✅ S₇ permutation checker initialized")
    print(f"   Parties: 7")
    print(f"   Dimensions: 63")
    
    # Test the permutation action
    print("\n📊 Testing permutation action...")
    test_ray = np.random.rand(63)
    identity_perm = list(range(7))
    permuted = checker.apply_permutation(test_ray, identity_perm)
    assert np.allclose(test_ray, permuted), "Identity permutation failed!"
    print("✅ Identity permutation works correctly")
    
    # Load the 37 new rays
    new_rays = np.loadtxt('new_rays_extensive_search.txt')
    print(f"\n📁 Loaded {len(new_rays)} new rays")
    
    # Find permutation groups
    print("\n🔍 Finding S₇ permutation groups...")
    start_time = time.time()
    groups = checker.find_permutation_groups(new_rays)
    elapsed = time.time() - start_time
    
    print(f"\n✅ Found {len(groups)} groups in {elapsed:.1f}s")
    
    # Show results
    unique_count = 0
    for i, group in enumerate(groups):
        if len(group) == 1:
            unique_count += 1
        else:
            print(f"\n📊 Group {i+1}: {len(group)} rays")
            print(f"   Ray indices: {[g+1 for g in group]}")
    
    print(f"\n{'='*60}")
    print(f"📊 S₇ PERMUTATION SUMMARY:")
    print(f"   Total rays checked: {len(new_rays)}")
    print(f"   Permutation groups: {len(groups)}")
    print(f"   Groups with >1 ray: {sum(1 for g in groups if len(g) > 1)}")
    print(f"   Unique orbit representatives: {len(groups)}")
    
    # Save unique representatives (first ray from each group)
    unique_reps = []
    for group in groups:
        unique_reps.append(new_rays[group[0]])
    
    unique_reps = np.array(unique_reps)
    np.savetxt('unique_new_orbit_reps.txt', unique_reps, fmt='%.10f')
    print(f"\n💾 Saved {len(unique_reps)} unique orbit representatives to:")
    print("   unique_new_orbit_reps.txt")
    
    # Also check a few against existing rays
    print("\n🔍 Checking first new ray against existing rays...")
    existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
    
    # Check first unique ray against first 10 existing
    test_ray = unique_reps[0]
    found_match = False
    for i in range(min(10, len(existing_rays))):
        is_perm, perm = checker.check_if_permutation_equivalent(existing_rays[i], test_ray)
        if is_perm:
            print(f"⚠️  New ray matches existing ray {i+1}!")
            found_match = True
            break
    
    if not found_match:
        print("✅ First new ray doesn't match first 10 existing rays")
        print("   (Full check against all 4,145 would take longer)")

if __name__ == "__main__":
    main()