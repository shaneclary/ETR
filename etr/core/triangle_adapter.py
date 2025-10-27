"""
Adapter between Triangle Splatting's representation and ETR's right triangle format.

This module bridges the gap between the original vertex-based triangles
and Grant's parameterized (base, height, hypotenuse) right triangles.
"""

from typing import Tuple, Optional, Dict
import math

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from .entangled_triangles import RightTriangle
from .torch_triangle_ops import TorchTriangleOps


class TriangleSplattingAdapter:
    """
    Convert between Triangle Splatting format and ETR format.

    Triangle Splatting stores triangles as vertex positions in `_triangles_points`
    with shape (N, nb_points, 3) where nb_points is typically 3.

    We need to decompose these into right triangles for ETR processing.
    """

    @staticmethod
    def vertices_to_right_triangle(v0,
                                   v1,
                                   v2,
                                   epsilon: float = 1e-8) -> Optional[RightTriangle]:
        """
        Convert three vertices to right triangle representation.

        Strategy:
        1. Compute edge lengths
        2. Check if any angle is ~90 degrees
        3. If not right triangle, approximate or skip

        Args:
            v0, v1, v2: Triangle vertices as (x, y, z) arrays/tensors
            epsilon: Tolerance for right angle detection

        Returns:
            RightTriangle if convertible, None otherwise
        """
        if not NUMPY_AVAILABLE:
            raise RuntimeError("NumPy is required for vertex conversion")

        # Convert to numpy if needed
        if TORCH_AVAILABLE and torch.is_tensor(v0):
            v0 = v0.detach().cpu().numpy()
            v1 = v1.detach().cpu().numpy()
            v2 = v2.detach().cpu().numpy()

        # Compute edge vectors
        e0 = v1 - v0
        e1 = v2 - v1
        e2 = v0 - v2

        # Edge lengths
        a = np.linalg.norm(e0)
        b = np.linalg.norm(e1)
        c = np.linalg.norm(e2)

        # Check for right angle using dot product
        # If dot product ≈ 0, angle is 90°
        dot01 = np.dot(e0, e1)
        dot12 = np.dot(e1, e2)
        dot20 = np.dot(e2, e0)

        # Find which angle (if any) is closest to 90°
        dots = [abs(dot01), abs(dot12), abs(dot20)]
        min_dot_idx = np.argmin(dots)

        if dots[min_dot_idx] > epsilon * max(a, b, c):
            # Not a right triangle - could approximate or skip
            return None

        # Identify base, height, hypotenuse based on right angle position
        if min_dot_idx == 0:  # Right angle at v1
            base, height, hyp = a, b, c
        elif min_dot_idx == 1:  # Right angle at v2
            base, height, hyp = b, c, a
        else:  # Right angle at v0
            base, height, hyp = c, a, b

        try:
            return RightTriangle(base=base, height=height, hypotenuse=hyp)
        except ValueError:
            return None

    @staticmethod
    def right_triangle_to_vertices(rt: RightTriangle,
                                   center,
                                   rotation) -> Tuple:
        """
        Convert right triangle back to 3D vertices.

        Args:
            rt: Right triangle specification
            center: (x, y, z) center position
            rotation: Rotation matrix or quaternion

        Returns:
            (v0, v1, v2) vertex positions
        """
        if not NUMPY_AVAILABLE:
            raise RuntimeError("NumPy is required for vertex conversion")

        # Convert center to numpy
        if TORCH_AVAILABLE and torch.is_tensor(center):
            center = center.detach().cpu().numpy()

        # Convert rotation to numpy
        if TORCH_AVAILABLE and torch.is_tensor(rotation):
            rotation = rotation.detach().cpu().numpy()

        # Local 2D coordinates (right angle at origin)
        v0_local = np.array([0, 0, 0])
        v1_local = np.array([rt.base, 0, 0])
        v2_local = np.array([0, rt.height, 0])

        # Apply rotation (assuming rotation is 3x3 matrix)
        v0_rot = rotation @ v0_local
        v1_rot = rotation @ v1_local
        v2_rot = rotation @ v2_local

        # Translate to center
        v0 = v0_rot + center
        v1 = v1_rot + center
        v2 = v2_rot + center

        return v0, v1, v2

    @staticmethod
    def batch_convert_to_etr_format(triangle_data: Dict) -> Dict:
        """
        Convert entire batch of Triangle Splatting triangles to ETR format.

        Args:
            triangle_data: Dictionary from Triangle Splatting containing:
                - 'triangles_points': (N, 3, 3) tensor of triangle vertices

        Returns:
            Dictionary with ETR-formatted data including:
            - bases, heights, hypotenuses
            - scaling_factors
            - logarithmic_bases
            - valid_mask (which triangles are right triangles)
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for batch conversion")

        vertices = triangle_data.get('triangles_points')
        if vertices is None:
            raise ValueError("No triangles_points found in triangle_data")

        n_triangles = vertices.shape[0]

        bases = []
        heights = []
        hypotenuses = []
        valid_mask = []

        for i in range(n_triangles):
            v0, v1, v2 = vertices[i]
            rt = TriangleSplattingAdapter.vertices_to_right_triangle(v0, v1, v2)

            if rt is not None:
                bases.append(rt.base)
                heights.append(rt.height)
                hypotenuses.append(rt.hypotenuse)
                valid_mask.append(True)
            else:
                # Fallback for non-right triangles
                bases.append(0.0)
                heights.append(0.0)
                hypotenuses.append(0.0)
                valid_mask.append(False)

        return {
            'bases': torch.tensor(bases, dtype=torch.float32, device=vertices.device),
            'heights': torch.tensor(heights, dtype=torch.float32, device=vertices.device),
            'hypotenuses': torch.tensor(hypotenuses, dtype=torch.float32, device=vertices.device),
            'valid_mask': torch.tensor(valid_mask, dtype=torch.bool, device=vertices.device),
            'n_valid': sum(valid_mask)
        }

    @staticmethod
    def apply_etr_to_triangle_model(triangle_model) -> Dict:
        """
        Apply ETR transformation to a TriangleModel instance.

        Args:
            triangle_model: Instance of scene.TriangleModel

        Returns:
            Dictionary with original and ETR-transformed triangles
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for ETR transformation")

        # Get triangle vertices from the model
        triangles_points = triangle_model.get_triangles_points

        # Convert to ETR format
        etr_data = TriangleSplattingAdapter.batch_convert_to_etr_format({
            'triangles_points': triangles_points
        })

        # Generate left triangles for valid right triangles
        if etr_data['n_valid'] > 0:
            valid_mask = etr_data['valid_mask']

            lt_bases, lt_heights, lt_hyps, scaling = TorchTriangleOps.batch_generate_left_triangles(
                etr_data['bases'][valid_mask],
                etr_data['heights'][valid_mask],
                etr_data['hypotenuses'][valid_mask]
            )

            # Store left triangle data
            etr_data['left_bases'] = torch.zeros_like(etr_data['bases'])
            etr_data['left_heights'] = torch.zeros_like(etr_data['heights'])
            etr_data['left_hypotenuses'] = torch.zeros_like(etr_data['hypotenuses'])
            etr_data['scaling_factors'] = torch.zeros_like(etr_data['bases'])

            etr_data['left_bases'][valid_mask] = lt_bases
            etr_data['left_heights'][valid_mask] = lt_heights
            etr_data['left_hypotenuses'][valid_mask] = lt_hyps
            etr_data['scaling_factors'][valid_mask] = scaling

            # Compute logarithmic bases
            etr_data['logarithmic_bases'] = TorchTriangleOps.compute_logarithmic_bases(
                etr_data['heights'],
                etr_data['hypotenuses']
            )

        return etr_data
