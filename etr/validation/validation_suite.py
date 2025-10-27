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
        ]

        if TORCH_AVAILABLE:
            tests.append(("Batch Processing", self.test_batch_processing))

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
