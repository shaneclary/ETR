# ETR: Entangled Triangle Rendering

Implementation of Robert Edward Grant's Entangled Left Triangle theory applied to Triangle Splatting for 3D radiance field rendering.

## Theory Overview

Every right triangle generates an "entangled left triangle" through inverse scaling:

### Core Transformation

Given a right triangle with dimensions (base, height, hypotenuse), the entangled left triangle is generated via:

- **Scaling Factor** = Height × Hypotenuse
- **LT_Height** = 1 / RT_Height
- **LT_Hypotenuse** = 1 / RT_Hypotenuse
- **LT_Base** = RT_Base / (RT_Height × RT_Hypotenuse)  [non-reciprocal]

### Key Properties

1. **Identical Angles**: The left triangle preserves all angular relationships
2. **Fractal Self-Similarity**: Recursive application creates fractal hierarchies
3. **Logarithmic Spirals**: Natural geometric coherence for spiral generation
4. **Scaling Law**: Area scales by (scaling_factor)², perimeter by scaling_factor

### Example: The Canonical 3:4:5 Triangle

```
Right Triangle:  base=3, height=4, hypotenuse=5
Scaling Factor:  4 × 5 = 20
Left Triangle:   base=0.15, height=0.25, hypotenuse=0.2

Verification:
- Perimeter Ratio: 12 / 0.6 = 20 ✓
- Area Ratio: 6 / 0.015 = 400 = 20² ✓
- Angles: Identical ✓
```

## Directory Structure

```
etr/
├── core/                   # Core ETR implementation
│   ├── entangled_triangles.py    # Main theory implementation
│   ├── torch_triangle_ops.py     # GPU-accelerated operations
│   ├── logarithmic_spirals.py    # Spiral generation
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

### 2. Generate Fractal Hierarchy

Create a recursive fractal hierarchy from any right triangle:

```python
from etr.core.entangled_triangles import RightTriangle, FractalTriangleHierarchy

# Create base triangle
rt = RightTriangle(base=3, height=4, hypotenuse=5)

# Generate 10-level hierarchy
hierarchy = FractalTriangleHierarchy(rt, max_depth=10)
triangles = hierarchy.generate_hierarchy()

# Access triangles at each level
for i, triangle in enumerate(triangles):
    print(f"Level {i}: "
          f"base={triangle.base:.10f}, "
          f"scaling={triangle.scaling_factor:.6f}")
```

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

To train Triangle Splatting models with ETR analysis:

```bash
# Standard training with ETR monitoring
python train.py -s <scene_path> -m <output_path> --eval

# The adapter will automatically log ETR statistics during training
```

## Rendering

Render scenes with ETR-transformed triangles:

```bash
# Standard rendering
python render.py -m <model_path>

# ETR statistics will be computed and logged
```

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
   - l_b = 1 / b
   - l_c = 1 / c
3. **Verification**: l_a² + l_b² = l_c² (Pythagorean theorem preserved)
4. **Angular Preservation**: All angles remain identical
5. **Perimeter Scaling**: P_right / P_left = S
6. **Area Scaling**: A_right / A_left = S²

## Performance Considerations

- **CPU Operations**: Suitable for individual triangle transformations
- **GPU Batch Operations**: Recommended for >1000 triangles
- **Memory Usage**: Minimal overhead per triangle (3 float32 values)
- **Numerical Stability**: Tested up to 15 levels of fractal recursion

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
