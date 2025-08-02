# StartingCobasis vs Linearity: Proper lrslib Restart Method

## Problem with Linearity Approach

**Initial misunderstanding**: Using `linearity` to declare the 11,766 saturated constraints as equalities.

**Why this is wrong**:
- `linearity` declares constraints as **equalities** (must be exactly zero)
- This creates a lower-dimensional subspace intersection of all 11,766 facet boundaries
- **Restricts the search space** instead of just setting the starting point
- Would only find rays that lie on ALL 11,766 facets simultaneously
- Does NOT explore the full 63-dimensional polytope

## Correct StartingCobasis Approach

**What startingcobasis means**:
- **Cobasis** = set of constraint indices that are NOT in the basis (non-tight constraints)
- **Basis** = set of tight constraints that define the current vertex/ray
- For ray #1381: 11,766 saturated constraints are basis (tight), remaining 8.65M are cobasis (non-tight)

**How startingcobasis works**:
1. Specify the NON-saturated constraint indices as startingcobasis
2. lrslib deduces the basis as the remaining constraints (the 11,766 saturated ones)
3. This uniquely positions lrslib at ray #1381
4. **Crucially**: Search space remains the full 63-dimensional polytope
5. lrslib can pivot to adjacent rays in the complete 8.7M-constraint system

## Implementation Details

**File created**: `n6_restart_startingcobasis.ine` (1.2 GB)
- Contains ALL 8,665,853 constraints (complete S7-expanded polytope)
- `startingcobasis` declaration with 8,654,087 non-saturated constraint indices
- Starting point: Ray #1381 (saturates exactly 11,766 constraints)
- Search space: Full 63-dimensional holographic entropy cone

**Verification**:
- Total constraints: 8,665,853
- Saturated by ray #1381: 11,766
- Non-saturated (cobasis): 8,654,087
- Check: 11,766 + 8,654,087 = 8,665,853 ✓

## Expected Results

**What this will discover**:
- New extreme rays adjacent to ray #1381 in the complete polytope
- Efficient exploration starting from known ray instead of random search
- Full 6-party holographic entropy cone structure around ray #1381

**Ready to run**:
```bash
./.libs/lrs n6_restart_startingcobasis.ine > new_rays_from_1381.ext
```

This approach correctly balances:
- **Starting point**: Exactly at ray #1381 (using cobasis mechanism)
- **Search space**: Complete 8.7M-constraint polytope (no dimensional restriction)