<!--
SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)

SPDX-License-Identifier: MIT
-->

# FAIM Wako SearchFirst



[![DOI](https://zenodo.org/badge/571745733.svg)](https://zenodo.org/badge/latestdoi/571745733)
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
file_selection:
    channel: C01
segmentation:
    threshold: 128
    include_holes: yes
    min_size: 10
    max_size: 99999999999
    min_eccentricity: 0.0
    max_eccentricity: 0.4
bounding_box:
    min_x: 0
    min_y: 0
    max_x: 256
    max_y: 256
additional_analysis:
    enabled: yes
    target_channel: C03
    min_intensity: 128
output:
    type: grid
grid_sampling:
    mag_first_pass: 4
    mag_second_pass: 40
    overlap_percent: 0
    offset_grid_origin_percent: 50
```

The Python script called by Wako Automation Software needs to accept the acquisition folder `folder_path` as only parameter:

```python
import typer as typer
from faim_wako_searchfirst.segment import run

def main(folder_path: str):
    run(folder=folder_path, configfile="config.yml")

if __name__ == "__main__":
    typer.run(main)
```

## License

`faim-wako-searchfirst` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
