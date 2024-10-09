# SPDX-FileCopyrightText: 2024 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test faim_wako_searchfirst.filter module."""

from pathlib import Path

import numpy as np
import pytest
from skimage.io import imread

from faim_wako_searchfirst.filter import border, dilate, feature


@pytest.fixture
def _label_image():
    return imread(Path("tests") / "resources" / "simple_labels.tif")


def test_feature(_label_image: np.ndarray):
    """Test generic feature filter."""
    labels = _label_image.copy()
    feature(
        tif_file=None,
        labels=labels,
        feature="solidity",
        min_value=0.9,
        max_value=1.0,
    )
    assert np.unique(labels).tolist() == [0, 2, 3, 4]


def test_border(_label_image: np.ndarray):
    """Test discard border objects."""
    labels = _label_image.copy()
    assert np.unique(labels).tolist() == [0, 1, 2, 3, 4]
    border(
        tif_file=None,
        labels=labels,
        margin=15,
    )
    assert np.unique(labels).tolist() == [0, 3, 4]


def test_dilate(_label_image: np.ndarray):
    """Test oject dilation."""
    labels = _label_image.copy()
    assert np.sum(labels[labels == 1]) == 1353
    dilate(
        tif_file=None,
        labels=labels,
        pixel_distance=5.0,
    )
    assert np.sum(labels[labels == 1]) == 2803
