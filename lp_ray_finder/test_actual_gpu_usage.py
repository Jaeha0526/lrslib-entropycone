#!/usr/bin/env python3
"""
Test GPU performance with realistic problem size (8.6M constraints)
"""

import numpy as np
import time
import cupy as cp

def test_large_scale():
    print("🚀 Testing GPU with 8.6M constraints (like our actual problem)")
    print("=" * 60)
    
    # Realistic sizes
    n_constraints = 8_665_853
    n_dims = 63
    
    print(f"Problem size: {n_constraints:,} constraints × {n_dims} dimensions")
    print(f"Matrix size: {(n_constraints * n_dims * 4) / 1024**3:.1f} GB (float32)")
    
    # We can't actually create the full matrix in RAM, so let's test batches
    batch_size = 1_000_000
    n_batches = 10
    
    print(f"\nTesting with {n_batches} batches of {batch_size:,} constraints each")
    
    # Generate one batch
    print("\nGenerating test batch...")
    A_batch = np.random.randn(batch_size, n_dims).astype(np.float32)
    x = np.random.randn(n_dims).astype(np.float32)
    b_batch = np.random.randn(batch_size).astype(np.float32)
    
    # CPU test
    print("\n⏱️  CPU Performance (per batch):")
    cpu_times = []
    for i in range(3):  # Average of 3 runs
        start = time.time()
        violations = np.sum(A_batch @ x > b_batch)
        cpu_time = time.time() - start
        cpu_times.append(cpu_time)
    
    avg_cpu_time = np.mean(cpu_times)
    print(f"   Average time: {avg_cpu_time:.4f} seconds")
    print(f"   Estimated for 8.6M: {avg_cpu_time * 8.66:.2f} seconds")
    
    # GPU test
    print("\n⚡ GPU Performance (per batch):")
    
    # Transfer to GPU
    A_gpu = cp.asarray(A_batch)
    x_gpu = cp.asarray(x)
    b_gpu = cp.asarray(b_batch)
    
    # Warm up GPU
    _ = A_gpu @ x_gpu
    cp.cuda.Stream.null.synchronize()
    
    gpu_times = []
    for i in range(3):  # Average of 3 runs
        start = time.time()
        violations_gpu = cp.sum(A_gpu @ x_gpu > b_gpu)
        cp.cuda.Stream.null.synchronize()  # Ensure computation completes
        gpu_time = time.time() - start
        gpu_times.append(gpu_time)
    
    avg_gpu_time = np.mean(gpu_times)
    print(f"   Average time: {avg_gpu_time:.4f} seconds")
    print(f"   Estimated for 8.6M: {avg_gpu_time * 8.66:.2f} seconds")
    
    # Speedup
    speedup = avg_cpu_time / avg_gpu_time
    print(f"\n🚀 Speedup: {speedup:.1f}x faster on GPU!")
    
    # Memory info
    mempool = cp.get_default_memory_pool()
    print(f"\n💾 GPU Memory Usage:")
    print(f"   Used: {mempool.used_bytes() / 1024**3:.2f} GB")
    print(f"   Matrix size on GPU: {(batch_size * n_dims * 4) / 1024**3:.3f} GB")
    
    # Check available GPU memory
    free_mem, total_mem = cp.cuda.runtime.memGetInfo()
    print(f"   Free GPU memory: {free_mem / 1024**3:.1f} GB")
    print(f"   Total GPU memory: {total_mem / 1024**3:.1f} GB")
    
    # Estimate for full problem
    full_matrix_size = (n_constraints * n_dims * 4) / 1024**3
    print(f"\n📊 Full Problem Estimate:")
    print(f"   Full matrix would need: {full_matrix_size:.1f} GB")
    print(f"   Can fit in GPU memory: {'Yes' if full_matrix_size < free_mem/1024**3 else 'No'}")
    
    if speedup > 1:
        total_speedup_time = (avg_cpu_time * 8.66) - (avg_gpu_time * 8.66)
        print(f"   Time saved per check: {total_speedup_time:.2f} seconds")
        print(f"   With 16,000 LP iterations: {total_speedup_time * 16000 / 3600:.1f} hours saved!")

if __name__ == "__main__":
    test_large_scale()