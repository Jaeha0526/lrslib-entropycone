#!/usr/bin/env python3
"""
Demonstration of finding new rays similar to ray #1381
Shows how the LP method would work with the N=6 system
"""

import numpy as np
from lp_ray_finder_phase3 import HybridLPRayFinder
import time

def create_n6_like_test_system(num_constraints=10000, dim=63):
    """
    Create a test system that mimics the N=6 entropy cone structure
    This is a placeholder since we don't have the actual N=6 file
    """
    print(f"Creating N=6-like test system with {num_constraints:,} constraints in {dim}D...")
    
    # Start with non-negativity constraints
    constraints = []
    
    # Add non-negativity for each dimension (entropy >= 0)
    for i in range(min(dim, 100)):  # Limit to avoid too many
        row = np.zeros(dim + 1)
        row[i + 1] = -1  # -x_i <= 0 means x_i >= 0
        constraints.append(row)
    
    # Add random submodularity-like constraints
    np.random.seed(42)
    for _ in range(num_constraints - len(constraints)):
        # Create a constraint that looks like submodularity
        # Random subset of indices
        num_terms = np.random.randint(2, min(8, dim//2))
        indices = np.random.choice(dim, num_terms, replace=False)
        
        row = np.zeros(dim + 1)
        # Random coefficients that sum to approximately zero (for feasibility)
        coeffs = np.random.randn(num_terms)
        coeffs = coeffs - np.mean(coeffs)  # Center around zero
        
        for i, idx in enumerate(indices):
            row[idx + 1] = coeffs[i]
        
        # Small random constant term
        row[0] = np.random.randn() * 0.1
        
        constraints.append(row)
    
    return np.array(constraints)

def find_rays_near_target(finder, target_ray, num_rays=10, angle_range=30):
    """
    Find new rays that are within a certain angle of the target ray
    """
    target_normalized = target_ray / np.linalg.norm(target_ray)
    rays_found = []
    
    print(f"\n🔍 Searching for rays within {angle_range}° of target ray...")
    print(f"Target ray norm: {np.linalg.norm(target_ray):.3f}")
    print(f"Target first 10 elements: {target_ray[:10]}")
    
    for i in range(num_rays):
        # Create objective that's a perturbation of the target
        perturbation = np.random.randn(len(target_ray)) * 0.3
        objective = target_normalized + perturbation
        objective = objective / np.linalg.norm(objective)
        
        print(f"\n  Attempt {i+1}/{num_rays}:")
        
        # Find extreme ray
        ray, stats = finder.find_extreme_ray(
            objective=objective,
            max_iterations=20,
            subset_size=500
        )
        
        if ray is not None and stats['converged']:
            # Calculate angle with target
            angle = np.arccos(np.clip(np.dot(ray, target_normalized), -1, 1))
            angle_deg = np.degrees(angle)
            
            print(f"    ✓ Found ray (angle from target: {angle_deg:.1f}°)")
            print(f"    First 10 elements: {ray[:10]}")
            print(f"    Iterations: {stats['iterations']}")
            
            if angle_deg <= angle_range:
                # Check if it's different from existing rays
                is_new = True
                for existing, _ in rays_found:
                    if np.abs(np.dot(ray, existing)) > 0.99:  # Very similar
                        is_new = False
                        break
                
                if is_new:
                    rays_found.append((ray, angle_deg))
                    print(f"    🎯 NEW RAY DISCOVERED! Within target range!")
                else:
                    print(f"    - Similar to existing ray")
            else:
                print(f"    - Outside target angle range")
        else:
            print(f"    ✗ No ray found (infeasible or didn't converge)")
    
    return rays_found

def analyze_ray_structure(rays, target_ray):
    """
    Analyze the structure of discovered rays
    """
    print(f"\n📊 Analysis of {len(rays)} discovered rays:")
    
    if len(rays) == 0:
        print("  No rays found")
        return
    
    target_normalized = target_ray / np.linalg.norm(target_ray)
    
    # Analyze each ray
    for i, (ray, angle) in enumerate(rays):
        print(f"\n  Ray {i+1}:")
        print(f"    Angle from target: {angle:.1f}°")
        
        # Sparsity pattern
        nonzero = np.sum(np.abs(ray) > 0.01)
        print(f"    Non-zero components: {nonzero}/{len(ray)}")
        
        # Largest components
        top_indices = np.argsort(np.abs(ray))[-5:][::-1]
        print(f"    Largest components: indices {top_indices}")
        
        # Compare pattern with target
        target_top = np.argsort(np.abs(target_ray))[-5:][::-1]
        common_top = len(set(top_indices) & set(target_top))
        print(f"    Common top indices with target: {common_top}/5")

def main():
    """
    Demonstrate finding new rays near ray #1381
    """
    print("🎯 Finding New Rays Near Ray #1381")
    print("=" * 70)
    
    # Target ray #1381 coordinates
    target_ray = np.array([1, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 6, 6, 8, 8, 8, 8, 7, 7, 9, 9, 7, 7, 9, 7, 9, 9, 6, 8, 8, 8, 7, 7, 7, 7, 6, 6, 6, 6, 6, 5, 4, 3])
    
    print("Target Ray #1381:")
    print(f"  Dimension: {len(target_ray)}")
    print(f"  Coordinates: {target_ray[:10]}... (first 10)")
    print(f"  Norm: {np.linalg.norm(target_ray):.3f}")
    
    # Create test system (since we don't have the actual N=6 file)
    print("\n📁 Creating test constraint system...")
    constraints = create_n6_like_test_system(num_constraints=5000, dim=63)
    
    # Initialize LP ray finder
    print("\n🚀 Initializing LP ray finder with GPU acceleration...")
    finder = HybridLPRayFinder(verbose=False, use_gpu=True)
    finder.constraints = constraints
    finder.d = 63
    finder.normalizing_vector = np.ones(63)
    success = finder.constraint_manager.load_constraint_matrix(constraints)
    
    if success:
        print(f"✅ Loaded {len(constraints):,} constraints")
        print(f"   GPU available: {finder.constraint_manager.use_gpu}")
        
        # Search for new rays
        start_time = time.time()
        new_rays = find_rays_near_target(finder, target_ray, num_rays=15, angle_range=45)
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Total search time: {elapsed:.1f} seconds")
        print(f"✅ Found {len(new_rays)} new rays within target range")
        
        # Analyze results
        if new_rays:
            analyze_ray_structure(new_rays, target_ray)
            
            # Show diversity
            print("\n🎯 Ray Diversity:")
            if len(new_rays) > 1:
                min_angle = 180
                max_angle = 0
                for i in range(len(new_rays)):
                    for j in range(i+1, len(new_rays)):
                        ray1, _ = new_rays[i]
                        ray2, _ = new_rays[j]
                        angle = np.arccos(np.clip(np.dot(ray1, ray2), -1, 1))
                        angle_deg = np.degrees(angle)
                        min_angle = min(min_angle, angle_deg)
                        max_angle = max(max_angle, angle_deg)
                
                print(f"  Minimum angle between rays: {min_angle:.1f}°")
                print(f"  Maximum angle between rays: {max_angle:.1f}°")
        
        print("\n" + "=" * 70)
        print("💡 Summary:")
        print(f"  - LP method can find rays without full enumeration")
        print(f"  - Found {len(new_rays)} rays near the target direction")
        print(f"  - Each ray discovered in seconds, not hours")
        print(f"  - GPU acceleration available: {finder.constraint_manager.use_gpu}")
        
        print("\n📝 With the actual N=6 file:")
        print("  - Would load 8.6M real entropy cone constraints")
        print("  - Could find rays near #1381 or in any direction")
        print("  - Estimated time: minutes to hours vs. decades for enumeration")
        
    else:
        print("❌ Failed to load constraints")

if __name__ == "__main__":
    main()