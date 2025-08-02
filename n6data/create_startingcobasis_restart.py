#!/usr/bin/env python3
"""
Create proper lrslib restart file using startingcobasis mechanism:
- Use ALL 8.7M constraints to define the complete polytope  
- Specify the NON-saturated constraint indices as startingcobasis
- This positions lrslib at ray #1381 without constraining search space
- lrslib can then explore the FULL polytope for adjacent rays
"""

import os

def create_startingcobasis_restart():
    """Create restart file using startingcobasis for proper ray #1381 starting point"""
    print("🚀 Creating PROPER lrslib restart file using startingcobasis...")
    print("   • Using ALL 8.7M constraints (complete polytope)")
    print("   • Specifying NON-saturated indices as startingcobasis")
    print("   • This starts at ray #1381 without constraining search space")
    
    # Load saturated constraint indices
    print("📊 Loading saturated constraint indices...")
    saturated_indices = set()
    with open('n6data/saturated_facets_ray1381_streaming.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                saturated_indices.add(int(line))
    
    print(f"   Found {len(saturated_indices)} saturated indices")
    print(f"   Range: {min(saturated_indices)} to {max(saturated_indices)}")
    
    # Get total number of constraints
    input_file = 'n6data/n6_correct_s7_expansion.ine'
    print(f"📊 Analyzing constraint system: {input_file}")
    
    total_constraints = 0
    with open(input_file, 'r') as f:
        parsing = False
        for line in f:
            line = line.strip()
            if line == "begin":
                parsing = True
                continue
            elif line == "end":
                break
            elif not parsing:
                continue
            
            # Skip dimension line
            parts = line.split()
            if len(parts) >= 3 and parts[2] == "integer":
                total_constraints = int(parts[0])  # Get from dimension line
                break
    
    print(f"   Total constraints: {total_constraints:,}")
    
    # Generate NON-saturated indices for startingcobasis
    print("🔍 Generating NON-saturated constraint indices...")
    non_saturated_indices = []
    for i in range(1, total_constraints + 1):  # 1-based indexing
        if i not in saturated_indices:
            non_saturated_indices.append(i)
    
    num_non_saturated = len(non_saturated_indices)
    print(f"   Non-saturated constraints: {num_non_saturated:,}")
    print(f"   Verification: {len(saturated_indices)} + {num_non_saturated} = {len(saturated_indices) + num_non_saturated}")
    
    # Create restart file
    output_file = 'n6_restart_startingcobasis.ine'
    print(f"💾 Creating startingcobasis restart file: {output_file}")
    
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # Read input file
        lines = infile.readlines()
        
        # Write header
        outfile.write("n6_restart_startingcobasis\n")
        outfile.write("H-representation\n")
        
        # Copy constraints (begin, dimensions, all constraints, end)
        print("📋 Copying ALL constraint data...")
        parsing_started = False
        constraint_count = 0
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip original header lines
            if line_stripped in ["n6_correct_s7_expansion", "H-representation"]:
                continue
            
            # Start copying from "begin"
            if line_stripped == "begin":
                parsing_started = True
                outfile.write(line)
                continue
            
            if parsing_started:
                outfile.write(line)
                
                # Count constraints for progress
                if line_stripped and line_stripped != "end":
                    parts = line_stripped.split()
                    # Count actual constraints
                    if len(parts) == 63:
                        constraint_count += 1
                        if constraint_count % 100000 == 0:
                            print(f"   Copied {constraint_count:,} constraints...")
        
        # Write startingcobasis declaration
        print("✍️  Writing startingcobasis declaration...")
        outfile.write(f"startingcobasis")
        
        # Write non-saturated indices (split across lines for readability)
        indices_per_line = 50
        for i, idx in enumerate(non_saturated_indices):
            if i % indices_per_line == 0:
                outfile.write("\n")  # New line every 50 indices
            outfile.write(f" {idx}")
        
        outfile.write("\n")  # Final newline
    
    # Check output file
    output_size_mb = os.path.getsize(output_file) / (1024*1024)
    
    print(f"✅ Created PROPER restart file: {output_file}")
    print(f"📊 Output file size: {output_size_mb:.1f} MB")
    print(f"📊 Contains ALL {total_constraints:,} constraints")
    print(f"📊 Startingcobasis: {num_non_saturated:,} indices")
    
    # Show file structure
    print(f"\n📋 File structure:")
    with open(output_file, 'r') as f:
        lines = f.readlines()
        print(f"   Total lines: {len(lines):,}")
        # Show first few lines
        for i, line in enumerate(lines[:5]):
            display_line = line.strip()
            if len(display_line) > 100:
                display_line = display_line[:100] + "..."
            print(f"   Line {i+1}: {display_line}")
        
        # Show last few lines (startingcobasis)
        print("   ...")
        for i, line in enumerate(lines[-5:]):
            display_line = line.strip()
            if len(display_line) > 100:
                display_line = display_line[:100] + "..."
            print(f"   Line {len(lines)-5+i+1}: {display_line}")
    
    return output_file, num_non_saturated

if __name__ == "__main__":
    restart_file, num_cobasis = create_startingcobasis_restart()
    
    print(f"\n🎯 PROPER RESTART FILE READY!")
    print(f"📁 File: {restart_file}")
    print(f"📊 Complete polytope: ALL {8665853:,} constraints")
    print(f"📊 Starting cobasis: {num_cobasis:,} non-saturated constraints")
    print(f"🎯 Starting point: Ray #1381")
    
    print(f"\n💡 How this works:")
    print(f"   • Polytope defined by ALL 8.7M constraints (no restriction)")
    print(f"   • startingcobasis specifies {num_cobasis:,} non-tight constraints")
    print(f"   • This positions lrslib exactly at ray #1381")
    print(f"   • lrslib explores the FULL polytope for adjacent rays")
    print(f"   • Search space is NOT constrained to saturated facets")
    
    print(f"\n🚀 Ready to run:")
    print(f"   ./.libs/lrs {restart_file} > new_rays_from_1381.ext")
    print(f"   # Discovers new rays in the COMPLETE polytope starting from ray #1381!")