#!/usr/bin/env python3
"""
Monitor N=6 file transfer and automatically start ray finding when complete
"""

import os
import time
import numpy as np
from datetime import datetime
from lp_ray_finder_phase3 import HybridLPRayFinder

def monitor_file_transfer(filepath, check_interval=10, stable_duration=30, max_wait=1800):
    """
    Monitor file size until it stops growing
    
    Args:
        filepath: Path to file being transferred
        check_interval: Seconds between size checks
        stable_duration: Seconds file must remain same size to consider complete
        max_wait: Maximum seconds to wait (default 30 minutes)
    
    Returns:
        True if file is stable, False if timeout
    """
    print(f"📁 Monitoring file transfer: {filepath}")
    print(f"⏱️  Will check every {check_interval}s until stable for {stable_duration}s")
    print(f"⏰ Maximum wait time: {max_wait/60:.1f} minutes\n")
    
    start_time = time.time()
    last_size = -1
    stable_start = None
    
    while True:
        try:
            current_size = os.path.getsize(filepath)
            current_mb = current_size / (1024 * 1024)
            elapsed = time.time() - start_time
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if current_size != last_size:
                # Size changed, reset stability timer
                print(f"[{timestamp}] Size: {current_mb:.1f} MB (growing...)")
                last_size = current_size
                stable_start = time.time()
            else:
                # Size unchanged
                stable_time = time.time() - stable_start
                print(f"[{timestamp}] Size: {current_mb:.1f} MB (stable for {stable_time:.0f}s)")
                
                if stable_time >= stable_duration:
                    print(f"\n✅ File transfer complete! Final size: {current_mb:.1f} MB")
                    return True
            
            # Check timeout
            if elapsed > max_wait:
                print(f"\n⏰ Timeout reached after {elapsed/60:.1f} minutes")
                return False
            
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"❌ Error monitoring file: {e}")
            return False

def find_rays_from_n6():
    """Find extreme rays using the N=6 holographic entropy cone"""
    print("\n" + "="*70)
    print("🎯 Starting LP-Based Ray Discovery on N=6 Holographic Entropy Cone")
    print("="*70)
    
    # Target ray #1381
    target_ray_1381 = np.array([
        1, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
        7, 7, 7, 7, 7, 7, 6, 6, 8, 8, 8, 8, 7, 7, 9, 9, 7, 7, 9, 7, 9, 9, 6, 8, 8,
        8, 7, 7, 7, 7, 6, 6, 6, 6, 6, 5, 4, 3
    ])
    
    print("Target Ray #1381:")
    print(f"  Coordinates: {target_ray_1381[:10]}... (first 10 of 63)")
    print(f"  Norm: {np.linalg.norm(target_ray_1381):.3f}")
    
    # Initialize LP ray finder
    print("\n📁 Loading N=6 constraint file with GPU acceleration...")
    
    try:
        finder = HybridLPRayFinder(
            constraint_file="/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine",
            verbose=True,
            use_gpu=True,
            chunk_size=500000  # Adjust based on GPU memory
        )
        
        if finder.constraints is None:
            print("❌ Failed to load constraints!")
            return
        
        print(f"\n✅ Successfully loaded {len(finder.constraints):,} constraints")
        print(f"   Dimensions: {finder.d}")
        print(f"   GPU available: {finder.constraint_manager.use_gpu}")
        
        # Find rays with different strategies
        rays_found = []
        
        # Strategy 1: Find ray in direction of target ray #1381
        print("\n🔍 Strategy 1: Searching in direction of ray #1381...")
        objective = target_ray_1381 / np.linalg.norm(target_ray_1381)
        
        start_time = time.time()
        ray, stats = finder.find_extreme_ray(
            objective=objective,
            max_iterations=100,
            subset_size=1500
        )
        elapsed = time.time() - start_time
        
        if ray is not None and stats['converged']:
            rays_found.append(ray)
            print(f"✅ Found ray in {elapsed:.1f}s ({stats['iterations']} iterations)")
            print(f"   First 10 components: {ray[:10]}")
            
            # Check similarity to target
            similarity = np.dot(ray, objective)
            print(f"   Similarity to target direction: {similarity:.4f}")
        else:
            print(f"❌ No ray found in target direction")
        
        # Strategy 2: Find rays with random objectives
        print("\n🔍 Strategy 2: Searching with random objectives...")
        num_random = 5
        
        for i in range(num_random):
            print(f"\n  Attempt {i+1}/{num_random}:")
            
            # Random objective
            objective = np.random.randn(finder.d)
            objective = objective / np.linalg.norm(objective)
            
            start_time = time.time()
            ray, stats = finder.find_extreme_ray(
                objective=objective,
                max_iterations=50,
                subset_size=1000
            )
            elapsed = time.time() - start_time
            
            if ray is not None and stats['converged']:
                # Check if truly new
                is_new = True
                for existing in rays_found:
                    if np.abs(np.dot(ray, existing)) > 0.99:
                        is_new = False
                        break
                
                if is_new:
                    rays_found.append(ray)
                    print(f"  ✅ New ray found in {elapsed:.1f}s!")
                    print(f"     First 10 components: {ray[:10]}")
                else:
                    print(f"  - Similar to existing ray")
            else:
                print(f"  ❌ No ray found")
        
        # Save results
        print(f"\n📊 Summary:")
        print(f"  Total unique rays found: {len(rays_found)}")
        
        if rays_found:
            # Save rays
            rays_array = np.array(rays_found)
            output_file = "n6_discovered_rays.npy"
            np.save(output_file, rays_array)
            print(f"  Saved rays to: {output_file}")
            
            # Also save in text format
            with open("n6_discovered_rays.txt", "w") as f:
                f.write(f"# Discovered {len(rays_found)} extreme rays from N=6 holographic entropy cone\n")
                f.write(f"# Each row is a 63-dimensional ray\n")
                for i, ray in enumerate(rays_found):
                    f.write(f"# Ray {i+1}\n")
                    f.write(" ".join(f"{x:.10f}" for x in ray) + "\n")
            
            print(f"  Saved rays (text) to: n6_discovered_rays.txt")
            
            # Analyze ray structure
            print("\n📈 Ray Analysis:")
            for i, ray in enumerate(rays_found[:3]):  # First 3 rays
                nonzero = np.sum(np.abs(ray) > 0.01)
                max_comp = np.max(np.abs(ray))
                print(f"  Ray {i+1}: {nonzero} non-zero components, max = {max_comp:.3f}")
        
        print("\n✅ Ray discovery complete!")
        
    except Exception as e:
        print(f"\n❌ Error during ray finding: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main monitoring and execution function"""
    n6_file = "/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine"
    
    # Check if file exists
    if not os.path.exists(n6_file):
        print(f"❌ File not found: {n6_file}")
        return
    
    # Monitor file transfer
    print("🔄 N=6 File Transfer Monitor")
    print("="*50)
    
    transfer_complete = monitor_file_transfer(
        n6_file,
        check_interval=10,      # Check every 10 seconds
        stable_duration=30,     # Must be stable for 30 seconds
        max_wait=1800          # Max wait 30 minutes
    )
    
    if transfer_complete:
        # Wait a bit more to ensure file is fully written
        print("\n⏳ Waiting 10 more seconds to ensure file is fully written...")
        time.sleep(10)
        
        # Start ray finding
        find_rays_from_n6()
    else:
        print("\n❌ File transfer monitoring failed or timed out")
        print("   You may need to run ray finding manually once transfer is complete")

if __name__ == "__main__":
    main()