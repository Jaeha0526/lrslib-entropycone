#!/usr/bin/env python3
"""
Test LP-based ray finding using the existing facets and rays data
"""

import numpy as np
from scipy.optimize import linprog
import time

def load_data():
    """Load existing facets and rays"""
    print("Loading existing data...")
    facets = np.loadtxt('/workspace/lrslib-entropycone/n6data/facets.txt')
    rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
    print(f"Loaded {len(facets)} facets and {len(rays)} rays")
    return facets, rays

def find_ray_lp(facets, objective):
    """
    Find extreme ray using LP with facet constraints
    The cone is defined by: facet · ray >= 0 for all facets
    We maximize: objective · ray
    Subject to: facet_i · ray >= 0 for all i, and ||ray||_∞ <= 1
    """
    n_facets, d = facets.shape
    
    # Convert to standard form: Ax <= b
    # facet · ray >= 0 becomes -facet · ray <= 0
    A_ub = -facets
    b_ub = np.zeros(n_facets)
    
    # Bounds: -1 <= ray_i <= 1 for all i (infinity norm constraint)
    bounds = [(-1, 1) for _ in range(d)]
    
    # Solve LP
    result = linprog(
        -objective,  # Maximize objective · ray
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        method='highs',
        options={'disp': False}
    )
    
    if result.success:
        ray = result.x
        # Normalize so largest component is 1
        max_val = np.max(np.abs(ray))
        if max_val > 0:
            ray = ray / max_val
        return ray
    else:
        return None

def test_ray_finding():
    """Test LP-based ray finding"""
    facets, rays = load_data()
    
    print("\n🔍 Testing LP-based ray finding...")
    
    # Test 1: Try to recover ray #1381
    print("\n1. Attempting to recover ray #1381...")
    target_ray = rays[1380]  # 0-indexed
    print(f"   Target ray: {target_ray[:10]}... (first 10 components)")
    
    # Use target ray as objective
    objective = target_ray / np.linalg.norm(target_ray)
    
    start = time.time()
    found_ray = find_ray_lp(facets, objective)
    elapsed = time.time() - start
    
    if found_ray is not None:
        # Scale to match target
        scale = target_ray[0] / found_ray[0] if found_ray[0] != 0 else 1
        found_ray_scaled = found_ray * scale
        
        print(f"   Found ray: {found_ray_scaled[:10]}... (first 10 components)")
        print(f"   Time: {elapsed:.3f}s")
        
        # Check similarity
        found_norm = found_ray / np.linalg.norm(found_ray)
        target_norm = target_ray / np.linalg.norm(target_ray)
        similarity = np.dot(found_norm, target_norm)
        print(f"   Similarity: {similarity:.6f}")
        
        if similarity > 0.999:
            print("   ✅ Successfully recovered ray #1381!")
        else:
            print("   ⚠️  Found different ray")
    else:
        print("   ❌ LP failed")
    
    # Test 2: Search for potentially new rays
    print("\n2. Searching for new rays with random objectives...")
    
    new_rays = []
    num_attempts = 50
    
    for i in range(num_attempts):
        if i % 10 == 0:
            print(f"   Progress: {i}/{num_attempts}", end='\r')
        
        # Random objective
        objective = np.random.randn(63)
        objective = objective / np.linalg.norm(objective)
        
        found_ray = find_ray_lp(facets, objective)
        
        if found_ray is not None:
            # Check if it's new
            is_new = True
            found_norm = found_ray / np.linalg.norm(found_ray)
            
            for existing_ray in rays:
                existing_norm = existing_ray / np.linalg.norm(existing_ray)
                similarity = abs(np.dot(found_norm, existing_norm))
                if similarity > 0.9999:
                    is_new = False
                    break
            
            if is_new:
                new_rays.append(found_ray)
                print(f"\n   ✅ Found potentially new ray #{len(new_rays)}!")
                print(f"      First 10: {found_ray[:10]}")
    
    print(f"\n\n📊 Summary:")
    print(f"   Existing rays: {len(rays)}")
    print(f"   New rays found: {len(new_rays)}")
    
    if len(new_rays) == 0:
        print("   💡 No new rays found - existing set appears complete")
    else:
        print("   🎯 Found new rays not in the existing set!")
    
    # Verify constraints
    if len(new_rays) > 0:
        print("\n3. Verifying new rays satisfy all facet constraints...")
        for i, ray in enumerate(new_rays):
            violations = np.sum(facets @ ray < -1e-10)
            if violations > 0:
                print(f"   Ray {i+1}: {violations} constraint violations")
            else:
                print(f"   Ray {i+1}: ✅ All constraints satisfied")

if __name__ == "__main__":
    test_ray_finding()