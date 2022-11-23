# Mars Rover Analysis Tools
This repository contains a set of tools to perform various analysis on the data collected by the Mars Rover as well as coincident data from other remote sensing sensors.


## Installation and Quickstart

```bash
# Clone the repo -- request from colorado.j.reed@gmail.com if you do not have permission
# by sending your github username
git clone TODO
cd mranalyzer

# Create and activate a virtual environment
conda create -n "mra" python=3.10
conda activate mra

# Install [py]graphviz with conda
# because binary tends to work better across systems compared to using pip
# MIT license
conda install --channel conda-forge pygraphviz

# Install mranalyzer (in editable mode, so that you can update as desired)
pip install -e .

# Example correlation analysis
mra corr

# see more options
mra corr --help

# Example segmentation
mra seg

# see more options
mra seg --help
```


## Development

### Install Development Libraries

### Precommit Hooks
To keep the code tidy and avoid oh-so-common python mistakes, we use precommit hooks. To install them, run the following:


```bash

```

### Profiling
```bash
# Generate profiling output
mra --profile corr

# Visualize profiling output (make sure snakeviz is installed)
snakeviz mra.prof
```