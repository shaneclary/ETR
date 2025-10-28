"""
Entangled Triangle Rendering - Core Theory Implementation
Based on Robert Edward Grant's discovery (June 30, 2021)

Core Principle: Every right triangle generates an "entangled left triangle"
via inverse scaling through Height × Hypotenuse multiplication.
"""

import numpy as np
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RightTriangle:
    """
    Right triangle representation with full geometric properties.

    Convention:
    - base (a): side opposite to right angle
    - height (b): perpendicular side
    - hypotenuse (c): longest side
    - All satisfy: a² + b² = c²
    """
    base: float
    height: float
    hypotenuse: float

    # Cached computed values
    scaling_factor: Optional[float] = None
    logarithmic_base: Optional[float] = None
    area: Optional[float] = None
    perimeter: Optional[float] = None
    inradius: Optional[float] = None
    circumradius: Optional[float] = None

    def __post_init__(self):
        """Validate Pythagorean relationship and compute cached values."""
        self._validate()
        self._compute_properties()

    def _validate(self, epsilon: float = 1e-10):
        """Verify this is a valid right triangle."""
        if self.height <= 0 or self.hypotenuse <= 0:
            raise ValueError(f"Height and hypotenuse must be positive: h={self.height}, c={self.hypotenuse}")

        # Check Pythagorean theorem
        expected_hyp_sq = self.base**2 + self.height**2
        actual_hyp_sq = self.hypotenuse**2

        if abs(expected_hyp_sq - actual_hyp_sq) > epsilon:
            raise ValueError(
                f"Triangle violates Pythagorean theorem: "
                f"a²+b²={expected_hyp_sq:.10f}, c²={actual_hyp_sq:.10f}, "
                f"difference={abs(expected_hyp_sq - actual_hyp_sq):.2e}"
            )

    def _compute_properties(self):
        """Compute all geometric properties."""
        # Grant's scaling factor (THE FUNDAMENTAL RELATIONSHIP)
        self.scaling_factor = self.height * self.hypotenuse

        # Logarithmic base (Hypotenuse/Height ratio)
        self.logarithmic_base = self.hypotenuse / self.height

        # Standard geometric properties
        self.area = 0.5 * self.base * self.height
        self.perimeter = self.base + self.height + self.hypotenuse
        self.inradius = (self.base + self.height - self.hypotenuse) / 2.0
        self.circumradius = self.hypotenuse / 2.0

    def get_angles_radians(self) -> Tuple[float, float, float]:
        """Return (angle_at_base, angle_at_height, right_angle)."""
        import math
        angle_base = math.atan2(self.height, self.base)
        angle_height = math.atan2(self.base, self.height)
        return (angle_base, angle_height, math.pi/2)

    def to_dict(self) -> Dict:
        """Export all properties as dictionary."""
        return {
            'dimensions': {
                'base': self.base,
                'height': self.height,
                'hypotenuse': self.hypotenuse
            },
            'properties': {
                'scaling_factor': self.scaling_factor,
                'logarithmic_base': self.logarithmic_base,
                'area': self.area,
                'perimeter': self.perimeter,
                'inradius': self.inradius,
                'circumradius': self.circumradius
            }
        }


class LeftTriangleGenerator:
    """
    Generate entangled left triangles from right triangles.

    Implements Grant's transformation:
    - LT_Height = 1 / RT_Height
    - LT_Hypotenuse = 1 / RT_Hypotenuse
    - LT_Base = RT_Base / (RT_Height × RT_Hypotenuse)  [NON-RECIPROCAL]
    """

    @staticmethod
    def generate_left_triangle(rt: RightTriangle) -> RightTriangle:
        """
        Transform right triangle to its entangled left triangle.

        Args:
            rt: Right triangle to transform

        Returns:
            Left triangle with identical angles but inverse scaling
        """
        # Apply Grant's formulas
        # Note: The transformation swaps height and hypotenuse roles
        lt_height = 1.0 / rt.hypotenuse  # Height becomes reciprocal of hypotenuse
        lt_hypotenuse = 1.0 / rt.height  # Hypotenuse becomes reciprocal of height
        lt_base = rt.base / rt.scaling_factor  # Non-reciprocal!

        # Create left triangle (validation happens automatically)
        left_triangle = RightTriangle(
            base=lt_base,
            height=lt_height,
            hypotenuse=lt_hypotenuse
        )

        logger.debug(
            f"Generated left triangle: RT({rt.base:.4f}, {rt.height:.4f}, {rt.hypotenuse:.4f}) -> "
            f"LT({lt_base:.6f}, {lt_height:.6f}, {lt_hypotenuse:.6f}), "
            f"scaling={rt.scaling_factor:.2f}"
        )

        return left_triangle

    @staticmethod
    def verify_angle_preservation(rt: RightTriangle, lt: RightTriangle,
                                   epsilon: float = 1e-8) -> bool:
        """Verify that angles are preserved between right and left triangles."""
        rt_angles = rt.get_angles_radians()
        lt_angles = lt.get_angles_radians()

        for i, (rt_ang, lt_ang) in enumerate(zip(rt_angles, lt_angles)):
            if abs(rt_ang - lt_ang) > epsilon:
                logger.warning(
                    f"Angle {i} mismatch: RT={np.degrees(rt_ang):.6f}°, "
                    f"LT={np.degrees(lt_ang):.6f}°, diff={np.degrees(abs(rt_ang - lt_ang)):.2e}°"
                )
                return False

        return True

    @staticmethod
    def verify_scaling_relationship(rt: RightTriangle, lt: RightTriangle,
                                    epsilon: float = 1e-8) -> bool:
        """Verify perimeter and area scaling relationships."""
        # Perimeter should scale by scaling_factor
        expected_lt_perimeter = rt.perimeter / rt.scaling_factor
        if abs(lt.perimeter - expected_lt_perimeter) > epsilon:
            logger.warning(
                f"Perimeter scaling mismatch: expected={expected_lt_perimeter:.6f}, "
                f"actual={lt.perimeter:.6f}"
            )
            return False

        # Area should scale by scaling_factor²
        expected_lt_area = rt.area / (rt.scaling_factor ** 2)
        if abs(lt.area - expected_lt_area) > epsilon:
            logger.warning(
                f"Area scaling mismatch: expected={expected_lt_area:.10f}, "
                f"actual={lt.area:.10f}"
            )
            return False

        return True


class FractalTriangleHierarchy:
    """
    Generate recursive fractal hierarchies of entangled triangles.

    Each level applies the left triangle transformation, creating
    progressively smaller triangles with preserved angular relationships.
    """

    def __init__(self, base_triangle: RightTriangle, max_depth: int = 10):
        """
        Initialize fractal hierarchy.

        Args:
            base_triangle: Starting right triangle
            max_depth: Maximum recursion depth
        """
        self.base_triangle = base_triangle
        self.max_depth = max_depth
        self.hierarchy: List[RightTriangle] = []
        self.cumulative_scaling: List[float] = []

    def generate_hierarchy(self, depth: Optional[int] = None) -> List[RightTriangle]:
        """
        Generate complete fractal hierarchy.

        Args:
            depth: Override max_depth if provided

        Returns:
            List of triangles from level 0 (base) to depth
        """
        if depth is None:
            depth = self.max_depth

        self.hierarchy = [self.base_triangle]
        self.cumulative_scaling = [self.base_triangle.scaling_factor]

        current = self.base_triangle

        for level in range(1, depth + 1):
            # Generate next left triangle
            next_triangle = LeftTriangleGenerator.generate_left_triangle(current)

            # Compute cumulative scaling
            cumulative = self.cumulative_scaling[-1] * next_triangle.scaling_factor

            self.hierarchy.append(next_triangle)
            self.cumulative_scaling.append(cumulative)

            current = next_triangle

            logger.info(
                f"Level {level}: base={current.base:.10f}, "
                f"scaling={current.scaling_factor:.6f}, "
                f"cumulative={cumulative:.2e}"
            )

        return self.hierarchy

    def get_lod_triangle(self, distance: float, screen_threshold: float = 0.01) -> RightTriangle:
        """
        Select appropriate triangle level based on distance (LOD).

        Args:
            distance: Distance from camera
            screen_threshold: Minimum screen-space size (0-1)

        Returns:
            Triangle at appropriate detail level
        """
        if not self.hierarchy:
            self.generate_hierarchy()

        for triangle in self.hierarchy:
            projected_size = triangle.base / distance
            if projected_size >= screen_threshold:
                return triangle

        # Return smallest triangle if all are too small
        return self.hierarchy[-1]


# Validation and Testing
def run_3_4_5_validation():
    """
    Validate the canonical 3:4:5 right triangle transformation.

    Expected results:
    - Left triangle: 0.15:0.2:0.25
    - Scaling factor: 20
    - Perimeter ratio: 12 / 0.6 = 20
    - Area ratio: 6 / 0.015 = 400 = 20²
    """
    print("="*70)
    print("VALIDATING 3:4:5 CANONICAL EXAMPLE")
    print("="*70)

    # Create right triangle
    rt = RightTriangle(base=3, height=4, hypotenuse=5)
    print(f"\nRight Triangle: {rt.to_dict()}")

    # Generate left triangle
    lt = LeftTriangleGenerator.generate_left_triangle(rt)
    print(f"\nLeft Triangle: {lt.to_dict()}")

    # Verify results
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)

    # Check dimensions
    assert abs(lt.base - 0.15) < 1e-10, f"Left base should be 0.15, got {lt.base}"
    assert abs(lt.height - 0.25) < 1e-10, f"Left height should be 0.25, got {lt.height}"
    assert abs(lt.hypotenuse - 0.2) < 1e-10, f"Left hypotenuse should be 0.2, got {lt.hypotenuse}"
    print("✓ Dimension transformation correct")

    # Check scaling factor
    assert abs(rt.scaling_factor - 20) < 1e-10, f"Scaling should be 20, got {rt.scaling_factor}"
    print(f"✓ Scaling factor: {rt.scaling_factor}")

    # Check perimeter ratio
    perimeter_ratio = rt.perimeter / lt.perimeter
    assert abs(perimeter_ratio - 20) < 1e-10, f"Perimeter ratio should be 20, got {perimeter_ratio}"
    print(f"✓ Perimeter ratio: {perimeter_ratio}")

    # Check area ratio
    area_ratio = rt.area / lt.area
    assert abs(area_ratio - 400) < 1e-10, f"Area ratio should be 400, got {area_ratio}"
    print(f"✓ Area ratio: {area_ratio} (20²)")

    # Verify angle preservation
    angles_preserved = LeftTriangleGenerator.verify_angle_preservation(rt, lt)
    assert angles_preserved, "Angles not preserved!"
    print("✓ Angles preserved")

    # Verify scaling relationships
    scaling_valid = LeftTriangleGenerator.verify_scaling_relationship(rt, lt)
    assert scaling_valid, "Scaling relationships invalid!"
    print("✓ Scaling relationships valid")

    print("\n" + "="*70)
    print("3:4:5 VALIDATION PASSED ✓")
    print("="*70)


if __name__ == "__main__":
    # Run validation
    run_3_4_5_validation()

    # Test fractal hierarchy
    print("\n\nGENERATING FRACTAL HIERARCHY")
    print("="*70)
    rt = RightTriangle(base=3, height=4, hypotenuse=5)
    hierarchy = FractalTriangleHierarchy(rt, max_depth=5)
    triangles = hierarchy.generate_hierarchy()

    for i, tri in enumerate(triangles):
        print(f"Level {i}: base={tri.base:.10f}, scaling={tri.scaling_factor:.6f}")
