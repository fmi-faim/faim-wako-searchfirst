# SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
#
# SPDX-License-Identifier: MIT

"""Process images of a Wako SearchFirst first pass acquisition.

The processing workflow consists of three parts:
  * Segment the input image.
  * Optionally filter objects.
  * Sample the resulting mask to write hit coordinates into csv file.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import List, Union

import confuse
from skimage import img_as_float, img_as_ubyte
from skimage.color import label2rgb
from skimage.exposure import rescale_intensity
from skimage.io import imread, imsave
from tqdm import tqdm

from faim_wako_searchfirst import filter, sample, segment


def run(folder: Union[str, Path], configfile: Union[str, Path]):
    """Analyse first pass of a Wako SearchFirst experiment."""
    # Check if folder_path is valid
    folder_path = Path(folder)
    if not folder_path.is_dir():
        raise ValueError(f"Invalid input folder: {folder}")

    # Setup logging
    logging.basicConfig(
        filename=folder_path / (__name__ + ".log"),
        format="%(asctime)s - %(name)s - [%(levelname)s] %(message)s",
        level=logging.INFO,
        # encoding="utf-8",
    )
    logger = logging.getLogger(__name__)

    # Read config
    config_path = Path(configfile)
    # source = confuse.YamlSource(config_path, base_for_paths=True)
    # config = confuse.RootView(sources=[source])
    config = confuse.Configuration("faim-wako-searchfirst", read=False)
    config.set_file(config_path, base_for_paths=True)

    # Copy config file to destination
    config_filename = datetime.now().strftime("%Y%m%d_%H%M_") + __name__.replace(".", "_") + "_config.yml"
    config_copy = folder_path / config_filename
    config_copy.write_text(config.dump())

    # Select files
    tif_files = _select_files(
        folder=folder_path,
        **(config["file_selection"].get()),
    )

    logger.info(f"Found {len(tif_files)} matching files.")

    # Process
    process = partial(_process_tif, config=config, logger=logger)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process, tif_file) for tif_file in tif_files]
        for _ in tqdm(as_completed(futures), total=len(futures)):
            pass
    logger.info("Done processing.")


def _process_tif(tif_file, config, logger):
    # Setup
    # Segment
    segment_method = config["process"]["segment"].get(str)
    segment_config = config[segment_method].get()
    logger.info(f"Segment using '{segment_method}'.")
    segment_fn = getattr(segment, segment_method)

    # Filter
    filter_methods = config["process"]["filter"].as_str_seq()
    filter_funcs = {f: getattr(filter, f) for f in filter_methods}

    # Sample
    sample_method = config["process"]["sample"].get(str)
    sample_config = config[sample_method].get(confuse.Optional(dict, default={}))
    sample_fn = getattr(sample, sample_method)

    # Read image
    img = imread(tif_file)

    # Segment
    labels = segment_fn(
        img,
        **segment_config,
        logger=logger,
    )

    # Filter
    for name, func in filter_funcs.items():
        conf = config[name].get(confuse.Optional(dict, default={}))
        func(
            tif_file,
            labels,
            **conf,
        )

    # Sample
    # mask -> csv
    csv_path = tif_file.parent / (tif_file.stem + ".csv")
    sample_fn(
        labels,
        csv_path,
        **sample_config,
    )

    # mask + image -> preview
    _save_segmentation_image(tif_file.parent, tif_file.name, img, labels)


def _select_files(
    folder: Path,
    channel: str = "C01",
) -> List[Path]:
    """Filter all TIFs in folder starting with folder name - and containing channel ID."""
    return sorted(folder.rglob(folder.name + "*" + channel + ".tif"))


def _save_segmentation_image(folder_path, filename, img, labels):
    """Save segmentation overlay as RGB image into separate folder."""
    destination_folder = folder_path.parent / (folder_path.name + "_segmentation")
    destination_folder.mkdir(exist_ok=True)
    rescaled = rescale_intensity(img_as_float(img))
    preview = label2rgb(labels, image=rescaled)
    imsave(destination_folder / (Path(filename).stem + ".png"), img_as_ubyte(preview))


# def process(
#         folder: Path,
#         file_selection_params: dict,
#         segmentation_params: dict,
#         bounding_box_params: dict,
#         additional_analysis_params: dict,
#         output_params: dict,
#         grid_sampling_params: dict,
#         logger=logging,
# ) -> None:
#     """Segment images with the provided segmentation parameters."""
#     logger.info("File selection parameters: " + json.dumps(file_selection_params, indent=4))
#     logger.info("Segmentation parameters: " + json.dumps(segmentation_params, indent=4))
#     logger.info("Additional analysis parameters: " + json.dumps(additional_analysis_params, indent=4))
#     logger.info("Output parameters: " + json.dumps(output_params, indent=4))
#     logger.info("Grid sampling parameters: " + json.dumps(grid_sampling_params, indent=4))

#     logger.info(f"Finished processing {len(tif_files)} image(s).")
