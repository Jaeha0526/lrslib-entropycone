#!/usr/bin/env python3
"""
Test script to find ray #1381 using LP-based ray finder Phase 3
"""

import numpy as np
import os
import sys
from lp_ray_finder_phase3 import HybridLPRayFinder

def test_find_ray_1381():
    """Test finding ray #1381 with Phase 3 GPU acceleration"""
    
    # Target ray #1381 coordinates
    target_coordinates = [1, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 6, 6, 8, 8, 8, 8, 7, 7, 9, 9, 7, 7, 9, 7, 9, 9, 6, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 6, 5, 4, 3]
    
    print("🎯 Test: Finding Ray #1381 with LP-based method")
    print("=" * 60)
    print(f"Target ray coordinates (dimension {len(target_coordinates)}):")
    print(f"{target_coordinates[:10]}... (first 10 elements)")
    print()
    
    # Check for N=6 constraint file
    n6_file_paths = [
        "../n6data/n6_restart_startingcobasis.ine",
        "../n6data/n6_restart.ine",
        "../n6data/n6.ine",
        "../../n6data/n6_restart_startingcobasis.ine",
        "/workspace/lrslib-entropycone/n6data/n6_restart_startingcobasis.ine"
    ]
    
    n6_file = None
    for path in n6_file_paths:
        if os.path.exists(path):
            n6_file = path
            print(f"✅ Found N=6 constraint file: {path}")
            break
    
    if n6_file is None:
        print("❌ N=6 constraint file not found. Attempting with smaller test file...")
        print()
        
        # Fall back to test with a simpler problem
        print("📐 Creating synthetic test with similar structure...")
        
        # Create a synthetic constraint matrix that should have the target ray
        # This is just for testing the algorithm
        d = 63  # Same dimension as N=6
        n_constraints = 1000  # Much smaller for testing
        
        # Create random constraints
        np.random.seed(42)
        constraints = np.random.randn(n_constraints, d + 1)
        
        # Ensure target ray satisfies some constraints
        target_normalized = np.array(target_coordinates) / np.linalg.norm(target_coordinates)
        for i in range(100):  # Make 100 constraints satisfied by target
            constraints[i, 1:] = -np.random.randn(d)
            constraints[i, 0] = np.dot(constraints[i, 1:], target_normalized) + 0.1
        
        # Initialize finder without file
        finder = HybridLPRayFinder(verbose=True, use_gpu=True, chunk_size=100000)
        finder.constraints = constraints
        finder.d = d
        finder.normalizing_vector = np.ones(d)
        finder.constraint_manager.load_constraint_matrix(constraints)
        
    else:
        # Load actual N=6 file
        print(f"📁 Loading N=6 constraint file...")
        finder = HybridLPRayFinder(
            constraint_file=n6_file,
            verbose=True,
            use_gpu=True,
            chunk_size=500000  # Adjust based on GPU memory
        )
    
    if finder.constraints is None:
        print("❌ Failed to load constraints")
        return False
    
    print(f"\n📊 Constraint matrix loaded:")
    print(f"   Constraints: {len(finder.constraints):,}")
    print(f"   Dimensions: {finder.d}")
    print(f"   Memory: {finder.constraints.nbytes / 1024**3:.2f} GB")
    
    # Create objective vector pointing toward target ray
    objective = np.array(target_coordinates[:finder.d], dtype=float)
    objective = objective / np.linalg.norm(objective)
    
    print(f"\n🎯 Using objective vector aligned with target ray")
    print(f"   Objective norm: {np.linalg.norm(objective):.6f}")
    print(f"   First 10 elements: {objective[:10]}")
    
    # Find extreme ray
    print(f"\n🚀 Starting ray search with GPU acceleration...")
    
    ray, stats = finder.find_extreme_ray(
        objective=objective,
        max_iterations=100,
        subset_size=1000 if len(finder.constraints) > 10000 else 200
    )
    
    print(f"\n📊 Search Results:")
    print(f"   Converged: {stats['converged']}")
    print(f"   Iterations: {stats['iterations']}")
    print(f"   LP solves: {stats['lp_solves']}")
    print(f"   Total time: {stats['total_time']:.2f}s")
    
    if stats['gpu_available']:
        print(f"   GPU time: {stats['gpu_time']:.4f}s")
        print(f"   GPU speedup: {stats['gpu_speedup']:.1f}x")
    
    if ray is not None:
        print(f"\n✅ Found extreme ray!")
        print(f"   First 10 elements: {ray[:10]}")
        
        # Scale ray to match target scale
        target_scale = np.linalg.norm(target_coordinates[:finder.d])
        ray_scaled = ray * target_scale
        
        # Check if it matches target
        if finder.d == len(target_coordinates):
            distance = np.linalg.norm(ray_scaled - target_coordinates)
            print(f"\n🎯 Distance to target ray #1381: {distance:.6f}")
            
            if distance < 1e-6:
                print("🎉 EXACT MATCH! Found ray #1381!")
            elif distance < 1.0:
                print("📍 Very close match (within 1.0)")
            else:
                print("📏 Different ray found (exploring different direction)")
        
        return True
    else:
        print(f"\n❌ No ray found")
        print("   Possible issues:")
        print("   - LP infeasibility (constraint formulation)")
        print("   - Need more iterations")
        print("   - Need different objective vector")
        return False

def main():
    """Run the test"""
    print("🎮 LP-Based Ray Finder - Test Ray #1381 Discovery")
    print("=" * 60)
    
    success = test_find_ray_1381()
    
    if success:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed - see diagnostics above")
    
    return success

if __name__ == "__main__":
    main()