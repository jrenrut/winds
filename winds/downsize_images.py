#!/usr/bin/env python

import argparse
import shutil
from pathlib import Path, WindowsPath

from PIL import Image
from tqdm import tqdm


def resize_image(image_file: WindowsPath, new_max_dim: int = 400):
    """Resize image maintaining aspect ratio.

    Args:
        image_file (WindowsPath): Path to image file.
        new_max_dim (int, optional): New size in pixels of max image dimension. Defaults to 400.
    """

    image = Image.open(image_file)
    exif = image.info["exif"]
    width, height = image.size
    max_dim = max(width, height)
    scale = float(
        new_max_dim / max_dim
    )  # calculate scale from current and desired max dimensions
    image = image.resize(
        (int(width * scale), int(height * scale)),
        Image.Resampling.LANCZOS,  # allows for plotting with Folium
    )
    image.save(image_file, quality=100, exif=exif)


def resize_images(
    path: WindowsPath, new_max_dim: int = 400, disable_pbar: bool = False
):
    """Find image files in directory and downsize them.

    Args:
        path (WindowsPath): Top level path where images are located.
        new_max_dim (int, optional): New size in pixels of max image dimension. Defaults to 400.
        disable_pbar (bool, optional): Do not show progress bar. Defaults to False.
    """

    # find files with common image suffixes
    exts = [".png", ".jpg", ".jpeg"]
    image_files = [file for file in path.rglob("*") if file.suffix in exts]

    # create tqdm progress bar
    pbar = tqdm(
        image_files,
        desc="Downsampling Images",
        total=len(image_files),
        disable=disable_pbar,
    )

    for image_file in pbar:
        resize_image(image_file, new_max_dim=new_max_dim)


def main():
    """Parse arguments and run functions to downsample images."""

    parser = argparse.ArgumentParser(
        description="Script to resize images to be displayed in a folium map."
    )
    parser.add_argument(
        "directory",
        help="Top level directory",
        type=str,
    )
    parser.add_argument(
        "-m",
        "--max-dim",
        help="Size of maximum downsampled image dimension in pixels",
        required=False,
        type=int,
        default=400,
    )
    parser.add_argument(
        "-i",
        "--in-place",
        help="Whether to resize images in place or not",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Don't show progress bar",
        required=False,
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    path = Path(args.directory).resolve()

    # if not downsampling inplace, copy images to 'original' directory
    if not args.in_place:
        new_dir = path.parent / f"{path.name}_original"
        shutil.copytree(path, new_dir)

    resize_images(path, new_max_dim=args.max_dim, disable_pbar=args.quiet)


if __name__ == "__main__":
    main()
