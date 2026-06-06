# Etapa 05: Russian Roulette Path Termination

**Status:** Not yet implemented
**Target Points:** +0.5 pt (extension from Etapa 04)
**Complexity:** Medium (adds variance reduction without changing illumination)

---

## 1. Problem Statement

### 1.1 Issue: Inefficient Deep Paths

Currently, all paths trace to `max_depth` regardless of termination likelihood.

**Example:** A ray bouncing in a corner with ρ=0.8:

```
Depth 4: β = 1 × 0.8 = 0.8
Depth 5: β = 0.8 × 0.8 = 0.64  ← still 64% throughput
Depth 6: β = 0.64 × 0.8 = 0.512  ← still 51% throughput
Depth 8: β = 0.262 × 0.8 = 0.210  ← only 21% chance of continuing
Depth 10: β = 0.053 × 0.8 = 0.043  ← marginally contributes
```

**Problem:** Compute wasted on paths with negligible contribution (β << 1)

### 1.2 Solution: Probabilistic Termination

**Russian Roulette (RR) Principle:**

- Terminate path with probability (1 - p)
- If continued, scale radiance by 1/p (unbiased resampling)

**Effect:**

- Paths with low β terminate early (99% chance)
- Paths with high β continue (keep all samples)
- Result: Same expected value, lower variance, faster convergence

---

## 2. Mathematical Formulation

### 2.1 Unbiased Termination

Original contribution (without RR):

$$
L = L_0 + \beta_1 L_1 + \beta_2 L_2 + ... + \beta_n L_n
$$

With RR termination at depth d ≥ min_depth:

**Survival probability:**

$$
p(d) = \min\left(\frac{\max(\beta(d))}{C}, 1.0\right)
$$

where C is a reference constant (typically C=1.0, meaning max β=1.0)

**Contribution if continued:**

$$
L'_d = \frac{L_d}{p(d)}
$$

**Expected value (bias check):**

$$
E[L'] = p(d) \cdot E\left[\frac{L_d}{p(d)}\right] + (1-p(d)) \cdot 0 = E[L_d] \quad \checkmark \text{Unbiased}
$$

### 2.2 Common Variants

**Variant A: Maximal Throughput**

```python
if depth >= min_depth:
    p_survive = min(max(beta.r, beta.g, beta.b), 1.0)
```

Rationale: Use maximum RGB channel (conservative)

**Variant B: Mean Throughput**

```python
if depth >= min_depth:
    p_survive = min((beta.r + beta.g + beta.b) / 3.0, 1.0)
```

Rationale: Balance all channels equally

**Variant C: Luminance**

```python
if depth >= min_depth:
    luminance = 0.299 * beta.r + 0.587 * beta.g + 0.114 * beta.b
    p_survive = min(luminance, 1.0)
```

Rationale: Perceptual importance weighting

**Preferred:** Variant A (maximal) is most common in production renderers

---

## 3. Implementation Guide

### 3.1 Code Structure

**File to modify:** `src/path_tracing/integrators/path_tracer.py`

**Location:** In main path loop, after bounce calculation

```python
# Path tracing loop
for iter_depth in range(1, self.max_depth + 1):
    # ... intersection test, BSDF/NEE sampling ...

    # Russian Roulette termination (NEW)
    if iter_depth >= self.min_depth:
        p_continue = max(beta.x, max(beta.y, beta.z))  # Maximal throughput
        p_continue = min(p_continue, 1.0)  # Clamp to [0, 1]

        if random() > p_continue:
            break  # Path terminated

        beta /= p_continue  # Unbiased resampling

    # Continue to next bounce...
```

### 3.2 Pseudocode

```python
def trace_path_rr(ray, scene, max_depth=8, min_depth=4):
    L = Vector3(0, 0, 0)
    beta = Vector3(1, 1, 1)

    for depth in range(1, max_depth + 1):
        # Ray-scene intersection
        hit = scene.intersect(ray)
        if not hit:
            L += beta * scene.background  # Skybox
            break

        # ... BSDF/NEE/MIS sampling ...
        # (existing code)
        # ...

        # Russian Roulette (NEW)
        if depth >= min_depth:
            p_survive = min(max(beta.x, beta.y, beta.z), 1.0)

            # Probabilistic termination
            if random() > p_survive:
                break  # Dead path

            # Scale contribution (unbiased)
            beta /= p_survive

        # Continue to next bounce
        ray = scattered_ray

    return L
```

### 3.3 Integration with Existing Code

**Current path_tracer.py structure:**

```python
def Li(self, ray, scene, depth=0):
    if depth >= self.max_depth:
        return Vector3(0, 0, 0)

    # Intersection, BSDF/NEE sampling, emissive accumulation
    # ... ~80 lines ...

    # Recursive call
    if scattered:
        L += beta * self.Li(scattered_ray, scene, depth + 1)

    return L
```

**Modified with RR:**

```python
def Li(self, ray, scene, depth=0):
    if depth >= self.max_depth:
        return Vector3(0, 0, 0)

    # ... existing BSDF/NEE sampling ...

    # Russian Roulette (INSERT HERE)
    if depth >= self.min_depth:
        p_survive = min(max(beta.x, beta.y, beta.z), 1.0)
        if random() > p_survive:
            return L  # Path dies here
        beta /= p_survive

    # Recursive call (beta now scaled)
    if scattered:
        L += beta * self.Li(scattered_ray, scene, depth + 1)

    return L
```

---

## 4. Expected Effects

### 4.1 Variance Reduction

**Theoretical improvement (Veach 1995):**

```
Variance reduction: ≈ 30-50% at SPP=16
                    ≈ 20-30% at SPP=64 (more dramatic at low SPP)
                    ≈ 10-15% at SPP=256+ (law of large numbers)
```

**Why RR helps:**

1. Eliminates low-contribution paths (β < 0.1)
2. Preserves high-contribution paths
3. Concentrates computation on important samples

### 4.2 Render Time Impact

**Expected:** 5-10% _faster_ per sample (fewer deep paths)

```
Without RR: 1.05M paths × avg_10_bounces = 10.5M path segments
With RR:    1.05M paths × avg_6_bounces  = 6.3M path segments
Speedup:    6.3 / 10.5 = 0.60 → 40% fewer segments
```

But slightly slower per segment (RR check overhead):

```
Net effect: ~20-30% faster overall with same quality
```

### 4.3 Visual Result

At same SPP, renders with RR should be:

- ✅ Noisier (fewer samples per mode)
- ✅ Faster (shorter paths)
- ✅ Better noise distribution (RR de-emphasizes artifacts)

At same render time, RR should show:

- ✅ Lower noise
- ✅ Better convergence
- ✅ Smoother results

---

## 5. Testing Strategy

### 5.1 Validation Checklist

```python
# 1. Correctness: Same expected value
assert abs(E[with_rr] - E[without_rr]) < 0.01  # Unbiased

# 2. Variance: Should be lower or equal
assert Var[with_rr] <= Var[without_rr]  # Always true

# 3. Speed: Should be faster or same
assert time[with_rr] <= time[without_rr] * 1.1  # Allow 10% margin

# 4. Visual: Convergence should be faster
E_error[with_rr, SPP=32] ~< E_error[without_rr, SPP=16]
```

### 5.2 Reference Renders

Create script `proj2_req5_rr.py`:

```bash
python -m path_tracing.scripts.proj2_req5_rr \
  --use-rr true \
  --min-depth 4 \
  --spp 16 --depth 12 \
  --width 256 --height 256 \
  --seed 42
```

**Expected output comparison (vs Etapa 04):**

| Config                     | Time (s) | Quality               | Notes                |
| -------------------------- | -------- | --------------------- | -------------------- |
| MIS, no RR, depth=6        | 119.6    | SPP=16                | Baseline             |
| MIS + RR, depth=12         | ~90      | SPP=16 better quality | Faster, same noise   |
| MIS + RR, depth=12, SPP=32 | ~180     | SPP=32                | More samples in time |

### 5.3 Measurement Script

```python
# Compare convergence: plot MSE vs render_time
import matplotlib.pyplot as plt

configs = [
    ('MIS no-RR depth=6', 'out/proj2/req3/...'),
    ('MIS + RR depth=12', 'out/proj2/req5/...'),
]

for name, path in configs:
    # Extract properties.json, render.png
    # Compute MSE vs reference (ground truth or high-SPP render)
    # Plot convergence curve
```

---

## 6. Implementation Roadmap

### Phase 1: Add RR Toggle (30 min)

```python
# src/path_tracing/integrators/path_tracer.py

class PathIntegrator:
    def __init__(self, use_rr=False, min_depth=4, **kwargs):
        self.use_rr = use_rr
        self.min_depth = min_depth
        # ... existing init ...
```

### Phase 2: Implement RR Logic (15 min)

```python
# In Li() method, after BSDF/NEE/MIS block:
if self.use_rr and depth >= self.min_depth:
    p_survive = min(max(beta.x, beta.y, beta.z), 1.0)
    if random() > p_survive:
        return L
    beta /= p_survive
```

### Phase 3: Create CLI Script (15 min)

```bash
cp src/path_tracing/scripts/proj2_req3_mis.py \
   src/path_tracing/scripts/proj2_req5_rr.py

# Update:
# - Parser: add --use-rr flag
# - Help text: "Enable Russian Roulette termination"
# - IntegratorKwargs: use_rr=args.use_rr
```

### Phase 4: Testing & Documentation (45 min)

- Render 256×256 SPP=16 with/without RR
- Compare render times, visual quality
- Create ETAPA_05_RR.md with results
- Update ETAPA_04_MIS_TESTING.md with RR comparison

**Total Estimated Time:** ~2 hours hands-on, well-suited for next session

---

## 7. Common Pitfalls

### Pitfall 1: Forgetting to Scale β

```python
# ❌ WRONG: β not scaled
if depth >= min_depth:
    p_survive = min(max(beta), 1.0)
    if random() > p_survive:
        return L
    # Missing: beta /= p_survive

# ✅ CORRECT: β scaled for unbiased resampling
if depth >= min_depth:
    p_survive = min(max(beta), 1.0)
    if random() > p_survive:
        return L
    beta /= p_survive  # Crucial!
```

**Effect if forgotten:** Image becomes darker with RR (biased estimator)

### Pitfall 2: RR at depth=0

```python
# ❌ WRONG: Terminating primary ray (almost always black)
if depth >= 0:  # All depths including 0!
    ...

# ✅ CORRECT: Only deep paths
if depth >= self.min_depth:  # Default 4
    ...
```

**Effect if wrong:** Image mostly black (primary rays killed)

### Pitfall 3: p_survive > 1.0

```python
# ❌ WRONG: No clamping
p_survive = max(beta.x, beta.y, beta.z)  # Could be 2.0!

# ✅ CORRECT: Clamped to [0, 1]
p_survive = min(max(beta.x, beta.y, beta.z), 1.0)
```

**Effect if wrong:** Probability > 1 is undefined (numerical instability)

### Pitfall 4: Not updating CLI help text

```python
# ❌ Help still says "Etapa 04"
parser = ArgumentParser(description="ETAPA 04: MIS...")

# ✅ Updated
parser = ArgumentParser(description="ETAPA 05: MIS + Russian Roulette...")
```

---

## 8. Advanced Variants (Future)

### 8.1 Adaptive RR (Etapa 05b)

Scale survival probability by local luminance:

```python
p_survive = min(luminance(beta) / reference_luminance, 1.0)
```

**Benefit:** Locally adaptive termination probability

### 8.2 Weighted RR (Etapa 05c)

Incorporate MIS weights into survival probability:

```python
if mode == 'mis':
    p_survive = min(max(beta * w_combined), 1.0)
```

**Benefit:** Downweight low-MIS-weighted paths

### 8.3 Spectral RR (Etapa 05d)

Per-channel termination (complex):

```python
p_r = min(beta.r, 1.0)
p_g = min(beta.g, 1.0)
p_b = min(beta.b, 1.0)
# Randomly terminate one channel at a time
```

**Benefit:** Fine-grained control, rarely used

---

## 9. References

1. **Veach, E.** (1997). "Robust Monte Carlo Methods for Light Transport Simulation" (PhD). Stanford. Chapter 2.2.2: Russian Roulette.
2. **Pharr et al.** (2016). "PBRT 3e." Ch. 14, Section 14.2.2: Terminating Paths.
3. **Novák et al.** (2018). "Monte Carlo Methods for Volumetric Light Transport Simulation." SIGGRAPH Courses.

---

**Document Status:** Complete, ready for implementation
**Author:** Path Tracing Project (Etapa 05 planning)
**Next Action:** Implement in follow-up session
