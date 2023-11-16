# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Collection of methods to segment an image and return a label image.

Each method must accept an input image as first argument,
and must return a label image.
"""

import logging

import numpy as np
from scipy.ndimage import binary_fill_holes
from skimage.measure import label, regionprops


def threshold(
    img,
    threshold: int,
    include_holes: bool,
    logger=logging,
):
    """Segment a given image by global thresholding.

    :param img: input image
    :param threshold: global threshold
    :param include_holes: if true, holes will be filled
    :param min_size: minimum object size
    :param max_size: maximum object size
    :param min_eccentricity: minimum eccentricity of object
    :param max_eccentricity: maximum eccentricity of object
    :param logger:

    :return: a label image representing the detected objects
    """
    mask = img > threshold
    if include_holes:
        mask = binary_fill_holes(mask)
    labeled_image = label(mask).astype(np.uint16)
    regions = regionprops(labeled_image)
    logger.info(f"Found {len(regions)} connected components.")
    return labeled_image
