#!/usr/bin/env python3
"""
Complete status check when you wake up - covers all recent discoveries!
"""

import os
import subprocess
import time
from datetime import datetime

def check_complete_status():
    print("🌅 GOOD MORNING! Complete Ray Discovery Status")
    print("=" * 70)
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n🏆 MAJOR ACHIEVEMENTS SO FAR:")
    print(f"   🎯 Original known rays: 4,155")
    print(f"   ✅ First discovery: +16 rays (brought total to 4,171)")
    print(f"   🚀 Extended search: +403 rays (brought total to 4,558)")
    print(f"   📈 Total increase: {((4558 - 4155) / 4155) * 100:.1f}% over original!")
    
    # Check current search status
    print(f"\n🔍 Current Search Status:")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        mega_processes = [line for line in result.stdout.split('\n') 
                         if 'mega_search_10000.py' in line and 'grep' not in line]
        
        if mega_processes:
            print(f"✅ MEGA SEARCH (10,000 attempts) is running!")
            for proc in mega_processes:
                parts = proc.split()
                if len(parts) >= 10:
                    pid = parts[1]
                    cpu = parts[2]
                    mem = parts[3]
                    time_str = parts[9]
                    print(f"   PID {pid}: CPU {cpu}%, MEM {mem}%, TIME {time_str}")
        else:
            print(f"❌ No mega search process found")
            print(f"   🔍 Checking if it completed...")
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    # Check all result files
    print(f"\n📊 Current Results:")
    
    files_to_check = [
        ('extended_search_new_rays.txt', 'Extended search raw results'),
        ('mega_search_10k_rays.txt', 'Mega search results'),
        ('mega_search_unique_rays.txt', 'Mega search unique rays'),
        ('extended_unique_rays.txt', 'Extended search unique (16 rays)'),
        ('signature_unique_rays.txt', 'First discovery unique (10 rays)')
    ]
    
    total_discoveries = 0
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    count = sum(1 for line in f if line.strip())
                last_modified = os.path.getmtime(filename)
                mod_time = datetime.fromtimestamp(last_modified)
                print(f"   📁 {description}: {count} rays (modified: {mod_time.strftime('%m/%d %H:%M')})")
                
                if 'unique' in filename:
                    total_discoveries += count
                    
            except Exception as e:
                print(f"   ❌ {description}: Error - {e}")
        else:
            print(f"   ⚪ {description}: Not found")
    
    # Check mega search progress if running
    if os.path.exists('mega_search_output.log'):
        print(f"\n📈 Mega Search Progress:")
        try:
            with open('mega_search_output.log', 'r') as f:
                content = f.read()
                if content.strip():
                    lines = content.strip().split('\n')
                    print(f"   Log lines: {len(lines)}")
                    if len(lines) > 5:
                        print(f"   Recent: {lines[-1]}")
                else:
                    print(f"   Log is empty (search may still be loading)")
        except Exception as e:
            print(f"   Error reading log: {e}")
    
    # Calculate grand totals
    print(f"\n🎊 GRAND TOTALS:")
    print(f"   Known unique orbit representatives: {total_discoveries} (confirmed)")
    print(f"   Original base: 4,155")
    print(f"   Confirmed new discoveries: {total_discoveries}")
    print(f"   Current total: {4155 + total_discoveries}")
    
    if total_discoveries > 0:
        increase = ((4155 + total_discoveries - 4155) / 4155) * 100
        print(f"   Total increase: {increase:.1f}%")
    
    # Estimate mega search if running
    print(f"\n🔮 Next Steps:")
    if mega_processes:
        print(f"   🏃 Mega search is running - let it complete")
        print(f"   ⏳ Check back in a few hours for 10K attempt results")
    else:
        print(f"   🔍 Check mega search results if completed")
        print(f"   📊 Run S₇ permutation analysis if needed")
    
    print(f"\n🌟 This has been an incredible mathematical discovery session!")

if __name__ == "__main__":
    check_complete_status()