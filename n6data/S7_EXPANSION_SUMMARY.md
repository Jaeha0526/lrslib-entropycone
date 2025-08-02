# S₇ Full Expansion for Holographic Entropy Cone

## Overview
This document explains the S₇ full expansion process for finding complete facets in the 6-party holographic entropy cone.

## Mathematical Background

### The Problem
- **System**: 6 boundary regions {A, B, C, D, E, F} + 1 purifier P
- **Dimensions**: 63 coordinates (2⁶ - 1 = 63 non-empty subsets)
- **Goal**: Find complete facet description of holographic entropy cone

### Symmetry Group S₇
- **Size**: 7! = 5,040 permutations
- **Elements**: All permutations of {A, B, C, D, E, F, P}
- **Physical meaning**: Boundary regions can be swapped, purifier can be moved

### Purifier Constraint
Key holographic property: **S(X ∪ {P}) = S(X^c)**
- When purifier P is included, entropy equals complement's entropy
- This creates the fundamental holographic duality constraint

## The S₇ Expansion Process

### Input
- **Base facets**: 1,877 known facets from previous analysis
- **Source**: Original 6-party entropy cone constraints

### Process
1. **Generate S₇ orbit**: Apply all 5,040 permutations to each base facet
2. **Handle purifier logic**: When P appears in permuted subsets, apply complement mapping
3. **Deduplicate**: Remove identical constraints (many permutations create duplicates)
4. **Output**: Complete S₇-symmetric constraint system

### Mathematical Details
```
For each base facet F and each permutation σ ∈ S₇:
- Apply σ to subset indices in F
- If subset contains P after permutation:
  - Map to complement subset (holographic duality)
- Store unique resulting constraint
```

### Computational Scale
- **Input**: 1,877 × 5,040 = 9,460,080 facet-permutation pairs
- **Output**: ~8.7M unique constraints (after deduplication)
- **File size**: ~1.16 GB in lrs format
- **Processing time**: ~20 minutes

## Why This Matters

### Complete Coverage
- Previous S₆ expansion missed 85% of symmetries (only 720 vs 5,040 permutations)
- Missing purifier logic meant incomplete holographic constraints
- S₇ expansion provides mathematically complete facet system

### Ray Discovery
- Complete facet system enables finding ALL extreme rays
- Critical for understanding full geometry of holographic entropy cone
- Enables systematic restart methods for computational efficiency

### Physical Interpretation
- Each facet represents a holographic entropy inequality
- S₇ symmetry ensures all physical configurations are covered
- Purifier constraints capture quantum error correction properties

## Files Generated
- `n6_correct_s7_expansion.ine`: Complete S₇-expanded constraint system (lrs format)
- Processing logs and verification data

## Next Steps
1. Use expanded system for systematic ray discovery
2. Apply restart methods with saturated facets from known rays
3. Complete characterization of 6-party holographic entropy cone