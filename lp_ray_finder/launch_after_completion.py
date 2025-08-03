#!/usr/bin/env python3
"""
Monitor current search and launch mega search when it completes
"""

import time
import subprocess
import os
from datetime import datetime

def wait_for_completion_and_launch():
    print("⏰ Waiting for Current Search to Complete...")
    print("=" * 50)
    
    # Wait for current search to finish
    while True:
        try:
            # Check if extended search processes are still running
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            extended_processes = [line for line in result.stdout.split('\\n') 
                                if 'extended_search_5000.py' in line and 'grep' not in line]
            
            if not extended_processes:
                print(f"✅ Current search completed at {datetime.now().strftime('%H:%M:%S')}")
                break
            else:
                print(f"🔄 Still running... {len(extended_processes)} processes active")
                time.sleep(60)  # Check every minute
                
        except Exception as e:
            print(f"Error checking processes: {e}")
            time.sleep(60)
    
    print("\\n🔍 Analyzing Current Search Results...")
    
    # Quick analysis of completed search
    try:
        if os.path.exists('extended_search_new_rays.txt'):
            # Clean and analyze the results
            os.system("python -c \\"
                      "import numpy as np; "
                      "valid_rays = []; "
                      "with open('extended_search_new_rays.txt', 'r') as f: "
                      "    for line in f: "
                      "        try: "
                      "            values = [float(x) for x in line.strip().split()]; "
                      "            if len(values) == 63: valid_rays.append(values) "
                      "        except: pass; "
                      "np.savetxt('final_extended_valid.txt', valid_rays, fmt='%.10f'); "
                      "print(f'Final count: {len(valid_rays)} valid rays')\\"")
            
            # Run S7 analysis on final results
            os.system("python check_extended_permutations.py")
    except Exception as e:
        print(f"Error analyzing results: {e}")
    
    print("\\n🚀 Launching MEGA SEARCH (10,000 attempts)...")
    print(f"Launch time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Launch mega search in background
    subprocess.Popen([
        'nohup', 'python', 'mega_search_10000.py'
    ], stdout=open('mega_search_output.log', 'w'), 
       stderr=subprocess.STDOUT)
    
    print("✅ Mega search launched!")
    print("📋 Monitor with: tail -f mega_search_output.log")
    print("🎯 Expected completion: ~2-3 hours for 10,000 attempts")

if __name__ == "__main__":
    wait_for_completion_and_launch()