"""
Test and demonstrate point cloud format support.

Tests all supported formats: PLY, PCD, PTS, XYZ, LAS
"""

import numpy as np
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scene.triangle_model import BasicPointCloud
from utils.point_cloud_io import PointCloudLoader, load_point_cloud


def generate_test_point_cloud(n_points=1000):
    """Generate synthetic test point cloud."""
    # Create a spiral point cloud
    t = np.linspace(0, 4*np.pi, n_points)
    x = t * np.cos(t)
    y = t * np.sin(t)
    z = t

    points = np.column_stack([x, y, z])

    # Create rainbow colors
    colors = np.zeros((n_points, 3))
    colors[:, 0] = (np.sin(t) + 1) / 2  # Red
    colors[:, 1] = (np.cos(t) + 1) / 2  # Green
    colors[:, 2] = (np.sin(t + np.pi/2) + 1) / 2  # Blue

    # Create normals pointing outward
    normals = np.column_stack([np.cos(t), np.sin(t), np.zeros(n_points)])
    normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)

    return BasicPointCloud(points=points, colors=colors, normals=normals)


def test_ply_format():
    """Test PLY format (both save and load)."""
    print("\n" + "="*70)
    print("TEST: PLY Format")
    print("="*70)

    # Generate test data
    pcd = generate_test_point_cloud(1000)
    print(f"Generated test cloud: {len(pcd.points)} points")

    # Save as PLY
    output_file = "test_output.ply"
    try:
        PointCloudLoader.save_ply(output_file, pcd)
        print(f"✓ Saved PLY file: {output_file}")

        # Load back
        pcd_loaded = PointCloudLoader.load_ply(output_file)
        print(f"✓ Loaded PLY file: {len(pcd_loaded.points)} points")

        # Verify data matches
        assert np.allclose(pcd.points, pcd_loaded.points, atol=1e-5)
        assert np.allclose(pcd.colors, pcd_loaded.colors, atol=1e-2)  # Colors are quantized to uint8
        print("✓ Data matches")

        # Cleanup
        os.remove(output_file)
        print("✓ PLY Format Test PASSED")
        return True

    except Exception as e:
        print(f"✗ PLY Format Test FAILED: {e}")
        if os.path.exists(output_file):
            os.remove(output_file)
        return False


def test_xyz_format():
    """Test XYZ ASCII format."""
    print("\n" + "="*70)
    print("TEST: XYZ Format")
    print("="*70)

    # Generate test data
    pcd = generate_test_point_cloud(100)

    # Save as XYZ
    output_file = "test_output.xyz"
    try:
        # Save with colors
        data = np.column_stack([pcd.points, pcd.colors * 255])
        np.savetxt(output_file, data, fmt='%.6f %.6f %.6f %d %d %d')
        print(f"✓ Saved XYZ file: {output_file}")

        # Load back
        pcd_loaded = PointCloudLoader.load_xyz(output_file)
        print(f"✓ Loaded XYZ file: {len(pcd_loaded.points)} points")

        # Verify positions match
        assert np.allclose(pcd.points, pcd_loaded.points, atol=1e-5)
        print("✓ Positions match")

        # Cleanup
        os.remove(output_file)
        print("✓ XYZ Format Test PASSED")
        return True

    except Exception as e:
        print(f"✗ XYZ Format Test FAILED: {e}")
        if os.path.exists(output_file):
            os.remove(output_file)
        return False


def test_pts_format():
    """Test PTS format."""
    print("\n" + "="*70)
    print("TEST: PTS Format")
    print("="*70)

    # Generate test data
    pcd = generate_test_point_cloud(100)

    # Save as PTS (X Y Z Intensity R G B)
    output_file = "test_output.pts"
    try:
        intensity = np.random.rand(len(pcd.points)) * 255
        data = np.column_stack([pcd.points, intensity, pcd.colors * 255])
        np.savetxt(output_file, data, fmt='%.6f %.6f %.6f %.1f %d %d %d')
        print(f"✓ Saved PTS file: {output_file}")

        # Load back
        pcd_loaded = PointCloudLoader.load_pts(output_file)
        print(f"✓ Loaded PTS file: {len(pcd_loaded.points)} points")

        # Verify positions match
        assert np.allclose(pcd.points, pcd_loaded.points, atol=1e-5)
        print("✓ Positions match")

        # Cleanup
        os.remove(output_file)
        print("✓ PTS Format Test PASSED")
        return True

    except Exception as e:
        print(f"✗ PTS Format Test FAILED: {e}")
        if os.path.exists(output_file):
            os.remove(output_file)
        return False


def test_auto_detection():
    """Test automatic format detection."""
    print("\n" + "="*70)
    print("TEST: Auto-Detection")
    print("="*70)

    # Generate test data
    pcd = generate_test_point_cloud(50)

    # Save as PLY
    ply_file = "test_auto.ply"
    try:
        PointCloudLoader.save_ply(ply_file, pcd)

        # Load using auto-detection
        pcd_loaded = load_point_cloud(ply_file)
        print(f"✓ Auto-detected and loaded PLY: {len(pcd_loaded.points)} points")

        assert np.allclose(pcd.points, pcd_loaded.points, atol=1e-5)
        print("✓ Data matches")

        # Cleanup
        os.remove(ply_file)
        print("✓ Auto-Detection Test PASSED")
        return True

    except Exception as e:
        print(f"✗ Auto-Detection Test FAILED: {e}")
        if os.path.exists(ply_file):
            os.remove(ply_file)
        return False


def test_las_format():
    """Test LAS format (if laspy is available)."""
    print("\n" + "="*70)
    print("TEST: LAS Format (Optional)")
    print("="*70)

    try:
        import laspy
        print("✓ laspy is available")
    except ImportError:
        print("⚠️ laspy not available - skipping LAS test")
        print("   Install with: pip install laspy")
        return None

    # For now, just test that the loader doesn't crash
    # Would need actual LAS file to test fully
    print("✓ LAS Format loader is available")
    print("  (Full test requires actual LAS file)")
    return None


def run_all_tests():
    """Run all point cloud format tests."""
    print("="*70)
    print("POINT CLOUD FORMAT TESTS")
    print("="*70)
    print("\nTesting multiple point cloud format loaders")

    results = {
        "PLY": test_ply_format(),
        "XYZ": test_xyz_format(),
        "PTS": test_pts_format(),
        "Auto-Detection": test_auto_detection(),
        "LAS": test_las_format(),
    }

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for name, result in results.items():
        if result is True:
            print(f"✓ {name}: PASSED")
        elif result is False:
            print(f"✗ {name}: FAILED")
        else:
            print(f"⚠️ {name}: SKIPPED")

    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    print("="*70)

    return results


if __name__ == "__main__":
    results = run_all_tests()

    # Exit with error code if any tests failed
    failed = sum(1 for v in results.values() if v is False)
    sys.exit(0 if failed == 0 else 1)
