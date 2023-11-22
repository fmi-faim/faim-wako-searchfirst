# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Collection of methods to sample a label image and write coordinates into a csv file.

Each method must accept a label image and an output file path as first two arguments.
"""

import csv
from pathlib import Path

import numpy as np
from numpy import ndarray
from skimage.measure import block_reduce, regionprops


def dense_grid(
    labels: ndarray,
    output_path: Path,
    binning_factor: int = 50,
):
    """Save densely sampled grid positions for object hits."""
    downscaled = block_reduce(
        image=labels,
        block_size=(binning_factor, binning_factor),
        func=np.max,
    )
    print(downscaled.shape)
    with open(output_path, "w", newline="") as csv_file:
        c = csv.writer(csv_file)
        count = 0
        it = np.nditer(downscaled, flags=["multi_index"])
        for label in it:
            if label > 0:
                c.writerow([count] + _grid_coordinate(it.multi_index, binning_factor))
                count += 1


def _grid_coordinate(index, factor):
    return [(index[1] + 0.5) * factor, (index[0] + 0.5) * factor]


def grid_overlap(
    labeled_img: ndarray,
    path,
    mag_first_pass,
    mag_second_pass,
    overlap_ratio: float = 0.0,
):
    """Save grid positions of the tiles that contain objects."""
    factor = mag_first_pass / mag_second_pass
    shift_percent = 1.0 - overlap_ratio
    tile_size_y = labeled_img.shape[0] * factor * shift_percent
    tile_size_x = labeled_img.shape[1] * factor * shift_percent

    with open(path, "w", newline="") as csv_file:
        c = csv.writer(csv_file)
        count = 0
        for y in np.arange(0, labeled_img.shape[0], tile_size_y):  # TODO: use np.linspace
            for x in np.arange(0, labeled_img.shape[1], tile_size_x):
                if (
                    np.max(
                        labeled_img[
                            int(np.floor(y)) : int(np.ceil(y + tile_size_y)),
                            int(np.floor(x)) : int(np.ceil(x + tile_size_x)),
                        ]
                    )
                    > 0
                ):
                    c.writerow([count, x + tile_size_x / 2, y + tile_size_y / 2])
                    count += 1


def centers(labeled_img, path):
    """Save center position of each object in 'labeled_img'."""
    regions = regionprops(labeled_img)
    with open(path, "w", newline="") as csv_file:
        c = csv.writer(csv_file)
        for region in regions:
            c.writerow([region.label, *reversed(region.centroid)])
