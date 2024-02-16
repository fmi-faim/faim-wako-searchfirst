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


def _filter_points(points, weights, y_threshold, x_threshold):
    points = np.array(points)
    weights = np.array(weights)
    num_points = len(points)
    keep_indices = np.ones(num_points, dtype=bool)

    for i in range(num_points):
        within_threshold = (np.abs(points[:, 0] - points[i, 0]) < x_threshold) & (
            np.abs(points[:, 1] - points[i, 1]) < y_threshold
        )
        within_threshold[i] = False
        if np.any(within_threshold):
            less_weight_indices = np.where((weights < weights[i]) & within_threshold)[0]
            keep_indices[less_weight_indices] = False
    return keep_indices


def object_centered_grid(
    labeled_img: ndarray,
    path: Path,
    mag_first_pass: float,
    mag_second_pass: float,
    overlap_ratio: float = 0.0,
):
    """Sample each labeled object with a centered grid of tiles.

    If the object fits into a single field of view, record just the centroid coordinate.
    Otherwise, compute how many tiles are required to fit the object, and record only
    those grid coordinates that cover the object mask.

    For objects where the resulting fields of view would be overlapping,
    only keep the largest object and discard all others.
    """
    factor = mag_first_pass / mag_second_pass
    shift_percent = 1.0 - overlap_ratio
    tile_size_y = labeled_img.shape[0] * factor * shift_percent
    tile_size_x = labeled_img.shape[1] * factor * shift_percent

    props = regionprops(label_image=labeled_img)
    labels = []
    coordinates = []
    areas = []
    # loop over labels (and sort by descending size?)
    for p in props:
        # compute bounding box of label
        bbox = p.bbox
        n_tiles_y = int(np.ceil((bbox[2] - bbox[0]) / tile_size_y))
        n_tiles_x = int(np.ceil((bbox[3] - bbox[1]) / tile_size_x))
        # compute center of bounding box
        center_x = (bbox[1] + bbox[3]) / 2
        center_y = (bbox[0] + bbox[2]) / 2
        center = (center_y, center_x)

        y_coords = [center[0] + ((p + 1) - (n_tiles_y + 1) / 2) * tile_size_y for p in range(n_tiles_y)]
        x_coords = [center[1] + ((p + 1) - (n_tiles_x + 1) / 2) * tile_size_x for p in range(n_tiles_x)]

        Y, X = np.meshgrid(y_coords, x_coords)
        pairs = list(zip(Y.flatten(), X.flatten()))
        valid_points = []
        for y, x in pairs:
            # Calculate the bounding box coordinates
            y_min = max(0, int(y - tile_size_y / 2))
            y_max = min(labeled_img.shape[0], int(y + tile_size_y / 2))
            x_min = max(0, int(x - tile_size_x / 2))
            x_max = min(labeled_img.shape[1], int(x + tile_size_x / 2))

            if np.any(labeled_img[y_min:y_max, x_min:x_max] == p.label):
                valid_points.append((y, x))

        coordinates.extend(valid_points)
        areas.extend([p.area] * len(valid_points))
        labels.extend([p.label] * len(valid_points))

    # filter overlapping coordinates
    keep_points = _filter_points(
        points=coordinates,
        weights=areas,
        y_threshold=tile_size_y,
        x_threshold=tile_size_x,
    )

    coordinates = np.array(coordinates)[keep_points]
    areas = np.array(areas)[keep_points]
    labels = np.array(labels)[keep_points]

    with open(path, "w", newline="") as csv_file:
        c = csv.writer(csv_file)
        for label, point in zip(labels, coordinates):
            c.writerow([label, point[1], point[0]])
