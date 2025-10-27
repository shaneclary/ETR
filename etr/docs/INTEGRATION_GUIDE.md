# ETR Integration Guide

This guide shows how to integrate ETR with Triangle Splatting's training and rendering pipelines.

## Training Integration

### Option 1: Add ETR Analysis to Existing Training

To add ETR analysis to your training loop without modifying core functionality:

```python
# At the top of train.py, add:
from etr.core.triangle_adapter import TriangleSplattingAdapter
from etr.utils.etr_metrics import ETRMetrics

# In the training loop (e.g., every 1000 iterations):
if iteration % 1000 == 0:
    # Apply ETR transformation
    etr_data = TriangleSplattingAdapter.apply_etr_to_triangle_model(triangle_model)

    # Compute and log statistics
    stats = ETRMetrics.compute_statistics(etr_data)
    ETRMetrics.log_statistics(stats, logger=None, prefix=f"Iteration {iteration}")

    # Optional: Log to TensorBoard
    if tb_writer:
        tb_dict = ETRMetrics.format_for_tensorboard(stats, iteration)
        for key, value in tb_dict.items():
            tb_writer.add_scalar(key, value, iteration)
```

### Option 2: Create ETR-Enhanced Training Script

Create a new training script `etr_train.py`:

```python
"""
ETR-Enhanced Triangle Splatting Training
Based on train.py with integrated ETR analysis
"""

import torch
from scene.triangle_model import TriangleModel
from etr.core.triangle_adapter import TriangleSplattingAdapter
from etr.utils.etr_metrics import ETRMetrics

# Import original training utilities
# ... (standard imports from train.py)

def training_step_with_etr(iteration, triangle_model, optimizers, scene, ...):
    """Enhanced training step with ETR monitoring."""

    # === ORIGINAL TRIANGLE SPLATTING LOGIC ===
    # [Keep all existing training code here]
    # ...

    # === ETR ANALYSIS (Every N iterations) ===
    if iteration % args.etr_analysis_freq == 0:
        with torch.no_grad():
            # Apply ETR transformation
            etr_data = TriangleSplattingAdapter.apply_etr_to_triangle_model(triangle_model)

            # Compute statistics
            stats = ETRMetrics.compute_statistics(etr_data)

            # Log to console
            ETRMetrics.log_statistics(stats, prefix=f"Iter {iteration}")

            # Log to TensorBoard
            if tb_writer:
                tb_dict = ETRMetrics.format_for_tensorboard(stats, iteration)
                for key, value in tb_dict.items():
                    tb_writer.add_scalar(key, value, iteration)

            # Save ETR data periodically
            if iteration % (args.etr_analysis_freq * 10) == 0:
                save_etr_checkpoint(etr_data, iteration, args.model_path)

    return loss  # or whatever the original function returns

def save_etr_checkpoint(etr_data, iteration, model_path):
    """Save ETR analysis checkpoint."""
    import os
    etr_dir = os.path.join(model_path, "etr_analysis")
    os.makedirs(etr_dir, exist_ok=True)

    checkpoint = {
        'iteration': iteration,
        'n_valid_right_triangles': etr_data['n_valid'],
        'scaling_factors': etr_data['scaling_factors'][etr_data['valid_mask']].cpu(),
        'logarithmic_bases': etr_data['logarithmic_bases'][etr_data['valid_mask']].cpu(),
    }

    torch.save(checkpoint, os.path.join(etr_dir, f"etr_iter_{iteration}.pt"))

# Main training loop
def main(args):
    # ... (setup code)

    # Training loop
    for iteration in range(1, args.iterations + 1):
        loss = training_step_with_etr(
            iteration, triangle_model, optimizers, scene, ...
        )

        # ... (rest of training loop)
```

## Rendering Integration

### Add ETR Analysis to Rendering

In `render.py`, add:

```python
from etr.core.triangle_adapter import TriangleSplattingAdapter
from etr.utils.etr_metrics import ETRMetrics

def render_scene_with_etr_analysis(model_path, ...):
    # Load model
    triangle_model = TriangleModel(sh_degree=3)
    triangle_model.load(model_path)

    # Apply ETR transformation
    print("Computing ETR statistics...")
    etr_data = TriangleSplattingAdapter.apply_etr_to_triangle_model(triangle_model)

    # Compute and display statistics
    stats = ETRMetrics.compute_statistics(etr_data)
    ETRMetrics.log_statistics(stats, prefix="Rendering Scene")

    # Render images
    # ... (existing rendering code)

    return rendered_images, stats
```

## Visualization Integration

### Create Comparison Visualizations

```python
import matplotlib.pyplot as plt
from etr.utils.etr_metrics import ETRMetrics

def visualize_etr_statistics(model_paths, output_path="etr_comparison.png"):
    """Compare ETR statistics across multiple models."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    models = []
    scaling_factors_all = []
    log_bases_all = []

    for model_path in model_paths:
        # Load and analyze
        model = TriangleModel(sh_degree=3)
        model.load(model_path)
        etr_data = TriangleSplattingAdapter.apply_etr_to_triangle_model(model)

        models.append(model_path.split('/')[-1])

        valid_mask = etr_data['valid_mask']
        scaling_factors_all.append(
            etr_data['scaling_factors'][valid_mask].cpu().numpy()
        )
        log_bases_all.append(
            etr_data['logarithmic_bases'][valid_mask].cpu().numpy()
        )

    # Plot scaling factor distributions
    axes[0, 0].boxplot(scaling_factors_all, labels=models)
    axes[0, 0].set_title("Scaling Factor Distribution")
    axes[0, 0].set_ylabel("Scaling Factor (Height × Hypotenuse)")
    axes[0, 0].grid(True, alpha=0.3)

    # Plot logarithmic base distributions
    axes[0, 1].boxplot(log_bases_all, labels=models)
    axes[0, 1].set_title("Logarithmic Base Distribution")
    axes[0, 1].set_ylabel("Log Base (Hypotenuse / Height)")
    axes[0, 1].grid(True, alpha=0.3)

    # Plot histograms
    for i, (sf, lb, label) in enumerate(zip(scaling_factors_all, log_bases_all, models)):
        axes[1, 0].hist(sf, bins=50, alpha=0.5, label=label)
        axes[1, 1].hist(lb, bins=50, alpha=0.5, label=label)

    axes[1, 0].set_xlabel("Scaling Factor")
    axes[1, 0].set_ylabel("Frequency")
    axes[1, 0].set_title("Scaling Factor Histogram")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].set_xlabel("Logarithmic Base")
    axes[1, 1].set_ylabel("Frequency")
    axes[1, 1].set_title("Logarithmic Base Histogram")
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Visualization saved to {output_path}")
```

## Command-Line Integration

### Add ETR Arguments

```python
# In train.py argument parser
parser.add_argument("--etr_analysis", action="store_true",
                   help="Enable ETR analysis during training")
parser.add_argument("--etr_analysis_freq", type=int, default=1000,
                   help="Frequency of ETR analysis (iterations)")
parser.add_argument("--etr_save_checkpoints", action="store_true",
                   help="Save ETR analysis checkpoints")
```

Usage:
```bash
# Train with ETR analysis every 1000 iterations
python train.py -s <scene> -m <output> --etr_analysis --etr_analysis_freq 1000

# Train with ETR checkpoints
python train.py -s <scene> -m <output> --etr_analysis --etr_save_checkpoints
```

## Best Practices

### 1. Performance Considerations

ETR analysis is computational. Recommended frequencies:
- **Training**: Every 1000-5000 iterations
- **Validation**: Once per epoch
- **Final Rendering**: Once at the end

### 2. Memory Management

For large scenes (>100K triangles):
```python
# Process in chunks
chunk_size = 10000
all_stats = []

for i in range(0, n_triangles, chunk_size):
    chunk = triangles[i:i+chunk_size]
    chunk_stats = process_chunk(chunk)
    all_stats.append(chunk_stats)

# Aggregate statistics
final_stats = aggregate_stats(all_stats)
```

### 3. Logging

Use structured logging:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ETR] %(message)s',
    handlers=[
        logging.FileHandler('etr_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ETR')
ETRMetrics.log_statistics(stats, logger=logger)
```

### 4. Checkpoint Integration

Save ETR data with model checkpoints:
```python
def save_checkpoint(iteration, model, etr_data, path):
    checkpoint = {
        'iteration': iteration,
        'model_state_dict': model.state_dict(),
        'etr_statistics': ETRMetrics.compute_statistics(etr_data),
    }
    torch.save(checkpoint, path)
```

## Troubleshooting

### Issue: "No right triangles found"

If `etr_data['n_valid'] == 0`:
- Triangle Splatting may use non-right triangles
- This is normal for some scenes
- ETR analysis will be limited but won't crash

### Issue: High memory usage

Solution:
```python
# Use torch.no_grad() for analysis
with torch.no_grad():
    etr_data = TriangleSplattingAdapter.apply_etr_to_triangle_model(model)

# Clear cache periodically
if iteration % 10000 == 0:
    torch.cuda.empty_cache()
```

### Issue: Slow analysis

Solutions:
- Increase `etr_analysis_freq`
- Process fewer triangles per analysis
- Use mixed precision: `torch.cuda.amp.autocast()`

## Example: Complete Integration

See `etr/examples/integrated_training.py` for a complete example of ETR-integrated training.

---

For more information, see:
- [ETR README](../README.md)
- [Triangle Splatting Documentation](../../README.md)
- [Validation Guide](VALIDATION.md)
