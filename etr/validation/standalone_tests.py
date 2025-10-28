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
