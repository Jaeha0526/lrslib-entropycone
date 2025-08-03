#!/usr/bin/env python3
"""
Quick status check for extended search when you wake up
"""

import os
import subprocess
import time
from datetime import datetime

def check_search_status():
    print("🌅 Good Morning! Extended Search Status Check")
    print("=" * 60)
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if processes are still running
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        extended_processes = [line for line in result.stdout.split('\n') 
                            if 'extended_search_5000.py' in line and 'grep' not in line]
        
        if extended_processes:
            print(f"✅ Search is still running! Found {len(extended_processes)} active processes")
            for proc in extended_processes:
                parts = proc.split()
                if len(parts) >= 10:
                    pid = parts[1]
                    cpu = parts[2]
                    mem = parts[3]
                    time_str = parts[9]
                    print(f"   PID {pid}: CPU {cpu}%, MEM {mem}%, TIME {time_str}")
        else:
            print("❌ No extended search processes found - search may have completed")
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    # Check current ray count
    files_to_check = [
        ('extended_search_new_rays.txt', 'Raw rays from search'),
        ('extended_search_valid.txt', 'Valid rays (cleaned)'),
        ('extended_unique_rays.txt', 'Unique orbit representatives')
    ]
    
    print(f"\n📊 Current Results:")
    for filename, description in files_to_check:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    count = sum(1 for line in f if line.strip())
                last_modified = os.path.getmtime(filename)
                mod_time = datetime.fromtimestamp(last_modified)
                print(f"   {description}: {count} rays (last modified: {mod_time.strftime('%H:%M:%S')})")
            except Exception as e:
                print(f"   {description}: Error reading file - {e}")
        else:
            print(f"   {description}: File not found")
    
    # Estimate progress
    try:
        if os.path.exists('extended_search_valid.txt'):
            with open('extended_search_valid.txt', 'r') as f:
                current_rays = sum(1 for line in f if line.strip())
            
            estimated_attempts = current_rays / 0.037  # 3.7% success rate
            progress = (estimated_attempts / 5000) * 100
            
            print(f"\n📈 Progress Estimation:")
            print(f"   Current rays: {current_rays}")
            print(f"   Estimated attempts: {estimated_attempts:.0f} / 5000")
            print(f"   Estimated progress: {progress:.1f}%")
            
            if progress < 100:
                remaining_attempts = 5000 - estimated_attempts
                print(f"   Remaining attempts: ~{remaining_attempts:.0f}")
            else:
                print("   🎉 Search may be complete!")
    except Exception as e:
        print(f"Error estimating progress: {e}")
    
    # System resources
    print(f"\n💻 System Status:")
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        memory_lines = result.stdout.strip().split('\n')[1:3]
        for line in memory_lines:
            print(f"   {line}")
    except:
        print("   Could not check memory usage")
    
    print(f"\n🔍 Next Steps:")
    print(f"   1. If search is still running: Let it continue")
    print(f"   2. If search completed: Run S₇ permutation analysis on new results")
    print(f"   3. Check for any new unique orbit representatives")
    print(f"   4. Update discovery summary with final results")

if __name__ == "__main__":
    check_search_status()