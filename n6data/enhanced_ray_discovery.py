#!/usr/bin/env python3
"""
Enhanced lrslib ray discovery with proper logging and progress monitoring:
- Real-time logging of facet loading progress
- Detection of starting point identification
- Live output of discovered rays
- Progress tracking and timestamps
- Intermediate results saving
"""

import subprocess
import threading
import time
import os
import re
from datetime import datetime

class EnhancedLRSRunner:
    def __init__(self, input_file, output_file, log_file):
        self.input_file = input_file
        self.output_file = output_file
        self.log_file = log_file
        self.process = None
        self.rays_found = 0
        self.start_time = None
        
    def log_with_timestamp(self, message):
        """Log message with timestamp to both console and log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        
        with open(self.log_file, 'a') as f:
            f.write(log_line + "\n")
            f.flush()
    
    def parse_lrs_output(self, line):
        """Parse lrslib output for key events and progress"""
        original_line = line
        line = line.strip()
        
        # Starting point identification
        if "startingcobasis" in line:
            self.log_with_timestamp("🎯 STARTING POINT: lrslib processing startingcobasis declaration")
            
        # Facet/constraint loading progress
        if "begin" in line:
            self.log_with_timestamp("📊 FACET LOADING: Starting to load constraint system")
            
        # Ray discovery - look for ray output format (lrs outputs with leading space)
        if original_line.startswith(" 1 ") and len(original_line.split()) >= 4:  # Look for " 1 " and at least 4 coordinates
            self.rays_found += 1
            ray_coords = original_line.split()[:10]  # Show first 10 coordinates
            self.log_with_timestamp(f"🔍 RAY #{self.rays_found} FOUND: [{', '.join(ray_coords)}...]")
            print(f"DEBUG: Ray detected! Line: '{line}'")
            
            # Save ray immediately to intermediate file
            with open(f"{self.output_file}.rays", 'a') as f:
                f.write(original_line.strip() + "\n")
                f.flush()
        
        # End of computation
        if line.startswith("end") or "hull" in line.lower():
            self.log_with_timestamp("✅ RAY DISCOVERY: lrslib enumeration completed")
            
        # Memory/resource info
        if "memory" in line.lower() or "time" in line.lower():
            self.log_with_timestamp(f"📈 RESOURCE: {line}")
            
        # Error detection
        if "error" in line.lower() or "failed" in line.lower():
            self.log_with_timestamp(f"❌ ERROR: {line}")
    
    def monitor_output(self, pipe):
        """Monitor lrslib output in real-time"""
        try:
            for line in iter(pipe.readline, b''):
                line_str = line.decode('utf-8', errors='ignore')
                self.parse_lrs_output(line_str)
        except Exception as e:
            self.log_with_timestamp(f"❌ OUTPUT MONITORING ERROR: {e}")
        finally:
            pipe.close()
    
    def run_with_monitoring(self):
        """Run lrslib with enhanced monitoring and logging"""
        self.start_time = time.time()
        
        # Initialize log file
        with open(self.log_file, 'w') as f:
            f.write(f"Enhanced lrslib ray discovery log\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Input: {self.input_file}\n")
            f.write(f"Output: {self.output_file}\n")
            f.write("=" * 60 + "\n\n")
        
        # Clear intermediate rays file
        with open(f"{self.output_file}.rays", 'w') as f:
            f.write("# Intermediate rays discovered during enumeration\n")
            f.write("# Format: ray coordinates (63 dimensions)\n\n")
        
        self.log_with_timestamp("🚀 STARTING: Enhanced lrslib ray discovery")
        self.log_with_timestamp(f"📁 INPUT: {self.input_file}")
        self.log_with_timestamp(f"📁 OUTPUT: {self.output_file}")
        self.log_with_timestamp(f"📁 LOG: {self.log_file}")
        
        # Check input file
        if not os.path.exists(self.input_file):
            self.log_with_timestamp(f"❌ ERROR: Input file not found: {self.input_file}")
            return False
            
        input_size_mb = os.path.getsize(self.input_file) / (1024*1024)
        self.log_with_timestamp(f"📊 INPUT SIZE: {input_size_mb:.1f} MB")
        
        try:
            # Set library path and run lrslib
            env = os.environ.copy()
            env['DYLD_LIBRARY_PATH'] = '.libs'
            
            self.log_with_timestamp("⚡ LAUNCHING: lrslib process with monitoring")
            
            # Start lrslib process
            self.process = subprocess.Popen(
                ['./.libs/lrs', self.input_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                env=env,
                cwd='/Users/jaeha/repos/lrslib'
            )
            
            # Start output monitoring thread
            monitor_thread = threading.Thread(
                target=self.monitor_output, 
                args=(self.process.stdout,)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Progress reporting timer
            def progress_reporter():
                while self.process.poll() is None:
                    elapsed = time.time() - self.start_time
                    self.log_with_timestamp(
                        f"⏰ PROGRESS: {elapsed:.0f}s elapsed, {self.rays_found} rays found"
                    )
                    time.sleep(30)  # Report every 30 seconds
            
            progress_thread = threading.Thread(target=progress_reporter)
            progress_thread.daemon = True
            progress_thread.start()
            
            # Wait for completion
            return_code = self.process.wait()
            
            # Final status
            total_time = time.time() - self.start_time
            self.log_with_timestamp(f"🏁 COMPLETED: Process finished with code {return_code}")
            self.log_with_timestamp(f"⏱️  TOTAL TIME: {total_time:.1f} seconds")
            self.log_with_timestamp(f"🎯 RAYS FOUND: {self.rays_found} total rays discovered")
            
            # Copy final output
            if os.path.exists(f"{self.output_file}.rays"):
                with open(f"{self.output_file}.rays", 'r') as f:
                    lines = f.readlines()
                    ray_lines = [l for l in lines if not l.startswith('#') and l.strip()]
                    self.log_with_timestamp(f"💾 SAVED: {len(ray_lines)} rays to {self.output_file}.rays")
            
            return return_code == 0
            
        except Exception as e:
            self.log_with_timestamp(f"❌ FATAL ERROR: {e}")
            return False

def run_enhanced_discovery():
    """Run enhanced ray discovery with full logging"""
    input_file = "n6data/n6_restart_startingcobasis.ine"
    output_file = "n6data/new_rays_from_1381_enhanced.ext"
    log_file = "n6data/ray_discovery_enhanced.log"
    
    runner = EnhancedLRSRunner(input_file, output_file, log_file)
    success = runner.run_with_monitoring()
    
    if success:
        print(f"\n✅ Enhanced ray discovery completed successfully!")
        print(f"📁 Results: {output_file}")
        print(f"📁 Rays: {output_file}.rays")
        print(f"📁 Log: {log_file}")
    else:
        print(f"\n❌ Enhanced ray discovery failed!")
        print(f"📁 Check log: {log_file}")

if __name__ == "__main__":
    run_enhanced_discovery()