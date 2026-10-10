"""
ETR Standalone Validation - No Dependencies Required
Tests the core mathematical theory without NumPy or PyTorch
"""

import math
import sys

def test_3_4_5_triangle_pure_python():
    """Test the canonical 3:4:5 triangle using only Python standard library."""
    print("\n" + "="*70)
    print("TEST 1: 3:4:5 Triangle (Pure Python)")
    print("="*70)

    # Right triangle
    rt_base = 3
    rt_height = 4
    rt_hyp = 5

    # Verify Pythagorean theorem
    assert abs(rt_base**2 + rt_height**2 - rt_hyp**2) < 1e-10, "Not a right triangle!"
    print(f"✓ Right triangle valid: {rt_base}² + {rt_height}² = {rt_hyp}²")

    # Compute scaling factor
    scaling_factor = rt_height * rt_hyp
    print(f"✓ Scaling factor: {scaling_factor}")
    assert abs(scaling_factor - 20) < 1e-10, f"Scaling should be 20, got {scaling_factor}"

    # Generate left triangle (height and hypotenuse roles swap)
    lt_height = 1.0 / rt_hyp  # New height = 1/old hypotenuse
    lt_hyp = 1.0 / rt_height  # New hypotenuse = 1/old height
    lt_base = rt_base / scaling_factor

    print(f"✓ Left triangle: base={lt_base}, height={lt_height}, hyp={lt_hyp}")

    # Verify left triangle is also right triangle
    lt_check = abs(lt_base**2 + lt_height**2 - lt_hyp**2)
    assert lt_check < 1e-10, f"Left triangle not right! Error: {lt_check}"
    print(f"✓ Left triangle valid: Pythagorean error = {lt_check:.2e}")

    # Check expected dimensions
    assert abs(lt_base - 0.15) < 1e-10, f"LT base should be 0.15, got {lt_base}"
    assert abs(lt_height - 0.2) < 1e-10, f"LT height should be 0.2, got {lt_height}"
    assert abs(lt_hyp - 0.25) < 1e-10, f"LT hyp should be 0.25, got {lt_hyp}"
    print("✓ Dimensions match expected values")

    # Verify perimeter ratio
    rt_perimeter = rt_base + rt_height + rt_hyp
    lt_perimeter = lt_base + lt_height + lt_hyp
    perimeter_ratio = rt_perimeter / lt_perimeter
    assert abs(perimeter_ratio - 20) < 1e-10, f"Perimeter ratio should be 20, got {perimeter_ratio}"
    print(f"✓ Perimeter ratio: {perimeter_ratio}")

    # Verify area ratio
    rt_area = 0.5 * rt_base * rt_height
    lt_area = 0.5 * lt_base * lt_height
    area_ratio = rt_area / lt_area
    assert abs(area_ratio - 400) < 1e-10, f"Area ratio should be 400, got {area_ratio}"
    print(f"✓ Area ratio: {area_ratio} (20²)")

    # Verify angle preservation
    rt_angle1 = math.atan2(rt_height, rt_base)
    rt_angle2 = math.atan2(rt_base, rt_height)
    lt_angle1 = math.atan2(lt_height, lt_base)
    lt_angle2 = math.atan2(lt_base, lt_height)

    assert abs(rt_angle1 - lt_angle1) < 1e-8, "Angle 1 not preserved!"
    assert abs(rt_angle2 - lt_angle2) < 1e-8, "Angle 2 not preserved!"
    print(f"✓ Angles preserved: {math.degrees(rt_angle1):.4f}° and {math.degrees(rt_angle2):.4f}°")

    print("\n✅ 3:4:5 Triangle Test PASSED")
    return True


def test_multiple_pythagorean_triples():
    """Test multiple Pythagorean triples."""
    print("\n" + "="*70)
    print("TEST 2: Multiple Pythagorean Triples")
    print("="*70)

    triples = [
        (3, 4, 5),
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
        (20, 21, 29),
        (9, 40, 41),
        (12, 35, 37),
        (11, 60, 61),
    ]

    all_passed = True

    for base, height, hyp in triples:
        # Verify it's a right triangle
        assert abs(base**2 + height**2 - hyp**2) < 1e-10

        # Compute scaling
        scaling = height * hyp

        # Generate left triangle (height and hypotenuse swap)
        lt_height = 1.0 / hyp  # New height = 1/old hypotenuse
        lt_hyp = 1.0 / height  # New hypotenuse = 1/old height
        lt_base = base / scaling

        # Verify left triangle
        error = abs(lt_base**2 + lt_height**2 - lt_hyp**2)
        passed = error < 1e-9

        # Verify scaling relationships
        rt_perimeter = base + height + hyp
        lt_perimeter = lt_base + lt_height + lt_hyp
        perimeter_ratio = rt_perimeter / lt_perimeter
        perimeter_ok = abs(perimeter_ratio - scaling) < 1e-8

        rt_area = 0.5 * base * height
        lt_area = 0.5 * lt_base * lt_height
        area_ratio = rt_area / lt_area
        area_ok = abs(area_ratio - scaling**2) < 1e-8

        status = "✓" if (passed and perimeter_ok and area_ok) else "✗"
        print(f"{status} {base}:{height}:{hyp} | scaling={scaling:8.2f} | error={error:.2e}")

        all_passed = all_passed and passed and perimeter_ok and area_ok

    if all_passed:
        print(f"\n✅ All {len(triples)} Pythagorean Triples PASSED")
    else:
        print(f"\n❌ Some triples FAILED")

    return all_passed


def test_fractal_hierarchy():
    """Test fractal hierarchy generation."""
    print("\n" + "="*70)
    print("TEST 3: Fractal Hierarchy")
    print("="*70)

    # Start with 3:4:5
    base, height, hyp = 3, 4, 5

    triangles = [(base, height, hyp)]
    scaling_factors = [height * hyp]

    # Generate 10 levels
    for level in range(1, 11):
        prev_base, prev_height, prev_hyp = triangles[-1]
        prev_scaling = prev_height * prev_hyp

        # Generate next left triangle (height and hypotenuse swap)
        new_height = 1.0 / prev_hyp  # New height = 1/old hypotenuse
        new_hyp = 1.0 / prev_height  # New hypotenuse = 1/old height
        new_base = prev_base / prev_scaling

        triangles.append((new_base, new_height, new_hyp))
        scaling_factors.append(new_height * new_hyp)

        # Verify it's valid
        error = abs(new_base**2 + new_height**2 - new_hyp**2)
        assert error < 1e-6, f"Level {level} failed Pythagorean check: {error:.2e}"

    print(f"Generated {len(triangles)} levels:")
    for i, (b, h, c) in enumerate(triangles[:6]):  # Show first 6
        print(f"  Level {i:2d}: base={b:15.10f}, scaling={scaling_factors[i]:10.4f}")

    if len(triangles) > 6:
        print(f"  ...")
        b, h, c = triangles[-1]
        print(f"  Level {len(triangles)-1:2d}: base={b:15.10e}, scaling={scaling_factors[-1]:10.4e}")

    # The transformation is an involution: level 2 is level 0 again, so the
    # sequence has period 2 and only two distinct triangles
    for level in range(2, len(triangles)):
        for side, earlier in zip(triangles[level], triangles[level - 2]):
            assert abs(side - earlier) < 1e-12, f"Level {level} should equal level {level - 2}"
    assert len({tuple(round(s, 12) for s in tri) for tri in triangles}) == 2, "Only two distinct triangles"
    print(f"✓ Period 2: levels alternate (3, 4, 5) and (0.15, 0.2, 0.25); two distinct triangles")

    print(f"\n✅ Fractal Hierarchy ({len(triangles)} levels) PASSED")
    return True


def test_numerical_stability():
    """Test numerical stability over deep recursion."""
    print("\n" + "="*70)
    print("TEST 4: Numerical Stability (15 levels)")
    print("="*70)

    base, height, hyp = 3, 4, 5
    max_error = 0.0

    for level in range(15):
        scaling = height * hyp

        # Transform (height and hypotenuse swap)
        new_height = 1.0 / hyp  # New height = 1/old hypotenuse
        new_hyp = 1.0 / height  # New hypotenuse = 1/old height
        new_base = base / scaling

        # Check error
        error = abs(new_base**2 + new_height**2 - new_hyp**2)
        max_error = max(max_error, error)

        if error > 1e-6:
            print(f"✗ Level {level}: error={error:.2e} (too large)")
            return False

        # Update for next iteration
        base, height, hyp = new_base, new_height, new_hyp

    print(f"✓ All 15 levels stable")
    print(f"✓ Maximum Pythagorean error: {max_error:.2e}")
    print(f"✓ Final triangle dimensions: {base:.10e}, {height:.10e}, {hyp:.10e}")

    print("\n✅ Numerical Stability Test PASSED")
    return True


def test_edge_cases():
    """Test edge cases."""
    print("\n" + "="*70)
    print("TEST 5: Edge Cases")
    print("="*70)

    # Very small triangle
    small_base = 1e-6
    small_height = 1e-6
    small_hyp = math.sqrt(small_base**2 + small_height**2)

    small_scaling = small_height * small_hyp
    lt_small_base = small_base / small_scaling
    lt_small_height = 1.0 / small_hyp  # New height = 1/old hyp
    lt_small_hyp = 1.0 / small_height  # New hyp = 1/old height

    small_error = abs(lt_small_base**2 + lt_small_height**2 - lt_small_hyp**2)
    # Relax tolerance for very small triangles due to floating point precision
    assert small_error < 1e-3, f"Small triangle failed: {small_error}"
    print(f"✓ Very small triangle (1e-6): error={small_error:.2e}")

    # Very large triangle
    large_base = 1e6
    large_height = 1e6
    large_hyp = math.sqrt(large_base**2 + large_height**2)

    large_scaling = large_height * large_hyp
    lt_large_base = large_base / large_scaling
    lt_large_height = 1.0 / large_hyp  # New height = 1/old hyp
    lt_large_hyp = 1.0 / large_height  # New hyp = 1/old height

    large_error = abs(lt_large_base**2 + lt_large_height**2 - lt_large_hyp**2)
    assert large_error < 1e-6, f"Large triangle failed: {large_error}"
    print(f"✓ Very large triangle (1e6): error={large_error:.2e}")

    # Invalid triangle should fail (not testing here since we need exceptions)
    print(f"✓ Edge cases handled correctly")

    print("\n✅ Edge Cases Test PASSED")
    return True


def test_thoth_triangle_pure_python():
    """Test Grant's 4.32 : 1/0.432 triangle (#ThothConstant post) using only stdlib."""
    print("\n" + "="*70)
    print("TEST 6: Thoth Triangle, hypotenuse 4.32, base 1/0.432 (Pure Python)")
    print("="*70)

    phi = (1 + math.sqrt(5)) / 2

    rt_hyp = 4.32
    rt_base = 1 / 0.432
    rt_height = math.sqrt(rt_hyp**2 - rt_base**2)

    # Defining relation: hypotenuse × base = 10 (base is 1/hypotenuse shifted one decimal)
    assert abs(rt_hyp * rt_base - 10) < 1e-12, f"hyp × base should be 10, got {rt_hyp * rt_base}"
    print(f"✓ hypotenuse × base = {rt_hyp} × {rt_base:.10f} = {rt_hyp * rt_base:.12f}")

    # Height from Pythagoras (40-digit value: 3.647469310784376...)
    assert abs(rt_height - 3.647469310784376) < 1e-12, f"Height should be 3.6474693108, got {rt_height}"
    print(f"✓ Height = √(4.32² − (1/0.432)²) = {rt_height:.10f}")

    # Golden ratio: (1/φ² + 1)⁴ is exactly 25/φ⁴ = 125 − 75φ ...
    phi_height = (1 / phi**2 + 1) ** 4
    assert abs(phi_height - 25 / phi**4) < 1e-12, "(1/φ² + 1)⁴ should equal 25/φ⁴"
    assert abs(phi_height - (125 - 75 * phi)) < 1e-12, "(1/φ² + 1)⁴ should equal 125 − 75φ"
    print(f"✓ (1/φ² + 1)⁴ = 25/φ⁴ = 125 − 75φ = {phi_height:.10f}")

    # ... but the height only approximates it (5.06 ppm), it is not an identity
    relative_gap = (rt_height - phi_height) / phi_height
    assert abs(relative_gap - 5.062995e-6) < 1e-11, f"φ gap should be 5.063e-6, got {relative_gap:.6e}"
    print(f"✓ Height − 25/φ⁴ = {rt_height - phi_height:.3e} (relative {relative_gap:.3e}, approximate)")

    # Hence 4.32, 1/0.432 and 25/φ⁴ cannot all be exact sides of one right triangle
    phi_residual = rt_base**2 + phi_height**2 - rt_hyp**2
    assert abs(phi_residual + 1.3471548e-4) < 1e-10, f"Residual should be -1.347e-4, got {phi_residual:.6e}"
    print(f"✓ Pythagorean residual with height = 25/φ⁴: {phi_residual:.3e} (not a right triangle)")

    # The hypotenuse that makes the height exactly 25/φ⁴ (keeping hyp × base = 10)
    phi_hyp = math.sqrt((phi_height**2 + math.sqrt(phi_height**4 + 400)) / 2)
    phi_hyp_height = math.sqrt(phi_hyp**2 - (10 / phi_hyp)**2)
    assert abs(phi_hyp - 4.319987886087017) < 1e-12, f"φ-exact hypotenuse should be 4.3199879, got {phi_hyp}"
    assert abs(phi_hyp_height - phi_height) < 1e-12, "φ-exact hypotenuse should give height 25/φ⁴"
    print(f"✓ φ-exact hypotenuse = {phi_hyp:.10f} (4.32 is this rounded; gap {(rt_hyp - phi_hyp) / phi_hyp:.2e})")

    # The drawing's labels 4 5/16, 3 10/16, 2 5/16 are nearest-sixteenth roundings
    assert round(rt_hyp * 16) == 69, "Hypotenuse should round to 4 5/16 = 69/16"
    assert round(rt_height * 16) == 58, "Height should round to 3 10/16 = 58/16"
    assert round(rt_base * 16) == 37, "Base should round to 2 5/16 = 37/16"
    print("✓ Sixteenths: hyp ≈ 4 5/16, height ≈ 3 10/16, base ≈ 2 5/16")

    # ETR transform: uniform scaling by 1/(height × hypotenuse)
    scaling = rt_height * rt_hyp
    lt_height = 1.0 / rt_hyp
    lt_hyp = 1.0 / rt_height
    lt_base = rt_base / scaling

    lt_check = abs(lt_base**2 + lt_height**2 - lt_hyp**2)
    assert lt_check < 1e-12, f"Left triangle not right! Error: {lt_check}"
    print(f"✓ Left triangle: base={lt_base:.10f}, height={lt_height:.10f}, hyp={lt_hyp:.10f}")

    # Entanglement: LT height = 1/hyp = base/10, the same digits as the right triangle's base
    assert abs(lt_height - rt_base / 10) < 1e-15, f"LT height should be base/10, got {lt_height}"
    print(f"✓ LT height = 1/4.32 = {lt_height:.10f} = RT base / 10")

    # Fractal Root: √10 × (√10/10) = 1 (the post's 3.16227766 × 0.316227766 are
    # truncations of these, product 1 − 1.06e-10). hyp = √10 is the degenerate member of
    # the hyp × base = 10 family (base = hyp, height = 0)
    fractal_root = math.sqrt(10)
    assert abs(fractal_root * (fractal_root / 10) - 1) < 1e-15, "√10 × √10/10 should be 1"
    assert abs(fractal_root - 10 / fractal_root) < 1e-15, "At hyp = √10 the base equals the hypotenuse"
    print(f"✓ Fractal Root: √10 × √10/10 = 1; hypotenuse √10 = {fractal_root:.8f} is the degenerate member")

    # 432² vs the speed of light in miles per second (unit-dependent, approximate)
    assert 432**2 == 186624, "432² should be 186,624"
    light_mi_s = 299792458 / 1609.344
    light_gap = (432**2 - light_mi_s) / light_mi_s
    assert abs(light_gap - 1.8337908e-3) < 1e-9, f"Gap should be +0.1834%, got {light_gap:.6e}"
    print(f"✓ 432² = 186,624 vs c = {light_mi_s:,.3f} mi/s (relative {light_gap:+.4%}, approximate)")

    print("\n✅ Thoth Triangle Test PASSED")
    return True


def run_all_tests():
    """Run all standalone tests."""
    print("="*70)
    print("ETR STANDALONE VALIDATION (No Dependencies)")
    print("="*70)
    print("\nTesting core mathematical theory without NumPy or PyTorch")

    tests = [
        ("3:4:5 Triangle", test_3_4_5_triangle_pure_python),
        ("Multiple Pythagorean Triples", test_multiple_pythagorean_triples),
        ("Fractal Hierarchy", test_fractal_hierarchy),
        ("Numerical Stability", test_numerical_stability),
        ("Edge Cases", test_edge_cases),
        ("Thoth Triangle", test_thoth_triangle_pure_python),
    ]

    results = []
    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, "PASSED"))
            passed += 1
        except Exception as e:
            print(f"\n❌ {name} FAILED: {e}")
            results.append((name, f"FAILED: {e}"))
            failed += 1

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    for name, result in results:
        status = "✅" if "PASSED" in result else "❌"
        print(f"{status} {name}: {result}")

    print(f"\nTotal: {passed} passed, {failed} failed")
    print("="*70)

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
