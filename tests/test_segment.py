# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test 'faim_wako_searchfirst.segment' module."""
import pytest
from faim_wako_searchfirst.segment import run


def test_segment_test_set():
    """Run a segmentation on the test set."""
    run("tests/resources/TestSet", configfile="config.yml")


def test_segment_invalid_folder():
    """Test error on non-existing folder."""
    with pytest.raises(AssertionError):
        run("/some/invalid/folder", configfile="config.yml")
