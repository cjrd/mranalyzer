# Challenge Notes
This file includes notes on the JPL coding challenge. I've separated these notes from the main documentation to decouple my notes from the type of documentation I would provide to other users. Generally speaking, I treated this challenge similar to a real-world open source project, where I aimed for usability, documentation, and reproducibility. 

## Changes
* I separated the correlation and segmentation commands into separate files and added a cli file for managing the command line interface and a file for the general utils.
* I made a binary for the `mra` command and added subcommands for `corr` and `seg`. I made most of the options arguments that could be passed to the subcommands using the [click](https://pypi.org/project/click/) library, which provides a nice interface for managing command line arguments (arg validation, help messages, and documentation).
* For the correlation analysis, I fixed a bug in loading multiple csvs simultaneously, where in `util.py` the function `combine_multiple_csvs_to_dataframe` uses pandas to load multiple csvs into a single dataframe that keeps them aligned in the event that some of the data is malformed (and prints warnings to the user). I also added tests for this function in `test_utils.py`. Switching to a pandas loader resulted in a significant speedup in loading the data, as the previous method was loading and processing the data line by line. I also updated the decision tree to use the attribute names from the csv file.
* For the segmentation analysis, I parallelized and vectorized the code to speed up the segmentation, where the original behavior can be reproduced using the `--match_edges` flag. Each image takes around 4 seconds to process using the `--match_edges` flag, where it originally took around 20 seconds on my machine. Also, without the `--match_edges` command, the code will simply check if a pixel is within `--seg_npx` of the edge and if so, it will be segmented. This is much faster than the original method, but it does not produce the exact same results (though they are similar). Each image takes around 0.5 seconds to process in this case. I also added a `--rover_npx_thresh` flag that will not output a rover image if it has fewer than `--rover_npx_thresh` edge pixels (default value at 100px seems to perform best with the 20 example images I added).
* I added 10 positive (has rover) and 10 negative (no rover) images to the `images` directory for testing the segmentation analysis.
* I added a script that runs the segmentation analysis on the 20 example images and evaluates the results. This script can be run using `./scripts/segment_images.sh`. This script also outputs the performance of the segmentation analysis on the 20 example images. The script segments the images in parallel and takes around 13 seconds to run on my machine (the original script would take 20s per image = 260s).
* I added a `--profile` option to allow for profiling.
* I added unit test and integration tests in the `tests` directory. The state of the tests is roughly what I would aim for at this stage of the project, i.e. some sanity checks and a few tests for the main functions. I would continue to add more tests as the project progresses.
* I added [rich](https://pypi.org/project/rich/) for pretty printing of the logs and results.
* Added documenation and a `--help` option to the `mra` command.
* Added pre-commit hooks to enforce code style and linting.
* Added a README with installation instructions, quickstart example, and more detailed walkthroughs and instructions.
* Made the package pip-installable and added a setup.cfg file (with a list of open source licenses used)
* I removed the k-fold SVM analysis in the correlation analysis. Currently, it is not clear if we want to create a robust classifier or simply understand the correlations in the data. If we want a robust classifier, then it may makes sense to use all data from all lat/lons. If we want to understand the correlations, then it may make sense to use a subset of the data. I would want to understand the use case better to make a decision on this. Also, the unnamed 0/1/2 labels in the csvs are not clear to me, so I'm not sure how to interpret the results of the SVM analysis.


## Testing
All tests can be run through:
```bash
pytest
```

`pytest` runs a set of unit tests, where the ``unit tests'' in `test_end2end.py` are simple integration test around the correlation and segmentation analysis. I've included some standard unit tests at `tests/test_util.py` and `tests/test_seg.py`. This unit tests the functions in `utils.py` and `seg.py`. As a design choice, I try not to write unit tests for functions that call a sequence of third-party functions (like those in the `corr` files), because this often leads to brittle tests that constantly break as the analysis evolves. Instead, I prefer to write integration tests that test the entire analysis pipeline so that the internals can easily change without breaking the tests. These tests are not meant to be exhaustive, but rather to provide a quick sanity check that the code is working as expected. I find this type of testing is useful during rapid development periods, but I would not rely on these tests for a full production release.



## Future Work
Ideas and directions for future work:

* Would an image classification pipeline be more helpful instead of a segmentation pipeline? This would allow the science team to easily classify collections of photos as having/not-having a rover and then quickly skim through the photos that have a rover to find the appropriate images for their analysis. Also, since the images are pretty small, I think a classification pipeline would be more robust than a segmentation pipeline without requiring more mental overhead from the users.
* Integrate tests/examples/pre-commit hooks a Github Actions workflow
* Explore more correlation workflows and classifiers
* Explore more unsupervised segmentation workflows.
