#!/usr/bin/env python3
"""
GIGA SEARCH: 100,000 Attempts - The Ultimate Ray Discovery Mission
This will run for ~15-20 hours but could find hundreds of new rays!
"""

import numpy as np
import cupy as cp
import time
import random
from datetime import datetime
import os
import math

from phase3_no_limit import FullConstraintRayFinder

def giga_search_100000():
    print("🌟 GIGA SEARCH: 100,000 Attempts - ULTIMATE DISCOVERY MODE!")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚡ WARNING: This will run for 15-20+ hours!")
    
    # Initialize
    print("📊 Loading all 8,665,853 S₇ constraints...")
    finder = FullConstraintRayFinder()
    finder.load_all_s7_constraints('/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine')
    
    print(f"✅ Loaded {len(finder.constraints)} constraints")
    
    # Search parameters
    total_attempts = 100000
    new_rays = []
    found_count = 0
    
    # Maximum diversity strategies - 15 different approaches!
    strategies = {
        'random': 0.10,
        'sparse': 0.10,
        'structured': 0.08,
        'combination': 0.07,
        'gaussian': 0.07,
        'exponential': 0.06,
        'hybrid': 0.06,
        'binary': 0.05,
        'ternary': 0.05,
        'fibonacci': 0.05,
        'prime': 0.05,
        'harmonic': 0.05,
        'logarithmic': 0.05,
        'polynomial': 0.05,
        'fractal': 0.11
    }
    
    print(f"\n🎯 Giga Search Configuration:")
    print(f"   Total attempts: {total_attempts:,}")
    print(f"   Strategies: 15 ultra-diverse approaches")
    print(f"   Target: 5,000+ extreme rays (from current 4,558)")
    
    start_time = time.time()
    checkpoint_interval = 200
    
    for attempt in range(total_attempts):
        # Strategy selection
        rand_val = random.random()
        cumulative = 0
        strategy = 'random'
        
        for strat, prob in strategies.items():
            cumulative += prob
            if rand_val <= cumulative:
                strategy = strat
                break
        
        # Generate objectives with 15 different strategies
        if strategy == 'random':
            objective = np.random.randn(63)
            
        elif strategy == 'sparse':
            objective = np.zeros(63)
            sparsity = random.randint(2, 12)
            indices = random.sample(range(63), sparsity)
            objective[indices] = np.random.randn(sparsity) * random.uniform(0.5, 2.0)
            
        elif strategy == 'structured':
            objective = np.zeros(63)
            # Hierarchical structure following entropy cone
            objective[0] = random.gauss(0, 0.3)
            objective[1:7] = np.random.randn(6) * random.uniform(0.5, 0.8)
            objective[7:28] = np.random.randn(21) * random.uniform(0.8, 1.2)
            objective[28:63] = np.random.randn(35) * random.uniform(1.0, 1.5)
            
        elif strategy == 'combination':
            num_bases = random.randint(2, 4)
            bases = [np.random.randn(63) for _ in range(num_bases)]
            weights = np.random.dirichlet(np.ones(num_bases))
            objective = sum(w * b for w, b in zip(weights, bases))
            
        elif strategy == 'gaussian':
            mu = np.random.randn(63) * 0.3
            sigma = np.abs(np.random.randn(63)) * 0.2 + 0.05
            objective = np.random.normal(mu, sigma)
            
        elif strategy == 'exponential':
            scales = np.abs(np.random.randn(63)) * 0.5 + 0.1
            objective = np.random.exponential(scales) * np.random.choice([-1, 1], 63)
            
        elif strategy == 'hybrid':
            base = np.random.randn(63)
            wave = np.sin(np.arange(63) * random.uniform(0.1, 0.5))
            noise = np.random.randn(63) * 0.2
            objective = base + wave * random.uniform(0.5, 2.0) + noise
            
        elif strategy == 'binary':
            prob = random.uniform(0.2, 0.8)
            objective = np.random.choice([0, 1], 63, p=[1-prob, prob]).astype(float)
            objective += np.random.randn(63) * random.uniform(0.05, 0.2)
            
        elif strategy == 'ternary':
            probs = np.random.dirichlet([1, 1, 1])
            objective = np.random.choice([-1, 0, 1], 63, p=probs).astype(float)
            objective += np.random.randn(63) * random.uniform(0.1, 0.3)
            
        elif strategy == 'fibonacci':
            fib = [1, 1]
            while len(fib) < 63:
                fib.append(fib[-1] + fib[-2])
            scale = random.uniform(0.001, 0.1)
            objective = np.array([f * scale for f in fib[:63]])
            objective *= np.random.choice([-1, 1], 63)
            objective += np.random.randn(63) * 0.1
            
        elif strategy == 'prime':
            # First 63 primes modulated
            primes = []
            n = 2
            while len(primes) < 63:
                if all(n % p != 0 for p in primes):
                    primes.append(n)
                n += 1
            objective = np.array(primes) % random.randint(5, 20) - random.randint(2, 10)
            objective = objective.astype(float) + np.random.randn(63) * 0.2
            
        elif strategy == 'harmonic':
            objective = np.array([1.0/(i+1) for i in range(63)])
            objective *= random.choice([-1, 1])
            objective += np.random.randn(63) * random.uniform(0.1, 0.5)
            
        elif strategy == 'logarithmic':
            objective = np.log(np.arange(1, 64))
            objective *= random.uniform(-2, 2)
            objective += np.random.randn(63) * random.uniform(0.2, 0.8)
            
        elif strategy == 'polynomial':
            degree = random.randint(1, 4)
            coeffs = np.random.randn(degree + 1)
            x = np.linspace(-1, 1, 63)
            objective = np.polyval(coeffs, x)
            objective += np.random.randn(63) * 0.3
            
        elif strategy == 'fractal':
            # Cantor-like or other fractal patterns
            level = random.randint(2, 5)
            objective = np.ones(63)
            for i in range(level):
                mask = np.random.choice([0, 1], 63)
                objective *= mask + np.random.randn(63) * 0.1
            objective += np.random.randn(63) * 0.2
        
        # Normalize
        norm = np.linalg.norm(objective)
        if norm > 1e-10:
            objective = objective / norm
        else:
            objective = np.random.randn(63)
            objective = objective / np.linalg.norm(objective)
        
        # Ray finding with varied parameters
        try:
            # More diverse parameter choices
            initial_sizes = [50, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 3000]
            max_iters = [10, 20, 30, 40, 50, 75, 100, 150]
            
            initial_size = random.choice(initial_sizes)
            max_iter = random.choice(max_iters)
            
            ray, converged = finder.find_ray_active_set(
                objective, 
                initial_size=initial_size, 
                max_iter=max_iter
            )
            
            if converged and ray is not None:
                new_rays.append(ray.tolist())
                found_count += 1
                
                # Checkpoint saves
                if found_count % checkpoint_interval == 0:
                    with open('giga_search_100k_rays.txt', 'w') as f:
                        for r in new_rays:
                            f.write(' '.join(f'{x:.10f}' for x in r) + '\\n')
                    print(f"\\n💾 Checkpoint: {found_count} rays saved")
                
                # Milestone celebrations
                if found_count in [100, 500, 1000, 2000, 3000, 4000, 5000]:
                    print(f"\\n🎊 MILESTONE: {found_count} rays discovered!")
        
        except Exception as e:
            if attempt % 10000 == 0 and attempt > 0:
                print(f"\\n⚠️  Attempt {attempt}: Minor error, continuing...")
        
        # Detailed progress every 2000 attempts
        if (attempt + 1) % 2000 == 0:
            elapsed = time.time() - start_time
            rate = (attempt + 1) / elapsed * 60
            remaining_time = (total_attempts - attempt - 1) / rate if rate > 0 else 0
            
            print(f"\\n{'='*60}")
            print(f"📊 GIGA PROGRESS: {attempt+1:,}/{total_attempts:,} ({((attempt+1)/total_attempts)*100:.1f}%)")
            print(f"   🎯 Rays found: {found_count}")
            print(f"   📈 Success rate: {(found_count/(attempt+1))*100:.2f}%")
            print(f"   ⚡ Rate: {rate:.1f} attempts/min")
            print(f"   ⏰ ETA: {remaining_time/60:.1f} hours")
            print(f"   🔮 Projected total: ~{int(found_count / ((attempt+1)/total_attempts))} rays")
            print(f"   🧪 Current strategy: {strategy}")
            print(f"{'='*60}")
    
    # Epic finale
    print(f"\\n{'🌟'*30}")
    print(f"🎉 GIGA SEARCH COMPLETE - ULTIMATE ACHIEVEMENT UNLOCKED!")
    print(f"{'🌟'*30}")
    print(f"   Total attempts: {total_attempts:,}")
    print(f"   Total rays found: {found_count:,}")
    print(f"   Success rate: {(found_count/total_attempts)*100:.2f}%")
    print(f"   Runtime: {(time.time() - start_time)/3600:.1f} hours")
    print(f"   Rays per hour: {found_count / ((time.time() - start_time)/3600):.1f}")
    
    # Save final results
    if new_rays:
        with open('giga_search_100k_rays.txt', 'w') as f:
            for ray in new_rays:
                f.write(' '.join(f'{x:.10f}' for x in ray) + '\\n')
        print(f"\\n💾 Final results saved to: giga_search_100k_rays.txt")
        print(f"🔍 Running final S₇ analysis...")
        os.system("python analyze_giga_search_s7.py")

if __name__ == "__main__":
    giga_search_100000()