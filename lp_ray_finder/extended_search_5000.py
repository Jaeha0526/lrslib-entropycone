#!/usr/bin/env python3
"""
Extended search with 5000 attempts to find more new rays
"""

import numpy as np
import time
from phase3_no_limit import FullConstraintRayFinder

def main():
    print("🚀 Extended Ray Search with 5000 Attempts")
    print("="*60)
    
    # Load existing rays (now 4155 with our new ones)
    existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
    new_rays_found = np.loadtxt('signature_unique_rays.txt')
    
    # Combine existing and new
    all_known_rays = np.vstack([existing_rays, new_rays_found])
    print(f"Total known orbit representatives: {len(all_known_rays)}")
    
    # Normalize for comparison
    known_normalized = []
    for ray in all_known_rays:
        known_normalized.append(ray / np.linalg.norm(ray))
    known_normalized = np.array(known_normalized)
    
    # Create finder
    finder = FullConstraintRayFinder(verbose=False)
    
    # Load ALL S₇ constraints
    print("\n📁 Loading 8.6M S₇ constraints...")
    s7_file = '/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine'
    start_time = time.time()
    num_constraints = finder.load_all_s7_constraints(s7_file)
    print(f"✅ Loaded {num_constraints:,} constraints in {time.time()-start_time:.1f}s")
    
    # Prepare for extended search
    print("\n🔍 Starting extended search with 5000 attempts...")
    print("   Using varied strategies and parameters")
    
    # Open file to save new rays
    new_rays_file = open('extended_search_new_rays.txt', 'w')
    new_rays_count = 0
    attempts = 5000
    found_existing = 0
    failed = 0
    
    start_search_time = time.time()
    
    for i in range(attempts):
        if i % 100 == 0:
            elapsed = time.time() - start_search_time
            rate = i / elapsed if elapsed > 0 and i > 0 else 0
            print(f"\n📊 Progress: {i}/{attempts} attempts")
            print(f"   New rays found: {new_rays_count}")
            print(f"   Existing rays found: {found_existing}")
            print(f"   Failed attempts: {failed}")
            print(f"   Rate: {rate:.1f} attempts/second")
            
            # Estimate time remaining
            if i > 0:
                eta = (attempts - i) / rate
                print(f"   ETA: {eta/60:.1f} minutes")
        
        # Vary the strategy
        strategy = i % 4
        
        if strategy == 0:
            # Random objective
            objective = np.random.rand(63)
        elif strategy == 1:
            # Sparse objective (more zeros)
            objective = np.random.rand(63)
            objective[np.random.choice(63, 40, replace=False)] = 0
        elif strategy == 2:
            # Objective based on existing ray patterns
            # Use combinations of values from known rays
            idx1, idx2 = np.random.choice(len(all_known_rays), 2, replace=False)
            objective = 0.7 * all_known_rays[idx1] + 0.3 * all_known_rays[idx2]
            objective += 0.1 * np.random.randn(63)  # Add noise
        else:
            # Structured objective (emphasize certain subset sizes)
            objective = np.zeros(63)
            # Emphasize size-2 subsets (components 7-27)
            objective[7:28] = np.random.rand(21)
            objective += 0.1 * np.random.rand(63)
        
        # Normalize objective
        objective = objective / np.linalg.norm(objective)
        
        # Vary initial subset size
        initial_sizes = [500, 750, 1000, 1500, 2000]
        initial_size = initial_sizes[i % len(initial_sizes)]
        
        # Vary max iterations
        max_iters = [30, 50, 75, 100]
        max_iter = max_iters[i % len(max_iters)]
        
        try:
            ray, converged = finder.find_ray_active_set(
                objective, 
                initial_size=initial_size, 
                max_iter=max_iter
            )
            
            if ray is not None and converged:
                # Check if new
                max_dot = np.max(np.abs(known_normalized @ ray))
                
                if max_dot < 0.9999:
                    # Found new ray!
                    new_rays_count += 1
                    
                    # Save to file
                    np.savetxt(new_rays_file, [ray], fmt='%.10f')
                    new_rays_file.flush()
                    
                    # Add to known rays
                    known_normalized = np.vstack([known_normalized, ray])
                    
                    print(f"\n🎉 NEW RAY #{new_rays_count} found at attempt {i+1}!")
                    print(f"   Strategy: {['random', 'sparse', 'combination', 'structured'][strategy]}")
                    print(f"   Initial size: {initial_size}, Max iter: {max_iter}")
                else:
                    found_existing += 1
            else:
                failed += 1
                
        except Exception as e:
            failed += 1
            if i % 100 == 0:  # Only print errors occasionally
                print(f"   Error in attempt {i+1}: {e}")
    
    # Final results
    elapsed_total = time.time() - start_search_time
    new_rays_file.close()
    
    print(f"\n{'='*60}")
    print(f"📊 EXTENDED SEARCH RESULTS:")
    print(f"   Total attempts: {attempts}")
    print(f"   New rays found: {new_rays_count}")
    print(f"   Existing rays found: {found_existing}")
    print(f"   Failed attempts: {failed}")
    print(f"   Total time: {elapsed_total:.1f}s ({elapsed_total/60:.1f} minutes)")
    print(f"   Average time per attempt: {elapsed_total/attempts:.2f}s")
    
    if new_rays_count > 0:
        print(f"\n✅ New rays saved to: extended_search_new_rays.txt")
        print(f"🎉 FOUND {new_rays_count} MORE NEW RAYS!")
        print(f"   Total orbit representatives now: {4155 + new_rays_count}")
        
        # Run S7 check on new rays
        print("\n🔍 Running S₇ permutation analysis on new rays...")
        import subprocess
        subprocess.run(['python', 'check_extended_permutations.py'])
    else:
        print("\n💡 No additional new rays found in this extended search")

if __name__ == "__main__":
    main()