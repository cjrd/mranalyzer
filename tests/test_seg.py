"""Test segmentation logic.
"""
import numpy as np
import pytest
import scipy.spatial as spsp

from mranalyzer.seg import crop_rover, crop_rover_fast, shares_std_val_within_dist


@pytest.fixture
def image():
    # Create and return a sample input image
    return np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])


@pytest.fixture
def canny():
    # Create and return a sample Canny edge detection map
    return np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]])


@pytest.fixture
def sigmaMap():
    # Create and return a sample standard deviation map
    return np.array([[1, 1, 1], [1, 1, 1], [2, 2, 2]])


@pytest.fixture
def ptIndex():
    # Create and return a sample pixel index
    return spsp.KDTree([(1, 1), (1, 2), (2, 1), (2, 2)])


@pytest.fixture
def ptVals():
    # Create and return a sample list of standard deviation values
    return [1, 1, 2, 2]


def test_crop_rover(image, canny, sigmaMap):
    # Test the crop_rover function with the sample input arrays
    result = crop_rover(image, canny, sigmaMap)

    # Assert that the result is a numpy array
    assert isinstance(result, np.ndarray)

    # Assert that the shape of the result array is the same as the input arrays
    assert result.shape == image.shape

    # Assert that the result array has the expected values
    expected_result = np.array([[1, 2, 3], [4, 5, 6], [0, 0, 0]])
    assert np.allclose(result, expected_result, atol=0.1)


def test_crop_rover_fast():
    #
    # Test case with all non-zero pixels within xydist of an edge pixel
    #
    img = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]])
    canny = np.array([[0, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 1, 0, 0, 0]])

    # expect all pixels within 1 of an edge pixel to be non-zero
    expected_output = np.array([[0, 0, 3, 4, 5], [0, 7, 8, 9, 0], [11, 12, 13, 0, 0]])
    res = crop_rover_fast(img, canny, xydist=1)

    # will only print if the test fails
    print(f"Expected:\n {expected_output}")
    print(f"Actual:\n {res}")
    assert np.allclose(res, expected_output, atol=0.1)

    #
    # Test case with no non-zero pixels within xydist of an edge pixel
    #
    expected_output = np.array([[0, 0, 0, 4, 0], [0, 0, 8, 0, 0], [0, 12, 0, 0, 0]])

    # will only print if the test fails
    res = crop_rover_fast(img, canny, xydist=0)
    print(f"\nExpected:\n {expected_output}")
    print(f"Actual:\n {res}")
    assert np.allclose(res, expected_output)

    #
    # Test case with xydist greater than the max distance to any edge pixel
    #
    assert np.array_equal(crop_rover_fast(img, canny, xydist=100), img)


def test_shares_std_val_within_dist(ptIndex, ptVals, sigmaMap):
    # Test the shares_std_val_within_dist function with sample input data
    result = shares_std_val_within_dist((1, 1), ptIndex, ptVals, sigmaMap, 1)
    assert result, "Expected the share_std_val_within_dist function to return True"

    # Test the function with a different distance
    result = shares_std_val_within_dist((3, 3), ptIndex, ptVals, sigmaMap, 1)
    assert not result, "Expected the share_std_val_within_dist function to return False"
