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

# Install mranalyzer (in editable mode, so that you can update the code and have the updates propagated)
pip install -e .

# This should install a binary called `mra`
mra --help

# Which has two key subcommands: `corr` and `seg`

# Example correlation analysis
# reads in the data from `data/7500_data.csv` and `data/7500_labels.csv`
# and prints information about it and outputs a decision tree to `data/rover_data.pdf`
mra corr

# see all options
mra corr --help

# Example segmentation
# reads in an example image from `images/pos/rover.jpg`
# and outputs a debugging image to `output/image_processing_progression.png`
mra seg

# see all options
mra seg --help
```

## Correlation Analysis `mra corr`
The correlation analysis tool is used to analyze the data collected by the Mars Rover and determine which features are most important in predicting the labels. The tool uses a decision tree to determine the most important features. The tool can also be used to determine the most important features in predicting the labels for the data collected by the Mars Rover. The `mra` correlation analysis tool can be executed with the following command:

```bash
# Example correlation analysis
# reads in the data from `data/7500_data.csv` and `data/7500_labels.csv`
# and prints information about it and outputs a decision tree to `data/rover_data.pdf`
mra corr

# see all options
mra corr --help
```


## Rover Segmentation `mra seg`
The rover segmentation tool is used to segment the images collected by the Mars Rover. The tool uses a combination of simple image processing techniques to segment the images into rover/background regions.

```bash
# Example segmentation
# reads in an example image from `images/pos/rover.jpg`
# and outputs a debugging image to `output/image_processing_progression.png`
mra seg

# see all options
mra seg --help
```

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