# Mars Rover Analysis Tools
This repository contains a set of tools to perform various analysis on the data collected by the Mars Rover as well as coincident data from other remote sensing sensors.


## Installation and Quickstart

```bash
# Clone the repo -- request from colorado.j.reed@gmail.com if you do not have permission
git clone git@github.com:cjrd/mranalyzer.git
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

## Correlation Analysis `mra corr`
The `mra` correlation analysis tool can be executed with the following command:

```bash
# Example correlation analysis
mra corr

# see more options
mra corr --help
```


## Rover Segmentation `mra seg`



## Development

### Install Development Libraries
```bash
# install development libraries
pip install -e ".[dev]"

# enable pre-commit hooks
pre-commit install
```

Note that to keep the code tidy and avoid oh-so-common python mistakes, we use precommit hooks. The pre-commit hooks will be installed using the above pip development install command. To run the pre-commit hooks, run the following command (they will also be run automatically when you commit code):
```bash
pre-commit run  --all-files
```

### Profiling
```bash
# Generate profiling output
mra --profile corr

# Visualize profiling output (make sure snakeviz is installed)
snakeviz mra.prof
```