# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test 'faim_wako_searchfirst.segment' module."""
import csv
from pathlib import Path

import pytest
from faim_wako_searchfirst.segment import process, run


@pytest.fixture()
def _data_path():
    return Path("tests/resources/TestSet")


@pytest.fixture(autouse=True)
def _clean_up(_data_path):
    yield  # Run tests
    # Remove all .csv and .yml from test_set_path
    for f in _data_path.glob("*.csv"):
        f.unlink()
    for f in _data_path.glob("*.yml"):
        f.unlink()


def test_run_test_set(_data_path):
    """Run a segmentation on the test set."""
    run(_data_path, configfile="config.yml")
    csv_path = _data_path / "TestSet_D07_T0001F002L01A02Z01C01.csv"
    assert csv_path.exists()
    # TODO assert csv data correct
    with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        assert sum(1 for _ in reader) == 12, "Incorrect number of objects detected."


def test_process_test_set(_data_path):
    """Test process() with defined parameters."""
    file_selection_params = {
        "channel": "C01",
    }
    segmentation_params = {
        "threshold": 1,
        "include_holes": False,
        "min_size": 10,
        "max_eccentricity": 0.9,
    }
    additional_analysis_params = {
        "enabled": False,
    }
    output_params = {
        "type": "centers",
    }
    grid_sampling_params = {}

    process(
        _data_path,
        file_selection_params,
        segmentation_params,
        additional_analysis_params,
        output_params,
        grid_sampling_params,
    )

    csv_path = _data_path / "TestSet_D07_T0001F002L01A02Z01C01.csv"
    assert csv_path.exists()
    # TODO assert csv data correct
    with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        assert sum(1 for _ in reader) == 5, "Incorrect number of objects detected."


def test_run_invalid_folder():
    """Test AssertionError on non-existing folder."""
    with pytest.raises(AssertionError):
        run("/some/invalid/folder", configfile="config.yml")


def test_process_invalid_second_channel(_data_path):
    """Test FileNotFoundError on invalid target channel."""
    file_selection_params = {
        "channel": "C01",
    }
    segmentation_params = {
        "threshold": 1,
        "include_holes": False,
        "min_size": 10,
        "max_eccentricity": 0.9,
    }
    additional_analysis_params = {
        "enabled": True,
        "target_channel": "C04",
    }
    output_params = {}
    grid_sampling_params = {}

    with pytest.raises(FileNotFoundError):
        process(
            _data_path,
            file_selection_params,
            segmentation_params,
            additional_analysis_params,
            output_params,
            grid_sampling_params,
        )
