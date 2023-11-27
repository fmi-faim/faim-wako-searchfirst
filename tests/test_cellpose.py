# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test faim_wako_searchfirst module."""
import csv
import shutil
from pathlib import Path

import pytest
from faim_wako_searchfirst.main import run


@pytest.fixture
def _data_path(tmp_path):
    # copy test set into tmp_path, return resulting Path
    testset_path = Path("tests/resources/TestSet")
    assert testset_path.exists()
    return shutil.copytree(testset_path, tmp_path / "TestSet")


def test_cellpose(_data_path):
    """Test run with parameters defined in the sample config_cellpose.yml file."""
    run(_data_path, configfile="config_cellpose.yml")
    csv_path = _data_path / "TestSet_D07_T0001F002L01A02Z01C01.csv"
    assert csv_path.exists()
    with open(csv_path, "r") as csv_file:
        reader = csv.reader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        entries = list(reader)
        assert len(entries) == 3, "Incorrect number of objects detected."
        assert entries[0] == pytest.approx([1, 40.5, 30.5])
        assert entries[1] == pytest.approx([2, 158.5, 58.5])
        assert entries[2] == pytest.approx([3, 79.5287, 146.4483])

    segmentation_folder = _data_path.parent / (_data_path.name + "_segmentation")
    assert sum(1 for _ in segmentation_folder.glob("*")) == 1
