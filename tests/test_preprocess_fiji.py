# SPDX-FileCopyrightText: 2024 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Test preprocessing with Fiji scripts."""
import os
from pathlib import Path
import shutil
import pytest

from faim_wako_searchfirst.main import run


CONFIG_FILE = "config_preprocess_fiji.yml"

@pytest.fixture
def _data_path(tmp_path):
    # copy test set into tmp_path, return resulting Path
    testset_path = Path("tests/resources/worms")
    assert testset_path.exists()
    return shutil.copytree(testset_path, tmp_path / "worms")

@pytest.mark.skipif(os.getenv("GITHUB_ACTIONS") == "true", reason="Skip on GitHub Actions")
def test_run(_data_path):
    """Test run with parameters defined in config_preprocess_fiji.yml."""
    run(_data_path, configfile=CONFIG_FILE)

    csv_path = _data_path / "worms_C01.csv"
    assert csv_path.exists()
