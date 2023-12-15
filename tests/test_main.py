# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test faim_wako_searchfirst module."""
import csv
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from faim_wako_searchfirst.filter import area, bounding_box, solidity
from faim_wako_searchfirst.main import run
from faim_wako_searchfirst.sample import centers, dense_grid, grid_overlap
from faim_wako_searchfirst.segment import threshold
from skimage.io import imread


@pytest.fixture
def _data_path(tmp_path):
    # copy test set into tmp_path, return resulting Path
    testset_path = Path("tests/resources/TestSet")
    assert testset_path.exists()
    return shutil.copytree(testset_path, tmp_path / "TestSet")


@pytest.fixture
def _image(_data_path):
    return imread(_data_path / "TestSet_D07_T0001F002L01A02Z01C01.tif")


def test_run(_data_path):
    """Test run with parameters defined in the sample config.yml file."""
    run(_data_path, configfile="config.yml")
    csv_path = _data_path / "TestSet_D07_T0001F002L01A02Z01C01.csv"
    assert csv_path.exists()
    with open(csv_path, "r") as csv_file:
        reader = csv.reader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        entries = list(reader)
        assert len(entries) == 1, "Incorrect number of objects detected."
        assert entries[0] == pytest.approx([4, 87.5, 84.5])

    segmentation_folder = _data_path.parent / (_data_path.name + "_segmentation")
    assert sum(1 for _ in segmentation_folder.glob("*")) == 1


def test_partial(_image, tmp_path):
    """Test segment, filter and sample functionality separately."""
    # segment
    labels: np.ndarray = threshold(
        _image,
        threshold=128,
        include_holes=True,
    )
    assert np.max(labels) == 7

    # segment with gaussian
    labels_blurred: np.ndarray = threshold(
        _image,
        threshold=128,
        include_holes=True,
        gaussian_sigma=5.5,
    )
    assert np.max(labels_blurred) == 4

    # filter
    label2 = labels.copy()
    bounding_box(
        tif_file=None,
        labels=label2,
        min_x=180,
        min_y=30,
        max_x=250,
        max_y=100,
    )
    assert np.max(label2) == 2

    label_small = labels.copy()
    area(
        tif_file=None,
        labels=label_small,
        min_area=0,
        max_area=100,
    )
    assert list(np.unique(label_small)) == [0, 1, 3, 5]

    label_cross = labels.copy()
    solidity(
        tif_file=None,
        labels=label_cross,
        min_solidity=0.0,
        max_solidity=0.9,
    )
    assert np.max(label_cross) == 2

    # sample centers
    centers_csv = tmp_path / "centers.csv"
    centers(
        labeled_img=labels,
        path=centers_csv,
    )
    assert centers_csv.exists()
    centers_table = pd.read_csv(centers_csv, header=None)
    print(centers_table)
    assert len(centers_table) == 7

    # sample grid
    overlap_csv = tmp_path / "overlap.csv"
    grid_overlap(
        labeled_img=labels,
        path=overlap_csv,
        mag_first_pass=10,
        mag_second_pass=20,
        overlap_ratio=0.25,
    )
    assert overlap_csv.exists()
    overlap_table = pd.read_csv(overlap_csv, header=None)
    print(overlap_table)
    assert len(overlap_table) == 8

    # sample dense grid
    dense_csv = tmp_path / "dense.csv"
    dense_grid(
        labels=labels,
        output_path=dense_csv,
        binning_factor=32,
    )
    assert dense_csv.exists()
    dense_table = pd.read_csv(dense_csv, header=None)
    print(dense_table)
    assert len(dense_table) == 19
    assert list(dense_table[1]) == [
        48,
        48,
        144,
        176,
        208,
        240,
        80,
        112,
        208,
        240,
        80,
        176,
        208,
        176,
        208,
        80,
        112,
        80,
        112,
    ]
    assert list(dense_table[2]) == [16, 48, 48, 48, 48, 48, 80, 80, 80, 80, 144, 144, 144, 176, 176, 208, 208, 240, 240]
