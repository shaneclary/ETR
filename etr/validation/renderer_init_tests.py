"""
Renderer initialisation tests - CPU only, no CUDA extension needed.

Checks scene.triangle_model.generate_triangles_in_chunks:
1. init_shape="fibonacci" (the default) reproduces the upstream Triangle
   Splatting function bit-for-bit
2. init_shape="thoth" places Grant's Thoth triangle on every point
3. ETR recognises the result end to end (adapter and metrics)

Requires torch and plyfile. The simple_knn CUDA extension is replaced by a
CPU stand-in when it is not installed; it is only used by create_from_pcd,
which these tests do not call.
"""

import math
import subprocess
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_COMMIT = "e373957"  # last commit before init_shape existed

try:
    import torch
    import plyfile  # noqa: F401  (imported by scene.dataset_readers)
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


def install_simple_knn_stand_in():
    """Register a CPU simple_knn._C.distCUDA2 if the CUDA extension is absent."""
    try:
        import simple_knn._C  # noqa: F401
        return
    except ImportError:
        pass

    def distCUDA2(points):
        squared = torch.cdist(points, points) ** 2
        squared.fill_diagonal_(float("inf"))
        return squared.topk(3, dim=1, largest=False).values.mean(dim=1)

    extension = types.ModuleType("simple_knn._C")
    extension.distCUDA2 = distCUDA2
    package = types.ModuleType("simple_knn")
    package._C = extension
    sys.modules["simple_knn"] = package
    sys.modules["simple_knn._C"] = extension


def load_upstream_generate():
    """The original generate_triangles_in_chunks, straight from git."""
    source = subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), "show", f"{UPSTREAM_COMMIT}:scene/triangle_model.py"], text=True)
    module = types.ModuleType("upstream_triangle_model")
    exec(compile(source, "upstream_triangle_model.py", "exec"), module.__dict__)
    return module.generate_triangles_in_chunks


def sample_centers(n_centers, seed, center_spread=5.0, min_radius=0.01, radius_spread=0.5):
    torch.manual_seed(seed)
    centers = torch.randn(n_centers, 3) * center_spread
    radii = torch.rand(n_centers, 1) * radius_spread + min_radius
    return centers, radii


def test_default_matches_upstream():
    """init_shape="fibonacci" must reproduce the upstream function bit-for-bit."""
    print("\n" + "="*70)
    print("TEST 1: Default init reproduces upstream Triangle Splatting")
    print("="*70)

    from scene.triangle_model import generate_triangles_in_chunks

    upstream = load_upstream_generate()
    centers, radii = sample_centers(4500, seed=7)  # more than one chunk of 2000
    x, y, z = centers[:, 0], centers[:, 1], centers[:, 2]

    torch.manual_seed(11)
    ours = generate_triangles_in_chunks(x, y, z, radii, 3)
    torch.manual_seed(11)
    theirs = upstream(x, y, z, radii, 3)

    assert torch.equal(ours, theirs), f"default init_shape must match upstream {UPSTREAM_COMMIT} exactly"
    print(f"✓ {ours.shape[0]} triangles identical to upstream {UPSTREAM_COMMIT}")

    print("\n✅ Default Init Test PASSED")
    return True


def thoth_measurements(triangles, centers, radii):
    """Vertex roles follow the Fibonacci layout: hypotenuse v0-v2, right angle at v1."""
    vertex_distances = (triangles - centers[:, None, :]).norm(dim=-1)
    hypotenuses = (triangles[:, 0] - triangles[:, 2]).norm(dim=-1)
    leg_height = triangles[:, 0] - triangles[:, 1]
    leg_base = triangles[:, 2] - triangles[:, 1]
    cos_right = (leg_height * leg_base).sum(-1) / (leg_height.norm(dim=-1) * leg_base.norm(dim=-1))
    return vertex_distances, hypotenuses, leg_height, leg_base, cos_right


def test_thoth_init_shape():
    """init_shape="thoth" puts a Thoth triangle of circumradius r on every point."""
    print("\n" + "="*70)
    print("TEST 2: Thoth init shape")
    print("="*70)

    from scene.triangle_model import fibonacci_directions, right_triangle_directions, thoth_directions, generate_triangles_in_chunks
    from etr.core.entangled_triangles import RightTriangle
    from etr.core.thoth_geometry import thoth_triangle

    thoth = thoth_triangle()
    base_ratio = thoth.base / thoth.hypotenuse
    height_ratio = thoth.height / thoth.hypotenuse

    # Same seed plane as the default: a 45-45-90 triangle reproduces fibonacci_directions(3) exactly,
    # and the Thoth directions share its hypotenuse axis and its plane
    isosceles = right_triangle_directions(RightTriangle(base=1.0, height=1.0, hypotenuse=math.sqrt(2.0)))
    assert torch.equal(isosceles, fibonacci_directions(3)), "45-45-90 layout must equal the Fibonacci directions"
    directions = thoth_directions(3)
    fib = fibonacci_directions(3)
    assert torch.equal(directions[0], fib[0]) and torch.equal(directions[2], fib[2]), "hypotenuse axis must match"
    assert abs(torch.dot(directions[1], torch.cross(fib[0], fib[1], dim=0)).item()) < 1e-7, "right-angle vertex must lie in the Fibonacci plane"
    print("✓ Thoth directions share the Fibonacci seed plane; 45-45-90 reproduces fibonacci_directions(3)")

    # Near the origin float32 rounding is negligible: the geometry must be exact
    centers, radii = sample_centers(4500, seed=5, center_spread=0.01, min_radius=0.5, radius_spread=1.0)
    x, y, z = centers[:, 0], centers[:, 1], centers[:, 2]
    triangles = generate_triangles_in_chunks(x, y, z, radii, 3, init_shape="thoth")
    assert triangles.shape == (4500, 3, 3)
    vertex_distances, hypotenuses, leg_height, leg_base, cos_right = thoth_measurements(triangles, centers, radii)

    assert torch.allclose(vertex_distances, radii.expand(-1, 3), rtol=1e-6, atol=1e-6), "vertices must sit at circumradius r"
    assert torch.allclose(hypotenuses, 2 * radii[:, 0], rtol=1e-6, atol=1e-6), "hypotenuse must be the diameter 2r"
    assert cos_right.abs().max() < 2e-6, f"right angle at v1 violated, max |cos| = {cos_right.abs().max():.2e}"
    assert torch.allclose(leg_height.norm(dim=-1) / hypotenuses, torch.full_like(hypotenuses, height_ratio), atol=2e-6)
    assert torch.allclose(leg_base.norm(dim=-1) / hypotenuses, torch.full_like(hypotenuses, base_ratio), atol=2e-6)
    print(f"✓ Near origin: {triangles.shape[0]} Thoth triangles, max |cos right angle| = {cos_right.abs().max():.1e}")

    normals = torch.cross(leg_height, leg_base, dim=-1)
    normals = normals / normals.norm(dim=-1, keepdim=True)
    assert normals.std(dim=0).min() > 0.3, "triangles should be randomly rotated"
    print("✓ Orientations are random")

    # At scene scale the only error is float32 rounding of center + r × direction,
    # the same as for the upstream 45-45-90 init on the same centers
    centers, radii = sample_centers(4500, seed=3)
    x, y, z = centers[:, 0], centers[:, 1], centers[:, 2]
    torch.manual_seed(5)
    triangles = generate_triangles_in_chunks(x, y, z, radii, 3, init_shape="thoth")
    _, _, _, _, cos_right = thoth_measurements(triangles, centers, radii)
    float32_eps = torch.finfo(torch.float32).eps
    rounding_bound = 4 * float32_eps * centers.norm(dim=-1) / (radii[:, 0] * base_ratio)
    assert (cos_right.abs() <= rounding_bound).all(), "right-angle error exceeds float32 rounding"

    torch.manual_seed(5)
    upstream_triangles = generate_triangles_in_chunks(x, y, z, radii, 3)
    _, _, _, _, upstream_cos = thoth_measurements(upstream_triangles, centers, radii)
    assert cos_right.abs().max() <= 2 * upstream_cos.abs().max(), "thoth init should round like the upstream init"
    print(f"✓ Scene scale: max |cos right angle| = {cos_right.abs().max():.1e} "
          f"(upstream 45-45-90 init: {upstream_cos.abs().max():.1e})")

    for kwargs, message in [
        (dict(nb_points=3, init_shape="bogus"), "unknown init_shape"),
        (dict(nb_points=4, init_shape="thoth"), "thoth with nb_points != 3"),
    ]:
        try:
            generate_triangles_in_chunks(x[:10], y[:10], z[:10], radii[:10], **kwargs)
            raise AssertionError(f"{message} should raise ValueError")
        except ValueError:
            pass
    print("✓ Unknown shapes and non-triangles are rejected")

    print("\n✅ Thoth Init Test PASSED")
    return True


def test_init_to_etr_metrics():
    """Thoth init → TriangleModel → adapter → ETR metrics, on CPU float32."""
    print("\n" + "="*70)
    print("TEST 3: ETR recognises the renderer's Thoth triangles")
    print("="*70)

    from scene.triangle_model import TriangleModel, generate_triangles_in_chunks
    from etr.core.triangle_adapter import TriangleSplattingAdapter
    from etr.core.thoth_geometry import thoth_triangle
    from etr.utils.etr_metrics import ETRMetrics

    centers, radii = sample_centers(3000, seed=9)
    x, y, z = centers[:, 0], centers[:, 1], centers[:, 2]
    torch.manual_seed(2)
    model = TriangleModel(sh_degree=3)
    model._triangles_points = generate_triangles_in_chunks(x, y, z, radii, 3, init_shape="thoth")

    etr_data = TriangleSplattingAdapter.apply_etr_to_triangle_model(model)
    stats = ETRMetrics.compute_statistics(etr_data)
    thoth = thoth_triangle()

    assert stats["right_triangles"] == 3000 and stats["right_triangle_percentage"] == 100.0, stats
    assert abs(stats["mean_logarithmic_base"] - thoth.logarithmic_base) < 1e-4, stats["mean_logarithmic_base"]
    assert torch.allclose(etr_data["left_heights"], 1 / etr_data["hypotenuses"]), "left height = 1 / hypotenuse"
    assert torch.allclose(etr_data["left_hypotenuses"], 1 / etr_data["heights"]), "left hypotenuse = 1 / height"
    assert torch.allclose(etr_data["scaling_factors"], etr_data["heights"] * etr_data["hypotenuses"])
    assert torch.allclose(etr_data["bases"] / etr_data["hypotenuses"],
                          torch.full((3000,), thoth.base / thoth.hypotenuse), atol=1e-3), "longer leg is the height"
    print(f"✓ {stats['right_triangles']}/3000 right triangles, "
          f"logarithmic base {stats['mean_logarithmic_base']:.5f} (Thoth {thoth.logarithmic_base:.5f})")

    print("\n✅ ETR Metrics Test PASSED")
    return True


def run_all_tests():
    """Run all renderer init tests."""
    print("="*70)
    print("ETR RENDERER INIT TESTS (CPU)")
    print("="*70)

    if not DEPENDENCIES_AVAILABLE:
        print("\nSkipped: torch and plyfile are required")
        return 0, 0

    sys.path.insert(0, str(REPO_ROOT))
    install_simple_knn_stand_in()

    tests = [
        ("Default Init", test_default_matches_upstream),
        ("Thoth Init", test_thoth_init_shape),
        ("ETR Metrics", test_init_to_etr_metrics),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {name} FAILED: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"Total: {passed} passed, {failed} failed")
    print("="*70)

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
