# Training with MipNeRF360 Dataset and ETR

Complete guide for downloading MipNeRF360 dataset and training Triangle Splatting models with ETR (Entangled Triangle Rendering) integration.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Dataset Information](#dataset-information)
- [Downloading the Dataset](#downloading-the-dataset)
- [Training with ETR](#training-with-etr)
- [Understanding the Results](#understanding-the-results)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Overview

The **MipNeRF360** dataset contains high-quality multi-view images captured in both indoor and outdoor environments. This guide shows you how to:

1. Download and prepare MipNeRF360 scenes
2. Train Triangle Splatting models on these scenes
3. Apply ETR transformations for enhanced rendering
4. Analyze and visualize the results

### What is MipNeRF360?

MipNeRF360 is a benchmark dataset for neural radiance fields research, featuring:
- **9 high-quality scenes** (indoor and outdoor)
- **Multi-view images** with camera parameters
- **COLMAP sparse reconstructions** with point clouds
- **Ground truth test views** for evaluation

**Citation:**
```
@article{barron2022mipnerf360,
  title={Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields},
  author={Barron, Jonathan T and Mildenhall, Ben and Verbin, Dor and Srinivasan, Pratul P and Hedman, Peter},
  journal={CVPR},
  year={2022}
}
```

## Quick Start

### Step 1: Download a Scene

```bash
# Download bicycle scene
python scripts/download_mipnerf360.py --scenes bicycle --output data/mipnerf360

# Or download all outdoor scenes
python scripts/download_mipnerf360.py --outdoor --output data/mipnerf360
```

### Step 2: Train with ETR

```bash
# Basic training with ETR
python scripts/train_with_etr.py \
    --scene data/mipnerf360/bicycle \
    --output output/bicycle \
    --use-etr

# Or use the original train.py directly
python train.py -s data/mipnerf360/bicycle -m output/bicycle
```

### Step 3: Render and Evaluate

```bash
# Render test views
python render.py -m output/bicycle

# Compute metrics
python metrics.py -m output/bicycle
```

## Dataset Information

### Available Scenes

| Scene | Type | Images | Description | Training Time* |
|-------|------|--------|-------------|----------------|
| **bicycle** | Outdoor | ~150 | Bicycle on grass | ~2-3 hours |
| **garden** | Outdoor | ~200 | Garden with flowers | ~3-4 hours |
| **stump** | Outdoor | ~150 | Tree stump | ~2-3 hours |
| **flowers** | Outdoor | ~150 | Flower arrangement | ~2-3 hours |
| **treehill** | Outdoor | ~150 | Hill with trees | ~2-3 hours |
| **room** | Indoor | ~150 | Living room | ~2-3 hours |
| **counter** | Indoor | ~150 | Kitchen counter | ~2-3 hours |
| **kitchen** | Indoor | ~150 | Kitchen scene | ~2-3 hours |
| **bonsai** | Indoor | ~150 | Bonsai tree | ~2-3 hours |

*\*Training time on NVIDIA A100 GPU with 30,000 iterations*

### Scene Characteristics

**Outdoor Scenes:**
- Larger spatial extent
- Natural lighting variations
- Complex geometry (vegetation, terrain)
- Recommended: `--outdoor` flag for training

**Indoor Scenes:**
- Controlled lighting
- Simpler geometry
- Smaller spatial extent
- Standard training parameters work well

## Downloading the Dataset

### Using the Download Script

The `download_mipnerf360.py` script automates dataset acquisition:

```bash
# List available scenes
python scripts/download_mipnerf360.py --list

# Download specific scenes
python scripts/download_mipnerf360.py --scenes bicycle garden stump

# Download all outdoor scenes
python scripts/download_mipnerf360.py --outdoor

# Download all indoor scenes
python scripts/download_mipnerf360.py --indoor

# Download all scenes
python scripts/download_mipnerf360.py --all

# Custom output directory
python scripts/download_mipnerf360.py --scenes bicycle --output /path/to/data
```

### Manual Download

Alternatively, download directly from Google Storage:

```bash
# Outdoor scenes (360_v2.zip)
wget https://storage.googleapis.com/gresearch/refraw360/360_v2.zip

# Extra outdoor scenes (360_extra.zip)
wget https://storage.googleapis.com/gresearch/refraw360/360_extra.zip

# Extract
unzip 360_v2.zip -d data/mipnerf360/
unzip 360_extra.zip -d data/mipnerf360/
```

### Expected Directory Structure

After downloading, each scene should have this structure:

```
data/mipnerf360/bicycle/
├── images/                    # Training images
│   ├── frame_00001.jpg
│   ├── frame_00002.jpg
│   └── ...
├── images_2/                  # Test images (if available)
│   └── ...
├── images_4/                  # Additional views
│   └── ...
└── sparse/                    # COLMAP reconstruction
    └── 0/
        ├── cameras.bin        # Camera intrinsics
        ├── images.bin         # Camera poses
        └── points3D.bin       # Sparse point cloud
```

**Note:** Some scenes may have point clouds in different formats. Our multi-format loader supports:
- `points3D.ply` (PLY format)
- `points3D.pcd` (PCD format)
- `points3D.pts` (PTS format)
- `points3D.xyz` (XYZ format)
- `points3D.las` (LAS format)

## Training with ETR

### Basic Training

```bash
# Standard Triangle Splatting training
python train.py -s data/mipnerf360/bicycle -m output/bicycle
```

### Training with ETR Analysis

The ETR system analyzes triangles during training and generates:
- Fractal hierarchies for multi-scale rendering
- Triangle transformation statistics
- Scaling factor analysis
- Numerical stability metrics

```bash
# Train with ETR
python scripts/train_with_etr.py \
    --scene data/mipnerf360/bicycle \
    --output output/bicycle_etr \
    --use-etr \
    --etr-levels 7
```

### Training Parameters

**Common Parameters:**

```bash
python scripts/train_with_etr.py \
    --scene data/mipnerf360/bicycle \
    --output output/bicycle \
    --iterations 30000 \           # Training iterations
    --resolution -1 \               # -1 for original resolution
    --outdoor \                     # For outdoor scenes
    --use-etr \                     # Enable ETR
    --etr-levels 7                  # ETR fractal levels
```

**Scene-Specific Recommendations:**

```bash
# Outdoor scenes (bicycle, garden, stump, flowers, treehill)
python scripts/train_with_etr.py \
    --scene data/mipnerf360/bicycle \
    --output output/bicycle \
    --outdoor \
    --iterations 30000

# Indoor scenes (room, counter, kitchen, bonsai)
python scripts/train_with_etr.py \
    --scene data/mipnerf360/room \
    --output output/room \
    --iterations 30000
```

### ETR Configuration

When `--use-etr` is enabled, an ETR configuration file is created:

```json
{
  "enabled": true,
  "fractal_levels": 7,
  "compute_metrics": true,
  "log_interval": 1000,
  "output_dir": "output/bicycle/etr_analysis"
}
```

## Understanding the Results

### Output Directory Structure

After training, your output directory will contain:

```
output/bicycle/
├── point_cloud/
│   └── iteration_30000/
│       └── point_cloud.ply      # Final model
├── cfg_args                     # Training configuration
├── cameras.json                 # Camera parameters
├── input.ply                    # Input point cloud
└── etr_analysis/               # ETR results (if enabled)
    ├── fractal_hierarchies/    # Triangle hierarchies
    ├── metrics/                # ETR metrics logs
    └── visualizations/         # Charts and plots
```

### ETR Analysis Results

When training with ETR, you'll get:

1. **Fractal Hierarchies**
   - Multi-level triangle transformations
   - Right triangle → Left triangle pairs
   - Scaling factor progressions

2. **Triangle Statistics**
   - Distribution of triangle sizes
   - Transformation stability metrics
   - Pythagorean validation results

3. **Visualization Data**
   - Scaling factor charts
   - Triangle distribution plots
   - Level-by-level analysis

### Viewing Results

```bash
# Render novel views
python render.py -m output/bicycle

# Compute PSNR, SSIM, LPIPS
python metrics.py -m output/bicycle

# View ETR analysis
ls output/bicycle/etr_analysis/
```

## Advanced Usage

### Batch Training Multiple Scenes

Create a script to train all outdoor scenes:

```bash
#!/bin/bash
# train_all_outdoor.sh

SCENES="bicycle garden stump flowers treehill"
OUTPUT_BASE="output"

for scene in $SCENES; do
    echo "Training scene: $scene"
    python scripts/train_with_etr.py \
        --scene data/mipnerf360/$scene \
        --output $OUTPUT_BASE/$scene \
        --outdoor \
        --use-etr \
        --iterations 30000
done
```

### Custom ETR Levels

Adjust fractal hierarchy depth based on scene complexity:

```bash
# Simple scene - fewer levels
python scripts/train_with_etr.py \
    --scene data/mipnerf360/bonsai \
    --output output/bonsai \
    --use-etr \
    --etr-levels 5

# Complex scene - more levels
python scripts/train_with_etr.py \
    --scene data/mipnerf360/garden \
    --output output/garden \
    --outdoor \
    --use-etr \
    --etr-levels 10
```

### Resume Training

Resume from a checkpoint:

```bash
python train.py \
    -s data/mipnerf360/bicycle \
    -m output/bicycle \
    --start_checkpoint output/bicycle/chkpnt30000.pth
```

### Custom Resolution

Train at different resolutions:

```bash
# Half resolution (faster training)
python train.py -s data/mipnerf360/bicycle -m output/bicycle -r 2

# Quarter resolution (very fast)
python train.py -s data/mipnerf360/bicycle -m output/bicycle -r 4

# Full resolution
python train.py -s data/mipnerf360/bicycle -m output/bicycle -r 1
```

## Integrating ETR into Training Pipeline

### Option 1: Modify train.py (Advanced)

To fully integrate ETR into the training loop, you can modify `train.py`:

```python
# Add at the top of train.py
from etr.core.triangle_adapter import TriangleSplattingAdapter
from etr.utils.etr_metrics import ETRMetrics

# In training function
if use_etr:
    etr_adapter = TriangleSplattingAdapter()
    etr_metrics = ETRMetrics()

    # During training loop
    if iteration % 1000 == 0:
        # Extract triangles
        triangles_data = triangles.get_xyz  # Get triangle vertices

        # Convert to ETR format
        rt_triangles = etr_adapter.extract_right_triangles(triangles_data)

        # Compute metrics
        stats = etr_metrics.compute_statistics(rt_triangles)

        # Log to TensorBoard
        etr_metrics.log_to_tensorboard(tb_writer, iteration)
```

### Option 2: Post-Training Analysis

Analyze a trained model with ETR:

```python
# analyze_with_etr.py
import torch
from etr.core.triangle_adapter import TriangleSplattingAdapter
from etr.core.entangled_triangles import FractalTriangleHierarchy

# Load trained model
checkpoint = torch.load('output/bicycle/chkpnt30000.pth')

# Extract triangles
adapter = TriangleSplattingAdapter()
triangles = adapter.extract_right_triangles(checkpoint['xyz'])

# Generate fractal hierarchies
for triangle in triangles[:100]:  # Sample 100 triangles
    hierarchy = FractalTriangleHierarchy(triangle, max_levels=7)
    levels = hierarchy.generate()
    # Analyze levels...
```

## Troubleshooting

### Issue: "COLMAP sparse reconstruction not found"

**Solution:** The scene may need COLMAP processing first.

```bash
# Install COLMAP
sudo apt-get install colmap

# Run COLMAP on images
colmap automatic_reconstructor \
    --image_path data/mipnerf360/bicycle/images \
    --workspace_path data/mipnerf360/bicycle/sparse
```

### Issue: "Out of memory during training"

**Solutions:**

1. Reduce resolution:
```bash
python train.py -s data/mipnerf360/bicycle -m output/bicycle -r 2
```

2. Reduce max shapes:
```bash
python train.py -s data/mipnerf360/bicycle -m output/bicycle --max_shapes 2000000
```

3. Use a smaller scene (start with bonsai or counter)

### Issue: "ETR modules not found"

**Solution:** Ensure ETR dependencies are installed:

```bash
pip install numpy torch

# Verify import
python -c "from etr.core.entangled_triangles import RightTriangle; print('ETR OK')"
```

### Issue: "Training too slow"

**Solutions:**

1. Reduce iterations:
```bash
python train.py -s data/mipnerf360/bicycle -m output/bicycle --iterations 15000
```

2. Reduce resolution:
```bash
python train.py -s data/mipnerf360/bicycle -m output/bicycle -r 2
```

3. Disable some regularizations

### Issue: "Point cloud not loading"

**Solution:** Our multi-format loader should handle this automatically. Check supported formats:

```bash
ls data/mipnerf360/bicycle/sparse/0/points3D.*

# If you have a different format, convert it:
python utils/convert_point_cloud.py --input points3D.bin --output points3D.ply
```

## Performance Benchmarks

Training times on different hardware:

| Hardware | Scene | Resolution | Iterations | Time |
|----------|-------|------------|------------|------|
| A100 40GB | bicycle | Full | 30,000 | ~2.5 hrs |
| RTX 3090 | bicycle | Full | 30,000 | ~4 hrs |
| RTX 3080 | bicycle | Half | 30,000 | ~3 hrs |
| V100 16GB | bicycle | Half | 30,000 | ~6 hrs |

## Best Practices

### 1. Start Small

Begin with a simple indoor scene:

```bash
python scripts/download_mipnerf360.py --scenes bonsai
python train.py -s data/mipnerf360/bonsai -m output/bonsai
```

### 2. Use Appropriate Flags

- Outdoor scenes: Always use `--outdoor`
- Large scenes: Consider reducing resolution
- Quick tests: Use `--iterations 10000`

### 3. Monitor Training

Check training progress:

```bash
# View TensorBoard logs
tensorboard --logdir output/bicycle

# Check metrics in real-time
tail -f output/bicycle/train_log.txt
```

### 4. Verify Results

Always render and evaluate:

```bash
python render.py -m output/bicycle
python metrics.py -m output/bicycle
```

### 5. Save Checkpoints

Training saves checkpoints automatically at iterations 7,000 and 30,000. Use them to resume if needed.

## Additional Resources

- **Triangle Splatting Paper**: https://arxiv.org/abs/2505.19175
- **MipNeRF360 Paper**: https://jonbarron.info/mipnerf360/
- **ETR Documentation**: [../etr/README.md](../etr/README.md)
- **Point Cloud Formats**: [POINT_CLOUD_FORMATS.md](POINT_CLOUD_FORMATS.md)
- **Web Interface**: [../web/README.md](../web/README.md)

## Citation

If you use this work, please cite:

```bibtex
@article{held2024trianglesplatting,
  title={Triangle Splatting for Real-Time Radiance Field Rendering},
  author={Held, Jan and Vandeghen, Renaud and Deliege, Adrien and others},
  journal={arXiv preprint arXiv:2505.19175},
  year={2024}
}

@article{barron2022mipnerf360,
  title={Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields},
  author={Barron, Jonathan T and Mildenhall, Ben and Verbin, Dor and others},
  journal={CVPR},
  year={2022}
}
```

---

**Need Help?**

- Check [PROJECT_STATUS.md](../PROJECT_STATUS.md) for system overview
- Review [Integration Guide](../etr/docs/INTEGRATION_GUIDE.md) for ETR details
- Open an issue on GitHub with logs and error messages

**Happy Training! 🚀**
