# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Collection of methods to filter a label image.

Each method must accept a file path and a label image as first two arguments,
and must modify the label image inplace.
The file path can be used to find related files for more complex object filtering,
e.g. by intensity in a different channel.
"""

import re
from pathlib import Path

from numpy import ndarray
from skimage.measure import regionprops
from tifffile import imread


def bounding_box(tif_file: Path, labels, min_x: int, min_y: int, max_x: int, max_y: int):
    """Modify 'labels' to set everything outside the bounding box to zero."""
    labels[0 : max(min_y, 0), :] = 0
    labels[:, 0 : max(min_x, 0)] = 0
    y, x = labels.shape
    labels[min(max_y, y) : y, :] = 0
    labels[:, min(max_x, x) : x] = 0


def area(
    tif_file: Path,
    labels: ndarray,
    min_area: int,
    max_area: int,
):
    """Modify 'labels' to only keep objects within range."""
    regions = regionprops(labels)
    for region in regions:
        if not min_area <= region.area <= max_area:
            labels[labels == region.label] = 0


def solidity(
    tif_file: Path,
    labels: ndarray,
    min_solidity: int,
    max_solidity: int,
):
    """Modify 'labels' to only keep objects within range."""
    regions = regionprops(labels)
    for region in regions:
        if not min_solidity <= region.solidity <= max_solidity:
            labels[labels == region.label] = 0


def intensity(
    tif_file: Path,
    labels: ndarray,
    target_channel: str,
    min_intensity: int,
):
    """Filter objects in 'labels' using the provided function."""
    intensity_image = imread(_get_other_channel_file(tif_file, target_channel))
    _filter_objects_by_intensity(labels, intensity_image, min_intensity)


def _get_other_channel_file(tif_file: Path, target_channel: str) -> Path:
    """Detect the file of target channel with the same well and field as the given 'tif_file'."""
    pattern = re.compile(r"(.*_[A-Z]\d{2}_T\d{4}F\d{3}L\d{2})(A\d{2})(Z\d{2})(C\d{2})\.tif")
    m = pattern.fullmatch(tif_file.name)
    assert m is not None
    candidate_files = tif_file.parent.glob("*" + target_channel + ".[Tt][Ii][Ff]")
    for candidate in candidate_files:
        n = pattern.fullmatch(candidate.name)
        if (n is not None) and (n.group(4) == target_channel) and (m.group(1) == n.group(1)):
            return candidate
    raise FileNotFoundError(f"No matching file for channel {target_channel}.")


def _filter_objects_by_intensity(labels, img, min_intensity):
    """Filter objects in 'labels' by intensity in 'img'.

    Apply changes inplace in 'labels'.
    """
    regions = regionprops(labels, img)
    for region in regions:
        if region.intensity_mean < min_intensity:
            labels[labels == region.label] = 0
