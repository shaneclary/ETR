# Point Cloud Format Support

Triangle Splatting now supports multiple point cloud input formats for maximum flexibility.

## Supported Formats

| Format | Extension | Description | Library Required |
|--------|-----------|-------------|------------------|
| **PLY** | `.ply` | Polygon File Format (binary/ASCII) | `plyfile` ✅ |
| **PCD** | `.pcd` | Point Cloud Data (PCL format) | None (built-in parser) |
| **PTS** | `.pts` | Point cloud with intensity | None (built-in parser) |
| **XYZ** | `.xyz`, `.txt` | ASCII point cloud | None (built-in parser) |
| **LAS/LAZ** | `.las`, `.laz` | LiDAR format | `laspy` (optional) |

---

## Installation

### Basic (PLY support - already included)
```bash
pip install plyfile
```

### Full (all formats)
```bash
pip install plyfile laspy
```

---

## Format Specifications

### PLY Format (Recommended)

**Binary PLY Example:**
```
ply
format binary_little_endian 1.0
element vertex 1000
property float x
property float y
property float z
property float nx
property float ny
property float nz
property uchar red
property uchar green
property uchar blue
end_header
<binary data>
```

**Supports:**
- Points (x, y, z)
- Colors (red, green, blue or r, g, b)
- Normals (nx, ny, nz or normal_x, normal_y, normal_z)
- Both ASCII and binary formats

---

### PCD Format (Point Cloud Data)

**ASCII PCD Example:**
```
# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z rgb
SIZE 4 4 4 4
TYPE F F F U
COUNT 1 1 1 1
WIDTH 1000
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS 1000
DATA ascii
0.1 0.2 0.3 4278190080
0.2 0.3 0.4 4278190080
...
```

**Supports:**
- XYZ coordinates
- RGB colors (packed or separate)
- Normals
- Both ASCII and binary formats
- PCL (Point Cloud Library) compatible

---

### PTS Format

**Example:**
```
# X Y Z Intensity R G B
0.0 0.0 0.0 100 255 0 0
1.0 1.0 1.0 150 0 255 0
2.0 2.0 2.0 200 0 0 255
```

**Format:**
```
X Y Z [Intensity] [R G B] [Nx Ny Nz]
```

**Common variants:**
- `X Y Z Intensity R G B` (7 columns)
- `X Y Z R G B` (6 columns)
- `X Y Z` (3 columns, colors default to white)

---

### XYZ Format

**Simple XYZ:**
```
0.0 0.0 0.0
1.0 1.0 1.0
2.0 2.0 2.0
```

**XYZ with Colors:**
```
0.0 0.0 0.0 255 0 0
1.0 1.0 1.0 0 255 0
2.0 2.0 2.0 0 0 255
```

**XYZ with Colors and Normals:**
```
0.0 0.0 0.0 255 0 0 0.0 0.0 1.0
1.0 1.0 1.0 0 255 0 0.0 0.0 1.0
2.0 2.0 2.0 0 0 255 0.0 0.0 1.0
```

**Auto-detected layouts:**
- 3 columns: X Y Z (white colors, zero normals)
- 6 columns: X Y Z R G B (zero normals)
- 9 columns: X Y Z R G B Nx Ny Nz

---

### LAS/LAZ Format (LiDAR)

**Binary LiDAR format** used in aerial scanning, terrestrial scanning, etc.

**Supports:**
- High-precision XYZ (scaled integers)
- 16-bit RGB colors (0-65535)
- Intensity values
- Multiple point formats
- Compressed LAZ format
- LAS 1.2, 1.3, 1.4 versions

**Requires laspy:**
```bash
pip install laspy
```

---

## Usage Examples

### Python API

```python
from utils.point_cloud_io import load_point_cloud, PointCloudLoader

# Auto-detect format from extension
pcd = load_point_cloud("my_scan.pcd")
pcd = load_point_cloud("aerial_scan.las")
pcd = load_point_cloud("points.xyz")

# Or use specific loader
pcd = PointCloudLoader.load_pts("scan.pts")
pcd = PointCloudLoader.load_las("lidar.las")

# Access data
print(f"Points: {pcd.points.shape}")      # (N, 3)
print(f"Colors: {pcd.colors.shape}")      # (N, 3) in [0, 1]
print(f"Normals: {pcd.normals.shape}")    # (N, 3)
```

### Training with Different Formats

```bash
# Place your point cloud file in the scene directory
# Supported names:
#   sparse/0/points3D.ply
#   sparse/0/points3D.pcd
#   sparse/0/points3D.pts
#   sparse/0/points3D.xyz
#   sparse/0/points3D.las
#   point_cloud.ply
#   point_cloud.pcd
#   etc.

# Train as usual
python train.py -s <scene_path> -m <output_path>
```

### Converting Between Formats

```python
from utils.point_cloud_io import load_point_cloud, PointCloudLoader

# Load from any format
pcd = load_point_cloud("input.las")

# Save as PLY
PointCloudLoader.save_ply("output.ply", pcd)
```

---

## Scene Directory Structure

The loader searches for point clouds in the following locations (in order):

```
scene_root/
├── sparse/0/
│   ├── points3D.ply    ← Checked first
│   ├── points3D.pcd
│   ├── points3D.pts
│   ├── points3D.xyz
│   └── points3D.las
├── points3D.ply        ← Then root directory
├── points.ply
├── point_cloud.ply
├── point_cloud.pcd
├── point_cloud.pts
├── point_cloud.xyz
└── point_cloud.las
```

**The first file found will be loaded.**

---

## Format Comparison

| Feature | PLY | PCD | PTS | XYZ | LAS |
|---------|-----|-----|-----|-----|-----|
| Binary support | ✅ | ✅ | ❌ | ❌ | ✅ |
| Colors | ✅ | ✅ | ✅ | ✅ | ✅ |
| Normals | ✅ | ✅ | ✅ | ✅ | ❌ |
| Intensity | ❌ | ✅ | ✅ | ❌ | ✅ |
| Compression | ❌ | ❌ | ❌ | ❌ | ✅ (LAZ) |
| File size | Medium | Medium | Large | Large | Small |
| Speed | Fast | Fast | Medium | Medium | Fast |
| Industry standard | Research | Robotics | Scanning | Simple | LiDAR |

---

## Common Workflows

### From Photogrammetry Software

**Agisoft Metashape / RealityCapture:**
1. Export as PLY (already supported)
2. Or export as XYZ with colors
3. Place in `scene_root/sparse/0/points3D.ply`

**COLMAP:**
- Already supported via built-in conversion
- Can also manually export from COLMAP GUI

### From LiDAR Scanners

**Terrestrial/Aerial LiDAR:**
```bash
# Place LAS file directly
cp aerial_scan.las scene_root/point_cloud.las

# Train
python train.py -s scene_root -m output
```

**Post-processing:**
```python
# If LAS has too many points, downsample first
import laspy
las = laspy.read("huge_scan.las")
# ... downsample ...
las.write("downsampled.las")
```

### From PCL (Point Cloud Library)

**C++ PCL code:**
```cpp
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>

pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZRGB>);
// ... process cloud ...
pcl::io::savePCDFileBinary("output.pcd", *cloud);
```

**Then use directly:**
```bash
python train.py -s scene_with_pcd -m output
```

---

## Troubleshooting

### "laspy not available" warning
```bash
pip install laspy
```

### Colors look wrong
- Check if colors are in 0-255 or 0-1 range
- Loader auto-detects but may fail for edge cases
- Manually normalize: `colors = colors / 255.0`

### Missing normals
- Normal computation may be added in future
- Currently defaults to (0, 0, 0)
- For better results, pre-compute normals in your software

### File not found
- Check filename (case-sensitive on Linux)
- Check directory structure
- Supported names: `points3D.*`, `point_cloud.*`, `points.*`

### Large file performance
- Binary formats (PLY binary, PCD binary, LAS) are much faster than ASCII
- Consider downsampling very large point clouds (>10M points)
- LAZ compression can reduce file size significantly

---

## Creating Test Data

### Generate XYZ file
```python
import numpy as np

# Generate random points
points = np.random.rand(1000, 3) * 10
colors = np.random.randint(0, 256, (1000, 3))

# Save as XYZ with colors
data = np.column_stack([points, colors])
np.savetxt("test_cloud.xyz", data, fmt='%.6f %.6f %.6f %d %d %d')
```

### Generate PLY file
```python
from utils.point_cloud_io import PointCloudLoader, BasicPointCloud
import numpy as np

points = np.random.rand(1000, 3) * 10
colors = np.random.rand(1000, 3)  # 0-1 range
normals = np.zeros((1000, 3))

pcd = BasicPointCloud(points=points, colors=colors, normals=normals)
PointCloudLoader.save_ply("test_cloud.ply", pcd)
```

---

## API Reference

### PointCloudLoader

```python
class PointCloudLoader:
    @staticmethod
    def load(filepath: str) -> BasicPointCloud
        """Auto-detect format and load."""

    @staticmethod
    def load_ply(filepath: str) -> BasicPointCloud
        """Load PLY format."""

    @staticmethod
    def load_pcd(filepath: str) -> BasicPointCloud
        """Load PCD format."""

    @staticmethod
    def load_pts(filepath: str) -> BasicPointCloud
        """Load PTS format."""

    @staticmethod
    def load_xyz(filepath: str) -> BasicPointCloud
        """Load XYZ format."""

    @staticmethod
    def load_las(filepath: str) -> BasicPointCloud
        """Load LAS/LAZ format."""

    @staticmethod
    def save_ply(filepath: str, pcd: BasicPointCloud)
        """Save as PLY format."""
```

### BasicPointCloud

```python
class BasicPointCloud(NamedTuple):
    points: np.ndarray   # (N, 3) XYZ coordinates
    colors: np.ndarray   # (N, 3) RGB in [0, 1]
    normals: np.ndarray  # (N, 3) normal vectors
```

---

## Future Enhancements

Planned additions:
- ✅ PLY, PCD, PTS, XYZ, LAS support
- 🔄 Normal computation for formats without normals
- 🔄 Automatic downsampling for large files
- 🔄 E57 format support
- 🔄 OBJ mesh loading
- 🔄 PTX format (Leica scanners)

---

## Examples

See `etr/examples/` for:
- `convert_point_clouds.py` - Format conversion examples
- `test_loaders.py` - Test all format loaders
- `generate_test_data.py` - Create synthetic test clouds

---

## License

Point cloud format support follows the same license as Triangle Splatting.
- PLY support: Via plyfile (BSD license)
- LAS support: Via laspy (BSD license)
- PCD/PTS/XYZ: Built-in parsers (no external dependencies)
