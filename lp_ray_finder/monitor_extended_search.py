#!/usr/bin/env python3
"""
Monitor the extended search progress
"""

import time
import os

print("📊 Monitoring Extended Search (5000 attempts)")
print("="*50)

try:
    while True:
        # Check new rays file
        if os.path.exists('extended_search_new_rays.txt'):
            num_rays = sum(1 for _ in open('extended_search_new_rays.txt'))
            
            # Estimate progress (rough estimate based on 3.7% success rate)
            estimated_attempts = num_rays / 0.037
            progress = min(estimated_attempts / 5000 * 100, 100)
            
            print(f"\r🎯 New rays found: {num_rays} | Est. progress: {progress:.1f}% | Est. total: {4155 + num_rays}", 
                  end='', flush=True)
        
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\n\nStopped monitoring")
    if os.path.exists('extended_search_new_rays.txt'):
        final_count = sum(1 for _ in open('extended_search_new_rays.txt'))
        print(f"Final count: {final_count} new rays found")
        print(f"Total orbit representatives: {4155 + final_count}")