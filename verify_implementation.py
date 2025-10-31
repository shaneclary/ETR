#!/usr/bin/env python3
"""
Verification script to check implementation completeness
Does not require NumPy/PyTorch - just validates structure
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✓ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_import_structure(filepath, expected_classes=None, expected_functions=None):
    """Check if file has expected structure"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        issues = []
        if expected_classes:
            for cls in expected_classes:
                if f"class {cls}" not in content:
                    issues.append(f"Missing class: {cls}")

        if expected_functions:
            for func in expected_functions:
                if f"def {func}" not in content:
                    issues.append(f"Missing function: {func}")

        if issues:
            print(f"  ⚠ Issues in {filepath}:")
            for issue in issues:
                print(f"    - {issue}")
            return False
        return True
    except Exception as e:
        print(f"  ✗ Error reading {filepath}: {e}")
        return False

print("="*70)
print("IMPLEMENTATION VERIFICATION")
print("="*70)
print()

# ETR Core Implementation
print("ETR CORE IMPLEMENTATION")
print("-" * 70)

etr_files = [
    ("etr/core/entangled_triangles.py", "ETR Core Theory",
     ["RightTriangle", "LeftTriangleGenerator", "FractalTriangleHierarchy"], None),
    ("etr/core/torch_triangle_ops.py", "GPU Batch Operations",
     ["BatchTriangleProcessor"], None),
    ("etr/core/logarithmic_spirals.py", "Logarithmic Spirals",
     ["LogarithmicSpiral", "PolygonalSpiral"], None),
    ("etr/core/triangle_adapter.py", "Triangle Splatting Adapter",
     ["TriangleAdapter"], None),
    ("etr/utils/etr_metrics.py", "ETR Metrics",
     ["ETRMetrics"], None),
    ("etr/validation/validation_suite.py", "Validation Suite",
     None, ["run_all_tests"]),
    ("etr/validation/standalone_tests.py", "Standalone Tests",
     None, ["test_3_4_5_triangle_pure_python"]),
]

etr_passed = 0
for filepath, desc, classes, functions in etr_files:
    if check_file_exists(filepath, desc):
        if check_import_structure(filepath, classes, functions):
            etr_passed += 1

print(f"\nETR Core: {etr_passed}/{len(etr_files)} files verified")
print()

# Point Cloud Support
print("POINT CLOUD SUPPORT")
print("-" * 70)

pc_files = [
    ("utils/point_cloud_io.py", "Point Cloud Loader",
     ["PointCloudLoader"], ["load_point_cloud"]),
    ("etr/examples/test_point_cloud_formats.py", "Point Cloud Tests",
     None, ["test_ply_format"]),
]

pc_passed = 0
for filepath, desc, classes, functions in pc_files:
    if check_file_exists(filepath, desc):
        if check_import_structure(filepath, classes, functions):
            pc_passed += 1

print(f"\nPoint Cloud: {pc_passed}/{len(pc_files)} files verified")
print()

# Documentation
print("DOCUMENTATION")
print("-" * 70)

docs = [
    "etr/README.md",
    "etr/docs/INTEGRATION_GUIDE.md",
    "etr/docs/IMPLEMENTATION_SUMMARY.md",
    "etr/docs/VALIDATION_REPORT.md",
    "docs/POINT_CLOUD_FORMATS.md",
    "docs/POINT_CLOUD_SUPPORT_SUMMARY.md",
]

docs_passed = 0
for doc in docs:
    if check_file_exists(doc, Path(doc).name):
        docs_passed += 1

print(f"\nDocumentation: {docs_passed}/{len(docs)} files verified")
print()

# Integration Points
print("INTEGRATION POINTS")
print("-" * 70)

# Check scene/dataset_readers.py modifications
dataset_readers = "scene/dataset_readers.py"
if os.path.exists(dataset_readers):
    with open(dataset_readers, 'r') as f:
        content = f.read()

    checks = [
        ("Point cloud import", "from utils.point_cloud_io import"),
        ("PLY support", "points3D.ply"),
        ("PCD support", "points3D.pcd"),
        ("PTS support", "points3D.pts"),
        ("XYZ support", "points3D.xyz"),
        ("LAS support", "points3D.las"),
    ]

    integration_passed = 0
    for desc, pattern in checks:
        if pattern in content:
            print(f"✓ {desc}")
            integration_passed += 1
        else:
            print(f"✗ {desc} NOT FOUND")

    print(f"\nIntegration: {integration_passed}/{len(checks)} checks passed")
else:
    print(f"✗ {dataset_readers} NOT FOUND")

print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)

total_files = len(etr_files) + len(pc_files) + len(docs) + 1
total_passed = etr_passed + pc_passed + docs_passed + (1 if integration_passed > 0 else 0)

print(f"Files verified: {total_passed}/{total_files}")
print()

# Check if tests can be run
print("TEST EXECUTION STATUS:")
print("-" * 70)

try:
    import numpy
    import torch
    print("✓ Full environment available (NumPy + PyTorch)")
    print("  → Can run full test suite")
except ImportError:
    print("⚠ Limited environment (no NumPy/PyTorch)")
    print("  → Can run standalone tests only")
    print("  → Install dependencies to run full tests:")
    print("    micromamba create -f requirements.yaml")

print()

# ETR standalone test result
if os.path.exists("etr/validation/standalone_tests.py"):
    print("Standalone ETR tests can be run with:")
    print("  python etr/validation/standalone_tests.py")
    print()

print("="*70)
print("VERIFICATION COMPLETE")
print("="*70)
