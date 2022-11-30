import pytest

from faim_wako_searchfirst.single import run


def test_invalid_folder():
    with pytest.raises(AssertionError):
        run("/some/invalid/folder", configfile="config.yml")
