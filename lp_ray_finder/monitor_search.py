#!/usr/bin/env python3
"""
Monitor the extensive search progress
"""

import time
import os

print("📊 Monitoring extensive ray search...")
print("Press Ctrl+C to stop monitoring\n")

try:
    while True:
        # Check new rays file
        if os.path.exists('new_rays_extensive_search.txt'):
            num_lines = sum(1 for _ in open('new_rays_extensive_search.txt'))
            print(f"\r🎉 New rays found: {num_lines} | Total rays: {4145 + num_lines}", end='', flush=True)
        else:
            print("\rWaiting for results...", end='', flush=True)
        
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n\nMonitoring stopped.")
    if os.path.exists('new_rays_extensive_search.txt'):
        num_lines = sum(1 for _ in open('new_rays_extensive_search.txt'))
        print(f"Final count: {num_lines} new rays found")
        print(f"Total rays: {4145 + num_lines}")