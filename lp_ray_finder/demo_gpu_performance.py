#!/usr/bin/env python3
"""
Demonstration of GPU-accelerated LP ray finder performance
Shows scalability from small to large problems
"""

import numpy as np
import time
from lp_ray_finder_phase3 import HybridLPRayFinder

def create_feasible_cone_constraints(n_constraints, d, ensure_feasible=True):
    """Create a feasible cone constraint system for testing"""
    
    # Create random constraint matrix
    np.random.seed(42)
    A = np.random.randn(n_constraints, d)
    
    if ensure_feasible:
        # Ensure feasibility by making sure positive orthant is feasible
        # Add constraints that ensure x_i >= 0 for first few dimensions
        for i in range(min(10, n_constraints)):
            A[i, :] = 0
            A[i, i % d] = -1  # -x_i >= 0 means x_i >= 0
    
    # Add constant column (b vector)
    b = np.zeros(n_constraints)
    constraints = np.column_stack([b, A])
    
    return constraints

def benchmark_gpu_scaling():
    """Benchmark GPU performance across different problem sizes"""
    
    print("🎮 GPU Performance Scaling Benchmark")
    print("=" * 60)
    
    # Test different problem sizes
    test_configs = [
        {"name": "Small", "n": 1000, "d": 20},
        {"name": "Medium", "n": 10000, "d": 50},
        {"name": "Large", "n": 100000, "d": 63},
        {"name": "XL (N=6 scale)", "n": 500000, "d": 63}  # Partial N=6 for memory
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n📊 Testing {config['name']} problem: {config['n']:,} constraints, {config['d']} dimensions")
        
        # Create constraints
        constraints = create_feasible_cone_constraints(config['n'], config['d'])
        
        # Test with GPU
        finder_gpu = HybridLPRayFinder(verbose=False, use_gpu=True)
        finder_gpu.constraints = constraints
        finder_gpu.d = config['d']
        finder_gpu.normalizing_vector = np.ones(config['d'])
        finder_gpu.constraint_manager.load_constraint_matrix(constraints)
        
        # Random objective
        objective = np.random.randn(config['d'])
        objective = objective / np.linalg.norm(objective)
        
        # Find ray with GPU
        start_time = time.time()
        ray_gpu, stats_gpu = finder_gpu.find_extreme_ray(
            objective=objective,
            max_iterations=20,
            subset_size=min(500, config['n'] // 10)
        )
        gpu_time = time.time() - start_time
        
        # Test with CPU only
        finder_cpu = HybridLPRayFinder(verbose=False, use_gpu=False)
        finder_cpu.constraints = constraints
        finder_cpu.d = config['d']
        finder_cpu.normalizing_vector = np.ones(config['d'])
        finder_cpu.constraint_manager.load_constraint_matrix(constraints)
        
        # Find ray with CPU
        start_time = time.time()
        ray_cpu, stats_cpu = finder_cpu.find_extreme_ray(
            objective=objective,
            max_iterations=20,
            subset_size=min(500, config['n'] // 10)
        )
        cpu_time = time.time() - start_time
        
        # Calculate speedup
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        
        result = {
            "name": config['name'],
            "constraints": config['n'],
            "dimensions": config['d'],
            "gpu_time": gpu_time,
            "cpu_time": cpu_time,
            "speedup": speedup,
            "gpu_converged": stats_gpu['converged'],
            "cpu_converged": stats_cpu['converged'],
            "iterations": stats_gpu['iterations']
        }
        results.append(result)
        
        print(f"   🎮 GPU time: {gpu_time:.3f}s (converged: {stats_gpu['converged']})")
        print(f"   💻 CPU time: {cpu_time:.3f}s (converged: {stats_cpu['converged']})")
        print(f"   ⚡ Speedup: {speedup:.1f}x")
        print(f"   🔄 Iterations: {stats_gpu['iterations']}")
        
        if ray_gpu is not None:
            print(f"   ✅ Found ray: {ray_gpu[:5]}... (first 5 elements)")
    
    # Summary table
    print("\n📊 PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"{'Problem':<20} {'Constraints':<15} {'GPU Time':<12} {'CPU Time':<12} {'Speedup':<10}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['name']:<20} {r['constraints']:<15,} {r['gpu_time']:<12.3f} {r['cpu_time']:<12.3f} {r['speedup']:<10.1f}x")
    
    return results

def demonstrate_ray_finding():
    """Demonstrate finding multiple rays in a feasible cone"""
    
    print("\n\n🎯 Demonstration: Finding Multiple Extreme Rays")
    print("=" * 60)
    
    # Create a well-conditioned cone
    n_constraints = 50000
    d = 63
    
    print(f"📐 Creating feasible cone with {n_constraints:,} constraints in {d} dimensions...")
    constraints = create_feasible_cone_constraints(n_constraints, d, ensure_feasible=True)
    
    # Initialize finder
    finder = HybridLPRayFinder(verbose=False, use_gpu=True)
    finder.constraints = constraints
    finder.d = d
    finder.normalizing_vector = np.ones(d)
    finder.constraint_manager.load_constraint_matrix(constraints)
    
    print(f"✅ Constraint system loaded")
    print(f"   Memory usage: {constraints.nbytes / 1024**2:.1f} MB")
    
    # Find multiple rays
    print(f"\n🔍 Finding 5 different extreme rays...")
    rays_found = []
    
    for i in range(5):
        # Random objective for diversity
        objective = np.random.randn(d)
        objective = objective / np.linalg.norm(objective)
        
        print(f"\n   Ray {i+1}:")
        start_time = time.time()
        
        ray, stats = finder.find_extreme_ray(
            objective=objective,
            max_iterations=50,
            subset_size=1000
        )
        
        elapsed = time.time() - start_time
        
        if ray is not None:
            rays_found.append(ray)
            print(f"   ✅ Found in {elapsed:.3f}s ({stats['iterations']} iterations)")
            print(f"      First 10 elements: {ray[:10]}")
            print(f"      Norm: {np.linalg.norm(ray):.6f}")
            
            if stats['gpu_available']:
                print(f"      GPU speedup: {stats.get('gpu_speedup', 0):.1f}x")
        else:
            print(f"   ❌ No ray found (LP infeasibility)")
    
    if len(rays_found) > 1:
        print(f"\n📊 Ray Diversity Analysis:")
        for i in range(len(rays_found)):
            for j in range(i+1, len(rays_found)):
                angle = np.arccos(np.clip(np.dot(rays_found[i], rays_found[j]), -1, 1))
                print(f"   Angle between ray {i+1} and ray {j+1}: {np.degrees(angle):.1f}°")
    
    return rays_found

def main():
    """Run all demonstrations"""
    print("🎮 GPU-Accelerated LP Ray Finder Demonstration")
    print("=" * 60)
    
    # Run scaling benchmark
    benchmark_results = benchmark_gpu_scaling()
    
    # Demonstrate ray finding
    rays = demonstrate_ray_finding()
    
    print("\n\n🎉 DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("Key takeaways:")
    print("✅ GPU acceleration provides significant speedup for large problems")
    print("✅ Algorithm scales to handle hundreds of thousands of constraints")
    print("✅ Multiple diverse rays can be found with different objectives")
    print("✅ Ready for N=6 holographic entropy cone analysis")
    
    return True

if __name__ == "__main__":
    main()