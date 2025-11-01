#!/usr/bin/env python3
"""
Download MipNeRF360 Dataset

This script downloads the MipNeRF360 dataset scenes for training
with Triangle Splatting and ETR.

MipNeRF360 Dataset:
- Official paper: https://jonbarron.info/mipnerf360/
- Scenes: bicycle, bonsai, counter, garden, kitchen, room, stump, flowers, treehill

Usage:
    python scripts/download_mipnerf360.py --output data/mipnerf360 --scenes bicycle garden
    python scripts/download_mipnerf360.py --output data/mipnerf360 --all
"""

import argparse
import os
import sys
import urllib.request
import zipfile
from pathlib import Path
from tqdm import tqdm

# MipNeRF360 dataset information
SCENES = {
    'bicycle': 'https://storage.googleapis.com/gresearch/refraw360/360_v2.zip',
    'garden': 'https://storage.googleapis.com/gresearch/refraw360/360_v2.zip',
    'stump': 'https://storage.googleapis.com/gresearch/refraw360/360_v2.zip',
    'room': 'https://storage.googleapis.com/gresearch/refraw360/360_v2.zip',
    'counter': 'https://storage.googleapis.com/gresearch/refraw360/360_v2.zip',
    'kitchen': 'https://storage.googleapis.com/gresearch/refraw360/360_v2.zip',
    'bonsai': 'https://storage.googleapis.com/gresearch/refraw360/360_v2.zip',
    'flowers': 'https://storage.googleapis.com/gresearch/refraw360/360_extra.zip',
    'treehill': 'https://storage.googleapis.com/gresearch/refraw360/360_extra.zip',
}

OUTDOOR_SCENES = ['bicycle', 'garden', 'stump', 'flowers', 'treehill']
INDOOR_SCENES = ['room', 'counter', 'kitchen', 'bonsai']

class DownloadProgressBar(tqdm):
    """Progress bar for downloads"""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_url(url, output_path):
    """Download file from URL with progress bar"""
    print(f"Downloading from {url}")
    with DownloadProgressBar(unit='B', unit_scale=True,
                            miniters=1, desc=output_path.name) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)

def extract_zip(zip_path, extract_to):
    """Extract zip file with progress bar"""
    print(f"Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        members = zip_ref.namelist()
        with tqdm(total=len(members), desc="Extracting") as pbar:
            for member in members:
                zip_ref.extract(member, extract_to)
                pbar.update(1)

def download_scene(scene_name, output_dir, force=False):
    """Download a single MipNeRF360 scene"""
    if scene_name not in SCENES:
        print(f"Error: Unknown scene '{scene_name}'")
        print(f"Available scenes: {', '.join(SCENES.keys())}")
        return False

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    scene_dir = output_path / scene_name
    if scene_dir.exists() and not force:
        print(f"✓ Scene '{scene_name}' already exists at {scene_dir}")
        return True

    # Download zip file
    url = SCENES[scene_name]
    zip_name = url.split('/')[-1]
    zip_path = output_path / zip_name

    if not zip_path.exists():
        print(f"\n{'='*70}")
        print(f"Downloading scene: {scene_name}")
        print(f"{'='*70}")
        download_url(url, zip_path)
    else:
        print(f"✓ Archive already downloaded: {zip_path}")

    # Extract
    print(f"\n{'='*70}")
    print(f"Extracting scene: {scene_name}")
    print(f"{'='*70}")
    extract_zip(zip_path, output_path)

    # Verify extraction
    if scene_dir.exists():
        print(f"✓ Scene '{scene_name}' extracted successfully")

        # Count images
        images_dir = scene_dir / 'images'
        if images_dir.exists():
            num_images = len(list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png')))
            print(f"  Found {num_images} images")

        # Check for COLMAP data
        sparse_dir = scene_dir / 'sparse' / '0'
        if sparse_dir.exists():
            print(f"  ✓ COLMAP sparse reconstruction found")
        else:
            print(f"  ⚠ Warning: COLMAP sparse reconstruction not found")
            print(f"    You may need to run COLMAP first")

        return True
    else:
        print(f"✗ Error: Failed to extract scene '{scene_name}'")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download MipNeRF360 dataset scenes")
    parser.add_argument('--output', '-o', type=str, default='data/mipnerf360',
                       help='Output directory for downloaded scenes')
    parser.add_argument('--scenes', '-s', nargs='+',
                       help='Specific scenes to download (e.g., bicycle garden)')
    parser.add_argument('--all', action='store_true',
                       help='Download all scenes')
    parser.add_argument('--outdoor', action='store_true',
                       help='Download all outdoor scenes')
    parser.add_argument('--indoor', action='store_true',
                       help='Download all indoor scenes')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force re-download even if scene exists')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available scenes')

    args = parser.parse_args()

    # List scenes
    if args.list:
        print("\nAvailable MipNeRF360 scenes:\n")
        print("Indoor scenes:")
        for scene in INDOOR_SCENES:
            print(f"  - {scene}")
        print("\nOutdoor scenes:")
        for scene in OUTDOOR_SCENES:
            print(f"  - {scene}")
        print()
        return

    # Determine which scenes to download
    scenes_to_download = []

    if args.all:
        scenes_to_download = list(SCENES.keys())
    elif args.outdoor:
        scenes_to_download = OUTDOOR_SCENES
    elif args.indoor:
        scenes_to_download = INDOOR_SCENES
    elif args.scenes:
        scenes_to_download = args.scenes
    else:
        print("Error: Please specify scenes to download")
        print("Use --scenes, --all, --outdoor, --indoor, or --list")
        parser.print_help()
        return

    # Download scenes
    print("="*70)
    print("MipNeRF360 Dataset Downloader")
    print("="*70)
    print(f"Output directory: {args.output}")
    print(f"Scenes to download: {', '.join(scenes_to_download)}")
    print("="*70)
    print()

    success_count = 0
    for scene in scenes_to_download:
        if download_scene(scene, args.output, args.force):
            success_count += 1
        print()

    # Summary
    print("="*70)
    print("Download Summary")
    print("="*70)
    print(f"Successfully downloaded: {success_count}/{len(scenes_to_download)} scenes")
    print(f"Output directory: {os.path.abspath(args.output)}")
    print()
    print("Next steps:")
    print("1. Verify downloaded scenes")
    print("2. Run training:")
    print(f"   python train.py -s {args.output}/<scene_name> -m output/<scene_name>")
    print()
    print("Example:")
    print(f"   python train.py -s {args.output}/bicycle -m output/bicycle")
    print("="*70)

if __name__ == '__main__':
    main()
