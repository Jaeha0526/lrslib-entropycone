#!/usr/bin/env python3
"""
Real-time monitoring dashboard for all active searches
"""

import os
import subprocess
import time
from datetime import datetime

def get_file_line_count(filename):
    """Get line count safely"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return sum(1 for _ in f)
    except:
        pass
    return 0

def monitor_all_searches():
    print("🎯 EXTREME RAY DISCOVERY DASHBOARD")
    print("=" * 80)
    
    while True:
        os.system('clear')  # Clear screen
        
        print("🎯 EXTREME RAY DISCOVERY DASHBOARD")
        print("=" * 80)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check running processes
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            
            searches = {
                'extended_search_5000': '✅ COMPLETED',
                'mega_search_10000': None,
                'ultra_search_50000': None,
                'giga_search_100000': None
            }
            
            for line in result.stdout.split('\n'):
                for search_name in searches:
                    if search_name + '.py' in line and 'grep' not in line:
                        parts = line.split()
                        if len(parts) >= 10:
                            cpu = parts[2]
                            mem = parts[3]
                            time_str = parts[9]
                            searches[search_name] = f"🏃 RUNNING - CPU: {cpu}%, MEM: {mem}%, TIME: {time_str}"
            
            # Display status
            print("📊 SEARCH STATUS:")
            print(f"   Extended (5K):   {searches['extended_search_5000']}")
            print(f"   Mega (10K):      {searches['mega_search_10000'] or '⏸️  Not running'}")
            print(f"   Ultra (50K):     {searches['ultra_search_50000'] or '⏸️  Not running'}")
            print(f"   Giga (100K):     {searches['giga_search_100000'] or '⏸️  Not running'}")
            
        except Exception as e:
            print(f"Error checking processes: {e}")
        
        print()
        
        # Check results
        print("📈 CURRENT RESULTS:")
        
        result_files = [
            ('extended_search_new_rays.txt', 'Extended raw'),
            ('mega_search_10k_rays.txt', 'Mega raw'),
            ('ultra_search_50k_rays.txt', 'Ultra raw'),
            ('giga_search_100k_rays.txt', 'Giga raw'),
            ('extended_unique_rays.txt', 'Extended unique (16)'),
            ('mega_search_unique_rays.txt', 'Mega unique'),
            ('ultra_search_unique_rays.txt', 'Ultra unique'),
            ('giga_search_unique_rays.txt', 'Giga unique')
        ]
        
        total_unique = 4155  # Base
        for filename, desc in result_files:
            count = get_file_line_count(filename)
            if count > 0:
                print(f"   {desc:20}: {count:,} rays")
                if 'unique' in filename and count > 0:
                    total_unique += count
        
        print()
        print(f"🏆 TOTAL UNIQUE ORBIT REPRESENTATIVES: {total_unique:,}")
        print(f"🚀 Increase over original 4,155: {((total_unique - 4155) / 4155 * 100):.1f}%")
        
        if total_unique > 5000:
            print()
            print("🎊 HISTORIC ACHIEVEMENT: OVER 5,000 EXTREME RAYS!")
        
        print()
        print("Press Ctrl+C to exit monitoring...")
        
        time.sleep(30)  # Update every 30 seconds

if __name__ == "__main__":
    try:
        monitor_all_searches()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")