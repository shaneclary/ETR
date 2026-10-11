"""
Altitude subdivision: the self-similar split of a right triangle.

The altitude from the right angle to the hypotenuse divides a right triangle
into two triangles similar to it, scaled by base/hypotenuse and
height/hypotenuse (the geometric-mean theorem). Their areas add up to the
parent's because (base/c)² + (height/c)² = 1, so the two children tile the
parent exactly: Pythagoras is the conservation law of this subdivision.
Repeating the split on the larger child gives scales (height/c)^k = L^-k with
L = c/height, the growth ratio of Grant's polygonal spirals (arXiv
2111.02895), where each triangle's hypotenuse is the previous height.

For any triangle, the altitude from the vertex with the largest angle still
tiles the parent exactly; the children are similar to it only when that
angle is 90°.
"""

import numpy as np

from .entangled_triangles import RightTriangle


def altitude_split_right_triangle(rt: RightTriangle):
    """
    The two children of rt, as (smaller, larger).

    The smaller child is rt scaled by base/c and has hypotenuse = rt.base;
    the larger is rt scaled by height/c and has hypotenuse = rt.height.
    """
    children = []
    for scale in (rt.base / rt.hypotenuse, rt.height / rt.hypotenuse):
        children.append(RightTriangle(base=rt.base * scale,
                                      height=rt.height * scale,
                                      hypotenuse=rt.hypotenuse * scale))
    return tuple(children)


def spine(rt: RightTriangle, n: int) -> RightTriangle:
    """
    The n-th larger child: rt scaled by (height/c)^n = L^-n.

    This is Grant's spiral progression (hypotenuse(n+1) = height(n)) run
    inwards; n = 0 is rt itself.
    """
    scale = (rt.height / rt.hypotenuse) ** n
    return RightTriangle(base=rt.base * scale, height=rt.height * scale, hypotenuse=rt.hypotenuse * scale)


def altitude_split(vertices):
    """
    Split one triangle along the altitude from its largest angle.

    Args:
        vertices: (3, 3) array of the vertices v0, v1, v2

    Returns:
        (2, 3, 3) array of the two children, each with the same winding as
        the parent and the altitude foot as its second vertex (so, for a
        right parent, the right angle sits at index 1, like the renderer's
        init layout). Together they tile the parent exactly.
    """
    return altitude_split_batch(np.asarray(vertices, dtype=np.float64)[None])[0]


def altitude_split_batch(triangles):
    """
    altitude_split for a batch: (N, 3, 3) -> (N, 2, 3, 3).

    The largest angle is opposite the longest side, so its altitude foot
    lies inside that side and the split is always valid.
    """
    triangles = np.asarray(triangles, dtype=np.float64)
    side_lengths = np.stack([np.linalg.norm(triangles[:, (i + 1) % 3] - triangles[:, (i + 2) % 3], axis=-1)
                             for i in range(3)], axis=1)  # side i is opposite vertex i
    apex = np.argmax(side_lengths, axis=1)
    rows = np.arange(len(triangles))
    p = triangles[rows, apex]              # vertex with the largest angle
    q = triangles[rows, (apex + 1) % 3]    # the longest side runs q -> r, keeping the parent's winding
    r = triangles[rows, (apex + 2) % 3]

    qr = r - q
    t = np.einsum('ij,ij->i', p - q, qr) / np.einsum('ij,ij->i', qr, qr)
    foot = q + t[:, None] * qr

    return np.stack([np.stack([q, foot, p], axis=1),
                     np.stack([p, foot, r], axis=1)], axis=1)


def altitude_tree(vertices, depth: int):
    """
    Levels 0..depth of repeated altitude splits: level k holds 2^k triangles.

    Returns:
        list of (2^k, 3, 3) arrays; every level tiles the root exactly
    """
    levels = [np.asarray(vertices, dtype=np.float64)[None]]
    for _ in range(depth):
        levels.append(altitude_split_batch(levels[-1]).reshape(-1, 3, 3))
    return levels


def subdivide_until(vertices, max_longest_side: float, max_depth: int = 32):
    """
    Split recursively until every triangle's longest side is at most
    max_longest_side (or max_depth is reached). Returns (M, 3, 3) tiling
    the root exactly.
    """
    done = []
    pending = np.asarray(vertices, dtype=np.float64)[None]
    for _ in range(max_depth):
        if len(pending) == 0:
            break
        longest = longest_sides(pending)
        small_enough = longest <= max_longest_side
        done.append(pending[small_enough])
        pending = altitude_split_batch(pending[~small_enough]).reshape(-1, 3, 3)
    done.append(pending)
    return np.concatenate(done, axis=0)


def longest_sides(triangles):
    """(N,) longest side of each triangle in an (N, 3, 3) batch."""
    triangles = np.asarray(triangles, dtype=np.float64)
    return np.max(np.stack([np.linalg.norm(triangles[:, (i + 1) % 3] - triangles[:, (i + 2) % 3], axis=-1)
                            for i in range(3)], axis=1), axis=1)


def triangle_areas(triangles):
    """(N,) areas of an (N, 3, 3) batch."""
    triangles = np.asarray(triangles, dtype=np.float64)
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    return 0.5 * np.linalg.norm(cross, axis=-1)
