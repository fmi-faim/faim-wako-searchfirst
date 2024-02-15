# SPDX-FileCopyrightText: 2024 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test faim_wako_searchfirst.sample module."""
from pathlib import Path

import pandas as pd
import pytest
from faim_wako_searchfirst.sample import object_centered_grid
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
