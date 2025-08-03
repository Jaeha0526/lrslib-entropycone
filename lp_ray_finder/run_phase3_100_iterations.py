#!/usr/bin/env python3
"""
Run Phase 3 with 100 iterations on S₇ constraints
"""

from lp_ray_finder_phase3 import HybridLPRayFinder
import numpy as np
import time

def main():
    print("🎯 Phase 3 Active-Set with 100 Iterations")
    print("=" * 60)
    
    # Load existing rays
    existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
    print(f"Loaded {len(existing_rays)} existing rays")
    
    # Initialize finder
    finder = HybridLPRayFinder(
        constraint_file='/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine',
        verbose=True,
        use_gpu=True,
        chunk_size=500000
    )
    
    if finder.constraints is None:
        print("❌ Failed to load constraints")
        return
    
    print(f"\n✅ Loaded {len(finder.constraints)} constraints")
    print("Note: This is loading 100K test subset by default")
    
    # Search for new rays with 100 iterations
    print("\n🔍 Searching for new rays with 100 iterations max...")
    
    new_rays = []
    attempts = 20  # Try 20 different random objectives
    
    for i in range(attempts):
        print(f"\n{'='*50}")
        print(f"Attempt {i+1}/{attempts}")
        
        # Random objective
        objective = np.random.rand(63)
        objective = objective / np.linalg.norm(objective)
        
        start_time = time.time()
        
        # Use 100 iterations!
        ray, stats = finder.find_extreme_ray(
            objective=objective,
            max_iterations=100,  # 100 iterations
            subset_size=1000     # Start with 1000 constraints
        )
        
        elapsed = time.time() - start_time
        
        if ray is not None and stats['converged']:
            # Check if new
            is_new = True
            ray_norm = ray / np.linalg.norm(ray)
            
            for existing in existing_rays:
                existing_norm = existing / np.linalg.norm(existing)
                if np.dot(ray_norm, existing_norm) > 0.9999:
                    is_new = False
                    break
            
            if is_new:
                new_rays.append(ray)
                print(f"🎉 NEW RAY FOUND! Total: {len(new_rays)}")
                print(f"   Converged in {stats['iterations']} iterations")
                print(f"   Time: {elapsed:.1f}s")
                print(f"   First 10 components: {ray[:10]}")
                
                # Save immediately
                with open('new_rays_100iter.txt', 'a') as f:
                    f.write(" ".join(f"{x:.10f}" for x in ray) + "\n")
            else:
                print(f"✓ Found existing ray in {stats['iterations']} iterations ({elapsed:.1f}s)")
        else:
            print(f"✗ No convergence after {stats.get('iterations', 0)} iterations ({elapsed:.1f}s)")
            if not stats.get('converged', False):
                print(f"   LP status: Failed or infeasible")
    
    print(f"\n\n📊 FINAL RESULTS:")
    print(f"   Total attempts: {attempts}")
    print(f"   New rays found: {len(new_rays)}")
    print(f"   Success rate: {len(new_rays)/attempts*100:.1f}%")
    
    if len(new_rays) > 0:
        print(f"\n✅ New rays saved to: new_rays_100iter.txt")
        print("🎉 MAJOR DISCOVERY: Found new rays with S₇ constraints!")
    else:
        print("\n💡 No new rays found - existing set appears complete")

if __name__ == "__main__":
    main()