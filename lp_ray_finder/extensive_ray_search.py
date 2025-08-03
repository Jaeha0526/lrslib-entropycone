#!/usr/bin/env python3
"""
Extensive search for new rays with full S₇ constraints
"""

import numpy as np
import time
from phase3_no_limit import FullConstraintRayFinder

print("🚀 Extensive Ray Search with FULL S₇ Constraints")
print("="*60)

# Load existing rays
existing_rays = np.loadtxt('/workspace/lrslib-entropycone/n6data/rays.txt')
print(f"Loaded {len(existing_rays)} existing rays")

# Create finder
finder = FullConstraintRayFinder(verbose=False)  # Less verbose for many attempts

# Load ALL S₇ constraints
print("\n📁 Loading 8.6M S₇ constraints...")
s7_file = '/workspace/lrslib-entropycone/n6data/n6_correct_s7_expansion.ine'
start_time = time.time()
num_constraints = finder.load_all_s7_constraints(s7_file)
print(f"✅ Loaded {num_constraints:,} constraints in {time.time()-start_time:.1f}s")

# Prepare for search
print("\n🔍 Starting extensive search...")
print("   Will try 1000 random objectives")
print("   Each with different random initial constraint subsets")

# Open file to save new rays
new_rays_file = open('new_rays_extensive_search.txt', 'w')
new_rays_count = 0
total_attempts = 1000
found_existing = 0

# Normalize existing rays for faster comparison
existing_normalized = []
for ray in existing_rays:
    existing_normalized.append(ray / np.linalg.norm(ray))
existing_normalized = np.array(existing_normalized)

start_search_time = time.time()

for attempt in range(total_attempts):
    if attempt % 50 == 0:
        elapsed = time.time() - start_search_time
        rate = attempt / elapsed if elapsed > 0 else 0
        print(f"\n📊 Progress: {attempt}/{total_attempts} attempts")
        print(f"   New rays found: {new_rays_count}")
        print(f"   Existing rays found: {found_existing}")
        print(f"   Rate: {rate:.1f} attempts/second")
    
    # Random objective
    objective = np.random.rand(63)
    objective = objective / np.linalg.norm(objective)
    
    # Try with different initial subset sizes
    initial_size = np.random.choice([500, 750, 1000, 1500])
    
    try:
        ray, converged = finder.find_ray_active_set(
            objective, 
            initial_size=initial_size, 
            max_iter=50
        )
        
        if ray is not None and converged:
            # Check if new
            max_dot = np.max(np.abs(existing_normalized @ ray))
            
            if max_dot < 0.9999:
                # Found new ray!
                new_rays_count += 1
                
                # Save to file
                np.savetxt(new_rays_file, [ray], fmt='%.10f')
                new_rays_file.flush()
                
                # Add to existing set for future comparisons
                existing_normalized = np.vstack([existing_normalized, ray])
                
                if new_rays_count % 10 == 0:
                    print(f"\n🎉 Found {new_rays_count} new rays so far!")
            else:
                found_existing += 1
                
    except Exception as e:
        print(f"\n⚠️  Error in attempt {attempt+1}: {e}")
        continue

# Final results
elapsed_total = time.time() - start_search_time
new_rays_file.close()

print(f"\n{'='*60}")
print(f"📊 FINAL RESULTS:")
print(f"   Total attempts: {total_attempts}")
print(f"   New rays found: {new_rays_count}")
print(f"   Existing rays found: {found_existing}")
print(f"   Failed attempts: {total_attempts - new_rays_count - found_existing}")
print(f"   Total time: {elapsed_total:.1f}s")
print(f"   Average time per attempt: {elapsed_total/total_attempts:.2f}s")

if new_rays_count > 0:
    print(f"\n✅ New rays saved to: new_rays_extensive_search.txt")
    print(f"🎉 MAJOR DISCOVERY: Found {new_rays_count} new rays!")
    print(f"   Total rays now: {len(existing_rays) + new_rays_count}")
else:
    print("\n💡 No new rays found")

# Also save combined set
if new_rays_count > 0:
    print("\n💾 Creating combined rays file...")
    # Load new rays
    new_rays = np.loadtxt('new_rays_extensive_search.txt')
    if new_rays.ndim == 1:
        new_rays = new_rays.reshape(1, -1)
    
    # Combine with existing
    all_rays = np.vstack([existing_rays, new_rays])
    np.savetxt('all_rays_combined.txt', all_rays, fmt='%.10f')
    print(f"   Saved {len(all_rays)} total rays to: all_rays_combined.txt")