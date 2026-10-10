"""
Grant's 4.32 triangle (#ThothConstant post) expressed in ETR geometry.

The triangle is defined by hypotenuse × base = 10: hypotenuse 4.32,
base 1/0.432 = 10/4.32, height √(4.32² − (1/0.432)²) ≈ 3.6474693.

Exact (definitions and identities):
- hypotenuse × base = 10
- ETR left-triangle height = 1/hypotenuse = base/10 (same digits as the base)
- (1/φ² + 1)⁴ = 25/φ⁴ = 125 − 75φ ≈ 3.6474508
- √10 × (√10/10) = 1; hypotenuse √10 is the degenerate member (base = √10, height 0)

Approximate (numerical coincidences, checked at 40 digits):
- height ≈ 25/φ⁴, off by 5.06 ppm; 4.32 rounds the φ-exact hypotenuse 4.3199879
- the drawing's 4 5/16, 3 10/16, 2 5/16 are nearest-sixteenth roundings
- 432² = 186,624 vs the speed of light 186,282.397 mi/s: +0.18%, and only in miles
"""

import math

from .entangled_triangles import RightTriangle, LeftTriangleGenerator


PHI = (1 + math.sqrt(5)) / 2
FRACTAL_ROOT = math.sqrt(10)  # FRACTAL_ROOT × (FRACTAL_ROOT / 10) = 1

THOTH_HYPOTENUSE = 4.32
THOTH_HYPOTENUSE_BASE_PRODUCT = 10.0  # hypotenuse × base

# (1/φ² + 1)⁴ = 25/φ⁴. Approximates the 4.32 triangle's height; not equal to it.
PHI_HEIGHT = (1 / PHI**2 + 1) ** 4


def thoth_triangle(hypotenuse: float = THOTH_HYPOTENUSE) -> RightTriangle:
    """
    Right triangle with base = 10 / hypotenuse (1/0.432 for hypotenuse 4.32).

    The hypotenuse must exceed the Fractal Root √10: at √10 the base equals
    the hypotenuse and the height collapses to zero.
    """
    if hypotenuse <= FRACTAL_ROOT:
        raise ValueError(f"Hypotenuse must exceed √10 ≈ {FRACTAL_ROOT:.8f}, got {hypotenuse}")

    base = THOTH_HYPOTENUSE_BASE_PRODUCT / hypotenuse
    height = math.sqrt(hypotenuse**2 - base**2)
    return RightTriangle(base=base, height=height, hypotenuse=hypotenuse)


def run_thoth_validation():
    """
    Validate every equation from the post against ETR's geometry.

    Expected results:
    - Right triangle: base=2.3148148148, height=3.6474693108, hypotenuse=4.32
    - Left triangle height = 1/4.32 = 0.2314814815 = right base / 10
    - Height − 25/φ⁴ = 1.85e-5 (5.06 ppm), so height = 25/φ⁴ fails Pythagoras
    """
    print("="*70)
    print("VALIDATING THOTH TRIANGLE (HYPOTENUSE 4.32, BASE 1/0.432)")
    print("="*70)

    rt = thoth_triangle()
    print(f"\nRight Triangle: {rt.to_dict()}")

    lt = LeftTriangleGenerator.generate_left_triangle(rt)
    print(f"\nLeft Triangle: {lt.to_dict()}")

    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)

    # Dimensions
    assert abs(rt.base - 1 / 0.432) < 1e-12, f"Base should be 1/0.432, got {rt.base}"
    assert abs(rt.hypotenuse * rt.base - 10) < 1e-12, "Hypotenuse × base should be 10"
    assert abs(rt.height - 3.647469310784376) < 1e-12, f"Height should be 3.6474693108, got {rt.height}"
    print(f"✓ Height = √(4.32² − (1/0.432)²) = {rt.height:.10f}")

    # ETR entanglement: the left triangle's height carries the base's digits
    assert abs(lt.height - rt.base / 10) < 1e-15, f"Left height should be base/10, got {lt.height}"
    assert LeftTriangleGenerator.verify_angle_preservation(rt, lt), "Angles not preserved!"
    assert LeftTriangleGenerator.verify_scaling_relationship(rt, lt), "Scaling relationships invalid!"
    print(f"✓ Left height = 1/4.32 = {lt.height:.10f} = right base / 10")
    print(f"✓ Scaling factor: {rt.scaling_factor:.10f}, angles and scaling preserved")

    # Golden ratio: exact identity, approximate match
    assert abs(PHI_HEIGHT - 25 / PHI**4) < 1e-12, "(1/φ² + 1)⁴ should equal 25/φ⁴"
    relative_gap = (rt.height - PHI_HEIGHT) / PHI_HEIGHT
    assert abs(relative_gap - 5.062995e-6) < 1e-11, f"φ gap should be 5.063e-6, got {relative_gap:.6e}"
    print(f"✓ (1/φ² + 1)⁴ = 25/φ⁴ = {PHI_HEIGHT:.10f}, height differs by {relative_gap:.3e} (approximate)")

    try:
        RightTriangle(base=rt.base, height=PHI_HEIGHT, hypotenuse=rt.hypotenuse)
        assert False, "4.32, 1/0.432 and 25/φ⁴ should not form a right triangle"
    except ValueError:
        pass  # Expected: Pythagorean residual is −1.35e-4
    print("✓ Forcing height = 25/φ⁴ violates Pythagoras (residual −1.35e-4)")

    phi_hypotenuse = math.sqrt((PHI_HEIGHT**2 + math.sqrt(PHI_HEIGHT**4 + 400)) / 2)
    phi_rt = thoth_triangle(phi_hypotenuse)
    assert abs(phi_rt.height - PHI_HEIGHT) < 1e-12, "φ-exact hypotenuse should give height 25/φ⁴"
    assert round(phi_hypotenuse, 2) == THOTH_HYPOTENUSE, "4.32 should be the φ-exact hypotenuse rounded"
    print(f"✓ φ-exact hypotenuse = {phi_hypotenuse:.10f}, which rounds to 4.32")

    # Drawing labels
    assert [round(side * 16) for side in (rt.hypotenuse, rt.height, rt.base)] == [69, 58, 37], \
        "Sides should round to 4 5/16, 3 10/16, 2 5/16"
    print("✓ Sixteenths: hypotenuse ≈ 4 5/16, height ≈ 3 10/16, base ≈ 2 5/16")

    # Fractal Root
    assert abs(FRACTAL_ROOT * (FRACTAL_ROOT / 10) - 1) < 1e-15, "√10 × √10/10 should be 1"
    print(f"✓ Fractal Root: {FRACTAL_ROOT:.8f} × {FRACTAL_ROOT / 10:.9f} = 1 (degenerate hypotenuse)")

    # 432² and the speed of light
    light_miles_per_second = 299792458 / 1609.344
    light_gap = (432**2 - light_miles_per_second) / light_miles_per_second
    assert 432**2 == 186624, "432² should be 186,624"
    assert abs(light_gap - 1.8337908e-3) < 1e-9, f"Gap should be +0.1834%, got {light_gap:.6e}"
    print(f"✓ 432² = 186,624 vs {light_miles_per_second:,.3f} mi/s ({light_gap:+.4%}, approximate)")

    print("\n" + "="*70)
    print("THOTH TRIANGLE VALIDATION PASSED ✓")
    print("="*70)


if __name__ == "__main__":
    run_thoth_validation()
