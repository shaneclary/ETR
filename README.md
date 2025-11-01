<h1 align="center">Triangle Splatting for Real-Time Radiance Field Rendering</h1>

<div align="center">
  <a href="https://trianglesplatting.github.io/">Project page</a> &nbsp;|&nbsp;
  <a href="https://arxiv.org/abs/2505.19175">Arxiv</a> &nbsp;|&nbsp;
</div>
<br>

<p align="center">
  Jan Held*, Renaud Vandeghen*, Adrien Deliege, Abdullah Hamdi, Silvio Giancola, Anthony Cioppa, Andrea Vedaldi, Bernard Ghanem, Andrea Tagliasacchi, Marc Van Droogenbroeck
</p>

<br>

<div align="center">
  <img src="assets/teaser.png" width="800" height="304" alt="Abstract Image">
</div>


This repo contains the official implementation for the paper "Triangle Splatting for Real-Time Radiance Field Rendering". 

Our work represents a significant advancement in radiance field rendering by introducing 3D triangles as rendering primitive. By leveraging the same primitive used in classical mesh representations, our method bridges the gap between neural rendering and traditional graphics pipelines. Triangle Splatting offers a compelling alternative to volumetric and implicit methods, achieving high visual fidelity with faster rendering performance. These results establish Triangle Splatting as a promising step toward mesh-aware neural rendering, unifying decades of GPU-accelerated graphics with modern differentiable frameworks.

## Trained Models and Rendered Test Views on MipNeRF360

All trained models and rendered test views for MipNeRF360 are available at the [following link.](https://drive.google.com/drive/folders/14Ve16-0ZR4fg-F2Sq1XbZgCHRVHAUWot?usp=sharing)

## ETR: Entangled Triangle Rendering

This repository includes an implementation of **ETR (Entangled Triangle Rendering)**, based on Robert Edward Grant's Entangled Left Triangle theory. ETR provides:

- **Mathematical framework** for analyzing right triangles in the scene
- **Fractal hierarchy generation** for level-of-detail rendering
- **Batch GPU operations** for efficient triangle transformation
- **Integration tools** for Triangle Splatting models

### Quick ETR Demo

```bash
# Run simple ETR demonstration
python etr/examples/simple_etr_demo.py

# Run full validation suite
python -m etr.validation.validation_suite
```

### ETR Documentation

- [ETR README](etr/README.md) - Complete ETR documentation
- [Integration Guide](etr/docs/INTEGRATION_GUIDE.md) - How to integrate ETR with training/rendering
- [Theory Overview](etr/README.md#theory-overview) - Mathematical foundations

For more details on ETR, see the [`etr/`](etr/) directory.

## 📁 Multi-Format Point Cloud Support

Triangle Splatting now supports multiple point cloud input formats:

| Format | Extension | Description |
|--------|-----------|-------------|
| PLY | `.ply` | Polygon File Format ✅ |
| PCD | `.pcd` | Point Cloud Data (PCL format) ✅ |
| PTS | `.pts` | Point cloud with intensity ✅ |
| XYZ | `.xyz` | ASCII point cloud ✅ |
| LAS/LAZ | `.las`/`.laz` | LiDAR format ✅ |

**Usage:** Simply place your point cloud file in the scene directory. The system will auto-detect and load it.

```bash
# Supports: points3D.ply, points3D.pcd, points3D.pts, points3D.xyz, points3D.las
python train.py -s <scene_with_any_format> -m <output>
```

See [Point Cloud Format Documentation](docs/POINT_CLOUD_FORMATS.md) for details.

## 🌐 Web Interface

A modern web application for uploading and processing point clouds through ETR:

- **Drag & Drop Upload**: Intuitive file upload interface
- **Multi-Format Support**: Works with all supported point cloud formats
- **Interactive ETR Demo**: Try transformations without uploading files
- **Real-Time Visualization**: Charts and data tables
- **System Monitoring**: Check available features and dependencies

### Quick Start

```bash
cd web
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 in your browser.

See [Web Interface Documentation](web/README.md) for detailed usage and deployment instructions.

## 🎯 Training on MipNeRF360 Dataset

Download and train on the MipNeRF360 benchmark dataset with ETR integration:

```bash
# Step 1: Download a scene (bicycle, garden, room, etc.)
python scripts/download_mipnerf360.py --scenes bicycle --output data/mipnerf360

# Step 2: Train with ETR analysis
python scripts/train_with_etr.py --scene data/mipnerf360/bicycle --output output/bicycle --use-etr

# Step 3: Render and evaluate
python render.py -m output/bicycle
python metrics.py -m output/bicycle
```

**Quick Start:** See [QUICKSTART_MIPNERF360.md](QUICKSTART_MIPNERF360.md) for immediate training

**Full Guide:** See [MipNeRF360 + ETR Guide](docs/MIPNERF360_ETR_GUIDE.md) for comprehensive instructions

**Available scenes:** bicycle, garden, stump, flowers, treehill (outdoor) | room, counter, kitchen, bonsai (indoor)

**Note on Pretrained Models:** The HuggingFace pretrained models can be used for direct rendering, but training from scratch with the MipNeRF360 dataset allows full ETR analysis and triangle transformation insights.

## Cloning the Repository + Installation

The code has been used and tested with Python 3.11 and CUDA 12.6.

You should clone the repository with the different submodules by running the following command:

```bash
git clone https://github.com/trianglesplatting/triangle-splatting --recursive
cd triangle-splatting
```

Then, we suggest to use a virtual environment to install the dependencies.

```bash
micromamba create -f requirements.yaml
```

Finally, you can compile the custom CUDA kernels by running the following command:

```bash
bash compile.sh
cd submodules/simple-knn
pip install .
```

## Training
To train our model, you can use the following command:
```bash
python train.py -s <path_to_scenes> -m <output_model_path> --eval
```

If you want to train the model on outdoor scenes, you should add the following command:  
```bash
python train.py -s <path_to_scenes> -m <output_model_path> --outdoor --eval
```

## Rendering
To render a scene, you can use the following command:
```bash
python render.py -m <path_to_model>
```

## Evaluation
To evaluate the model, you can use the following command:
```bash
python metrics.py -m <path_to_model>
```

## Video
To render a video, you can use the following command:
```bash
python create_video.py -m <path_to_model>
```

## Replication of the results
To replicate the results of our paper, you can use the following command:
```bash
python full_eval.py --output_path <output_path> -m360 <path_to_MipNeRF360> -tat <path_to_T&T>
```

## Game engine
To create your own .off file:

1. Train your scene using ```train_game_engine.py```. This version includes some modifications, such as pruning low-opacity triangles and applying an additional loss in the final training iterations to encourage higher opacity. This makes the result more compatible with how game engines render geometry. These modifications are experimental, so feel free to adjust them or try your own variants. (For example, increasing the normal loss often improves quality by making triangles better aligned and reducing black holes.)

2. Run ```create_off.py``` to convert the optimized triangles into a .off file that can be imported into a game engine. You only need to provide the path to the trained model (e.g., point_cloud_state_dict.pt) and specify the desired output file name (e.g., mesh_colored.off).

Note: The script generates fully opaque triangles. If you want to include per-triangle opacity, you can extract and activate the raw opacity values using:
```
opacity_raw = sd["opacity"]
opacity = torch.sigmoid(opacity_raw.view(-1))
opacity_uint8 = (opacity * 255).to(torch.uint8)
```
Each triangle has a single opacity value, so if needed, assign the same value to all three of its vertices when exporting with:
```
for i, face in enumerate(faces):
            r, g, b = colors[i].tolist()
            a = opacity_uint8[i].item()
            f.write(f"3 {face[0].item()} {face[1].item()} {face[2].item()} {r} {g} {b} {a}\n")
```

If you want to run some pretrained scene on a game engine for yourself, you can download the *Garden* and *Room* scenes from the [following link](https://drive.google.com/drive/folders/1_TMXEFTdEACpHHvsmc5UeZMM-cMgJ3xW?usp=sharing). 

## BibTeX
If you find our work interesting or use any part of it, please cite our paper:
```bibtex
@article{Held2025Triangle,
title = {Triangle Splatting for Real-Time Radiance Field Rendering},
author = {Held, Jan and Vandeghen, Renaud and Deliege, Adrien and Hamdi, Abdullah and Cioppa, Anthony and Giancola, Silvio and Vedaldi, Andrea and Ghanem, Bernard and Tagliasacchi, Andrea and Van Droogenbroeck, Marc},
journal = {arXiv},
year = {2025},
}
```

As Triangle Splatting builds heavily on top of 3D Convex Splatting, please also cite it.
```bibtex
@InProceedings{held20243d,
title={3D Convex Splatting: Radiance Field Rendering with 3D Smooth Convexes},
  author={Held, Jan and Vandeghen, Renaud and Hamdi, Abdullah and Deliege, Adrien and Cioppa, Anthony and Giancola, Silvio and Vedaldi, Andrea and Ghanem, Bernard and Van Droogenbroeck, Marc},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year = {2025},
}
```

## Acknowledgements
This project is built upon 3D Convex Splatting and 3D Gaussian Splatting. We want to thank the authors for their contributions.

J. Held and A. Cioppa are funded by the F.R.S.-FNRS. The research reported in this publication was supported by funding from KAUST Center of Excellence on GenAI, under award number 5940. This work was also supported by KAUST Ibn Rushd Postdoc Fellowship program. The present research benefited from computational resources made available on Lucia, the Tier-1 supercomputer of the Walloon Region, infrastructure funded by the Walloon Region under the grant agreement n°1910247.

