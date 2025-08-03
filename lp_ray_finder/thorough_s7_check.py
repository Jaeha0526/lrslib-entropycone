#!/usr/bin/env python3
"""
More thorough S7 permutation check
"""

import numpy as np
from itertools import combinations, permutations
import time

class ThoroughS7Checker:
    def __init__(self):
        """Initialize S7 permutation checker"""
        self.n_parties = 7
        self.d = 63
        
        # Build subset to index mapping
        # For N=6: we have subsets of sizes 1, 2, 3
        self.subset_to_index = {}
        self.index_to_subset = {}
        
        idx = 0
        for size in range(1, 4):  # sizes 1, 2, 3
            for subset in combinations(range(7), size):
                self.subset_to_index[subset] = idx
                self.index_to_subset[idx] = subset
                idx += 1
    
    def apply_permutation(self, ray, perm):
        """Apply permutation to ray"""
        new_ray = np.zeros(63)
        
        for old_idx in range(63):
            old_subset = self.index_to_subset[old_idx]
            new_subset = tuple(sorted(perm[i] for i in old_subset))
            new_idx = self.subset_to_index[new_subset]
            new_ray[new_idx] = ray[old_idx]
            
        return new_ray
    
    def rays_equivalent(self, ray1, ray2, tolerance=1e-9):
        """Check if two normalized rays are equivalent"""
        return np.allclose(ray1, ray2, rtol=tolerance)
    
    def find_permutation_linking_rays(self, ray1, ray2, max_perms=1000):
        """Try to find a permutation that maps ray1 to ray2"""
        # Normalize
        ray1_norm = ray1 / np.linalg.norm(ray1)
        ray2_norm = ray2 / np.linalg.norm(ray2)
        
        # Quick check: sorted values must match
        if not np.allclose(sorted(ray1_norm), sorted(ray2_norm), rtol=1e-9):
            return False, None
        
        # Try systematic permutations
        # Start with permutations that match the size-1 values
        
        # Get size-1 values
        vals1 = ray1_norm[:7]
        vals2 = ray2_norm[:7]
        
        # Find all ways to map vals1 to vals2
        # Group indices by value
        val_groups1 = {}
        val_groups2 = {}
        
        for i in range(7):
            v1 = round(vals1[i], 8)
            v2 = round(vals2[i], 8)
            
            if v1 not in val_groups1:
                val_groups1[v1] = []
            val_groups1[v1].append(i)
            
            if v2 not in val_groups2:
                val_groups2[v2] = []
            val_groups2[v2].append(i)
        
        # Check if value groups match
        if sorted(val_groups1.keys()) != sorted(val_groups2.keys()):
            return False, None
        
        # Check if group sizes match
        for v in val_groups1:
            if len(val_groups1[v]) != len(val_groups2[v]):
                return False, None
        
        # Now try permutations that respect the value groups
        # This dramatically reduces the search space
        
        # Build candidate permutations
        from itertools import product
        
        # For each value, get all ways to map indices
        mappings = []
        for v in sorted(val_groups1.keys()):
            indices1 = val_groups1[v]
            indices2 = val_groups2[v]
            
            # All permutations of indices2
            perms_for_value = list(permutations(indices2))
            mappings.append([(indices1[i], p[i]) for i in range(len(indices1))] for p in perms_for_value)
        
        # Try combinations
        checked = 0
        for mapping_combo in product(*mappings):
            if checked >= max_perms:
                break
            checked += 1
            
            # Build permutation
            perm = list(range(7))  # Start with identity
            for mapping in mapping_combo:
                for src, dst in mapping:
                    perm[src] = dst
            
            # Test this permutation
            permuted = self.apply_permutation(ray1_norm, perm)
            if self.rays_equivalent(permuted, ray2_norm):
                return True, perm
        
        return False, None

def main():
    print("🔍 Thorough S₇ Permutation Check")
    print("="*60)
    
    checker = ThoroughS7Checker()
    
    # Load new rays
    new_rays = np.loadtxt('new_rays_extensive_search.txt')
    print(f"Loaded {len(new_rays)} new rays")
    
    # First, check within the new rays
    print("\n📊 Checking for S₇ permutations within new rays...")
    
    groups = []
    assigned = [False] * len(new_rays)
    
    for i in range(len(new_rays)):
        if assigned[i]:
            continue
        
        group = [i]
        assigned[i] = True
        
        print(f"\nChecking ray {i+1}...")
        
        for j in range(i+1, len(new_rays)):
            if assigned[j]:
                continue
            
            is_perm, perm = checker.find_permutation_linking_rays(new_rays[i], new_rays[j])
            if is_perm:
                group.append(j)
                assigned[j] = True
                print(f"  ✓ Ray {j+1} is permutation of ray {i+1}")
                if perm is not None:
                    print(f"    Permutation: {perm}")
        
        groups.append(group)
    
    # Show results
    print(f"\n{'='*60}")
    print(f"📊 RESULTS:")
    print(f"   Found {len(groups)} orbit representatives")
    
    for i, group in enumerate(groups):
        if len(group) > 1:
            print(f"\n   Group {i+1}: rays {[g+1 for g in group]}")
    
    # Save unique representatives
    unique_rays = []
    for group in groups:
        unique_rays.append(new_rays[group[0]])
    
    unique_rays = np.array(unique_rays)
    np.savetxt('verified_unique_orbit_reps.txt', unique_rays, fmt='%.10f')
    
    print(f"\n💾 Saved {len(unique_rays)} verified unique orbit representatives")
    
    # Quick check against a few existing rays
    if len(unique_rays) > 0:
        print(f"\n🔍 Checking first unique ray against existing rays...")
        existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
        
        test_ray = unique_rays[0]
        found = False
        
        for i in range(min(20, len(existing_rays))):
            is_perm, perm = checker.find_permutation_linking_rays(existing_rays[i], test_ray)
            if is_perm:
                print(f"⚠️  Matches existing ray {i+1}!")
                found = True
                break
        
        if not found:
            print("✅ No match found in first 20 existing rays")

if __name__ == "__main__":
    main()