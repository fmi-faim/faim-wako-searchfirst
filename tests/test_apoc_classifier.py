# SPDX-FileCopyrightText: 2024 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test faim_wako_searchfirst.segment.apoc_classifier funcionality."""
import csv
import shutil
from pathlib import Path

import numpy as np
import pytest
from faim_wako_searchfirst.main import run
from faim_wako_searchfirst.segment import apoc_classifier
from skimage.io import imread

SAMPLE_IMAGE_NAME = "worms_C01.tif"


@pytest.fixture
def _classifier_path():
    return Path("tests/resources/PixelClassifier.cl")


@pytest.fixture
def _sample_image():
    return imread(Path("tests/resources/worms") / SAMPLE_IMAGE_NAME)


@pytest.fixture
def _config_file():
    return Path("config_apoc.yml")


@pytest.fixture
def _data_path(tmp_path):
    # copy test set into tmp_path, return resulting Path
    testimage_path = Path("tests/resources/worms")
    assert testimage_path.exists()
    return Path(shutil.copytree(testimage_path, tmp_path / "worms"))


def test_apoc_classifier(_sample_image, _classifier_path):
    """Test segment.apoc_classifier function."""
    result = apoc_classifier(
        img=_sample_image,
        classifier_path=_classifier_path,
    )
    assert result.shape == (442, 442)
    assert np.count_nonzero(result == 1) == 181270
    assert np.count_nonzero(result == 2) == 14


def test_run(_data_path, _config_file):
    """Test run with apoc_classifier."""
    run(_data_path, configfile=_config_file)
    csv_path = _data_path / (SAMPLE_IMAGE_NAME[:-4] + ".csv")
    assert csv_path.exists()
    with open(csv_path, "r") as csv_file:
        reader = csv.reader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        entries = list(reader)
        assert len(entries) == 14, "Incorrect number of objects detected."
        assert entries[9] == pytest.approx([11, 178.863884, 340.5])
