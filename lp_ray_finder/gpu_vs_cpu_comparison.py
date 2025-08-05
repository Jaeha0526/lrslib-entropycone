#!/usr/bin/env python3
"""
Demonstrate GPU vs CPU performance for constraint checking
"""

import numpy as np
import time

# Check if GPU is available
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("✅ GPU is available via CuPy")
except ImportError:
    GPU_AVAILABLE = False
    print("❌ GPU not available - CuPy not installed")

def check_constraints_cpu(A, x, b):
    """Check Ax <= b on CPU"""
    violations = np.sum(A @ x > b)
    return violations

def check_constraints_gpu(A_gpu, x_gpu, b_gpu):
    """Check Ax <= b on GPU"""
    violations = cp.sum(A_gpu @ x_gpu > b_gpu)
    return int(violations)

def main():
    print("\n🔍 Comparing GPU vs CPU for Constraint Checking")
    print("=" * 50)
    
    # Test parameters
    n_constraints = 100000
    n_dims = 63
    
    print(f"Testing with {n_constraints:,} constraints in {n_dims} dimensions")
    
    # Generate random data
    print("\nGenerating test data...")
    A_cpu = np.random.randn(n_constraints, n_dims).astype(np.float32)
    x_cpu = np.random.randn(n_dims).astype(np.float32)
    b_cpu = np.random.randn(n_constraints).astype(np.float32)
    
    # CPU timing
    print("\n⏱️  CPU Performance:")
    start = time.time()
    violations_cpu = check_constraints_cpu(A_cpu, x_cpu, b_cpu)
    cpu_time = time.time() - start
    print(f"   Time: {cpu_time:.4f} seconds")
    print(f"   Violations: {violations_cpu}")
    
    if GPU_AVAILABLE:
        # Transfer to GPU
        print("\n📤 Transferring data to GPU...")
        start = time.time()
        A_gpu = cp.asarray(A_cpu)
        x_gpu = cp.asarray(x_cpu)
        b_gpu = cp.asarray(b_cpu)
        transfer_time = time.time() - start
        print(f"   Transfer time: {transfer_time:.4f} seconds")
        
        # GPU timing
        print("\n⚡ GPU Performance:")
        start = time.time()
        violations_gpu = check_constraints_gpu(A_gpu, x_gpu, b_gpu)
        gpu_time = time.time() - start
        print(f"   Time: {gpu_time:.4f} seconds")
        print(f"   Violations: {violations_gpu}")
        
        # Speedup
        print(f"\n🚀 Speedup: {cpu_time/gpu_time:.1f}x faster on GPU!")
        print(f"   (Not including transfer time)")
        
        # With transfer time
        total_gpu_time = transfer_time + gpu_time
        print(f"\n📊 Including transfer time:")
        print(f"   Total GPU time: {total_gpu_time:.4f} seconds")
        print(f"   Still {cpu_time/total_gpu_time:.1f}x faster than CPU")
        
        # Memory usage
        print(f"\n💾 GPU Memory:")
        mempool = cp.get_default_memory_pool()
        print(f"   Used: {mempool.used_bytes() / 1024**3:.2f} GB")
        print(f"   Total: {mempool.total_bytes() / 1024**3:.2f} GB")

if __name__ == "__main__":
    main()