"""
GPU-accelerated triangle operations using PyTorch.

For batch processing thousands/millions of triangles in Triangle Splatting.
"""

from typing import Tuple

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available. Tensor operations will not work.")


class TorchTriangleOps:
    """
    GPU-accelerated triangle operations using PyTorch.

    For batch processing thousands/millions of triangles.
    """

    @staticmethod
    def batch_generate_left_triangles(bases: 'torch.Tensor',
                                      heights: 'torch.Tensor',
                                      hypotenuses: 'torch.Tensor') -> Tuple['torch.Tensor', ...]:
        """
        Generate left triangles for batches of right triangles.

        Args:
            bases: (N,) tensor of base values
            heights: (N,) tensor of height values
            hypotenuses: (N,) tensor of hypotenuse values

        Returns:
            (lt_bases, lt_heights, lt_hypotenuses, scaling_factors)
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for batch operations")

        # Compute scaling factors
        scaling_factors = heights * hypotenuses

        # Apply transformations (note: height and hypotenuse roles swap)
        lt_heights = 1.0 / hypotenuses  # New height = 1/old_hypotenuse
        lt_hypotenuses = 1.0 / heights  # New hypotenuse = 1/old_height
        lt_bases = bases / scaling_factors  # Non-reciprocal

        return lt_bases, lt_heights, lt_hypotenuses, scaling_factors

    @staticmethod
    def validate_pythagorean_batch(bases: 'torch.Tensor',
                                    heights: 'torch.Tensor',
                                    hypotenuses: 'torch.Tensor',
                                    epsilon: float = 1e-6) -> 'torch.Tensor':
        """
        Validate Pythagorean relationship for batch of triangles.

        Returns:
            Boolean tensor indicating valid triangles
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for batch operations")

        expected = bases**2 + heights**2
        actual = hypotenuses**2
        return torch.abs(expected - actual) < epsilon

    @staticmethod
    def compute_logarithmic_bases(heights: 'torch.Tensor',
                                   hypotenuses: 'torch.Tensor') -> 'torch.Tensor':
        """Compute logarithmic base (Hypotenuse/Height) for batch."""
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for batch operations")

        return hypotenuses / heights

    @staticmethod
    def compute_scaling_factors(heights: 'torch.Tensor',
                               hypotenuses: 'torch.Tensor') -> 'torch.Tensor':
        """Compute Grant's scaling factors (Height × Hypotenuse) for batch."""
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for batch operations")

        return heights * hypotenuses
