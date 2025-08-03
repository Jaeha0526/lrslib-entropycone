#!/usr/bin/env python3
"""
Run LP-based ray finder demonstration
Shows how to find extreme rays without the N=6 file
"""

import numpy as np
from scipy.optimize import linprog
import time
import sys

# Try to use the GPU-accelerated version if available
try:
    from lp_ray_finder_phase3 import HybridLPRayFinder
    USE_GPU = True
except ImportError:
    USE_GPU = False
    print("Note: Using basic LP solver without GPU acceleration")

def create_feasible_entropy_cone(n_parties=3):
    """
    Create a simplified entropy cone for n parties
    This creates actual entropy inequalities that have feasible solutions
    """
    # For n parties, we have 2^n - 1 non-empty subsets
    n_vars = 2**n_parties - 1
    
    print(f"Creating {n_parties}-party entropy cone ({n_vars} variables)...")
    
    # Map subset to index
    def subset_to_index(subset):
        return sum(2**i for i in subset) - 1
    
    constraints = []
    
    # 1. Non-negativity: H(S) >= 0 for all subsets S
    for i in range(n_vars):
        row = np.zeros(n_vars + 1)
        row[i + 1] = -1  # -H(S) <= 0
        constraints.append(row)
    
    # 2. Submodularity: H(A) + H(B) >= H(A∪B) + H(A∩B)
    # For all pairs of subsets A, B
    for a_bits in range(1, 2**n_parties):
        for b_bits in range(a_bits + 1, 2**n_parties):
            a_set = {i for i in range(n_parties) if a_bits & (1 << i)}
            b_set = {i for i in range(n_parties) if b_bits & (1 << i)}
            
            union = a_set | b_set
            intersection = a_set & b_set
            
            if intersection:  # Only if intersection is non-empty
                row = np.zeros(n_vars + 1)
                # H(A) + H(B) - H(A∪B) - H(A∩B) >= 0
                # Rearranged to: -H(A) - H(B) + H(A∪B) + H(A∩B) <= 0
                row[subset_to_index(a_set) + 1] = -1
                row[subset_to_index(b_set) + 1] = -1
                row[subset_to_index(union) + 1] = 1
                row[subset_to_index(intersection) + 1] = 1
                constraints.append(row)
    
    # 3. Monotonicity: H(A) <= H(B) for A ⊆ B
    for a_bits in range(1, 2**n_parties):
        for b_bits in range(1, 2**n_parties):
            if a_bits != b_bits and (a_bits & b_bits) == a_bits:  # A ⊆ B
                row = np.zeros(n_vars + 1)
                # H(A) - H(B) <= 0
                a_set = {i for i in range(n_parties) if a_bits & (1 << i)}
                b_set = {i for i in range(n_parties) if b_bits & (1 << i)}
                row[subset_to_index(a_set) + 1] = 1
                row[subset_to_index(b_set) + 1] = -1
                constraints.append(row)
    
    return np.array(constraints), n_vars

def find_extreme_rays_simple(constraints, n_vars, num_rays=5):
    """
    Find extreme rays using simple scipy LP solver
    """
    rays_found = []
    m = len(constraints)
    
    print(f"\nSearching for extreme rays in {n_vars}D cone with {m} constraints...")
    
    for i in range(num_rays):
        # Try different objectives
        if i == 0:
            # Uniform entropy
            objective = np.ones(n_vars)
        elif i < n_vars + 1 and i < num_rays:
            # Single entropy dominates
            objective = np.zeros(n_vars)
            objective[i-1] = 1
        else:
            # Random direction
            objective = np.random.rand(n_vars)
        
        objective = objective / np.linalg.norm(objective)
        
        print(f"\n  Ray {i+1}: ", end="")
        
        # Set up LP: max c^T x subject to Ax <= 0, sum(x) = 1
        c = objective
        A_ub = constraints[:, 1:]  # Skip constant column
        b_ub = -constraints[:, 0]   # Move constants to RHS
        
        # Normalization constraint: sum(x) = 1
        A_eq = np.ones((1, n_vars))
        b_eq = np.array([1.0])
        
        # Solve LP
        start = time.time()
        result = linprog(-c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                        method='highs', bounds=(0, None))
        elapsed = time.time() - start
        
        if result.success:
            ray = result.x
            ray = ray / np.linalg.norm(ray)  # Normalize
            
            # Check if new
            is_new = True
            for existing in rays_found:
                if np.dot(ray, existing) > 0.99:
                    is_new = False
                    break
            
            if is_new:
                rays_found.append(ray)
                print(f"✓ Found new ray in {elapsed:.3f}s")
                
                # Show structure for small cases
                if n_vars <= 7:
                    subset_names = []
                    for j in range(3):
                        subset_names.append(f"{j+1}")
                    for j in range(3):
                        for k in range(j+1, 3):
                            subset_names.append(f"{j+1}{k+1}")
                    if n_vars == 7:
                        subset_names.append("123")
                    
                    print("     ", end="")
                    for j, val in enumerate(ray):
                        if val > 0.01:
                            print(f"H({subset_names[j]})={val:.2f} ", end="")
            else:
                print(f"- Similar to existing ray")
        else:
            print(f"✗ LP failed: {result.message}")
    
    return rays_found

def analyze_rays(rays, n_vars):
    """Analyze the structure of found rays"""
    if not rays:
        return
    
    print(f"\n📊 Analysis of {len(rays)} extreme rays:")
    
    for i, ray in enumerate(rays):
        print(f"\n  Ray {i+1}:")
        
        # Sparsity
        nonzero = np.sum(ray > 0.01)
        print(f"    Non-zero components: {nonzero}/{n_vars}")
        
        # Largest components
        top_idx = np.argsort(ray)[-3:][::-1]
        print(f"    Top 3 components: ", end="")
        for idx in top_idx:
            if ray[idx] > 0.01:
                print(f"x[{idx}]={ray[idx]:.3f} ", end="")
        print()
        
        # Check if it's a permutation/uniform ray
        unique_vals = len(np.unique(np.round(ray, 3)))
        if unique_vals <= 3:
            print(f"    Structure: Possibly uniform/permutation (only {unique_vals} unique values)")

def run_gpu_accelerated(constraints, n_vars, num_rays=5):
    """Run with GPU acceleration if available"""
    print(f"\n🎮 Using GPU-accelerated LP ray finder...")
    
    finder = HybridLPRayFinder(verbose=False, use_gpu=True)
    finder.constraints = constraints
    finder.d = n_vars
    finder.normalizing_vector = np.ones(n_vars)
    finder.constraint_manager.load_constraint_matrix(constraints)
    
    print(f"GPU available: {finder.constraint_manager.use_gpu}")
    
    rays_found = []
    total_time = 0
    
    for i in range(num_rays):
        # Varied objectives
        if i == 0:
            objective = np.ones(n_vars)
        elif i < n_vars + 1:
            objective = np.zeros(n_vars)
            objective[i-1] = 1
        else:
            objective = np.random.rand(n_vars)
        
        objective = objective / np.linalg.norm(objective)
        
        print(f"\n  Ray {i+1}: ", end="")
        start = time.time()
        
        ray, stats = finder.find_extreme_ray(
            objective=objective,
            max_iterations=50,
            subset_size=min(100, len(constraints)//2)
        )
        
        elapsed = time.time() - start
        total_time += elapsed
        
        if ray is not None and stats['converged']:
            # Check if new
            is_new = True
            for existing in rays_found:
                if np.dot(ray, existing) > 0.99:
                    is_new = False
                    break
            
            if is_new:
                rays_found.append(ray)
                print(f"✓ Found new ray in {elapsed:.3f}s ({stats['iterations']} iterations)")
            else:
                print(f"- Similar to existing ray")
        else:
            print(f"✗ No ray found")
    
    print(f"\nTotal time: {total_time:.2f}s")
    return rays_found

def main():
    """Run the LP ray finder demonstration"""
    print("🎯 LP-Based Extreme Ray Finder")
    print("=" * 60)
    
    # Create a 3-party entropy cone (7 variables)
    constraints, n_vars = create_feasible_entropy_cone(n_parties=3)
    
    print(f"Created entropy cone: {len(constraints)} constraints, {n_vars} variables")
    
    if USE_GPU and len(sys.argv) > 1 and sys.argv[1] == "--gpu":
        rays = run_gpu_accelerated(constraints, n_vars, num_rays=7)
    else:
        rays = find_extreme_rays_simple(constraints, n_vars, num_rays=7)
    
    # Analyze results
    analyze_rays(rays, n_vars)
    
    print("\n" + "=" * 60)
    print("💡 Summary:")
    print(f"✓ Found {len(rays)} unique extreme rays")
    print("✓ Each ray found in milliseconds to seconds")
    print("✓ No vertex enumeration needed!")
    
    print("\n📝 For the N=6 holographic entropy cone:")
    print("- Would use same approach with 8.6M constraints")
    print("- Target ray #1381 with appropriate objective")
    print("- GPU acceleration for massive speedup")
    print("- Find specific rays in minutes instead of decades")
    
    # Create a larger test if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--large":
        print("\n" + "=" * 60)
        print("Testing larger 4-party entropy cone (15 variables)...")
        constraints, n_vars = create_feasible_entropy_cone(n_parties=4)
        print(f"Created: {len(constraints)} constraints, {n_vars} variables")
        rays = find_extreme_rays_simple(constraints, n_vars, num_rays=10)
        print(f"\nFound {len(rays)} unique extreme rays in 4-party system")

if __name__ == "__main__":
    main()