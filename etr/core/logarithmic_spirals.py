"""
Polygonal Spiral Generation using Right Triangle Fractals
Based on Grant's arXiv paper 2111.02895
"""

import math
from typing import Tuple, List, Optional
from dataclasses import dataclass

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class SpiralConfiguration:
    """Configuration for polygonal spiral generation."""
    logarithmic_base: float  # Hypotenuse/Height ratio
    modular_config: int  # 14 (heptagon), 16 (octagon), 24 (dodecagon)
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = f"Mod{self.modular_config}_Base{self.logarithmic_base:.4f}"


class PolygonalSpiralGenerator:
    """
    Generate natural spirals using right triangle fractal progressions.

    Superior to traditional e-based logarithmic spirals for modeling
    galaxies, hurricanes, and other natural phenomena.
    """

    # Pre-configured spirals from Grant's research
    HEPTAGONAL = SpiralConfiguration(1.11, 14, "Heptagonal")
    OCTAGONAL = SpiralConfiguration(1.15, 16, "Octagonal")
    MOD24 = SpiralConfiguration(1.0526, 24, "Mod24_Icositetragon")

    def __init__(self, config: SpiralConfiguration):
        """Initialize spiral generator with configuration."""
        self.config = config
        self.angular_increment = 2 * math.pi / config.modular_config

    def generate_spiral_points(self,
                              turns: int,
                              points_per_turn: Optional[int] = None):
        """
        Generate spiral coordinates in polar form.

        Args:
            turns: Number of complete revolutions
            points_per_turn: Points per turn (default: modular_config)

        Returns:
            (N, 2) array of (r, theta) coordinates
        """
        if not NUMPY_AVAILABLE:
            raise RuntimeError("NumPy is required for spiral generation")

        if points_per_turn is None:
            points_per_turn = self.config.modular_config

        total_points = turns * points_per_turn
        points = np.zeros((total_points, 2))

        for i in range(total_points):
            # Position on modular wheel
            n = i / points_per_turn

            # Exponential radius growth (KEY FORMULA)
            r = self.config.logarithmic_base ** n

            # Angular position
            theta = i * (self.angular_increment * self.config.modular_config / points_per_turn)

            points[i] = [r, theta]

        return points

    def generate_cartesian_spiral(self, turns: int,
                                  points_per_turn: Optional[int] = None):
        """Generate spiral in Cartesian (x, y) coordinates."""
        if not NUMPY_AVAILABLE:
            raise RuntimeError("NumPy is required for spiral generation")

        polar = self.generate_spiral_points(turns, points_per_turn)

        x = polar[:, 0] * np.cos(polar[:, 1])
        y = polar[:, 0] * np.sin(polar[:, 1])

        return np.column_stack([x, y])

    def generate_3d_spiral_mesh(self,
                               base_triangle: Tuple[float, float, float],
                               turns: int) -> Tuple:
        """
        Generate 3D spiral mesh with right triangles at each position.

        Args:
            base_triangle: (base, height, hypotenuse) of triangle to place
            turns: Number of spiral turns

        Returns:
            (vertices, faces) for mesh rendering
        """
        if not NUMPY_AVAILABLE:
            raise RuntimeError("NumPy is required for spiral generation")

        spiral_points = self.generate_spiral_points(turns)

        vertices = []
        faces = []

        base, height, hyp = base_triangle

        for i, (r, theta) in enumerate(spiral_points):
            # Center of triangle at spiral position
            cx = r * np.cos(theta)
            cy = r * np.sin(theta)
            cz = 0

            # Scale triangle by radius
            scaled_base = base * r
            scaled_height = height * r

            # Triangle vertices rotated to align with spiral
            v0 = np.array([cx, cy, cz])
            v1 = v0 + scaled_base * np.array([np.cos(theta), np.sin(theta), 0])
            v2 = v0 + scaled_height * np.array([-np.sin(theta), np.cos(theta), 0])

            vert_idx = len(vertices)
            vertices.extend([v0, v1, v2])
            faces.append([vert_idx, vert_idx + 1, vert_idx + 2])

        return np.array(vertices), np.array(faces)


def visualize_spiral_comparison(output_path: str = "etr/docs/spiral_comparison.png"):
    """
    Compare traditional e-based spiral with polygonal triangle spiral.
    Requires matplotlib.
    """
    if not NUMPY_AVAILABLE:
        print("NumPy not available, skipping visualization")
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not available, skipping visualization")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # Traditional logarithmic spiral (e-based)
    theta_trad = np.linspace(0, 4*np.pi, 500)
    r_trad = np.exp(0.2 * theta_trad)
    x_trad = r_trad * np.cos(theta_trad)
    y_trad = r_trad * np.sin(theta_trad)

    axes[0].plot(x_trad, y_trad, 'b-', linewidth=2)
    axes[0].set_title("Traditional e-based Logarithmic Spiral", fontsize=14)
    axes[0].grid(True, alpha=0.3)
    axes[0].axis('equal')

    # Polygonal triangle spiral (Grant's method)
    heptagonal = PolygonalSpiralGenerator(PolygonalSpiralGenerator.HEPTAGONAL)
    cart_points = heptagonal.generate_cartesian_spiral(turns=4, points_per_turn=100)

    axes[1].plot(cart_points[:, 0], cart_points[:, 1], 'r-', linewidth=2)
    axes[1].set_title("Polygonal Triangle Spiral (Heptagonal, Mod 14)", fontsize=14)
    axes[1].grid(True, alpha=0.3)
    axes[1].axis('equal')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Spiral comparison saved to {output_path}")


if __name__ == "__main__":
    if NUMPY_AVAILABLE:
        visualize_spiral_comparison()
    else:
        print("NumPy not available. Install dependencies to run spiral generation.")
