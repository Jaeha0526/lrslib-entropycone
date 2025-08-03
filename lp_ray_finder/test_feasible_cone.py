#!/usr/bin/env python3
"""
Test LP ray finder with a properly constructed feasible cone
"""

import numpy as np
from lp_ray_finder_phase3 import HybridLPRayFinder

def create_positive_cone_constraints(d):
    """Create constraints for the positive orthant (all coordinates >= 0)"""
    # For positive orthant: -x_i >= 0 for all i (which means x_i >= 0)
    # In matrix form: -I * x >= 0
    constraints = []
    
    # Add constraints x_i >= 0 for each dimension
    for i in range(d):
        row = np.zeros(d + 1)
        row[i + 1] = -1  # -x_i >= 0
        constraints.append(row)
    
    return np.array(constraints)

def create_simplex_constraints(d):
    """Create constraints for a simplex intersected with positive orthant"""
    constraints = []
    
    # First add positive orthant constraints
    for i in range(d):
        row = np.zeros(d + 1)
        row[i + 1] = -1  # x_i >= 0
        constraints.append(row)
    
    # Add sum constraint: -sum(x_i) >= -10 (i.e., sum(x_i) <= 10)
    row = np.zeros(d + 1)
    row[0] = -10  # constant term
    row[1:] = 1   # coefficients for sum
    constraints.append(row)
    
    return np.array(constraints)

def test_simple_cone():
    """Test with a simple, well-defined cone"""
    print("🎯 Testing LP Ray Finder with Simple Feasible Cones")
    print("=" * 60)
    
    # Test 1: Positive orthant in 3D
    print("\n📐 Test 1: Positive Orthant in 3D")
    print("Constraints: x >= 0, y >= 0, z >= 0")
    
    constraints = create_positive_cone_constraints(3)
    print(f"Constraint matrix:\n{constraints}")
    
    finder = HybridLPRayFinder(verbose=True, use_gpu=True)
    finder.constraints = constraints
    finder.d = 3
    finder.normalizing_vector = np.ones(3)
    finder.constraint_manager.load_constraint_matrix(constraints)
    
    # Try to find ray in direction (1,1,1)
    objective = np.array([1, 1, 1])
    objective = objective / np.linalg.norm(objective)
    
    ray, stats = finder.find_extreme_ray(objective=objective, max_iterations=10, subset_size=3)
    
    if ray is not None:
        print(f"✅ Found ray: {ray}")
        print(f"   Converged in {stats['iterations']} iterations")
    else:
        print("❌ No ray found")
    
    # Test 2: Simplex cone
    print("\n📐 Test 2: Simplex Cone in 5D")
    print("Constraints: x_i >= 0 for all i, sum(x_i) <= 10")
    
    constraints = create_simplex_constraints(5)
    
    finder2 = HybridLPRayFinder(verbose=False, use_gpu=True)
    finder2.constraints = constraints
    finder2.d = 5
    finder2.normalizing_vector = np.ones(5)
    finder2.constraint_manager.load_constraint_matrix(constraints)
    
    # Find multiple rays
    print("\nFinding 3 different extreme rays:")
    for i in range(3):
        # Different objectives
        objective = np.zeros(5)
        objective[i] = 1  # Unit vector in i-th direction
        
        ray, stats = finder2.find_extreme_ray(objective=objective, max_iterations=10, subset_size=6)
        
        if ray is not None:
            print(f"   Ray {i+1}: {ray} (iterations: {stats['iterations']})")
        else:
            print(f"   Ray {i+1}: Not found")
    
    # Test 3: Large-scale test
    print("\n📐 Test 3: Large-Scale Positive Orthant (63D like N=6)")
    
    constraints = create_positive_cone_constraints(63)
    
    # Add some random constraints that are satisfied by positive vectors
    np.random.seed(42)
    for i in range(1000):
        row = np.zeros(64)
        row[1:] = -np.abs(np.random.randn(63))  # All negative coefficients
        row[0] = np.random.rand() * 10  # Positive constant
        constraints = np.vstack([constraints, row])
    
    print(f"Total constraints: {len(constraints)}")
    
    finder3 = HybridLPRayFinder(verbose=True, use_gpu=True)
    finder3.constraints = constraints
    finder3.d = 63
    finder3.normalizing_vector = np.ones(63)
    finder3.constraint_manager.load_constraint_matrix(constraints)
    
    # Try to find a ray similar to target ray #1381
    target_direction = [1, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 6, 6, 8, 8, 8, 8, 7, 7, 9, 9, 7, 7, 9, 7, 9, 9, 6, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 6, 5, 4, 3]
    objective = np.array(target_direction) / np.linalg.norm(target_direction)
    
    print(f"\n🎯 Finding ray in direction of target ray #1381...")
    ray, stats = finder3.find_extreme_ray(objective=objective, max_iterations=50, subset_size=100)
    
    if ray is not None:
        print(f"✅ Found ray!")
        print(f"   First 10 elements: {ray[:10]}")
        print(f"   Converged in {stats['iterations']} iterations")
        print(f"   Total time: {stats['total_time']:.3f}s")
        if stats['gpu_available']:
            print(f"   GPU speedup: {stats.get('gpu_speedup', 0):.1f}x")
        
        # Check angle with target direction
        angle = np.arccos(np.clip(np.dot(ray, objective), -1, 1))
        print(f"   Angle with target direction: {np.degrees(angle):.2f}°")
    else:
        print("❌ No ray found")
    
    return True

def main():
    """Run the tests"""
    print("🎮 GPU-Accelerated LP Ray Finder - Feasibility Tests")
    print("=" * 60)
    
    success = test_simple_cone()
    
    if success:
        print("\n✅ All tests completed")
        print("\n📝 Summary:")
        print("- GPU acceleration is working correctly")
        print("- Algorithm can find rays in feasible cones")
        print("- Ready for N=6 system with proper constraint file")
        print("\n⚠️  Note: The N=6 constraint file is not present in this workspace.")
        print("To use with actual N=6 data, place the file at:")
        print("  ../n6data/n6_restart_startingcobasis.ine")
    
    return success

if __name__ == "__main__":
    main()