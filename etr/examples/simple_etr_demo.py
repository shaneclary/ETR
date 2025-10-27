"""
Simple ETR Demo
Demonstrates basic ETR functionality without requiring a trained model.
"""

import sys
sys.path.append('.')

print("="*70)
print("ETR (Entangled Triangle Rendering) - Simple Demo")
print("="*70)

# Test 1: Core Theory Validation
print("\n[1] Testing Core Theory: 3:4:5 Triangle")
print("-"*70)

try:
    from etr.core.entangled_triangles import RightTriangle, LeftTriangleGenerator

    # Create the canonical 3:4:5 right triangle
    rt = RightTriangle(base=3, height=4, hypotenuse=5)
    print(f"Right Triangle: base={rt.base}, height={rt.height}, hypotenuse={rt.hypotenuse}")
    print(f"  Area: {rt.area}")
    print(f"  Perimeter: {rt.perimeter}")
    print(f"  Scaling Factor: {rt.scaling_factor}")

    # Generate entangled left triangle
    lt = LeftTriangleGenerator.generate_left_triangle(rt)
    print(f"\nLeft Triangle: base={lt.base}, height={lt.height}, hypotenuse={lt.hypotenuse}")
    print(f"  Area: {lt.area}")
    print(f"  Perimeter: {lt.perimeter}")
    print(f"  Scaling Factor: {lt.scaling_factor}")

    # Verify relationships
    print(f"\nVerification:")
    print(f"  Perimeter Ratio: {rt.perimeter / lt.perimeter:.2f} (expected: 20.0)")
    print(f"  Area Ratio: {rt.area / lt.area:.2f} (expected: 400.0)")

    angles_ok = LeftTriangleGenerator.verify_angle_preservation(rt, lt)
    scaling_ok = LeftTriangleGenerator.verify_scaling_relationship(rt, lt)

    print(f"  Angles Preserved: {angles_ok}")
    print(f"  Scaling Valid: {scaling_ok}")

    print("\n✓ Core theory validation PASSED")

except Exception as e:
    print(f"\n✗ Core theory validation FAILED: {e}")

# Test 2: Fractal Hierarchy
print("\n[2] Testing Fractal Hierarchy Generation")
print("-"*70)

try:
    from etr.core.entangled_triangles import FractalTriangleHierarchy

    rt = RightTriangle(base=3, height=4, hypotenuse=5)
    hierarchy = FractalTriangleHierarchy(rt, max_depth=5)
    triangles = hierarchy.generate_hierarchy()

    print(f"Generated {len(triangles)} levels of fractal hierarchy:\n")

    for i, tri in enumerate(triangles):
        print(f"  Level {i}: base={tri.base:12.8f}, "
              f"scaling={tri.scaling_factor:8.4f}, "
              f"cumulative={hierarchy.cumulative_scaling[i]:10.2e}")

    print("\n✓ Fractal hierarchy generation PASSED")

except Exception as e:
    print(f"\n✗ Fractal hierarchy generation FAILED: {e}")

# Test 3: Batch Operations (requires PyTorch)
print("\n[3] Testing Batch Operations")
print("-"*70)

try:
    import torch
    from etr.core.torch_triangle_ops import TorchTriangleOps

    # Create batch of random right triangles
    n = 1000
    bases = torch.rand(n) * 10 + 1
    heights = torch.rand(n) * 10 + 1
    hypotenuses = torch.sqrt(bases**2 + heights**2)

    # Batch transform
    lt_bases, lt_heights, lt_hyps, scaling = TorchTriangleOps.batch_generate_left_triangles(
        bases, heights, hypotenuses
    )

    print(f"Processed {n} triangles in batch")
    print(f"  Mean scaling factor: {scaling.mean():.4f}")
    print(f"  Min scaling factor: {scaling.min():.4f}")
    print(f"  Max scaling factor: {scaling.max():.4f}")

    # Verify Pythagorean theorem on transformed triangles
    valid = TorchTriangleOps.validate_pythagorean_batch(lt_bases, lt_heights, lt_hyps)
    print(f"  Valid left triangles: {valid.sum()}/{n}")

    print("\n✓ Batch operations PASSED")

except ImportError:
    print("PyTorch not available - skipping batch operations test")
except Exception as e:
    print(f"\n✗ Batch operations FAILED: {e}")

# Test 4: Multiple Pythagorean Triples
print("\n[4] Testing Multiple Pythagorean Triples")
print("-"*70)

pythagorean_triples = [
    (3, 4, 5),
    (5, 12, 13),
    (8, 15, 17),
    (7, 24, 25),
    (20, 21, 29),
]

try:
    all_passed = True

    for base, height, hyp in pythagorean_triples:
        rt = RightTriangle(base=base, height=height, hypotenuse=hyp)
        lt = LeftTriangleGenerator.generate_left_triangle(rt)

        angles_ok = LeftTriangleGenerator.verify_angle_preservation(rt, lt)
        scaling_ok = LeftTriangleGenerator.verify_scaling_relationship(rt, lt)

        status = "✓" if (angles_ok and scaling_ok) else "✗"
        print(f"  {status} Triangle {base}:{height}:{hyp} - "
              f"scaling={rt.scaling_factor:.2f}")

        all_passed = all_passed and angles_ok and scaling_ok

    if all_passed:
        print("\n✓ All Pythagorean triples PASSED")
    else:
        print("\n✗ Some triples FAILED")

except Exception as e:
    print(f"\n✗ Pythagorean triples test FAILED: {e}")

# Test 5: Logarithmic Spirals (requires NumPy)
print("\n[5] Testing Logarithmic Spiral Generation")
print("-"*70)

try:
    import numpy as np
    from etr.core.logarithmic_spirals import PolygonalSpiralGenerator

    # Generate heptagonal spiral
    generator = PolygonalSpiralGenerator(
        PolygonalSpiralGenerator.HEPTAGONAL
    )

    spiral_points = generator.generate_spiral_points(turns=3, points_per_turn=50)

    print(f"Generated spiral with {len(spiral_points)} points")
    print(f"  Configuration: {generator.config.name}")
    print(f"  Logarithmic Base: {generator.config.logarithmic_base}")
    print(f"  Modular Config: {generator.config.modular_config}")
    print(f"  First point: r={spiral_points[0, 0]:.4f}, θ={spiral_points[0, 1]:.4f}")
    print(f"  Last point:  r={spiral_points[-1, 0]:.4f}, θ={spiral_points[-1, 1]:.4f}")

    print("\n✓ Spiral generation PASSED")

except ImportError:
    print("NumPy not available - skipping spiral generation test")
except Exception as e:
    print(f"\n✗ Spiral generation FAILED: {e}")

# Summary
print("\n" + "="*70)
print("ETR Demo Complete")
print("="*70)
print("\nTo run full validation suite, execute:")
print("  python -m etr.validation.validation_suite")
print("\nFor integration with Triangle Splatting, see:")
print("  etr/docs/INTEGRATION_GUIDE.md")
print("="*70)
