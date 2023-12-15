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
file_selection:  # criteria for file selection in case of multiple channels/slices per position
    channel: C01
process:  # choose method how to segment, filter, and sample the objects
    segment: threshold  # choices: threshold, cellpose
    filter: [bounding_box, area, solidity, intensity]
    sample: centers  # choices: centers, grid_overlap, dense_grid

# Each subsequent section provides arguments to one of the methods defined in 'process'
threshold:
    threshold: 128
    include_holes: yes
    gaussian_sigma: 2.0 # optional 
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
intensity:
    target_channel: C03
    min_intensity: 128
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
