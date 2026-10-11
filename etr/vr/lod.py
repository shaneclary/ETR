"""
Foveated level of detail on the altitude tree.

Each triangle is split along its altitude until its angular size, seen from
the eye, is below a threshold that depends on how far it sits from the gaze
direction: tight in the fovea, loose in the periphery. Because every
altitude split tiles its parent exactly, any cut of the tree covers the
same surface as the original triangles; for right triangles the pieces are
scaled copies of their parents, so the Thoth shape survives every level.

Children inherit their parent's attributes here, which keeps coverage
exact but adds no detail. Detail per child is the training side's job: a
tree built during densification gives every node its own colour and
opacity, and this cut then chooses between them per frame.
"""

import math

import numpy as np

from etr.core.altitude_subdivision import altitude_split_batch, longest_sides


def angular_sizes(triangles, eye):
    """(N,) longest side over distance from the eye to the centroid, in radians (small-angle)."""
    triangles = np.asarray(triangles, dtype=np.float64)
    distances = np.linalg.norm(triangles.mean(axis=1) - np.asarray(eye, dtype=np.float64), axis=-1)
    return longest_sides(triangles) / np.maximum(distances, 1e-12)


def eccentricities(triangles, eye, gaze_direction):
    """(N,) angle in radians between the gaze direction and the direction to each centroid."""
    triangles = np.asarray(triangles, dtype=np.float64)
    to_centroids = triangles.mean(axis=1) - np.asarray(eye, dtype=np.float64)
    to_centroids /= np.maximum(np.linalg.norm(to_centroids, axis=-1, keepdims=True), 1e-12)
    gaze = np.asarray(gaze_direction, dtype=np.float64)
    gaze = gaze / np.linalg.norm(gaze)
    return np.arccos(np.clip(to_centroids @ gaze, -1.0, 1.0))


def foveated_thresholds(eccentricity, fovea_threshold, periphery_threshold,
                        fovea_radius=math.radians(5.0), periphery_radius=math.radians(30.0)):
    """
    Angular-size threshold per triangle: fovea_threshold inside fovea_radius,
    rising linearly to periphery_threshold at periphery_radius and beyond.
    """
    ramp = np.clip((eccentricity - fovea_radius) / (periphery_radius - fovea_radius), 0.0, 1.0)
    return fovea_threshold + ramp * (periphery_threshold - fovea_threshold)


def foveated_cut(triangles, eye, gaze_direction, fovea_threshold, periphery_threshold,
                 fovea_radius=math.radians(5.0), periphery_radius=math.radians(30.0), max_depth: int = 8):
    """
    Split triangles along their altitudes until each is below its foveated
    angular-size threshold or max_depth is reached.

    Returns:
        (selected (M, 3, 3), parent (M,) index of the input triangle each piece came from,
         depth (M,) number of splits applied)
    """
    pending = np.asarray(triangles, dtype=np.float64)
    parents = np.arange(len(pending))
    depths = np.zeros(len(pending), dtype=int)
    selected, selected_parents, selected_depths = [], [], []

    for _ in range(max_depth):
        if len(pending) == 0:
            break
        thresholds = foveated_thresholds(eccentricities(pending, eye, gaze_direction),
                                         fovea_threshold, periphery_threshold, fovea_radius, periphery_radius)
        fine_enough = angular_sizes(pending, eye) <= thresholds
        selected.append(pending[fine_enough])
        selected_parents.append(parents[fine_enough])
        selected_depths.append(depths[fine_enough])

        pending = altitude_split_batch(pending[~fine_enough]).reshape(-1, 3, 3)
        parents = np.repeat(parents[~fine_enough], 2)
        depths = np.repeat(depths[~fine_enough] + 1, 2)

    selected.append(pending)
    selected_parents.append(parents)
    selected_depths.append(depths)
    return (np.concatenate(selected, axis=0),
            np.concatenate(selected_parents, axis=0),
            np.concatenate(selected_depths, axis=0))


def inherit_attributes(attributes, parent):
    """Per-piece attributes for a cut: each piece carries its input triangle's values (N, ...) -> (M, ...)."""
    return np.asarray(attributes)[parent]
