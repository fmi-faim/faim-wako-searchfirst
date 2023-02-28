import csv
import json
import logging
from pathlib import Path

import confuse
from rich.progress import track
from skimage.io import imread
from skimage.measure import regionprops, label


def run(folder, configfile):
    # Check if folder_path is valid
    path = Path(folder)
    assert path.is_dir(), f"Invalid input folder: {folder}"

    logging.basicConfig(filename=Path(folder, __name__ + ".log"),
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
    config_copy = Path(folder, config_path.name)
    config_copy.write_text(config.dump())

    segment(folder, logger=logger, seg_params=segmentation_params, **file_selection_params)


def segment(folder, logger, channel, seg_params):
    logger.info("Starting segmentation...")

    # Filter all TIFs in folder starting with folder's name - and containing channel ID
    tifs = (sorted(path.rglob(path.name + "*" + channel + ".[Tt][Ii][Ff]")))

    # Write CSV file for each TIF
    for tif in track(tifs):
        process_file(tif, logger, **seg_params)

    logger.info(f"Finished processing {len(tifs)} image(s).")


def process_file(tif, logger, threshold, min_size=0, include_holes=False):
    logger.info(f"Opening {tif} ...")
    img = imread(tif)
    mask = img > threshold
    labeled_img, count = label(mask, return_num=True)
    regions = regionprops(labeled_img)

    # TODO implement size and eccentricity filtering

    logger.info(f"Found {len(regions)} regions.")
    with open(tif.parent / (tif.stem + ".csv"), "w", newline="") as csv_file:
        c = csv.writer(csv_file)
        for region in regions:
            c.writerow([region.label, *region.centroid])
