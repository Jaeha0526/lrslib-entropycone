#!/usr/bin/env python3
"""
Enhanced Ray Finder with RANDOM violation selection
Instead of greedily taking the most violated constraints,
randomly sample from ALL violated constraints.
"""

import numpy as np
import time
from scipy.optimize import linprog
import random
import os
import sys
from datetime import datetime, timedelta
import json

def load_s7_constraints(filename):
    """Load S₇ constraints in the correct format"""
    print(f"Loading S₇ constraints from {filename}...")
    print("This may take a few minutes for 8.6M constraints...")
    
    constraints = []
    loaded = 0
    
    with open(filename, 'r') as f:
        in_data = False
        for line in f:
            line = line.strip()
            
            if line == 'begin':
                in_data = True
                continue
            elif line == 'end':
                break
            elif in_data and line and (line[0].isdigit() or line[0] == '-'):
                if 'integer' in line:
                    continue
                
                values = line.split()
                if len(values) == 63:
                    facet = np.array([float(x) for x in values])
                    constraints.append(facet)
                    loaded += 1
                    
                    if loaded % 100000 == 0:
                        print(f"  Loaded {loaded:,} constraints...")
    
    constraints = np.array(constraints)
    print(f"Loaded {len(constraints):,} constraints")
    print(f"Memory usage: {constraints.nbytes / 1024**3:.2f} GB")
    
    return constraints

def load_known_rays(filepath):
    """Load the 4145 known rays from file"""
    known_rays = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        ray = np.fromstring(line.strip(), sep=' ')
                        if len(ray) == 63:  # Valid ray
                            known_rays.append(ray)
                    except:
                        pass
        print(f"Loaded {len(known_rays)} known rays from {filepath}")
    except:
        print(f"Warning: Could not load known rays from {filepath}")
    return known_rays

def find_ray_with_active_set_random(constraints, objective=None, max_iterations=100, 
                            subset_size=1000, verbose=False, 
                            num_violations_to_add=20, selection_method='random'):
    """
    Find extreme ray using active-set method with RANDOM violation selection
    
    selection_method options:
    - 'random': Randomly select from all violations
    - 'mixed': 50% random, 50% most violated
    - 'weighted': Random with probability proportional to violation amount
    - 'greedy': Original greedy (most violated) for comparison
    """
    m, n = constraints.shape
    
    if objective is None:
        objective = np.random.randn(n)
        objective = objective / np.linalg.norm(objective)
    
    # Start with random subset of constraints (active set)
    active_indices = random.sample(range(m), min(subset_size, m))
    
    for iteration in range(max_iterations):
        if verbose and iteration % 10 == 0:
            print(f"  Iteration {iteration}: {len(active_indices)} active constraints")
        
        # Extract active constraints
        active_constraints = constraints[active_indices]
        
        # Set up LP
        A_ub = -active_constraints
        b_ub = np.zeros(len(active_indices))
        
        # Normalization: sum(x) = 1
        A_eq = np.ones((1, n))
        b_eq = np.array([1.0])
        
        # Non-negativity bounds
        bounds = [(0, None) for _ in range(n)]
        
        # Solve LP
        result = linprog(
            -objective,  # Maximize
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method='highs',
            options={'disp': False}
        )
        
        if not result.success:
            if verbose:
                print(f"  LP failed at iteration {iteration}: {result.message}")
            return None, iteration + 1
        
        current_solution = result.x
        
        # Check violations across ALL constraints
        violations = np.dot(constraints, current_solution)
        violated_mask = violations < -1e-8
        violated_indices = np.where(violated_mask)[0]
        
        if len(violated_indices) == 0:
            # No violations - found an extreme ray!
            if verbose:
                print(f"  Converged in {iteration + 1} iterations!")
            return current_solution, iteration + 1
        
        # SELECT VIOLATIONS BASED ON METHOD
        if selection_method == 'random':
            # RANDOM SELECTION: Pick random violated constraints
            num_to_add = min(num_violations_to_add, len(violated_indices))
            selected_violations = np.random.choice(violated_indices, num_to_add, replace=False)
            
        elif selection_method == 'mixed':
            # MIXED: 50% random, 50% most violated
            num_to_add = min(num_violations_to_add, len(violated_indices))
            num_greedy = num_to_add // 2
            num_random = num_to_add - num_greedy
            
            violation_amounts = -violations[violated_indices]
            sorted_indices = violated_indices[np.argsort(violation_amounts)]
            
            greedy_selection = sorted_indices[-num_greedy:] if num_greedy > 0 else []
            remaining = sorted_indices[:-num_greedy] if num_greedy > 0 else sorted_indices
            random_selection = np.random.choice(remaining, min(num_random, len(remaining)), replace=False)
            selected_violations = np.concatenate([greedy_selection, random_selection])
            
        elif selection_method == 'weighted':
            # WEIGHTED RANDOM: Probability proportional to violation amount
            violation_amounts = -violations[violated_indices]
            # Add small epsilon to avoid zero probabilities
            probabilities = violation_amounts + 1e-10
            probabilities = probabilities / probabilities.sum()
            num_to_add = min(num_violations_to_add, len(violated_indices))
            selected_violations = np.random.choice(violated_indices, num_to_add, 
                                                  replace=False, p=probabilities)
            
        else:  # 'greedy' - original method
            violation_amounts = -violations[violated_indices]
            most_violated = violated_indices[np.argsort(violation_amounts)[-num_violations_to_add:]]
            selected_violations = most_violated
        
        # Add selected constraints not already in active set
        new_constraints = [idx for idx in selected_violations if idx not in active_indices]
        active_indices.extend(new_constraints)
        
        if verbose and len(new_constraints) > 0:
            print(f"    Added {len(new_constraints)} violated constraints ({selection_method})")
    
    if verbose:
        print(f"  Reached max iterations ({max_iterations})")
    return None, max_iterations

def check_ray_similarity(ray1, ray2, threshold=0.9999):
    """Check if two rays are similar (essentially the same)"""
    r1_norm = ray1 / np.linalg.norm(ray1)
    r2_norm = ray2 / np.linalg.norm(ray2)
    similarity = abs(np.dot(r1_norm, r2_norm))
    return similarity > threshold, similarity

def main():
    # Configuration - can be changed via command line args
    selection_method = sys.argv[1] if len(sys.argv) > 1 else 'random'
    num_violations = int(sys.argv[2]) if len(sys.argv) > 2 else 30  # Increased from 20
    
    print(f"Using selection method: {selection_method}")
    print(f"Adding {num_violations} violations per iteration")
    
    MAX_RUNTIME = timedelta(hours=9, minutes=30)
    # Create results directory inside lp_ray_finder for future repo separation
    script_dir = os.path.dirname(os.path.abspath(__file__))  # core/ directory
    lp_ray_finder_dir = os.path.dirname(script_dir)  # lp_ray_finder/ directory  
    
    # Add timestamp to prevent directory overwrites
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(lp_ray_finder_dir, "results", f"ray_results_{selection_method}_{num_violations}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Load constraints (relative to repo root)
    repo_root = os.path.dirname(lp_ray_finder_dir)  # Go up one level from lp_ray_finder to repo root
    constraint_file = os.path.join(repo_root, "n6data", "n6_correct_s7_expansion.ine")
    
    load_start = time.time()
    constraints = load_s7_constraints(constraint_file)
    load_time = time.time() - load_start
    
    m, n = constraints.shape
    print(f"Loaded {m:,} constraints in {n} dimensions")
    print(f"Load time: {load_time:.1f}s")
    
    # Load known rays (relative to repo root)
    known_rays_file = os.path.join(repo_root, "n6data", "rays.txt")
    known_rays = load_known_rays(known_rays_file)
    
    # Initialize tracking
    attempt_log = []
    session_rays = []
    unique_new_rays = []
    ray_discovery_count = {}
    
    # Output files
    log_file = os.path.join(output_dir, "attempt_log.jsonl")
    rays_file = os.path.join(output_dir, "discovered_rays.txt")
    summary_file = os.path.join(output_dir, "summary.txt")
    stats_file = os.path.join(output_dir, "statistics.json")
    
    # Initialize files
    with open(rays_file, 'w') as f:
        f.write(f"# Ray Discovery with {selection_method} selection\n")
        f.write(f"# Adding {num_violations} violations per iteration\n")
        f.write(f"# Session: {datetime.now()}\n")
        f.write(f"# Constraints: {m:,} in {n} dimensions\n")
        f.write(f"# Known rays: {len(known_rays)}\n")
        f.write("#" + "="*80 + "\n\n")
    
    start_time = datetime.now()
    attempt = 0
    
    print(f"\nStarting ray discovery with {selection_method} violation selection...")
    print("="*60)
    
    # Main discovery loop
    while datetime.now() - start_time < MAX_RUNTIME:
        attempt += 1
        elapsed = datetime.now() - start_time
        
        if attempt % 10 == 1:
            print(f"\nAttempt {attempt} | Elapsed: {elapsed} | Found: {len(unique_new_rays)} new rays")
        
        # Random objective
        objective = np.random.randn(n)
        objective = objective / np.linalg.norm(objective)
        
        # Find ray using active-set method with selected violation strategy
        ray, iterations = find_ray_with_active_set_random(
            constraints,
            objective=objective,
            max_iterations=100,
            subset_size=1000,
            verbose=(attempt % 50 == 1),
            num_violations_to_add=num_violations,
            selection_method=selection_method
        )
        
        # Initialize attempt record
        attempt_record = {
            "attempt": attempt,
            "timestamp": str(datetime.now()),
            "elapsed": str(elapsed),
            "iterations": iterations,
            "success": ray is not None,
            "duplicate_in_session": False,
            "duplicate_in_known": False,
            "ray_id": None,
            "similarity_score": None,
            "method": selection_method
        }
        
        if ray is not None:
            # Check against session rays
            session_duplicate = False
            for i, existing_ray in enumerate(session_rays):
                is_dup, similarity = check_ray_similarity(ray, existing_ray)
                if is_dup:
                    session_duplicate = True
                    attempt_record["duplicate_in_session"] = True
                    attempt_record["ray_id"] = f"session_{i+1}"
                    attempt_record["similarity_score"] = float(similarity)
                    
                    ray_key = f"session_{i+1}"
                    ray_discovery_count[ray_key] = ray_discovery_count.get(ray_key, 1) + 1
                    break
            
            # Check against known rays if not session duplicate
            if not session_duplicate:
                known_duplicate = False
                for i, known_ray in enumerate(known_rays):
                    is_dup, similarity = check_ray_similarity(ray, known_ray)
                    if is_dup:
                        known_duplicate = True
                        attempt_record["duplicate_in_known"] = True
                        attempt_record["ray_id"] = f"known_{i+1}"
                        attempt_record["similarity_score"] = float(similarity)
                        
                        ray_key = f"known_{i+1}"
                        ray_discovery_count[ray_key] = ray_discovery_count.get(ray_key, 0) + 1
                        break
                
                # If truly new ray
                if not known_duplicate:
                    session_rays.append(ray)
                    unique_new_rays.append(ray)
                    attempt_record["ray_id"] = f"new_{len(unique_new_rays)}"
                    
                    # Save ray
                    ray_str = " ".join(str(v) for v in ray)
                    with open(rays_file, 'a') as f:
                        f.write(f"{ray_str}  # Ray {len(unique_new_rays)} (attempt {attempt})\n")
                    
                    print(f"✓ Found NEW ray #{len(unique_new_rays)} at attempt {attempt}")
        else:
            attempt_record["reached_max_iterations"] = (iterations == 100)
        
        # Log attempt
        with open(log_file, 'a') as f:
            f.write(json.dumps(attempt_record) + "\n")
        
        # Update summary every 50 attempts
        if attempt % 50 == 0:
            success_count = sum(1 for _ in filter(lambda x: x, [r["success"] for r in attempt_log[-50:]]))
            max_iter_count = sum(1 for _ in filter(lambda x: x.get("reached_max_iterations", False), attempt_log[-50:]))
            
            with open(summary_file, 'w') as f:
                f.write(f"Ray Discovery Summary - {selection_method} method\n")
                f.write(f"="*60 + "\n")
                f.write(f"Runtime: {elapsed}\n")
                f.write(f"Attempts: {attempt}\n")
                f.write(f"Unique new rays: {len(unique_new_rays)}\n")
                f.write(f"Session rays (including duplicates): {len(session_rays)}\n")
                f.write(f"\nLast 50 attempts:\n")
                f.write(f"  Success rate: {success_count}/50 = {2*success_count}%\n")
                f.write(f"  Hit max iterations: {max_iter_count}/50\n")
                f.write(f"\nMost rediscovered rays:\n")
                sorted_rays = sorted(ray_discovery_count.items(), key=lambda x: x[1], reverse=True)[:10]
                for ray_id, count in sorted_rays:
                    f.write(f"  {ray_id}: found {count} times\n")
        
        attempt_log.append(attempt_record)
    
    # Final statistics
    total_runtime = datetime.now() - start_time
    
    stats = {
        "method": selection_method,
        "violations_per_iteration": num_violations,
        "total_attempts": attempt,
        "runtime": str(total_runtime),
        "unique_new_rays": len(unique_new_rays),
        "success_attempts": sum(1 for r in attempt_log if r["success"]),
        "max_iteration_failures": sum(1 for r in attempt_log if r.get("reached_max_iterations", False)),
        "session_duplicates": sum(1 for r in attempt_log if r["duplicate_in_session"]),
        "known_duplicates": sum(1 for r in attempt_log if r["duplicate_in_known"]),
        "ray_discovery_counts": ray_discovery_count,
        "success_rate": f"{100*len(unique_new_rays)/attempt:.1f}%"
    }
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print("\n" + "="*60)
    print(f"SESSION COMPLETE - {selection_method} method")
    print(f"Runtime: {total_runtime}")
    print(f"Attempts: {attempt}")
    print(f"Unique NEW rays found: {len(unique_new_rays)}")
    print(f"Overall success rate: {stats['success_rate']}")

if __name__ == "__main__":
    main()