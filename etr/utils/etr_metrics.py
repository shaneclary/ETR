"""
ETR Metrics and Statistics

Utilities for computing and logging ETR-related metrics during training and rendering.
"""

from typing import Dict, Optional
import logging

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class ETRMetrics:
    """Compute and track ETR-related metrics."""

    @staticmethod
    def compute_statistics(etr_data: Dict) -> Dict:
        """
        Compute comprehensive statistics from ETR data.

        Args:
            etr_data: Dictionary from TriangleSplattingAdapter.apply_etr_to_triangle_model()

        Returns:
            Dictionary of computed statistics
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for metrics computation")

        valid_mask = etr_data['valid_mask']
        n_valid = etr_data['n_valid']
        n_total = len(valid_mask)

        stats = {
            'total_triangles': n_total,
            'right_triangles': n_valid,
            'right_triangle_percentage': (n_valid / n_total * 100) if n_total > 0 else 0,
        }

        if n_valid > 0:
            # Extract valid data
            bases = etr_data['bases'][valid_mask]
            heights = etr_data['heights'][valid_mask]
            hypotenuses = etr_data['hypotenuses'][valid_mask]
            scaling_factors = etr_data['scaling_factors'][valid_mask]
            log_bases = etr_data['logarithmic_bases'][valid_mask]

            # Right triangle statistics
            stats.update({
                'rt_mean_base': bases.mean().item(),
                'rt_mean_height': heights.mean().item(),
                'rt_mean_hypotenuse': hypotenuses.mean().item(),
                'rt_std_base': bases.std().item(),
                'rt_std_height': heights.std().item(),
                'rt_std_hypotenuse': hypotenuses.std().item(),
            })

            # ETR-specific statistics
            stats.update({
                'mean_scaling_factor': scaling_factors.mean().item(),
                'std_scaling_factor': scaling_factors.std().item(),
                'min_scaling_factor': scaling_factors.min().item(),
                'max_scaling_factor': scaling_factors.max().item(),
                'mean_logarithmic_base': log_bases.mean().item(),
                'std_logarithmic_base': log_bases.std().item(),
            })

            # Left triangle statistics
            if 'left_bases' in etr_data:
                lt_bases = etr_data['left_bases'][valid_mask]
                lt_heights = etr_data['left_heights'][valid_mask]
                lt_hyps = etr_data['left_hypotenuses'][valid_mask]

                stats.update({
                    'lt_mean_base': lt_bases.mean().item(),
                    'lt_mean_height': lt_heights.mean().item(),
                    'lt_mean_hypotenuse': lt_hyps.mean().item(),
                })

        return stats

    @staticmethod
    def log_statistics(stats: Dict, logger: Optional[logging.Logger] = None, prefix: str = "ETR"):
        """
        Log ETR statistics in a formatted way.

        Args:
            stats: Statistics dictionary from compute_statistics()
            logger: Logger instance (uses print if None)
            prefix: Prefix for log messages
        """
        log_func = logger.info if logger else print

        log_func("=" * 70)
        log_func(f"{prefix} Statistics")
        log_func("=" * 70)

        log_func(f"Total triangles: {stats['total_triangles']}")
        log_func(f"Right triangles: {stats['right_triangles']} "
                f"({stats['right_triangle_percentage']:.2f}%)")

        if stats['right_triangles'] > 0:
            log_func(f"\nRight Triangle Dimensions:")
            log_func(f"  Base:       {stats['rt_mean_base']:.6f} ± {stats['rt_std_base']:.6f}")
            log_func(f"  Height:     {stats['rt_mean_height']:.6f} ± {stats['rt_std_height']:.6f}")
            log_func(f"  Hypotenuse: {stats['rt_mean_hypotenuse']:.6f} ± {stats['rt_std_hypotenuse']:.6f}")

            log_func(f"\nETR Properties:")
            log_func(f"  Scaling Factor:    {stats['mean_scaling_factor']:.4f} ± {stats['std_scaling_factor']:.4f}")
            log_func(f"    Range: [{stats['min_scaling_factor']:.4f}, {stats['max_scaling_factor']:.4f}]")
            log_func(f"  Logarithmic Base:  {stats['mean_logarithmic_base']:.6f} ± {stats['std_logarithmic_base']:.6f}")

            if 'lt_mean_base' in stats:
                log_func(f"\nLeft Triangle Dimensions:")
                log_func(f"  Base:       {stats['lt_mean_base']:.6f}")
                log_func(f"  Height:     {stats['lt_mean_height']:.6f}")
                log_func(f"  Hypotenuse: {stats['lt_mean_hypotenuse']:.6f}")

        log_func("=" * 70)

    @staticmethod
    def format_for_tensorboard(stats: Dict, step: int) -> Dict:
        """
        Format statistics for TensorBoard logging.

        Args:
            stats: Statistics dictionary
            step: Training step/iteration

        Returns:
            Dictionary suitable for TensorBoard writer
        """
        tb_dict = {
            'ETR/total_triangles': stats['total_triangles'],
            'ETR/right_triangles': stats['right_triangles'],
            'ETR/right_triangle_pct': stats['right_triangle_percentage'],
        }

        if stats['right_triangles'] > 0:
            tb_dict.update({
                'ETR/RT/mean_base': stats['rt_mean_base'],
                'ETR/RT/mean_height': stats['rt_mean_height'],
                'ETR/RT/mean_hypotenuse': stats['rt_mean_hypotenuse'],
                'ETR/scaling_factor/mean': stats['mean_scaling_factor'],
                'ETR/scaling_factor/std': stats['std_scaling_factor'],
                'ETR/scaling_factor/min': stats['min_scaling_factor'],
                'ETR/scaling_factor/max': stats['max_scaling_factor'],
                'ETR/logarithmic_base/mean': stats['mean_logarithmic_base'],
                'ETR/logarithmic_base/std': stats['std_logarithmic_base'],
            })

        return tb_dict
