# SPDX-FileCopyrightText: 2024 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT
"""Test segment.weka_classifier functionality."""
from pathlib import Path

import numpy as np
import pytest
from faim_wako_searchfirst.segment import weka_classifier
from skimage.io import imread

SAMPLE_IMAGE_NAME = "worms_C01.tif"


@pytest.fixture
def _classifier_path():
    return Path("tests/resources/classifier.model")


@pytest.fixture
def _sample_image():
    return imread(Path("tests/resources/worms") / SAMPLE_IMAGE_NAME)


def test_weka_classifier(_sample_image, _classifier_path):
    """Directly call weka_classifier."""
    result = weka_classifier(_sample_image, _classifier_path)
    assert result.shape == (442, 442)
    assert np.count_nonzero(result == 1) == 3
    assert np.count_nonzero(result == 2) == 8
    assert np.count_nonzero(result == 3) == 831
