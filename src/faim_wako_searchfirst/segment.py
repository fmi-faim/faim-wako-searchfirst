# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Segment images of a Wako SearchFirst first pass acquisition."""

import csv
import json
import logging
from pathlib import Path
from typing import Union

import confuse
from rich.progress import track
from skimage.io import imread
from skimage.measure import label, regionprops


def run(folder: Union[str, Path], configfile: str):
    """Analyse first pass of a Wako SearchFirst experiment."""
    # Check if folder_path is valid
    path = Path(folder)
    assert path.is_dir(), f"Invalid input folder: {folder}"

    logging.basicConfig(filename=path / (__name__ + ".log"),
                        format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s',
                        level=logging.INFO)  # encoding="utf-8",
    logger = logging.getLogger(__name__)

    config_path = Path(configfile)
    config = confuse.Configuration("faim-wako-searchfirst")
    config.set_file(config_path, base_for_paths=True)
    logger.info(f"Reading config parameters from file {config_path.absolute()}.")

    file_selection_params = config["file_selection"].get()
    segmentation_params = config["segmentation"].get()

    logger.info("Segmentation parameters: " + json.dumps(segmentation_params, indent=4))

    # Copy config file to destination
    config_copy = path / config_path.name
    config_copy.write_text(config.dump())

    segment(path, logger=logger, seg_params=segmentation_params, **file_selection_params)


def segment(folder, logger, channel, seg_params):
    """Segment images with the provided segmentation parameters."""
    logger.info("Starting segmentation...")

    # Filter all TIFs in folder starting with folder's name - and containing channel ID
    tifs = (sorted(folder.rglob(folder.name + "*" + channel + ".[Tt][Ii][Ff]")))

    # Write CSV file for each TIF
    for tif in track(tifs):
        process_file(tif, logger, **seg_params)

    logger.info(f"Finished processing {len(tifs)} image(s).")


def process_file(tif, logger, threshold, min_size=0, include_holes=False):
    """Run segmentation on a single file."""
    logger.info(f"Opening {tif} ...")
    img = imread(tif)
    mask = img > threshold
    labeled_img, count = label(mask, return_num=True)
    regions = regionprops(labeled_img)

    # TODO implement size and eccentricity filtering
    # TODO create segmentation preview
    # TODO implement object <-> grid sampling

    logger.info(f"Found {len(regions)} regions.")
    with open(tif.parent / (tif.stem + ".csv"), "w", newline="") as csv_file:
        c = csv.writer(csv_file)
        for region in regions:
            c.writerow([region.label, *region.centroid])
