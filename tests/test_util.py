import os
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from mranalyzer.util import combine_multiple_csvs_to_dataframe, make_dir_if_not_exist


@pytest.fixture(scope="session")
def tempdir():
    tmpdir = tempfile.mkdtemp()
    # yield so that we can remove the temp directory after the test
    yield tmpdir
    shutil.rmtree(tmpdir)


def test_make_dir_if_not_exist_exists(tempdir):
    # pass in an existing directory should not raise an assert
    make_dir_if_not_exist(tempdir)


def test_make_dir_if_not_exist_not_exists(tempdir):
    # pass in a non-existing directory should not raise an assert
    newtmpdir = os.path.join(tempdir, "no-exist-dirname")
    make_dir_if_not_exist(newtmpdir)
    # should now exist
    assert os.path.exists(newtmpdir), "Expected directory was not created"


def test_make_dir_if_not_exist_nondir(tempdir):
    # create a non-directory file, which should throw an assert
    nondir = os.path.join(tempdir, "non-dir")
    Path(nondir).touch()
    with pytest.raises(AssertionError):
        make_dir_if_not_exist(nondir)


def setup_csv_files(tempdir):
    d = {"x1": [1, 2], "x2": [3, 4]}
    d2 = {"labels": [10, 20]}
    dataPath = os.path.join(tempdir, "test_data.csv")
    labelPath = os.path.join(tempdir, "test_labels.csv")
    pd.DataFrame(data=d).to_csv(dataPath, index=False)
    pd.DataFrame(data=d2).to_csv(labelPath, index=False)
    return dataPath, labelPath


def test_combine_multiple_csvs_to_dataframe(tempdir):
    dataPath, labelPath = setup_csv_files(tempdir)
    combinedDF = combine_multiple_csvs_to_dataframe([dataPath, labelPath])

    # check data
    assert combinedDF.shape == (2, 3), "Combined dataframe has incorrect shape"

    # check data0
    assert combinedDF["x1"][0] == 1, "Combined dataframe has incorrect data"
    assert combinedDF["x2"][0] == 3, "Combined dataframe has incorrect data"
    assert combinedDF["labels"][0] == 10, "Combined dataframe has incorrect data"

    # check data1
    assert combinedDF["x1"].values[1] == 2, "Combined dataframe has incorrect data"
    assert combinedDF["x2"].values[1] == 4, "Combined dataframe has incorrect data"
    assert combinedDF["labels"].values[1] == 20, "Combined dataframe has incorrect data"


def test_combine_multiple_csvs_to_dataframe_empty(tempdir):
    # create empty csv file
    emptyPath = os.path.join(tempdir, "empty.csv")
    Path(emptyPath).touch()
    with pytest.raises(ValueError):
        combine_multiple_csvs_to_dataframe([emptyPath])


def test_combine_multiple_csvs_to_dataframe_diff_cols(tempdir):
    dataPath, labelPath = setup_csv_files(tempdir)
    # rewrite with different number of columns, should be fine
    d3 = {"x1": [30, 40]}
    pd.DataFrame(data=d3).to_csv(dataPath, index=False)
    combinedDF = combine_multiple_csvs_to_dataframe([dataPath, labelPath])
    assert combinedDF.shape == (2, 2), "Combined dataframe has incorrect shape"


def test_combine_multiple_csvs_to_dataframe_diff_rows(tempdir):
    dataPath, labelPath = setup_csv_files(tempdir)
    # rewrite with different number of rows as label file
    d3 = {"x1": [30, 40, 50], "x2": [50, 60, 70]}
    pd.DataFrame(data=d3).to_csv(dataPath, index=False)
    with pytest.raises(ValueError):
        combine_multiple_csvs_to_dataframe([dataPath, labelPath])


def test_combine_multiple_csvs_to_dataframe_invalid_row_skipped(tempdir):
    dataPath, labelPath = setup_csv_files(tempdir)
    # rewrite with one malformed row, which should be skipped
    outputStr = """x1,x2\n2,3\n4,5,6,50,60"""
    with open(dataPath, "w") as f:
        f.write(outputStr)
    combinedDF = combine_multiple_csvs_to_dataframe([dataPath, labelPath])
    assert combinedDF.shape == (1, 3), "Combined dataframe has incorrect shape"
    assert combinedDF["x1"][0] == 2, "Combined dataframe has incorrect data"
    assert combinedDF["x2"][0] == 3, "Combined dataframe has incorrect data"
    assert combinedDF["labels"][0] == 10, "Combined dataframe has incorrect data"
