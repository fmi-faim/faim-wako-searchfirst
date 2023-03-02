# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test 'faim_wako_searchfirst.segment' module."""
import csv
import shutil
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
    shutil.rmtree(_data_path.parent / (_data_path.name + "_segmentation"), ignore_errors=True)


def test_run_test_set(_data_path):
    """Run a segmentation on the test set."""
    run(_data_path, configfile="config.yml")
    csv_path = _data_path / "TestSet_D07_T0001F002L01A02Z01C01.csv"
    assert csv_path.exists()

    with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        entries = list(reader)
        assert len(entries) == 11, "Incorrect number of objects detected."
        assert entries[0] == ['0', '192.00000000000003', '38.400000000000006']
        assert entries[1] == ['1', '217.60000000000002', '38.400000000000006']
        assert entries[2] == ['2', '166.40000000000003', '64.0']
        assert entries[3] == ['3', '192.00000000000003', '64.0']
        assert entries[4] == ['4', '217.60000000000002', '64.0']
        assert entries[5] == ['5', '243.20000000000002', '64.0']
        assert entries[6] == ['6', '192.00000000000003', '89.60000000000001']
        assert entries[7] == ['7', '217.60000000000002', '89.60000000000001']
        assert entries[8] == ['8', '243.20000000000002', '89.60000000000001']
        assert entries[9] == ['9', '64.0', '140.8']
        assert entries[10] == ['10', '89.60000000000001', '140.8']

    segmentation_folder = _data_path.parent / (_data_path.name + "_segmentation")
    assert sum(1 for _ in segmentation_folder.glob("*")) == 1


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

    with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        entries = list(reader)
        assert len(entries) == 5, "Incorrect number of objects detected."
        assert entries[0] == ['1', '40.5', '30.5']
        assert entries[1] == ['2', '209.6689930209372', '67.93419740777667']
        assert entries[2] == ['3', '158.5', '58.5']
        assert entries[3] == ['5', '79.5', '146.5']
        assert entries[4] == ['7', '94.09634146341463', '210.34634146341463']

    segmentation_folder = _data_path.parent / (_data_path.name + "_segmentation")
    assert sum(1 for _ in segmentation_folder.glob("*")) == 1


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
