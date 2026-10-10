"""
Comprehensive validation of ETR implementation.

Tests:
1. 3:4:5 canonical example
2. Batch processing correctness
3. Numerical stability
4. Fractal hierarchy
5. Angle preservation
6. Scaling relationships
"""

import math
from typing import Dict
import logging

from etr.core.entangled_triangles import (
    RightTriangle,
    LeftTriangleGenerator,
    FractalTriangleHierarchy,
    run_3_4_5_validation
)
from etr.core.thoth_geometry import thoth_triangle, run_thoth_validation

# Try to import optional dependencies
try:
    import torch
    from etr.core.torch_triangle_ops import TorchTriangleOps
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class ValidationSuite:
    """Complete validation test suite for ETR."""

    def __init__(self):
        self.results = {}
        self.logger = logging.getLogger(__name__)

    def run_all_tests(self) -> Dict:
        """Run complete validation suite."""
        print("="*80)
        print("ETR VALIDATION SUITE")
        print("="*80)

        tests = [
            ("Canonical 3:4:5", self.test_canonical_345),
            ("5:12:13 Triangle", self.test_5_12_13),
            ("Angle Preservation", self.test_angle_preservation),
            ("Scaling Relationships", self.test_scaling_relationships),
            ("Fractal Hierarchy", self.test_fractal_hierarchy),
            ("Numerical Stability", self.test_numerical_stability),
            ("Edge Cases", self.test_edge_cases),
            ("Thoth Triangle", self.test_thoth_triangle),
        ]

        if TORCH_AVAILABLE:
            tests.append(("Batch Processing", self.test_batch_processing))
            tests.append(("Thoth Shape Regularizer", self.test_thoth_shape_regularizer))
            tests.append(("Adapter on Renderer Triangles", self.test_adapter_on_renderer_triangles))

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            print(f"\n{'='*80}")
            print(f"TEST: {test_name}")
            print(f"{'='*80}")

            try:
                test_func()
                print(f"✓ {test_name} PASSED")
                self.results[test_name] = "PASSED"
                passed += 1
            except Exception as e:
                print(f"✗ {test_name} FAILED: {str(e)}")
                self.results[test_name] = f"FAILED: {str(e)}"
                failed += 1

        print(f"\n{'='*80}")
        print(f"VALIDATION SUMMARY: {passed} passed, {failed} failed")
        print(f"{'='*80}")

        return self.results

    def test_canonical_345(self):
        """Test 3:4:5 triangle transformation."""
        run_3_4_5_validation()

    def test_5_12_13(self):
        """Test 5:12:13 triangle (another Pythagorean triple)."""
        rt = RightTriangle(base=5, height=12, hypotenuse=13)
        lt = LeftTriangleGenerator.generate_left_triangle(rt)

        # Scaling should be 12 * 13 = 156
        assert abs(rt.scaling_factor - 156) < 1e-10

        # Left base should be 5/156
        expected_base = 5 / 156
        assert abs(lt.base - expected_base) < 1e-10

        # Verify relationships
        assert LeftTriangleGenerator.verify_angle_preservation(rt, lt)
        assert LeftTriangleGenerator.verify_scaling_relationship(rt, lt)

        print(f"✓ 5:12:13 transformation correct")
        print(f"  Scaling factor: {rt.scaling_factor}")
        print(f"  Left base: {lt.base:.10f}")

    def test_batch_processing(self):
        """Test GPU batch processing with TorchTriangleOps."""
        if not TORCH_AVAILABLE:
            print("Skipping batch processing test (PyTorch not available)")
            return

        n_triangles = 10000

        # Generate random right triangles
        heights = torch.rand(n_triangles) * 10 + 1  # [1, 11]
        bases = torch.rand(n_triangles) * 10 + 1
        hypotenuses = torch.sqrt(bases**2 + heights**2)

        # Batch transform
        lt_bases, lt_heights, lt_hyps, scaling = TorchTriangleOps.batch_generate_left_triangles(
            bases, heights, hypotenuses
        )

        # Verify some samples
        for i in [0, 100, 500, 1000, 5000, 9999]:
            rt = RightTriangle(
                base=bases[i].item(),
                height=heights[i].item(),
                hypotenuse=hypotenuses[i].item()
            )
            lt = LeftTriangleGenerator.generate_left_triangle(rt)

            assert abs(lt.base - lt_bases[i].item()) < 1e-6
            assert abs(lt.height - lt_heights[i].item()) < 1e-6
            assert abs(lt.hypotenuse - lt_hyps[i].item()) < 1e-6

        print(f"✓ Batch processing validated on {n_triangles} triangles")
        print(f"  Mean scaling factor: {scaling.mean().item():.4f}")

    def test_thoth_shape_regularizer(self):
        """Test the training-time pull towards the Thoth shape (utils.loss_utils.shape_regularizer)."""
        if not TORCH_AVAILABLE:
            print("Skipping shape regularizer test (PyTorch not available)")
            return

        from utils.loss_utils import shape_regularizer
        from etr.core.thoth_geometry import THOTH_SIDE_RATIOS

        torch.manual_seed(0)
        thoth = torch.tensor(thoth_triangle().unit_circumcircle_vertices(), dtype=torch.float64)
        rotations = torch.linalg.qr(torch.randn(64, 3, 3, dtype=torch.float64)).Q
        scales = torch.logspace(-4, 3, 64, dtype=torch.float64).view(-1, 1, 1)
        permutation = torch.tensor([2, 0, 1])
        thoth_batch = (thoth[permutation] @ rotations.transpose(1, 2)) * scales + torch.randn(64, 1, 3, dtype=torch.float64) * 5

        # Zero for any triangle similar to Thoth, whatever its scale, rotation, position or vertex order
        loss = shape_regularizer(thoth_batch, THOTH_SIDE_RATIOS)
        assert loss.shape == (64,) and loss.max() < 1e-20, f"Thoth triangles should score 0, got max {loss.max():.2e}"

        # 3:4:5 scores (0.6 - 0.5358)² + (0.8 - 0.8443)² = 0.00608; equilateral scores 2 × (1 - ratio)²
        rt_345 = torch.tensor([[[0.0, 0, 0], [3, 0, 0], [0, 4, 0]]], dtype=torch.float64)
        expected_345 = (0.6 - THOTH_SIDE_RATIOS[0]) ** 2 + (0.8 - THOTH_SIDE_RATIOS[1]) ** 2
        assert abs(shape_regularizer(rt_345, THOTH_SIDE_RATIOS).item() - expected_345) < 1e-12
        assert abs(shape_regularizer(rt_345 * 1000, THOTH_SIDE_RATIOS).item() - expected_345) < 1e-12, "not scale invariant"
        equilateral = torch.tensor([[[0.0, 0, 0], [1, 0, 0], [0.5, math.sqrt(3) / 2, 0]]], dtype=torch.float64)
        expected_equilateral = sum((1 - ratio) ** 2 for ratio in THOTH_SIDE_RATIOS)
        assert abs(shape_regularizer(equilateral, THOTH_SIDE_RATIOS).item() - expected_equilateral) < 1e-12

        # Gradient descent on the regularizer alone turns a 45-45-90 triangle into a Thoth triangle
        vertices = torch.tensor([[[0.0, 0, 1], [1, 0, 0], [0, 0, -1]]], dtype=torch.float64, requires_grad=True)
        optimizer = torch.optim.Adam([vertices], lr=0.01)
        start = shape_regularizer(vertices, THOTH_SIDE_RATIOS).item()
        for _ in range(500):
            optimizer.zero_grad()
            shape_regularizer(vertices, THOTH_SIDE_RATIOS).sum().backward()
            optimizer.step()
        end = shape_regularizer(vertices, THOTH_SIDE_RATIOS).item()
        assert end < start * 1e-4, f"regularizer should drive the shape to Thoth: {start:.3e} -> {end:.3e}"
        sides = sorted((vertices[0, i] - vertices[0, j]).norm().item() for i, j in ((0, 1), (1, 2), (2, 0)))
        angle = math.degrees(math.atan2(sides[1], sides[0]))
        assert abs(angle - 57.599323592) < 0.05, f"optimised triangle should have the 57.6° Thoth angle, got {angle:.4f}°"

        print(f"✓ Shape regularizer: 0 on Thoth triangles, 3:4:5 scores {expected_345:.5f}, "
              f"45-45-90 optimised to {angle:.3f}° ({start:.2e} -> {end:.2e})")

    def test_adapter_on_renderer_triangles(self):
        """Test that ETR recognises float32 Thoth init triangles at scene scale (the renderer's data)."""
        if not TORCH_AVAILABLE:
            print("Skipping adapter test (PyTorch not available)")
            return

        from etr.core.triangle_adapter import TriangleSplattingAdapter

        torch.manual_seed(1)
        n_triangles = 2000
        thoth = torch.tensor(thoth_triangle().unit_circumcircle_vertices())
        rotations = torch.linalg.qr(torch.randn(n_triangles, 3, 3)).Q
        centers = torch.randn(n_triangles, 1, 3) * 5          # scene-scale positions ...
        radii = torch.rand(n_triangles, 1, 1) * 0.5 + 0.01     # ... with small triangles, as create_from_pcd makes
        triangles_points = (thoth @ rotations.transpose(1, 2)) * radii + centers
        assert triangles_points.dtype == torch.float32

        etr_data = TriangleSplattingAdapter.batch_convert_to_etr_format({'triangles_points': triangles_points})
        assert etr_data['n_valid'] == n_triangles, f"only {etr_data['n_valid']}/{n_triangles} recognised as right triangles"

        # Shape survives float32: hypotenuse = 2r, logarithmic base c/h = 1.18438
        assert torch.allclose(etr_data['hypotenuses'], 2 * radii[:, 0, 0], rtol=1e-4)
        log_bases = TorchTriangleOps.compute_logarithmic_bases(etr_data['heights'], etr_data['hypotenuses'])
        thoth_log_base = thoth_triangle().logarithmic_base
        assert (log_bases - thoth_log_base).abs().max() < 2e-3, f"log base drift {(log_bases - thoth_log_base).abs().max():.2e}"

        # A clearly non-right triangle is still rejected
        skewed = triangles_points[:1].clone()
        skewed[0, 2] = skewed[0, 2] + 0.3 * (skewed[0, 1] - skewed[0, 0])
        assert TriangleSplattingAdapter.batch_convert_to_etr_format({'triangles_points': skewed})['n_valid'] == 0

        print(f"✓ Adapter recognised {etr_data['n_valid']}/{n_triangles} float32 Thoth triangles, "
              f"logarithmic base {log_bases.mean():.5f} (Thoth {thoth_log_base:.5f})")

    def test_angle_preservation(self):
        """Test that angles are preserved in all transformations."""
        test_triangles = [
            (3, 4, 5),
            (5, 12, 13),
            (8, 15, 17),
            (7, 24, 25),
            (20, 21, 29),
        ]

        for base, height, hyp in test_triangles:
            rt = RightTriangle(base=base, height=height, hypotenuse=hyp)
            lt = LeftTriangleGenerator.generate_left_triangle(rt)

            assert LeftTriangleGenerator.verify_angle_preservation(rt, lt)

        print(f"✓ Angle preservation verified for {len(test_triangles)} triangles")

    def test_scaling_relationships(self):
        """Test perimeter and area scaling."""
        test_triangles = [
            (3, 4, 5),
            (5, 12, 13),
            (8, 15, 17),
        ]

        for base, height, hyp in test_triangles:
            rt = RightTriangle(base=base, height=height, hypotenuse=hyp)
            lt = LeftTriangleGenerator.generate_left_triangle(rt)

            assert LeftTriangleGenerator.verify_scaling_relationship(rt, lt)

        print("✓ Scaling relationships verified")

    def test_fractal_hierarchy(self):
        """Test multi-level fractal generation."""
        rt = RightTriangle(base=3, height=4, hypotenuse=5)
        hierarchy = FractalTriangleHierarchy(rt, max_depth=10)
        triangles = hierarchy.generate_hierarchy()

        assert len(triangles) == 11  # 0 to 10 inclusive

        # Verify each level
        for i in range(1, len(triangles)):
            prev = triangles[i-1]
            curr = triangles[i]

            # Verify transformation
            expected_lt = LeftTriangleGenerator.generate_left_triangle(prev)
            assert abs(curr.base - expected_lt.base) < 1e-10
            assert abs(curr.height - expected_lt.height) < 1e-10

        print(f"✓ Fractal hierarchy of depth 10 validated")
        print(f"  Level 0 scaling: {triangles[0].scaling_factor:.2f}")
        print(f"  Level 10 scaling: {triangles[10].scaling_factor:.2e}")

    def test_numerical_stability(self):
        """Test numerical stability over deep recursion."""
        rt = RightTriangle(base=3, height=4, hypotenuse=5)

        # Test up to depth 15
        max_safe_depth = 15
        hierarchy = FractalTriangleHierarchy(rt, max_depth=max_safe_depth)
        triangles = hierarchy.generate_hierarchy()

        # Check all remain valid right triangles
        for i, tri in enumerate(triangles):
            # Should not raise ValueError
            a_sq = tri.base ** 2
            b_sq = tri.height ** 2
            c_sq = tri.hypotenuse ** 2

            error = abs(a_sq + b_sq - c_sq)
            assert error < 1e-6, f"Level {i} Pythagorean error: {error:.2e}"

        print(f"✓ Numerical stability maintained to depth {max_safe_depth}")

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        if not NUMPY_AVAILABLE:
            print("Skipping edge cases test (NumPy not available)")
            return

        import numpy as np

        # Test very small triangle
        rt_small = RightTriangle(base=1e-6, height=1e-6, hypotenuse=np.sqrt(2)*1e-6)
        lt_small = LeftTriangleGenerator.generate_left_triangle(rt_small)
        assert lt_small is not None

        # Test very large triangle
        rt_large = RightTriangle(base=1e6, height=1e6, hypotenuse=np.sqrt(2)*1e6)
        lt_large = LeftTriangleGenerator.generate_left_triangle(rt_large)
        assert lt_large is not None

        # Test invalid triangles (should raise errors)
        try:
            RightTriangle(base=3, height=4, hypotenuse=6)  # Not Pythagorean
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected

        print("✓ Edge cases handled correctly")

    def test_thoth_triangle(self):
        """Test Grant's 4.32 : 1/0.432 triangle through the ETR classes."""
        run_thoth_validation()

        # Renderer init layout: vertices on the unit circumcircle, hypotenuse as
        # the diameter (same convention as the default 45-45-90 init triangle)
        rt = thoth_triangle()
        v0, v1, v2 = rt.unit_circumcircle_vertices()
        for vertex in (v0, v1, v2):
            assert abs(math.dist(vertex, (0, 0, 0)) - 1) < 1e-12, f"Vertex {vertex} not on unit circle"
            assert vertex[2] == 0, f"Vertex {vertex} not in the xy-plane"
        assert math.dist(v0, v1) == 2, "Hypotenuse should be the diameter"
        assert abs(math.dist(v0, v2) - 2 * rt.base / rt.hypotenuse) < 1e-12, "v0-v2 should be the scaled base"
        assert abs(math.dist(v1, v2) - 2 * rt.height / rt.hypotenuse) < 1e-12, "v1-v2 should be the scaled height"
        leg_a = tuple(v0[i] - v2[i] for i in range(3))
        leg_b = tuple(v1[i] - v2[i] for i in range(3))
        assert abs(sum(leg_a[i] * leg_b[i] for i in range(3))) < 1e-12, "Right angle should be at v2"
        assert abs(math.degrees(math.atan2(v2[1], v2[0])) - 2 * 57.599323592) < 1e-6, "v2 should sit at 2 × 57.6°"

        # The 3:4:5 layout is the same construction
        v0, v1, v2 = RightTriangle(base=3, height=4, hypotenuse=5).unit_circumcircle_vertices()
        assert v2 == (-0.28, 0.96, 0.0), f"3:4:5 right-angle vertex should be (-0.28, 0.96, 0), got {v2}"

        print("✓ Thoth triangle validated, including the unit-circumcircle init layout")


if __name__ == "__main__":
    suite = ValidationSuite()
    results = suite.run_all_tests()

    # Save results
    try:
        import json
        with open("etr/validation/results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n✓ Results saved to etr/validation/results.json")
    except Exception as e:
        print(f"\nCould not save results: {e}")
