#!/usr/bin/env python3
"""
Mega search with 10,000 attempts for maximum ray discovery
Launches automatically after current search completes
"""

import numpy as np
import cupy as cp
import time
import random
from datetime import datetime
import os

# Import our LP ray finder
from lp_ray_finder import LPRayFinder

def mega_search_10000():
    print("🚀 MEGA SEARCH: 10,000 Attempts Starting!")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize the ray finder with full S7 constraints  
    print("📊 Loading all 8,665,853 S₇ constraints...")
    
    # Use the same approach as extended_search_5000.py
    from phase3_no_limit import FullConstraintRayFinder
    finder = FullConstraintRayFinder()
    finder.load_all_s7_constraints('/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine')
    
    print(f"✅ Loaded {len(finder.constraints)} constraints")
    print(f"📐 Constraint matrix shape: {finder.constraints.shape}")
    
    # Search parameters
    total_attempts = 10000
    new_rays = []
    found_count = 0
    
    # Enhanced search strategies (more diverse than before)
    strategies = {
        'random': 0.20,        # 20% pure random
        'sparse': 0.20,        # 20% sparse objectives  
        'structured': 0.15,    # 15% structured patterns
        'combination': 0.15,   # 15% combinations
        'gaussian': 0.10,      # 10% Gaussian distributed
        'exponential': 0.10,   # 10% exponential decay
        'hybrid': 0.10         # 10% hybrid approaches
    }
    
    print(f"\n🎯 Search Configuration:")
    print(f"   Total attempts: {total_attempts:,}")
    print(f"   Strategies: {strategies}")
    print(f"   Expected new rays: {total_attempts * 0.037:.0f} (3.7% success rate)")
    
    start_time = time.time()
    
    for attempt in range(total_attempts):
        # Select strategy for this attempt
        rand_val = random.random()
        cumulative = 0
        strategy = 'random'
        
        for strat, prob in strategies.items():
            cumulative += prob
            if rand_val <= cumulative:
                strategy = strat
                break
        
        # Generate objective based on strategy
        if strategy == 'random':
            objective = np.random.randn(63)
            
        elif strategy == 'sparse':
            objective = np.zeros(63)
            num_nonzero = random.randint(5, 20)
            indices = random.sample(range(63), num_nonzero)
            for idx in indices:
                objective[idx] = random.gauss(0, 1)
                
        elif strategy == 'structured':
            # Patterns based on entropy structure
            objective = np.zeros(63)
            # Singles: positions 1-6
            objective[1:7] = np.random.randn(6) * 0.5
            # Pairs: positions 7-27  
            objective[7:28] = np.random.randn(21) * 1.0
            # Triples: positions 28-62
            objective[28:63] = np.random.randn(35) * 1.5
            
        elif strategy == 'combination':
            # Combine multiple patterns
            obj1 = np.random.randn(63)
            obj2 = np.zeros(63)
            obj2[random.sample(range(63), 15)] = np.random.randn(15)
            objective = 0.7 * obj1 + 0.3 * obj2
            
        elif strategy == 'gaussian':
            # Different variance for different regions
            objective = np.concatenate([
                np.random.normal(0, 0.5, 7),   # Empty + singles
                np.random.normal(0, 1.0, 21),  # Pairs
                np.random.normal(0, 1.5, 35)   # Triples
            ])
            
        elif strategy == 'exponential':
            # Exponential weights
            weights = np.exp(-np.arange(63) / 20)
            objective = np.random.randn(63) * weights
            
        elif strategy == 'hybrid':
            # Mix random with structure
            base = np.random.randn(63)
            structure = np.zeros(63)
            structure[::3] = 2.0  # Every 3rd position
            objective = base + structure * random.random()
        
        # Normalize objective
        if np.linalg.norm(objective) > 0:
            objective = objective / np.linalg.norm(objective)
        else:
            objective = np.random.randn(63)
            objective = objective / np.linalg.norm(objective)
        
        # Find ray using active set method
        try:
            initial_size = random.choice([50, 100, 150, 200, 300])
            max_iter = random.choice([10, 20, 30])
            
            ray, converged = finder.find_ray_active_set(
                objective, 
                initial_size=initial_size, 
                max_iter=max_iter
            )
            
            if converged and ray is not None:
                new_rays.append(ray.tolist())
                found_count += 1
                
                # Save incrementally every 50 rays
                if found_count % 50 == 0:
                    with open('mega_search_10k_rays.txt', 'w') as f:
                        for r in new_rays:
                            f.write(' '.join(f'{x:.10f}' for x in r) + '\\n')
                    print(f"💾 Saved {found_count} rays (attempt {attempt+1}/{total_attempts})")
        
        except Exception as e:
            if attempt % 1000 == 0:
                print(f"⚠️  Attempt {attempt+1}: {str(e)[:50]}...")
        
        # Progress updates
        if (attempt + 1) % 500 == 0:
            elapsed = time.time() - start_time
            rate = (attempt + 1) / elapsed * 60  # attempts per minute
            remaining_time = (total_attempts - attempt - 1) / rate if rate > 0 else 0
            
            print(f"📈 Progress: {attempt+1:,}/{total_attempts:,} ({((attempt+1)/total_attempts)*100:.1f}%)")
            print(f"   Found: {found_count} rays ({strategy} strategy)")
            print(f"   Rate: {rate:.1f} attempts/min")
            print(f"   ETA: {remaining_time:.1f} minutes")
            print(f"   Success rate: {(found_count/(attempt+1))*100:.2f}%")
    
    # Final save
    print(f"\\n🎉 MEGA SEARCH COMPLETE!")
    print(f"   Total attempts: {total_attempts:,}")
    print(f"   Total rays found: {found_count}")
    print(f"   Success rate: {(found_count/total_attempts)*100:.2f}%")
    print(f"   Runtime: {(time.time() - start_time)/60:.1f} minutes")
    
    # Save final results
    if new_rays:
        with open('mega_search_10k_rays.txt', 'w') as f:
            for ray in new_rays:
                f.write(' '.join(f'{x:.10f}' for x in ray) + '\\n')
        print(f"💾 Final results saved to: mega_search_10k_rays.txt")
        
        # Immediate S7 permutation analysis
        print(f"\\n🔍 Running S₇ permutation analysis...")
        os.system("python analyze_mega_search_s7.py")
    else:
        print("❌ No rays found")

if __name__ == "__main__":
    mega_search_10000()