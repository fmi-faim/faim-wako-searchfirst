# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""SearchFirst script to run a simple segmentation."""
import typer as typer
from faim_wako_searchfirst.segment import run


def main(folder_path: str):
    """Segment images in the given acquisition folder.

    All additional parameters are defined in the provided config file.

    :param folder_path: Folder containing the first pass acquisition.
    """
    run(folder=folder_path, configfile="config.yml")


if __name__ == "__main__":
    typer.run(main)
