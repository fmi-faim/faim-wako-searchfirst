# SPDX-FileCopyrightText: 2024 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Methods for preprocessing a list of files from a Wako SearchFirst first pass acquisition.

Each method must accept a list of files an output folder prefix as first two arguments.
"""

from pathlib import Path
import subprocess

def fiji_script(
    tif_files,
    folder_path: Path,
    fiji_executable,
    fiji_script_path,
    folder_suffix,
):
    """TODO"""
    # write csv file with file list, hand over csv path to script
    file_list_csv = folder_path / "faim-wako-searchfirst_files.csv"
    with open(file_list_csv, "w") as csv_file:
        csv_file.writelines(str(f) for f in tif_files)
    csv_file = str(file_list_csv)
    options = f"\"{csv_file=},{folder_suffix=}\""
    print(f"{options=}")
    subprocess.run(
        [
            Path(fiji_executable),
            "--ij2",
            "--headless",
            "--console",
            "--run",
            str(Path(fiji_script_path)),
            options,
        ],
        check=True,
    )
    result_folder: Path = folder_path.parent / f"{folder_path.name}_{folder_suffix}"
    # parameters: file_list_csv, folder_suffix, **all_others
    assert result_folder.exists()
    #return result_folder.iterdir()
    return tif_files
