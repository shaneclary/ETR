# MipNeRF360 + ETR Quick Start

**Get training in 3 steps!** 🚀

## Prerequisites

```bash
# Install dependencies
micromamba create -f requirements.yaml
micromamba activate triangle_splatting

# Compile CUDA kernels
bash compile.sh
cd submodules/simple-knn && pip install . && cd ../..
```

## Step 1: Download Data (5-10 minutes)

```bash
# Download a single scene
python scripts/download_mipnerf360.py --scenes bicycle --output data/mipnerf360

# Or download all outdoor scenes
python scripts/download_mipnerf360.py --outdoor --output data/mipnerf360
```

**Available scenes:**
- **Outdoor:** bicycle, garden, stump, flowers, treehill
- **Indoor:** room, counter, kitchen, bonsai

## Step 2: Train Model (2-4 hours on A100)

### Option A: Standard Training

```bash
python train.py -s data/mipnerf360/bicycle -m output/bicycle
```

### Option B: With ETR Analysis

```bash
python scripts/train_with_etr.py \
    --scene data/mipnerf360/bicycle \
    --output output/bicycle \
    --use-etr
```

### Option C: Quick Test (Faster)

```bash
# Reduced resolution and iterations for quick testing
python train.py \
    -s data/mipnerf360/bicycle \
    -m output/bicycle_test \
    -r 2 \
    --iterations 10000
```

## Step 3: Render & Evaluate

```bash
# Render novel views
python render.py -m output/bicycle

# Compute metrics (PSNR, SSIM, LPIPS)
python metrics.py -m output/bicycle

# View with TensorBoard
tensorboard --logdir output/bicycle
```

## Training Parameters Cheatsheet

| Scene Type | Command | Notes |
|------------|---------|-------|
| **Outdoor** | `python train.py -s <scene> -m <output> --outdoor` | bicycle, garden, stump |
| **Indoor** | `python train.py -s <scene> -m <output>` | room, counter, bonsai |
| **Quick Test** | `python train.py -s <scene> -m <output> -r 2 --iterations 10000` | Fast preview |
| **High Quality** | `python train.py -s <scene> -m <output> --iterations 40000` | Best results |
| **With ETR** | `python scripts/train_with_etr.py --scene <s> --output <o> --use-etr` | ETR analysis |

## Recommended First Training

Start with the **bonsai** scene (indoor, small, fast):

```bash
# Download
python scripts/download_mipnerf360.py --scenes bonsai --output data/mipnerf360

# Train
python train.py -s data/mipnerf360/bonsai -m output/bonsai

# Evaluate
python render.py -m output/bonsai
python metrics.py -m output/bonsai
```

**Training time:** ~2 hours on RTX 3090

## Web Interface

Upload and process point clouds through the web UI:

```bash
cd web
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Pretrained Models

The HuggingFace link you provided (https://huggingface.co/jojojohn/mipnerf360_pretrained) contains **pretrained models**, not training data.

To use pretrained models:
1. Download the models from HuggingFace
2. Place in `output/<scene_name>/`
3. Run rendering directly:
   ```bash
   python render.py -m output/<scene_name>
   ```

**Note:** ETR analysis works best with training from scratch, as it analyzes triangle evolution during training.

## Troubleshooting

### "Out of memory"
```bash
# Reduce resolution
python train.py -s <scene> -m <output> -r 2

# Or reduce max shapes
python train.py -s <scene> -m <output> --max_shapes 2000000
```

### "Too slow"
```bash
# Reduce iterations
python train.py -s <scene> -m <output> --iterations 15000

# Or use lower resolution
python train.py -s <scene> -m <output> -r 4
```

### "COLMAP not found"
The downloaded scenes should include COLMAP reconstructions. If missing:
```bash
# Check sparse directory
ls data/mipnerf360/bicycle/sparse/0/

# Should see: cameras.bin, images.bin, points3D.bin (or points3D.ply)
```

## Full Documentation

- **Comprehensive Guide**: [docs/MIPNERF360_ETR_GUIDE.md](docs/MIPNERF360_ETR_GUIDE.md)
- **ETR Documentation**: [etr/README.md](etr/README.md)
- **Point Cloud Formats**: [docs/POINT_CLOUD_FORMATS.md](docs/POINT_CLOUD_FORMATS.md)
- **Web Interface**: [web/README.md](web/README.md)
- **Project Status**: [PROJECT_STATUS.md](PROJECT_STATUS.md)

## Expected Results

After training on **bicycle** scene for 30,000 iterations:

- **PSNR**: ~24-26 dB
- **SSIM**: ~0.70-0.80
- **LPIPS**: ~0.20-0.30
- **Training time**: ~2-4 hours (GPU dependent)
- **Model size**: ~200-500 MB
- **Render time**: ~20-30 FPS (1080p)

## Common Commands

```bash
# List available scenes
python scripts/download_mipnerf360.py --list

# Download all
python scripts/download_mipnerf360.py --all --output data/mipnerf360

# Train with custom parameters
python train.py \
    -s data/mipnerf360/garden \
    -m output/garden \
    --outdoor \
    --iterations 40000 \
    --white_background

# Resume from checkpoint
python train.py \
    -s data/mipnerf360/bicycle \
    -m output/bicycle \
    --start_checkpoint output/bicycle/chkpnt30000.pth

# Extract mesh
python mesh.py -m output/bicycle

# Create video
python create_video.py -m output/bicycle
```

## Next Steps

1. ✅ Download a scene
2. ✅ Train your first model
3. ✅ Render and evaluate
4. 🎯 Try different scenes (indoor vs outdoor)
5. 🎯 Experiment with ETR analysis
6. 🎯 Use web interface for point cloud upload
7. 🎯 Train on your own data

---

**Questions?** See the [full guide](docs/MIPNERF360_ETR_GUIDE.md) or check [PROJECT_STATUS.md](PROJECT_STATUS.md)

**Happy Training! 🚀**
