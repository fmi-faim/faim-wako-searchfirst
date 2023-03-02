# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Segment images of a Wako SearchFirst first pass acquisition."""

import csv
import json
import logging
import re
from pathlib import Path
from typing import Callable, List, Union

import confuse
import numpy as np
from numpy import ndarray
from rich.progress import track
from scipy.ndimage import binary_fill_holes
from skimage.color import label2rgb
from skimage.io import imread
from skimage.measure import label, regionprops
from tifffile import imwrite


def run(folder: Union[str, Path], configfile: str):
    """Analyse first pass of a Wako SearchFirst experiment."""
    # Check if folder_path is valid
    folder_path = Path(folder)
    assert folder_path.is_dir(), f"Invalid input folder: {folder}"

    # Setup logging
    logging.basicConfig(filename=folder_path / (__name__ + ".log"),
                        format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s',
                        level=logging.INFO)  # encoding="utf-8",
    logger = logging.getLogger(__name__)

    # Read config
    config_path = Path(configfile)
    config = confuse.Configuration("faim-wako-searchfirst")
    config.set_file(config_path, base_for_paths=True)

    # Copy config file to destination
    config_copy = folder_path / config_path.name
    config_copy.write_text(config.dump())

    # Segment
    process(
        folder_path,
        file_selection_params=config["file_selection"].get(),
        segmentation_params=config["segmentation"].get(),
        additional_analysis_params=config["additional_analysis"].get(),
        output_params=config["output"].get(),
        grid_sampling_params=config["grid_sampling"].get(),
        logger=logger,
    )


def select_files(
        folder: Path,
        channel: str = "C01",
) -> List[Path]:
    """Filter all TIFs in folder starting with folder name - and containing channel ID."""
    return sorted(folder.rglob(folder.name + "*" + channel + ".[Tt][Ii][Ff]"))


def segment(
        img,
        threshold: int,
        include_holes: bool,
        min_size: int,
        max_eccentricity: float,
):
    """Segment a given image by global thresholding.

    :param img: input image
    :param threshold: global threshold
    :param include_holes: if true, holes will be filled
    :param min_size: minimum object size
    :param max_eccentricity: maximum eccentricity of object

    :return: a label image representing the detected objects
    """
    mask = img > threshold
    if include_holes:
        mask = binary_fill_holes(mask)
    labeled_image = label(mask).astype(np.uint16)
    regions = regionprops(labeled_image)
    for region in regions:
        if region.area < min_size or region.eccentricity > max_eccentricity:
            labeled_image[labeled_image == region.label] = 0
    return labeled_image


def segment_file(
        tif: str,
        segment_fn: Callable,
        **kwargs,
):
    """Segment a tif file using a provided segmentation function."""
    img = imread(tif)
    labeled_image = segment_fn(img, **kwargs)
    return img, labeled_image


def filter_objects_by_intensity(labels, img, min_intensity):
    """Filter objects in 'labels' by intensity in 'img'."""
    regions = regionprops(labels, img)
    for region in regions:
        if region.intensity_mean < min_intensity:
            labels[labels == region.label] = 0
    return labels


def sample_grid(labeled_img: ndarray, path, mag_first_pass, mag_second_pass, overlap_percent,
                offset_grid_origin_percent):
    """Save grid positions of the tiles that contain objects."""
    factor = mag_first_pass / mag_second_pass
    tile_size_y = labeled_img.shape[0] * factor
    tile_size_x = labeled_img.shape[1] * factor

    with open(path, "w", newline="") as csv_file:
        c = csv.writer(csv_file)
        count = 0
        for y in np.arange(0, labeled_img.shape[0], tile_size_y):
            for x in np.arange(0, labeled_img.shape[1], tile_size_x):
                if np.max(
                        labeled_img[
                        int(np.floor(y)):int(np.ceil(y + tile_size_y)),
                        int(np.floor(x)):int(np.ceil(x + tile_size_x))
                        ]
                ) > 0:
                    c.writerow([count, x + tile_size_x / 2, y + tile_size_y / 2])
                    count += 1


def report_center_coordinates(labeled_img, path):
    """Save center position of each object in 'labeled_img'."""
    regions = regionprops(labeled_img)
    with open(path, "w", newline="") as csv_file:
        c = csv.writer(csv_file)
        for region in regions:
            c.writerow([region.label, *reversed(region.centroid)])


def get_other_channel_file(tif_file: Path, target_channel: str) -> Path:
    """Detect the file of target channel with the same well and field as the given 'tif_file'."""
    pattern = re.compile(r"(.*_[A-Z]\d{2}_T\d{4}F\d{3}L\d{2})(A\d{2})(Z\d{2})(C\d{2})\.tif")
    m = pattern.fullmatch(tif_file.name)
    assert m is not None
    candidate_files = tif_file.parent.glob("*" + target_channel + ".[Tt][Ii][Ff]")
    for candidate in candidate_files:
        n = pattern.fullmatch(candidate.name)
        if (n is not None) and (n.group(4) == target_channel) and (m.group(1) == n.group(1)):
            return candidate
    raise FileNotFoundError(f"No matching file for channel {target_channel}.")


def additional_analysis(
        tif_file, labels, filter_fn, enabled=False, target_channel=None, min_intensity=None
):
    """Filter objects in 'labels' using the provided function."""
    if not enabled:
        return labels
    intensity_image = imread(get_other_channel_file(tif_file, target_channel))
    return filter_fn(labels, intensity_image, min_intensity)


def save_segmentation_image(folder_path, filename, img, labels):
    """Save segmentation overlay as RGB image into separate folder."""
    destination_folder = folder_path.parent / (folder_path.name + "_segmentation")
    destination_folder.mkdir(exist_ok=True)
    preview = label2rgb(labels, image=img).astype(np.uint16)
    imwrite(destination_folder / filename, preview, imagej=True)


def process(
        folder: Path,
        file_selection_params: dict,
        segmentation_params: dict,
        additional_analysis_params: dict,
        output_params: dict,
        grid_sampling_params: dict,
        logger=logging,
) -> None:
    """Segment images with the provided segmentation parameters."""
    logger.info("File selection parameters: " + json.dumps(file_selection_params, indent=4))
    logger.info("Segmentation parameters: " + json.dumps(segmentation_params, indent=4))
    logger.info("Additional analysis parameters: " + json.dumps(additional_analysis_params, indent=4))
    logger.info("Output parameters: " + json.dumps(output_params, indent=4))
    logger.info("Grid sampling parameters: " + json.dumps(grid_sampling_params, indent=4))

    tif_files = select_files(folder=folder, **file_selection_params)

    # Write CSV file for each TIF
    for tif_file in track(tif_files):
        # file -> segmentation mask and image
        img, labels = segment_file(tif_file, segment, **segmentation_params)

        # addition analysis (e.g. filter by intensity in other channel)
        labels = additional_analysis(
            tif_file, labels, filter_objects_by_intensity,
            **additional_analysis_params
        )

        # mask -> csv
        csv_path = tif_file.parent / (tif_file.stem + ".csv")
        if output_params["type"] == "grid":
            sample_grid(labels, csv_path, **grid_sampling_params)
        else:
            report_center_coordinates(labels, csv_path)

        # mask + image -> preview
        save_segmentation_image(tif_file.parent, tif_file.name, img, labels)

    logger.info(f"Finished processing {len(tif_files)} image(s).")
