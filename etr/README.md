# ETR: Entangled Triangle Rendering

Implementation of Robert Edward Grant's Entangled Left Triangle theory applied to Triangle Splatting for 3D radiance field rendering.

## Theory Overview

Every right triangle generates an "entangled left triangle" through inverse scaling:

### Core Transformation

Given a right triangle with dimensions (base, height, hypotenuse), the entangled left triangle is generated via:

- **Scaling Factor** = Height × Hypotenuse
- **LT_Height** = 1 / RT_Hypotenuse
- **LT_Hypotenuse** = 1 / RT_Height
- **LT_Base** = RT_Base / (RT_Height × RT_Hypotenuse)  [non-reciprocal]

### Key Properties

1. **Identical Angles**: The left triangle preserves all angular relationships
2. **Involution**: applying the transformation twice returns the original, so right and left form a period-2 pair
3. **Logarithmic Spirals**: Natural geometric coherence for spiral generation
4. **Scaling Law**: Area scales by (scaling_factor)², perimeter by scaling_factor

### Example: The Canonical 3:4:5 Triangle

```
Right Triangle:  base=3, height=4, hypotenuse=5
Scaling Factor:  4 × 5 = 20
Left Triangle:   base=0.15, height=0.2, hypotenuse=0.25

Verification:
- Perimeter Ratio: 12 / 0.6 = 20 ✓
- Area Ratio: 6 / 0.015 = 400 = 20² ✓
- Angles: Identical ✓
```

### Example: The Thoth Triangle (4.32 : 1/0.432)

From Grant's #ThothConstant post (Grant calls 432 the Thoth Constant). The triangle is defined by hypotenuse × base = 10.

```
Right Triangle:  base=1/0.432=2.3148148148, height=3.6474693108, hypotenuse=4.32
Scaling Factor:  3.6474693108 × 4.32 = 15.7570674226
Left Triangle:   base=0.1469064486, height=1/4.32=0.2314814815, hypotenuse=0.2741626906

Entanglement: left height = 1/hypotenuse = right base / 10 (same digits) ✓
```

What holds exactly and what only approximately (checked at 40 digits):

| Equation from the post | Status |
|---|---|
| 4.32 × (1/0.432) = 10 | Exact (definition) |
| (1/φ² + 1)⁴ = 25/φ⁴ = 125 − 75φ | Exact identity |
| height ≈ (1/φ² + 1)⁴ | Approximate: 3.6474693 vs 3.6474508, 5.06 ppm. Provably unequal, so 4.32, 1/0.432 and 25/φ⁴ cannot all be sides of one right triangle (Pythagorean residual −1.35e-4) |
| √10 × (√10/10) = 1 (Fractal Root; the post writes 3.16227766 × 0.316227766) | Exact for √10 (the post's truncated decimals multiply to 1 − 1.06e-10); hypotenuse √10 is the degenerate member (base = hypotenuse, height 0), so the family needs hypotenuse > √10 |
| 4 5/16, 3 10/16, 2 5/16 | Nearest-sixteenth roundings of the three sides |
| 432² = 186,624 ≈ speed of light | Approximate: 186,282.397 mi/s, +0.18%, and only in miles |

```python
from etr.core.thoth_geometry import thoth_triangle, run_thoth_validation

rt = thoth_triangle()        # hypotenuse 4.32; thoth_triangle(c) for other members
run_thoth_validation()       # asserts every row above through ETR's classes
```

## Directory Structure

```
etr/
├── core/                   # Core ETR implementation
│   ├── entangled_triangles.py    # Main theory implementation
│   ├── torch_triangle_ops.py     # GPU-accelerated operations
│   ├── logarithmic_spirals.py    # Spiral generation
│   ├── thoth_geometry.py         # Thoth triangle (4.32 : 1/0.432)
│   └── triangle_adapter.py       # Triangle Splatting integration
├── validation/             # Test suite
│   └── validation_suite.py
├── visualization/          # Rendering and comparison tools
├── utils/                  # Utility functions
└── docs/                   # Additional documentation
```

## Installation

### Prerequisites

ETR is integrated into the Triangle Splatting codebase. Ensure Triangle Splatting is properly set up first:

```bash
# Install Triangle Splatting dependencies
micromamba create -f requirements.yaml
micromamba activate triangle_splatting

# Compile CUDA kernels
bash compile.sh
cd submodules/simple-knn
pip install .
cd ../..
```

### ETR Requirements

ETR requires:
- Python 3.11+
- PyTorch 2.4.0+ with CUDA
- NumPy (included in Triangle Splatting environment)

## Usage

### 1. Basic Validation

Verify the ETR implementation is working correctly:

```python
from etr.core.entangled_triangles import run_3_4_5_validation

# Run canonical 3:4:5 triangle validation
run_3_4_5_validation()
```

Expected output:
```
VALIDATING 3:4:5 CANONICAL EXAMPLE
✓ Dimension transformation correct
✓ Scaling factor: 20.0
✓ Perimeter ratio: 20.0
✓ Area ratio: 400.0 (20²)
✓ Angles preserved
✓ Scaling relationships valid
3:4:5 VALIDATION PASSED ✓
```

### 2. The Entangled Pair

The transformation is an involution, so iterating it alternates between the two triangles of a pair; there is no deeper hierarchy. `FractalTriangleHierarchy` remains as an alias.

```python
from etr.core.entangled_triangles import RightTriangle, EntangledTrianglePair

pair = EntangledTrianglePair(RightTriangle(base=3, height=4, hypotenuse=5))
pair.right, pair.left        # (3, 4, 5) and (0.15, 0.2, 0.25)
pair.scaling_factor          # 20: length ratio right / left, in the triangle's own units
pair.generate_hierarchy(4)   # [right, left, right, left, right]; cumulative_scaling = [1, 20, 1, 20, 1]
```

The scaling factor is height × hypotenuse in the triangle's units, so the left triangle is smaller only when that product exceeds 1. A renderer triangle of circumradius 0.1 has a product of about 0.03, and its left triangle is 30× larger: the pair carries no level-of-detail meaning at scene scale.

### 3. Batch Processing with PyTorch

Process thousands of triangles efficiently on GPU:

```python
import torch
from etr.core.torch_triangle_ops import TorchTriangleOps

# Generate batch of right triangles
n_triangles = 10000
heights = torch.rand(n_triangles, device='cuda') * 10 + 1
bases = torch.rand(n_triangles, device='cuda') * 10 + 1
hypotenuses = torch.sqrt(bases**2 + heights**2)

# Batch transform to left triangles
lt_bases, lt_heights, lt_hyps, scaling_factors = \
    TorchTriangleOps.batch_generate_left_triangles(bases, heights, hypotenuses)

print(f"Processed {n_triangles} triangles")
print(f"Mean scaling factor: {scaling_factors.mean():.4f}")
```

### 4. Integration with Triangle Splatting

Apply ETR transformations to a trained Triangle Splatting model:

```python
from scene.triangle_model import TriangleModel
from etr.core.triangle_adapter import TriangleSplattingAdapter

# Load trained model
model = TriangleModel(sh_degree=3)
model.load("path/to/trained/model")

# Apply ETR transformation
etr_data = TriangleSplattingAdapter.apply_etr_to_triangle_model(model)

print(f"Total triangles: {len(model.get_triangles_points)}")
print(f"Right triangles found: {etr_data['n_valid']}")
print(f"Mean scaling factor: {etr_data['scaling_factors'][etr_data['valid_mask']].mean():.2f}")
print(f"Mean logarithmic base: {etr_data['logarithmic_bases'][etr_data['valid_mask']].mean():.4f}")
```

### 5. Run Complete Validation Suite

Test all ETR functionality:

```python
from etr.validation.validation_suite import ValidationSuite

suite = ValidationSuite()
results = suite.run_all_tests()

# Results are saved to etr/validation/results.json
```

### 6. Generate Logarithmic Spirals

Create natural spirals using triangle fractals:

```python
from etr.core.logarithmic_spirals import PolygonalSpiralGenerator

# Use pre-configured heptagonal spiral
generator = PolygonalSpiralGenerator(
    PolygonalSpiralGenerator.HEPTAGONAL
)

# Generate spiral points
spiral_points = generator.generate_cartesian_spiral(turns=4, points_per_turn=100)

# Or create 3D mesh
vertices, faces = generator.generate_3d_spiral_mesh(
    base_triangle=(3, 4, 5),
    turns=5
)
```

## Training with ETR

ETR enters the renderer at initialisation. Triangle Splatting starts every triangle as the three Fibonacci directions on the unit sphere (a 45-45-90 right triangle, hypotenuse as the diameter), scaled by `triangle_size` × nearest-neighbour distance and randomly rotated. With `--init_shape thoth` the seed is Grant's Thoth triangle on the same unit circumcircle (`RightTriangle.unit_circumcircle_vertices()`), so every triangle begins with the 57.6° / 32.4° / 90° proportions.

```bash
python train.py -s <scene_path> -m <output_path> --init_shape thoth
# equivalently
python scripts/train_with_etr.py --scene <scene_path> --output <output_path> --use-etr
```

Training then moves the vertices freely. Midpoint splitting during densification keeps the shape (four similar copies at half scale); cloning adds in-plane noise and image gradients reshape triangles. To keep pulling shapes back towards the Thoth proportions, set `--lambda_thoth` (default 0): a loss on each triangle's two shorter sides as fractions of its longest, zero exactly on Thoth-similar triangles (`utils.loss_utils.shape_regularizer`). Any non-zero weight trades image fidelity for shape; measure PSNR/SSIM/LPIPS against the default before recommending a value. At equal circumradius the Thoth triangle has 9.5% less area than the 45-45-90 one; `--triangle_size 2.34` matches the default's initial area.

## Rendering

`render.py` renders whatever a trained model holds, so a model trained with `--init_shape thoth` renders its Thoth-seeded triangles. ETR statistics come from the adapter, not from `render.py`:

```python
etr_data = TriangleSplattingAdapter.apply_etr_to_triangle_model(model)
ETRMetrics.log_statistics(ETRMetrics.compute_statistics(etr_data))
```

The adapter accepts a right angle to |cos| ≤ 1e-4 (0.006°, above the float32 rounding of the renderer's own init at scene scale), labels the longer leg as the height (Grant's convention: 3:4:5 has height 4, the Thoth triangle 3.647) and derives the hypotenuse from the legs. A freshly initialised Thoth model reports 100% right triangles with logarithmic base 1.18438.

## Theory References

### Robert Edward Grant's Discovery

The Entangled Left Triangle theory was discovered by Robert Edward Grant on June 30, 2021. Key publications:

- **Main Theory**: Scaling law through Height × Hypotenuse multiplication
- **Logarithmic Spirals**: arXiv paper 2111.02895 - Polygonal spiral generation using right triangle fractals
- **Applications**: Natural phenomena modeling (galaxies, hurricanes, nautilus shells)

### Mathematical Foundations

For any right triangle satisfying a² + b² = c²:

1. **Scaling Factor**: S = b × c (Height × Hypotenuse)
2. **Left Triangle Generation**:
   - l_a = a / S
   - l_b = 1 / c
   - l_c = 1 / b
3. **Verification**: l_a² + l_b² = l_c² (Pythagorean theorem preserved)
4. **Angular Preservation**: All angles remain identical
5. **Perimeter Scaling**: P_right / P_left = S
6. **Area Scaling**: A_right / A_left = S²

## Performance Considerations

- **CPU Operations**: Suitable for individual triangle transformations
- **GPU Batch Operations**: Recommended for >1000 triangles
- **Memory Usage**: Minimal overhead per triangle (3 float32 values)
- **Numerical Stability**: Tested over 15 iterations of the transformation (period 2)

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Ensure you're in the triangle-splatting root directory
cd /path/to/triangle-splatting

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### CUDA Out of Memory

For very large scenes:

```python
# Process in smaller batches
chunk_size = 5000
for i in range(0, n_triangles, chunk_size):
    chunk_etr_data = process_chunk(triangles[i:i+chunk_size])
```

### Non-Right Triangles

Triangle Splatting may contain non-right triangles. ETR handles this gracefully:

```python
etr_data = adapter.batch_convert_to_etr_format(triangles)
# Check etr_data['valid_mask'] to see which are right triangles
# Only valid right triangles are transformed
```

## Citation

If you use ETR in your research, please cite:

```bibtex
@misc{etr2025,
  title={ETR: Entangled Triangle Rendering},
  author={[Implementation Team]},
  note={Implementation of Robert Edward Grant's Entangled Left Triangle Theory},
  year={2025}
}

@article{Held2025Triangle,
  title={Triangle Splatting for Real-Time Radiance Field Rendering},
  author={Held, Jan and Vandeghen, Renaud and Deliege, Adrien and Hamdi, Abdullah and Cioppa, Anthony and Giancola, Silvio and Vedaldi, Andrea and Ghanem, Bernard and Tagliasacchi, Andrea and Van Droogenbroeck, Marc},
  journal={arXiv},
  year={2025}
}

@article{Grant2021Entangled,
  title={Entangled Left Triangle Discovery},
  author={Grant, Robert Edward},
  year={2021},
  note={Discovery date: June 30, 2021}
}
```

## License

ETR follows the same license as Triangle Splatting (see LICENSE.md and LICENSE_GS.md in the repository root).

## Acknowledgments

- **Robert Edward Grant** for the Entangled Left Triangle theory
- **Triangle Splatting Team** (Held et al.) for the base rendering framework
- **3D Gaussian Splatting** for the foundational work

## Contact

For questions about ETR implementation:
- Open an issue in the repository
- Refer to Triangle Splatting documentation for base framework questions

For questions about the underlying theory:
- Visit [Robert Edward Grant's website](https://robertedwardgrant.com/)

---

**Status**: v0.1.0 - Initial implementation complete
**Last Updated**: 2025
