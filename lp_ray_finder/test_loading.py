#!/usr/bin/env python3
import numpy as np

def test_load():
    with open("/resnick/groups/OoguriGroup/jaeha/lrslib-entropycone/lp_ray_finder/UNIQUE_RAYS_CONSOLIDATED/aug3_129_new_rays.txt", "r") as f:
        lines = f.readlines()[:10]
        
    for i, line in enumerate(lines):
        print(f"Line {i+1}: {line.strip()[:80]}...")
        if not line.startswith("#") and line.strip():
            try:
                ray_data = line.split("#")[0].strip()
                parts = ray_data.split()
                print(f"  Number of parts: {len(parts)}")
                ray = np.fromstring(ray_data, sep=" ")
                print(f"  Ray length: {len(ray)}")
                if len(ray) == 63:
                    print("  ✅ Valid 63-dimensional ray")
                else:
                    print(f"  ❌ Expected 63, got {len(ray)}")
                break
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    test_load()