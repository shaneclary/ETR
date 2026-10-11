"""
Stereo eye cameras from a head pose, in Triangle Splatting's camera convention.

A Camera(R, T) in this codebase has R = camera-to-world rotation (columns:
right, down, forward) and T = world-to-view translation, so the camera
centre is -R @ T. The two eyes share the head's rotation and sit ipd/2 to
either side of the head centre along the head's right axis.
"""

import math

import numpy as np
import torch

from utils.graphics_utils import getWorld2View2, getProjectionMatrix

DEFAULT_IPD = 0.064  # metres, adult mean


def eye_poses(head_rotation, head_position, ipd: float = DEFAULT_IPD):
    """
    (R, T) for the left and right eye.

    Args:
        head_rotation: (3, 3) camera-to-world rotation of the head
        head_position: (3,) head centre in world units
        ipd: interpupillary distance in the same units

    Returns:
        ((R, T_left), (R, T_right))
    """
    rotation = np.asarray(head_rotation, dtype=np.float64)
    head = np.asarray(head_position, dtype=np.float64)
    right_axis = rotation[:, 0]

    poses = []
    for side in (-1.0, 1.0):
        centre = head + side * 0.5 * ipd * right_axis
        poses.append((rotation, -rotation.T @ centre))
    return tuple(poses)


def eye_view_matrices(head_rotation, head_position, fov_x, fov_y, ipd: float = DEFAULT_IPD,
                      znear: float = 0.01, zfar: float = 100.0):
    """
    world_view_transform and full_proj_transform for both eyes, in the
    transposed (row-vector) layout Camera and MiniCam use.

    Returns:
        list of two dicts with keys world_view_transform, full_proj_transform,
        camera_center (torch float32 tensors, CPU)
    """
    projection = getProjectionMatrix(znear=znear, zfar=zfar, fovX=fov_x, fovY=fov_y).transpose(0, 1)
    eyes = []
    for rotation, translation in eye_poses(head_rotation, head_position, ipd):
        world_view = torch.tensor(getWorld2View2(rotation, translation)).transpose(0, 1)
        eyes.append({
            'world_view_transform': world_view,
            'full_proj_transform': world_view @ projection,
            'camera_center': world_view.inverse()[3, :3],
        })
    return eyes


def stereo_minicams(head_rotation, head_position, width: int, height: int, fov_x, fov_y,
                    ipd: float = DEFAULT_IPD, znear: float = 0.01, zfar: float = 100.0):
    """Two scene.cameras.MiniCam objects (left, right) ready for triangle_renderer.render."""
    from scene.cameras import MiniCam  # needs the full Triangle Splatting environment

    cams = []
    for eye in eye_view_matrices(head_rotation, head_position, fov_x, fov_y, ipd, znear, zfar):
        cams.append(MiniCam(width, height, fov_y, fov_x, znear, zfar,
                            eye['world_view_transform'], eye['full_proj_transform']))
    return tuple(cams)


def look_at_rotation(forward, up=(0.0, -1.0, 0.0)):
    """
    Camera-to-world rotation looking along `forward` (columns: right, down,
    forward). The default up vector keeps y pointing down, as COLMAP does.
    """
    forward = np.asarray(forward, dtype=np.float64)
    forward = forward / np.linalg.norm(forward)
    down = -np.asarray(up, dtype=np.float64)
    right = np.cross(down, forward)
    right = right / np.linalg.norm(right)
    down = np.cross(forward, right)
    return np.stack([right, down, forward], axis=1)


def disparity_pixels(depth: float, fov_x, width: int, ipd: float = DEFAULT_IPD) -> float:
    """Horizontal disparity, in pixels, of a point at `depth` straight ahead."""
    focal = width / (2 * math.tan(fov_x / 2))
    return ipd * focal / depth
