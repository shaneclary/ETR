"""
Multi-format Point Cloud Loader for Triangle Splatting

Supports the following formats:
- PLY (Polygon File Format) - already supported, enhanced
- PCD (Point Cloud Data - PCL format)
- PTS (Point Cloud format)
- XYZ (ASCII point cloud format)
- LAS/LAZ (LiDAR format)

All formats are converted to BasicPointCloud(points, colors, normals)
"""

import numpy as np
import os
import struct
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from plyfile import PlyData, PlyElement
    PLY_AVAILABLE = True
except ImportError:
    PLY_AVAILABLE = False
    logger.warning("plyfile not available. PLY format support limited.")

try:
    import laspy
    LAS_AVAILABLE = True
except ImportError:
    LAS_AVAILABLE = False
    logger.warning("laspy not available. LAS/LAZ format not supported.")

from scene.triangle_model import BasicPointCloud


class PointCloudLoader:
    """
    Unified point cloud loader supporting multiple formats.

    Supported formats:
    - PLY: Polygon File Format (binary or ASCII)
    - PCD: Point Cloud Data (PCL library format)
    - PTS: Simple point cloud format
    - XYZ: ASCII point cloud (X Y Z [R G B] [Nx Ny Nz])
    - LAS/LAZ: LiDAR format
    """

    @staticmethod
    def load(filepath: str) -> BasicPointCloud:
        """
        Load point cloud from file. Format is auto-detected from extension.

        Args:
            filepath: Path to point cloud file

        Returns:
            BasicPointCloud with points, colors, and normals
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Point cloud file not found: {filepath}")

        ext = filepath.suffix.lower()

        # Route to appropriate loader based on extension
        if ext == '.ply':
            return PointCloudLoader.load_ply(str(filepath))
        elif ext == '.pcd':
            return PointCloudLoader.load_pcd(str(filepath))
        elif ext == '.pts':
            return PointCloudLoader.load_pts(str(filepath))
        elif ext in ['.xyz', '.txt']:
            return PointCloudLoader.load_xyz(str(filepath))
        elif ext in ['.las', '.laz']:
            return PointCloudLoader.load_las(str(filepath))
        else:
            raise ValueError(f"Unsupported point cloud format: {ext}")

    @staticmethod
    def load_ply(filepath: str) -> BasicPointCloud:
        """
        Load PLY format point cloud.

        Enhanced version with better error handling and color normalization.
        """
        if not PLY_AVAILABLE:
            raise ImportError("plyfile is required for PLY support. Install with: pip install plyfile")

        try:
            plydata = PlyData.read(filepath)
            vertices = plydata['vertex']

            # Extract positions
            positions = np.vstack([vertices['x'], vertices['y'], vertices['z']]).T

            # Extract colors (handle different naming conventions)
            colors = None
            if 'red' in vertices.data.dtype.names:
                colors = np.vstack([vertices['red'], vertices['green'], vertices['blue']]).T
                # Normalize if values are in 0-255 range
                if colors.max() > 1.0:
                    colors = colors / 255.0
            elif 'r' in vertices.data.dtype.names:
                colors = np.vstack([vertices['r'], vertices['g'], vertices['b']]).T
                if colors.max() > 1.0:
                    colors = colors / 255.0
            else:
                # Default to white if no colors
                logger.warning(f"No color information in PLY file {filepath}, using white")
                colors = np.ones_like(positions)

            # Extract normals (if available)
            normals = None
            if 'nx' in vertices.data.dtype.names:
                normals = np.vstack([vertices['nx'], vertices['ny'], vertices['nz']]).T
            elif 'normal_x' in vertices.data.dtype.names:
                normals = np.vstack([vertices['normal_x'], vertices['normal_y'], vertices['normal_z']]).T
            else:
                logger.warning(f"No normal information in PLY file {filepath}, using zeros")
                normals = np.zeros_like(positions)

            logger.info(f"Loaded PLY: {len(positions)} points")
            return BasicPointCloud(points=positions, colors=colors, normals=normals)

        except Exception as e:
            raise RuntimeError(f"Failed to load PLY file {filepath}: {e}")

    @staticmethod
    def load_pcd(filepath: str) -> BasicPointCloud:
        """
        Load PCD (Point Cloud Data) format from PCL library.

        Supports both ASCII and binary PCD formats.
        """
        with open(filepath, 'rb') as f:
            # Read header
            header = {}
            while True:
                line = f.readline().decode('ascii').strip()
                if line.startswith('DATA'):
                    data_type = line.split()[1]
                    break
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        header[parts[0]] = parts[1:]

            # Parse header
            fields = header.get('FIELDS', [])
            size = header.get('SIZE', [])
            type_ = header.get('TYPE', [])
            count = header.get('COUNT', [])
            width = int(header.get('WIDTH', [0])[0])
            height = int(header.get('HEIGHT', [1])[0])
            points_count = int(header.get('POINTS', [0])[0])

            # Determine field indices
            x_idx = fields.index('x') if 'x' in fields else None
            y_idx = fields.index('y') if 'y' in fields else None
            z_idx = fields.index('z') if 'z' in fields else None

            rgb_idx = fields.index('rgb') if 'rgb' in fields else None
            r_idx = fields.index('r') if 'r' in fields else None

            nx_idx = fields.index('normal_x') if 'normal_x' in fields else None

            if data_type == 'ascii':
                # ASCII format
                data = np.loadtxt(f)

                positions = data[:, [x_idx, y_idx, z_idx]] if x_idx is not None else None

                if rgb_idx is not None:
                    # Packed RGB
                    rgb_packed = data[:, rgb_idx].astype(np.uint32)
                    r = ((rgb_packed >> 16) & 0xFF) / 255.0
                    g = ((rgb_packed >> 8) & 0xFF) / 255.0
                    b = (rgb_packed & 0xFF) / 255.0
                    colors = np.column_stack([r, g, b])
                elif r_idx is not None:
                    colors = data[:, [r_idx, r_idx+1, r_idx+2]]
                    if colors.max() > 1.0:
                        colors = colors / 255.0
                else:
                    colors = np.ones_like(positions)

                if nx_idx is not None:
                    normals = data[:, [nx_idx, nx_idx+1, nx_idx+2]]
                else:
                    normals = np.zeros_like(positions)

            else:  # binary
                # Binary format - read raw bytes
                point_step = sum([int(s) * int(c) for s, c in zip(size, count)])
                data_binary = f.read()

                # Simple parsing for XYZ
                positions = []
                colors = []
                normals = []

                for i in range(points_count):
                    offset = i * point_step
                    # Read XYZ (assuming float32)
                    x = struct.unpack('f', data_binary[offset:offset+4])[0]
                    y = struct.unpack('f', data_binary[offset+4:offset+8])[0]
                    z = struct.unpack('f', data_binary[offset+8:offset+12])[0]
                    positions.append([x, y, z])

                    # Default colors and normals
                    colors.append([1.0, 1.0, 1.0])
                    normals.append([0.0, 0.0, 0.0])

                positions = np.array(positions)
                colors = np.array(colors)
                normals = np.array(normals)

            logger.info(f"Loaded PCD: {len(positions)} points")
            return BasicPointCloud(points=positions, colors=colors, normals=normals)

    @staticmethod
    def load_pts(filepath: str) -> BasicPointCloud:
        """
        Load PTS format point cloud.

        PTS format: X Y Z [I] [R G B] [Nx Ny Nz]
        Usually: X Y Z Intensity R G B
        """
        data = np.loadtxt(filepath)

        # PTS usually has at least XYZ and intensity
        if data.shape[1] < 3:
            raise ValueError(f"PTS file must have at least X, Y, Z columns. Got {data.shape[1]}")

        positions = data[:, :3]

        # Try to extract colors (usually columns 4, 5, 6 after intensity)
        if data.shape[1] >= 7:
            # Columns 4-6 are R, G, B (after X, Y, Z, Intensity)
            colors = data[:, 4:7]
            if colors.max() > 1.0:
                colors = colors / 255.0
        elif data.shape[1] >= 6:
            # Might be X Y Z R G B without intensity
            colors = data[:, 3:6]
            if colors.max() > 1.0:
                colors = colors / 255.0
        else:
            colors = np.ones_like(positions)

        # Try to extract normals if available
        if data.shape[1] >= 10:
            normals = data[:, 7:10]
        else:
            normals = np.zeros_like(positions)

        logger.info(f"Loaded PTS: {len(positions)} points")
        return BasicPointCloud(points=positions, colors=colors, normals=normals)

    @staticmethod
    def load_xyz(filepath: str) -> BasicPointCloud:
        """
        Load XYZ ASCII format point cloud.

        Supports various formats:
        - X Y Z
        - X Y Z R G B
        - X Y Z R G B Nx Ny Nz
        - X Y Z Nx Ny Nz R G B
        """
        data = np.loadtxt(filepath)

        if data.shape[1] < 3:
            raise ValueError(f"XYZ file must have at least X, Y, Z columns. Got {data.shape[1]}")

        positions = data[:, :3]

        # Heuristic to determine column layout
        if data.shape[1] == 3:
            # Only positions
            colors = np.ones_like(positions)
            normals = np.zeros_like(positions)
        elif data.shape[1] == 6:
            # Could be X Y Z R G B or X Y Z Nx Ny Nz
            # Check if values are in [0, 255] or [0, 1] range (colors) vs [-1, 1] (normals)
            second_triplet = data[:, 3:6]
            if second_triplet.max() > 1.1 or second_triplet.min() < -0.1:
                # Likely colors in 0-255 range
                colors = second_triplet
                if colors.max() > 1.0:
                    colors = colors / 255.0
                normals = np.zeros_like(positions)
            else:
                # Likely normals
                normals = second_triplet
                colors = np.ones_like(positions)
        elif data.shape[1] >= 9:
            # X Y Z R G B Nx Ny Nz or X Y Z Nx Ny Nz R G B
            # Assume first format by default
            colors = data[:, 3:6]
            if colors.max() > 1.0:
                colors = colors / 255.0
            normals = data[:, 6:9]
        else:
            # Unknown format, use defaults
            logger.warning(f"Unknown XYZ format with {data.shape[1]} columns, using defaults")
            colors = np.ones_like(positions)
            normals = np.zeros_like(positions)

        logger.info(f"Loaded XYZ: {len(positions)} points")
        return BasicPointCloud(points=positions, colors=colors, normals=normals)

    @staticmethod
    def load_las(filepath: str) -> BasicPointCloud:
        """
        Load LAS/LAZ (LiDAR) format point cloud.

        Requires laspy library.
        """
        if not LAS_AVAILABLE:
            raise ImportError("laspy is required for LAS/LAZ support. Install with: pip install laspy")

        try:
            las = laspy.read(filepath)

            # Extract positions
            positions = np.vstack([las.x, las.y, las.z]).T

            # Extract colors if available
            if hasattr(las, 'red'):
                # LAS colors are 16-bit (0-65535)
                colors = np.vstack([las.red, las.green, las.blue]).T / 65535.0
            else:
                # Use intensity as grayscale if no colors
                if hasattr(las, 'intensity'):
                    intensity = las.intensity / las.intensity.max()
                    colors = np.column_stack([intensity, intensity, intensity])
                else:
                    colors = np.ones_like(positions)

            # LAS usually doesn't have normals
            normals = np.zeros_like(positions)

            logger.info(f"Loaded LAS: {len(positions)} points from {filepath}")
            logger.info(f"  LAS version: {las.header.version}")
            logger.info(f"  Point format: {las.header.point_format.id}")

            return BasicPointCloud(points=positions, colors=colors, normals=normals)

        except Exception as e:
            raise RuntimeError(f"Failed to load LAS file {filepath}: {e}")

    @staticmethod
    def save_ply(filepath: str, pcd: BasicPointCloud):
        """
        Save point cloud to PLY format.

        Args:
            filepath: Output PLY file path
            pcd: BasicPointCloud to save
        """
        if not PLY_AVAILABLE:
            raise ImportError("plyfile is required. Install with: pip install plyfile")

        # Convert colors to 0-255 range
        colors_255 = (pcd.colors * 255).astype(np.uint8)

        # Define dtype
        dtype = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
                ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'),
                ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')]

        # Create structured array
        elements = np.empty(pcd.points.shape[0], dtype=dtype)
        attributes = np.concatenate((pcd.points, pcd.normals, colors_255), axis=1)
        elements[:] = list(map(tuple, attributes))

        # Create and write PLY
        vertex_element = PlyElement.describe(elements, 'vertex')
        ply_data = PlyData([vertex_element])
        ply_data.write(filepath)

        logger.info(f"Saved PLY: {len(pcd.points)} points to {filepath}")


# Backwards compatibility with existing code
def fetchPly(path: str) -> BasicPointCloud:
    """Legacy function - redirects to PointCloudLoader."""
    return PointCloudLoader.load_ply(path)


def storePly(path: str, xyz: np.ndarray, rgb: np.ndarray):
    """Legacy function - redirects to PointCloudLoader."""
    normals = np.zeros_like(xyz)
    pcd = BasicPointCloud(points=xyz, colors=rgb/255.0 if rgb.max() > 1.0 else rgb, normals=normals)
    PointCloudLoader.save_ply(path, pcd)


# Convenience function for auto-detection
def load_point_cloud(filepath: str) -> BasicPointCloud:
    """
    Load point cloud from any supported format (auto-detected).

    Supported formats: PLY, PCD, PTS, XYZ, LAS/LAZ
    """
    return PointCloudLoader.load(filepath)
