#!/usr/bin/env python3
"""
ULTRA SEARCH: 50,000 Attempts for Maximum Ray Discovery
This is the most comprehensive search yet!
"""

import numpy as np
import cupy as cp
import time
import random
from datetime import datetime
import os

# Import the ray finder
from phase3_no_limit import FullConstraintRayFinder

def ultra_search_50000():
    print("⚡ ULTRA SEARCH: 50,000 Attempts Starting!")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Expected runtime: 8-10 hours")
    
    # Initialize with full S7 constraints
    print("📊 Loading all 8,665,853 S₇ constraints...")
    finder = FullConstraintRayFinder()
    finder.load_all_s7_constraints('/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine')
    
    print(f"✅ Loaded {len(finder.constraints)} constraints")
    print(f"📐 Constraint matrix shape: {finder.constraints.shape}")
    
    # Search parameters
    total_attempts = 50000
    new_rays = []
    found_count = 0
    
    # Ultra-diverse search strategies
    strategies = {
        'random': 0.15,         # 15% pure random
        'sparse': 0.15,         # 15% sparse objectives  
        'structured': 0.10,     # 10% structured patterns
        'combination': 0.10,    # 10% combinations
        'gaussian': 0.10,       # 10% Gaussian distributed
        'exponential': 0.08,    # 8% exponential decay
        'hybrid': 0.08,         # 8% hybrid approaches
        'binary': 0.06,         # 6% binary patterns
        'ternary': 0.06,        # 6% ternary patterns
        'fibonacci': 0.06,      # 6% Fibonacci-based
        'prime': 0.06          # 6% prime-based patterns
    }
    
    print(f"\n🎯 Ultra Search Configuration:")
    print(f"   Total attempts: {total_attempts:,}")
    print(f"   Strategies: 11 diverse approaches")
    print(f"   Expected new rays: ~{int(total_attempts * 0.08)} (8% success rate)")
    
    start_time = time.time()
    checkpoint_interval = 100  # Save every 100 rays
    
    for attempt in range(total_attempts):
        # Select strategy
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
            num_nonzero = random.randint(3, 15)
            indices = random.sample(range(63), num_nonzero)
            for idx in indices:
                objective[idx] = random.gauss(0, 1)
                
        elif strategy == 'structured':
            objective = np.zeros(63)
            objective[0] = random.gauss(0, 0.5)  # Empty set
            objective[1:7] = np.random.randn(6) * 0.7   # Singles
            objective[7:28] = np.random.randn(21) * 1.0  # Pairs
            objective[28:63] = np.random.randn(35) * 1.3 # Triples
            
        elif strategy == 'combination':
            obj1 = np.random.randn(63)
            obj2 = np.zeros(63)
            obj2[random.sample(range(63), 10)] = np.random.randn(10) * 2
            alpha = random.random()
            objective = alpha * obj1 + (1-alpha) * obj2
            
        elif strategy == 'gaussian':
            means = np.random.randn(63) * 0.5
            stds = np.abs(np.random.randn(63)) * 0.3 + 0.1
            objective = np.random.normal(means, stds)
            
        elif strategy == 'exponential':
            rates = np.abs(np.random.randn(63)) * 0.5 + 0.1
            objective = np.random.exponential(1/rates) * np.random.choice([-1, 1], 63)
            
        elif strategy == 'hybrid':
            base = np.random.randn(63)
            pattern = np.sin(np.arange(63) * random.random() * np.pi)
            objective = base + pattern * random.random() * 2
            
        elif strategy == 'binary':
            objective = np.random.choice([0, 1], 63).astype(float)
            objective = objective + np.random.randn(63) * 0.1  # Small noise
            
        elif strategy == 'ternary':
            objective = np.random.choice([-1, 0, 1], 63).astype(float)
            objective = objective + np.random.randn(63) * 0.15
            
        elif strategy == 'fibonacci':
            fib = [1, 1]
            while len(fib) < 63:
                fib.append(fib[-1] + fib[-2])
            objective = np.array(fib[:63]) % 10 - 5
            objective = objective + np.random.randn(63) * 0.2
            
        elif strategy == 'prime':
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
            objective = np.zeros(63)
            for i, p in enumerate(primes[:min(len(primes), 63)]):
                objective[p % 63] = (i + 1) * random.choice([-1, 1])
            objective = objective + np.random.randn(63) * 0.3
        
        # Normalize
        if np.linalg.norm(objective) > 0:
            objective = objective / np.linalg.norm(objective)
        else:
            objective = np.random.randn(63)
            objective = objective / np.linalg.norm(objective)
        
        # Find ray
        try:
            initial_size = random.choice([100, 200, 300, 500, 750, 1000, 1500, 2000])
            max_iter = random.choice([20, 30, 50, 100])
            
            ray, converged = finder.find_ray_active_set(
                objective, 
                initial_size=initial_size, 
                max_iter=max_iter
            )
            
            if converged and ray is not None:
                new_rays.append(ray.tolist())
                found_count += 1
                
                # Save checkpoint
                if found_count % checkpoint_interval == 0:
                    with open('ultra_search_50k_rays.txt', 'w') as f:
                        for r in new_rays:
                            f.write(' '.join(f'{x:.10f}' for x in r) + '\\n')
                    print(f"\\n💾 Checkpoint: {found_count} rays saved")
        
        except Exception as e:
            if attempt % 5000 == 0 and attempt > 0:
                print(f"\\n⚠️  Attempt {attempt}: {str(e)[:50]}...")
        
        # Progress updates
        if (attempt + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            rate = (attempt + 1) / elapsed * 60  # attempts per minute
            remaining_time = (total_attempts - attempt - 1) / rate if rate > 0 else 0
            
            print(f"\\n📈 Progress: {attempt+1:,}/{total_attempts:,} ({((attempt+1)/total_attempts)*100:.1f}%)")
            print(f"   Found: {found_count} rays (strategy: {strategy})")
            print(f"   Rate: {rate:.1f} attempts/min")
            print(f"   ETA: {remaining_time:.1f} minutes ({remaining_time/60:.1f} hours)")
            print(f"   Success rate: {(found_count/(attempt+1))*100:.2f}%")
            print(f"   Est. total: {int(found_count / ((attempt+1)/total_attempts))}")
    
    # Final save
    print(f"\\n🎉 ULTRA SEARCH COMPLETE!")
    print(f"   Total attempts: {total_attempts:,}")
    print(f"   Total rays found: {found_count}")
    print(f"   Success rate: {(found_count/total_attempts)*100:.2f}%")
    print(f"   Runtime: {(time.time() - start_time)/3600:.1f} hours")
    
    # Save final results
    if new_rays:
        with open('ultra_search_50k_rays.txt', 'w') as f:
            for ray in new_rays:
                f.write(' '.join(f'{x:.10f}' for x in ray) + '\\n')
        print(f"💾 Final results saved to: ultra_search_50k_rays.txt")
        
        # Run S7 analysis
        print(f"\\n🔍 Running S₇ permutation analysis...")
        os.system("python analyze_ultra_search_s7.py")
    else:
        print("❌ No rays found")

if __name__ == "__main__":
    ultra_search_50000()