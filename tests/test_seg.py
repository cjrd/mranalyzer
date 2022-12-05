"""Test segmentation logic.
"""
import numpy as np

from mranalyzer.seg import crop_rover_fast


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
