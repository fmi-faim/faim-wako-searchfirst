<!--
SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)

SPDX-License-Identifier: MIT
-->

# FAIM Wako SearchFirst



[![DOI](https://zenodo.org/badge/571745733.svg)](https://zenodo.org/badge/latestdoi/571745733)
[![codecov](https://codecov.io/gh/fmi-faim/faim-wako-searchfirst/graph/badge.svg?token=1LHDSD07R6)](https://codecov.io/gh/fmi-faim/faim-wako-searchfirst)
[![test](https://github.com/fmi-faim/faim-wako-searchfirst/actions/workflows/test.yml/badge.svg)](https://github.com/fmi-faim/faim-wako-searchfirst/actions/workflows/test.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/faim-wako-searchfirst.svg)](https://pypi.org/project/faim-wako-searchfirst)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/faim-wako-searchfirst.svg)](https://pypi.org/project/faim-wako-searchfirst)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install faim-wako-searchfirst
```

## Usage

Configuration is managed in a `config.yml` file:

```yaml
# Required

# criteria for file selection in case of multiple channels/slices per position
file_selection:
    channel: C01

# choose method how to segment, filter, and sample the objects
process:
    # segment methods: threshold, cellpose
    segment: threshold
    # filter methods: bounding_box, area, solidity, intensity
    filter: [bounding_box, area, solidity, feature, dilate, intensity]
    # sample methods: centers, grid_overlap, dense_grid,
    #                 object_centered_grid, region_centered_grid
    sample: centers

# Each section below provides arguments to one of the methods set in 'process'.
# Config sections for methods not selected above will be ignored.

# segment
threshold:
    threshold: 128
    include_holes: true
    gaussian_sigma: 0.0  # default: 0.0

# filter
bounding_box:
    min_x: 64
    min_y: 0
    max_x: 256
    max_y: 190
area:
    min_area: 100
    max_area: 10000
solidity:
    min_solidity: 0.9
    max_solidity: 1.0
feature:
    feature: eccentricity
    min_value: 0.0
    max_value: 0.99
dilate:
    pixel_distance: 1.0
intensity:
    target_channel: C03
    min_intensity: 128

# sample
dense_grid:
    binning_factor: 50  # default: 50
grid_overlap:
    mag_first_pass: 4
    mag_second_pass: 60
    overlap_ratio: 0.05  # default: 0
object_centered_grid:
    mag_first_pass: 4
    mag_second_pass: 60
    overlap_ratio: 0.05  # default: 0
region_centered_grid:
    mag_first_pass: 4
    mag_second_pass: 60
    overlap_ratio: 0.05  # default: 0
```

The Python script called by Wako Automation Software needs to accept the acquisition folder `folder_path` as only parameter:

```python
import typer
from faim_wako_searchfirst.main import run

def main(folder_path: str):
    run(folder=folder_path, configfile="config.yml")

if __name__ == "__main__":
    typer.run(main)
```

## License

`faim-wako-searchfirst` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
