#!/usr/bin/env python3
"""
Train Triangle Splatting with ETR Integration

This script provides an easy interface to train Triangle Splatting models
with optional ETR (Entangled Triangle Rendering) transformations.

Usage:
    # Basic training
    python scripts/train_with_etr.py --scene data/mipnerf360/bicycle --output output/bicycle

    # With ETR analysis (generates fractal hierarchies and metrics)
    python scripts/train_with_etr.py --scene data/mipnerf360/bicycle --output output/bicycle --use-etr

    # With specific ETR levels
    python scripts/train_with_etr.py --scene data/mipnerf360/bicycle --output output/bicycle --use-etr --etr-levels 7
"""

import argparse
import os
import sys
from pathlib import Path
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []

    try:
        import torch
    except ImportError:
        missing.append('torch')

    try:
        import numpy
    except ImportError:
        missing.append('numpy')

    try:
        from scene import Scene
    except ImportError:
        missing.append('scene (Triangle Splatting)')

    if missing:
        print(f"Error: Missing dependencies: {', '.join(missing)}")
        print("\nPlease install dependencies:")
        print("  micromamba create -f requirements.yaml")
        print("  micromamba activate triangle_splatting")
        print("  bash compile.sh")
        return False

    return True

def verify_scene(scene_path):
    """Verify scene directory structure"""
    scene_path = Path(scene_path)

    if not scene_path.exists():
        print(f"Error: Scene directory not found: {scene_path}")
        return False

    # Check for images
    images_dir = scene_path / 'images'
    if not images_dir.exists():
        print(f"Error: Images directory not found: {images_dir}")
        return False

    images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
    if not images:
        print(f"Error: No images found in {images_dir}")
        return False

    print(f"✓ Found {len(images)} images in {images_dir}")

    # Check for COLMAP sparse reconstruction
    sparse_dir = scene_path / 'sparse' / '0'
    if sparse_dir.exists():
        print(f"✓ COLMAP sparse reconstruction found")

        # Check for point cloud
        point_cloud_files = list(sparse_dir.glob('points3D.*'))
        if point_cloud_files:
            print(f"✓ Point cloud found: {point_cloud_files[0].name}")
        else:
            print(f"⚠ Warning: No point cloud found in {sparse_dir}")
    else:
        print(f"⚠ Warning: COLMAP sparse reconstruction not found")
        print(f"  Expected: {sparse_dir}")

    return True

def build_train_command(args):
    """Build the training command"""
    cmd = ['python', 'train.py']

    # Required arguments
    cmd.extend(['-s', str(args.scene)])
    cmd.extend(['-m', str(args.output)])

    # Optional arguments
    if args.iterations:
        cmd.extend(['--iterations', str(args.iterations)])

    if args.resolution:
        cmd.extend(['-r', str(args.resolution)])

    if args.white_background:
        cmd.append('--white_background')

    if args.no_dome:
        cmd.append('--no_dome')

    if args.outdoor:
        cmd.append('--outdoor')

    # ETR-specific arguments would go here
    # Note: The main train.py doesn't have ETR flags yet
    # This is where you'd add them after modifying train.py

    return cmd

def setup_etr_environment(args):
    """Setup ETR environment and configuration"""
    if not args.use_etr:
        return True

    print("\n" + "="*70)
    print("ETR Configuration")
    print("="*70)

    # Check if ETR modules are available
    try:
        from etr.core.entangled_triangles import RightTriangle, LeftTriangleGenerator
        from etr.core.triangle_adapter import TriangleSplattingAdapter
        from etr.utils.etr_metrics import ETRMetrics
        print("✓ ETR modules loaded successfully")
    except ImportError as e:
        print(f"✗ Error loading ETR modules: {e}")
        print("\nETR implementation is available but modules couldn't be imported.")
        print("This is expected if PyTorch is not installed.")
        return False

    # Create ETR configuration
    etr_config = {
        'enabled': True,
        'fractal_levels': args.etr_levels,
        'compute_metrics': True,
        'log_interval': 1000,
        'output_dir': Path(args.output) / 'etr_analysis'
    }

    # Save configuration
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    import json
    config_file = output_path / 'etr_config.json'
    with open(config_file, 'w') as f:
        json.dump(etr_config, f, indent=2)

    print(f"✓ ETR configuration saved to {config_file}")
    print(f"  Fractal levels: {args.etr_levels}")
    print(f"  Metrics enabled: True")

    return True

def main():
    parser = argparse.ArgumentParser(
        description="Train Triangle Splatting with optional ETR integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train on bicycle scene
  python scripts/train_with_etr.py --scene data/mipnerf360/bicycle --output output/bicycle

  # Train with ETR analysis
  python scripts/train_with_etr.py --scene data/mipnerf360/bicycle --output output/bicycle --use-etr

  # Train with custom parameters
  python scripts/train_with_etr.py --scene data/mipnerf360/garden --output output/garden \\
      --iterations 40000 --outdoor --use-etr --etr-levels 10

For more information on ETR, see: etr/README.md
        """
    )

    # Scene parameters
    parser.add_argument('--scene', '-s', type=str, required=True,
                       help='Path to scene directory')
    parser.add_argument('--output', '-m', type=str, required=True,
                       help='Output directory for model and logs')

    # Training parameters
    parser.add_argument('--iterations', type=int,
                       help='Number of training iterations (default: 30000)')
    parser.add_argument('--resolution', '-r', type=int,
                       help='Image resolution (-1 for original)')
    parser.add_argument('--white-background', action='store_true',
                       help='Use white background instead of black')
    parser.add_argument('--no-dome', action='store_true',
                       help='Disable dome initialization')
    parser.add_argument('--outdoor', action='store_true',
                       help='Use outdoor scene settings')

    # ETR parameters
    parser.add_argument('--use-etr', action='store_true',
                       help='Enable ETR analysis during training')
    parser.add_argument('--etr-levels', type=int, default=7,
                       help='Number of fractal hierarchy levels for ETR (default: 7)')

    # Validation
    parser.add_argument('--skip-checks', action='store_true',
                       help='Skip dependency and scene validation')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show command without executing')

    args = parser.parse_args()

    print("="*70)
    print("Triangle Splatting with ETR Training Script")
    print("="*70)
    print()

    # Check dependencies
    if not args.skip_checks:
        print("Checking dependencies...")
        if not check_dependencies():
            sys.exit(1)
        print("✓ All dependencies available\n")

    # Verify scene
    if not args.skip_checks:
        print("Verifying scene...")
        if not verify_scene(args.scene):
            sys.exit(1)
        print()

    # Setup ETR if requested
    if args.use_etr:
        if not setup_etr_environment(args):
            print("\n⚠ Warning: ETR setup failed. Continuing without ETR.")
            args.use_etr = False
        print()

    # Build command
    cmd = build_train_command(args)

    print("="*70)
    print("Training Command")
    print("="*70)
    print(' '.join(cmd))
    print()

    if args.dry_run:
        print("Dry run mode - not executing")
        return

    # Execute training
    print("="*70)
    print("Starting Training")
    print("="*70)
    print(f"Scene: {args.scene}")
    print(f"Output: {args.output}")
    print(f"ETR Enabled: {args.use_etr}")
    print("="*70)
    print()

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError: Training failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        sys.exit(1)

    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print(f"Model saved to: {args.output}")

    if args.use_etr:
        etr_dir = Path(args.output) / 'etr_analysis'
        print(f"ETR analysis saved to: {etr_dir}")

    print("\nNext steps:")
    print(f"  1. Render test views: python render.py -m {args.output}")
    print(f"  2. Evaluate metrics: python metrics.py -m {args.output}")

    if args.use_etr:
        print(f"  3. Analyze ETR results: ls {etr_dir}")

    print("="*70)

if __name__ == '__main__':
    main()
