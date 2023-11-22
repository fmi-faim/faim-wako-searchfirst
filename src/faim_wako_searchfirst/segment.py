# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Collection of methods to segment an image and return a label image.

Each method must accept an input image as first argument,
and must return a label image.
"""

import logging
from pathlib import Path
from typing import Union

import numpy as np
from cellpose import models
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


def cellpose(
    img,
    diameter: float,
    pretrained_model: Union[str, Path] = "cyto2",
    logger=logging,
    **kwargs,
):
    """Segment a given image by global thresholding.

    :param img: input image
    :param diameter: expected object diameter
    :param pretrained_model: name of cellpose model, or path to pretrained model
    :param logger:

    :return: a label image representing the detected objects
    """
    logger.info(f"Load cellpose model: {pretrained_model}")
    model: models.CellposeModel = models.CellposeModel(
        pretrained_model=pretrained_model,
    )
    mask, _, _ = model.eval(
        img,
        channels=[0, 0],
        diameter=diameter,
        **kwargs,
    )
    return mask
