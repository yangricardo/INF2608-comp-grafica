# Comparative Visual Analysis: BSDF-only vs NEE vs MIS

**Reference Renders:** 2024-06-06, 256×256, SPP=16, depth=6, seed=42
**Paths:** 1.05M per mode
**Hardware:** macOS (Apple Silicon estimated)

---

## Visual Quality Comparison Framework

### Inspection Checklist

For each render, evaluate:

| Aspect                | Metric                        | Check                            |
| --------------------- | ----------------------------- | -------------------------------- |
| **Noise**             | Standard deviation            | Uniform? Clustered?              |
| **Fireflies**         | Outlier pixels                | Bright spikes rare/common?       |
| **Shadow definition** | Direct light boundary         | Sharp? Fuzzy? Correct occlusion? |
| **Color accuracy**    | Wall colors (red/green/white) | Saturated? Washed out?           |
| **Indirect light**    | Box shadows                   | Visible? Correct color cast?     |
| **Convergence**       | Overall evenness              | Smooth? Noisy bands?             |

---

## Expected Observations

### BSDF-only (`proj2_req1_lambert_basic_20260606_162024/render.png`)

**Characteristics:**

- ✅ Good texture on specular surfaces (low direct light variance)
- ⚠️ High variance in shadow regions (multi-bounce indirect only)
- ⚠️ Occasional fireflies (rare paths hitting small solid angle to light)
- ✅ Correct color (Lambertian BRDF)
- ⚠️ Uneven noise (more variance near boxes, less near light)

**Typical noise pattern:**

```
Ceiling/near-light:  ░░░░░░░░  (low noise)
Mid-walls:          ░▓▒▒░░░░  (medium variance)
Floor/shadows:      ▓▒▒▒▒▒▒▓  (high noise)
```

### NEE-only (`proj2_req2_nee_only_20260606_162251/render.png`)

**Characteristics:**

- ✅ Very low variance in well-lit areas (direct light guaranteed)
- ✅ Sharp shadows (NEE explicitly samples occlusion)
- ⚠️ Potential artifacts in indirect-only regions (Le suppressed at depth>1)
- ✅ Excellent shadow boundary definition
- ⚠️ Possible dark corners (no BSDF sampling for far-light contributions)

**Typical noise pattern:**

```
Ceiling/direct:     ░░░░░░░░  (very low noise)
Walls/lit:          ░░░░░░░▓  (smooth, few spikes)
Shadows/indirect:   ▒▒▒▒░░░░  (still lower than BSDF)
```

### MIS (`proj2_req3_mis_20260606_161743/render.png`)

**Characteristics:**

- ✅ **Balanced noise** — combines both strategies' strengths
- ✅ **Reduced fireflies** — power heuristic downweights high-variance samples
- ✅ **Sharp direct shadows** — NEE contribution
- ✅ **Smooth indirect** — BSDF contribution to specular/far regions
- ✅ **Uniform noise distribution** — power heuristic allocates variance optimally

**Typical noise pattern:**

```
Ceiling/direct:     ░░░░░░░░  (low, sharp)
Walls/lit:          ░░░░░░░░  (smooth)
Shadows/indirect:   ░░▒░░░░░  (reduced noise vs BSDF)
Overall:            Consistent throughout
```

---

## Quantitative Measurement Guide

### 1. Extract Render Data

```bash
# List all three renders
ls out/proj2/req{1,2,3}/ | grep "20260606_16"

# Example output:
# out/proj2/req1/proj2_req1_lambert_basic_20260606_162024/
# out/proj2/req2/proj2_req2_nee_only_20260606_162251/
# out/proj2/req3/proj2_req3_mis_20260606_161743/
```

### 2. Check Metadata

```bash
# View all three properties files
cat out/proj2/req1/proj2_req1_lambert_basic_20260606_162024/properties.json | jq .
cat out/proj2/req2/proj2_req2_nee_only_20260606_162251/properties.json | jq .
cat out/proj2/req3/proj2_req3_mis_20260606_161743/properties.json | jq .
```

Expected JSON fields:

```json
{
  "mode": "bsdf_only|nee_only|mis",
  "render_time_s": <float>,
  "throughput_paths_per_sec": <int>,
  "spp": 16,
  "resolution": "256x256",
  "total_paths": 1052224,
  "lights": 1
}
```

### 3. Visual Noise Analysis (Manual)

Open all three PNGs in image viewer:

```
Zoom 4×: Focus on shadow regions
├─ BSDF-only: Look for noise variation, occasional bright pixels
├─ NEE-only: Expect smoother shadows
└─ MIS: Should show intermediate smoothness
```

### 4. Pixel Variance Estimation

Sample a region and estimate standard deviation:

```python
import numpy as np
from PIL import Image

# Load renders
img_bsdf = np.array(Image.open('out/proj2/req1/.../render.png')) / 255.0
img_nee = np.array(Image.open('out/proj2/req2/.../render.png')) / 255.0
img_mis = np.array(Image.open('out/proj2/req3/.../render.png')) / 255.0

# Sample shadow region (e.g., floor near tall box, 50×50 px)
shadow_bsdf = img_bsdf[150:200, 100:150]
shadow_nee = img_nee[150:200, 100:150]
shadow_mis = img_mis[150:200, 100:150]

# Compute standard deviation per channel
for name, img in [('BSDF', shadow_bsdf), ('NEE', shadow_nee), ('MIS', shadow_mis)]:
    std_rgb = np.std(img, axis=(0, 1))
    mean_std = np.mean(std_rgb)
    print(f"{name}: σ={mean_std:.4f}")
```

Expected result (lower = better):

```
BSDF: σ=0.0850  (highest variance)
NEE:  σ=0.0620  (lower)
MIS:  σ=0.0540  (optimal)
```

---

## Known Rendering Artifacts

### Scene-Specific Issues

1. **Tall box shadow (floor):** Often noisiest region in BSDF-only
   - NEE handles this well (direct light sampling)
   - MIS balances both

2. **Ceiling corner (far from light):** May be dark in NEE
   - BSDF-only recovers via multi-bounce indirects
   - MIS combines both

3. **Wall color saturation:** Should be identical in all modes
   - If significantly different → check gamut/tone mapping

### Convergence Artifacts (Expected at SPP=16)

- ✅ Normal: Some noise in shadows
- ✅ Normal: Occasional bright pixels (fireflies)
- ✅ Normal: Directional streaks (path tracing)
- ❌ Abnormal: Completely black regions (BVH bug)
- ❌ Abnormal: Color banding (16-bit overflow)

---

## Comparative Scoring (0-10 scale)

### Reference Scoring Frame

| Score | Interpretation                          |
| ----- | --------------------------------------- |
| 9-10  | Production quality, minimal noise       |
| 7-8   | Good quality, expected noise for SPP    |
| 5-6   | Acceptable, but visibly noisy           |
| 3-4   | Poor quality, heavy noise               |
| 0-2   | Broken (completely black, wrong colors) |

### Expected Scores

```
                   Smoothness  Sharpness  Color   Overall
BSDF-only              5          7       10        7
NEE-only               7          9        9        8
MIS                    8          8       10        9
```

---

## Troubleshooting Visual Issues

### Issue: All three modes look identical

**Possible causes:**

- Renders not from same scene (check `properties.md`)
- Display gamma mismatch (expect slight gamma in PNGs)
- Zoom level too low (visual differences subtle at SPP=16)

**Solution:** Compare at 2× zoom, focus on shadow regions

### Issue: NEE-only is darker than others

**Possible causes:**

- Le suppression too aggressive (depth > 1)
- Scene has no emissive surfaces (only lights)

**Check:** `properties.json` → `"lights": 1`

### Issue: MIS is noisier than NEE

**Possible causes:**

- Power heuristic weight calculation error
- BSDF PDF incorrect (zero-division in pdf_light_for_bsdf?)

**Debug:**

```python
# In path_tracer.py, add temporary logging:
if self.mode == 'mis':
    print(f"w_nee={w_nee:.3f}, w_bsdf={w_bsdf:.3f}")
```

Expected: weights near 0.5 on average (equal strategy strength)

---

## Next Steps

### For This Session

1. [ ] Load all three PNGs side-by-side
2. [ ] Zoom into shadow regions (floor near tall box)
3. [ ] Record qualitative observations
4. [ ] Run pixel variance script (if image processing available)
5. [ ] Update this document with findings

### For Future Sessions

- **Etapa 05 (Russian Roulette):** Compare variance reduction with min_depth
- **Etapa 06+ (Advanced):** Mesh lights, dielectrics (new strategies to combine)
- **Final Report:** Include rendered images + noise analysis plots

---

**Guide Status:** Complete, awaiting visual inspection
**Author:** Path Tracing Project (Proj 2, Etapa 04)
