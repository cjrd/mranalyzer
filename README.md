
<img width="150" align="left" alt="Screen Shot 2022-11-28 at 2 36 55 PM" src="https://user-images.githubusercontent.com/1455579/204395576-056cbbd1-687a-4fd2-824f-3814b2edd413.png">
<h1>MR Analyzer: Mars Rover Analyzer</h1>

This repository contains a set of tools to perform various analysis on the data collected by the Mars Rover as well as coincident data from other remote sensing sensors. This README provides a set of install instructions and quickstart, as well as more detailed walkthroughs and instructions. 

<br clear="left"/>

## Installation and Quickstart

```bash
# Clone the repo -- request from colorado.j.reed _at_ gmail.com if you do not have permission
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

## Doxygen Documentation
See the full doxygen documentation at [docs/html/index.html](docs/html/index.html)

## Correlation Analysis `mra corr`
The `mra` correlation analysis tool can be executed with the following command:

```bash
# Example correlation analysis
# reads in the data from `data/7500_data.csv` and `data/7500_labels.csv`
# and prints information about it and outputs a decision tree to `data/rover_data.pdf`
mra corr
```

This should produce an output similar to this: 
<img width="1512" alt="image" src="https://user-images.githubusercontent.com/1455579/204397037-14d522e4-bc24-4ae8-ae80-c3dbe2f8de0e.png">

```bash
# see more options
mra corr --help
```

with output similar to:

<img width="609" alt="image" src="https://user-images.githubusercontent.com/1455579/204397233-e1821643-628c-48bd-bc1f-fe2e77117701.png">

You can then visualize the decision tree that is written to file. Here, the decision tree is written to `./output/decision_tree.pdf` and looks something like this (the fill color inidicates the majority class):
<img width="1336" alt="image" src="https://user-images.githubusercontent.com/1455579/204398674-c1cffffe-3c83-4764-a042-e906866df274.png">

## Rover Segmentation `mra seg`
```bash
# Example segmentation
# reads in an example image from `images/pos/rover.jpg`
# and outputs a debugging image to `output/image_processing_progression.png`
mra seg
```

Here's the input image:

<img width="522" alt="image" src="https://user-images.githubusercontent.com/1455579/204400842-fcb5f84e-a9f7-4767-8d98-75553047ae1d.png">

Here's the debugging output (the default), which shows the input image, a map of the standard deviation of the pixel values, the output of a Canny edge detector, and the corresponding segmentation:
<img width="1136" alt="image" src="https://user-images.githubusercontent.com/1455579/204400962-970a4dc8-da69-44fc-bca7-ed27c3543c7a.png">

```bash
# see more options
mra seg --help
```
<img width="512" alt="image" src="https://user-images.githubusercontent.com/1455579/204401206-97aa5ab4-c636-447a-bcda-d14d925665f8.png">


**Tips**
* Pass in `--debug=False` to output only the segmented image, note that if a rover region is not detected, then no image will be output (the logs will indicate this as well)
* By default, each image segmentation takes less than half a second on standard laptop. The segmentation operates by determining if a pixel is within a pixel radius of an edge pixel detected by a Canny edge detector (after applying Gaussian blur to an image). A more computationally intense version can be done by passing `--match_edges` will perform only include pixels that have a similar range of pixel values as the pixel values of the detected edges within a certain pixel radius (this radius is controlled with `--seg_npx`).
* With `--debug=False`, images will not be output if they do not have more than `--rover_npx_thresh` edge pixels (default 100).

### Batch segmentation / performance analysis
[scripts/segment_images.sh](scripts/segment_images.sh) shows an example of batch processing 10 positive (rover present) and 10 negative (no rover) images. You can execute this script via 
```bash
./scripts/segment_images.sh
```

which shows the performance of the current default segmentation on the 20 examples (**note that segmenting all 20 images only takes about 13 seconds on my laptop**):

<img width="617" alt="image" src="https://user-images.githubusercontent.com/1455579/204402722-880a8aff-f084-497b-91b6-96bccecbc9b6.png">


You can use environment variables `IMGDIR` to set the directory with images to process, `OUTDIR` to set the output directory and `DEBUG` to determine whether to output the segmentation sequence or only the segmented image if it exceeds a `--seg_npx` threshold.

## Development
The following section provides startup instructions for further developing MR Analyzer.

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

### Testing
```bash
# run pytest after installing the dev libraries (see above)
pytest

# run pytest with html coverage output
pytest --cov=mranalyzer --cov-report=html
```

### Profiling
```bash
# Generate profiling output
mra --profile corr

# Visualize profiling output (make sure snakeviz is installed)
snakeviz mra.prof
```
