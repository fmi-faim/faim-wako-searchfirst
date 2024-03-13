# SPDX-FileCopyrightText: 2024 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test faim_wako_searchfirst.sample module."""
from pathlib import Path

import pandas as pd
import pytest
from faim_wako_searchfirst.sample import object_centered_grid, region_centered_grid
from skimage.io import imread


@pytest.fixture
def _label_image():
    return imread(Path("tests") / "resources" / "simple_labels.tif")


def test_object_centered_grid(_label_image, tmp_path):
    """Test object-centered grid sampling."""
    assert _label_image.shape == (200, 200)
    csv_path = tmp_path / "points.csv"
    object_centered_grid(
        labeled_img=_label_image,
        path=csv_path,
        mag_first_pass=4,
        mag_second_pass=20,
        overlap_ratio=0.0,
    )
    assert csv_path.exists()
    centers_table = pd.read_csv(csv_path, header=None)
    print(centers_table)
    assert len(centers_table) == 7
    assert centers_table[0].unique().tolist() == [1, 2, 3]


def test_region_centered_grid(_label_image, tmp_path):
    """Test object-centered grid sampling."""
    assert _label_image.shape == (200, 200)
    csv_path = tmp_path / "points_region_centered.csv"
    region_centered_grid(
        labeled_img=_label_image,
        path=csv_path,
        mag_first_pass=4,
        mag_second_pass=20,
        overlap_ratio=0.2,
    )
    assert csv_path.exists()
    centers_table = pd.read_csv(csv_path, header=None)
    print(centers_table)
    assert len(centers_table) == 12
    assert centers_table[0].unique().tolist() == [1, 2, 3]
    assert centers_table[0].tolist() == [1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3]
    assert centers_table.iloc[0].values.flatten().tolist() == pytest.approx([1, 18.5, 14.5])
    assert centers_table.iloc[1].values.flatten().tolist() == pytest.approx([1, 50.5, 14.5])
    assert centers_table.iloc[2].values.flatten().tolist() == pytest.approx([2, 28.0, 53.0])
    assert centers_table.iloc[3].values.flatten().tolist() == pytest.approx([2, 60.0, 53.0])
    assert centers_table.iloc[4].values.flatten().tolist() == pytest.approx([2, 92.0, 21.0])
    assert centers_table.iloc[5].values.flatten().tolist() == pytest.approx([2, 92.0, 53.0])
    assert centers_table.iloc[6].values.flatten().tolist() == pytest.approx([3, 136.5, 104.5])
    assert centers_table.iloc[7].values.flatten().tolist() == pytest.approx([3, 136.5, 136.5])
    assert centers_table.iloc[8].values.flatten().tolist() == pytest.approx([3, 136.5, 168.5])
    assert centers_table.iloc[9].values.flatten().tolist() == pytest.approx([3, 168.5, 104.5])
    assert centers_table.iloc[10].values.flatten().tolist() == pytest.approx([3, 168.5, 136.5])
    assert centers_table.iloc[11].values.flatten().tolist() == pytest.approx([3, 168.5, 168.5])
