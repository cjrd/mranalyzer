"""!
Segment images taken by the mars rover.

This subpackage contains functions for performing a segmentation of images
taken by the mars rover, such that it will segment out the rover itself.
The main function for this subpackage is
seg(), which can be called from the command line as follows: `mra seg`;
see `mra seg --help` for more information.
"""
import functools
import os
import time
from multiprocessing.pool import Pool
from typing import List

import click
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial as spsp
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.ndimage import distance_transform_edt
from skimage import feature
from skimage.color import rgb2gray

from mranalyzer.util import TLD, console, make_dir_if_not_exist


def shares_std_val_within_dist(
    xy: List[int],
    ptIndex: spsp.KDTree,
    ptVals: List[int],
    sigmaMap: np.ndarray,
    kdist: float,
) -> bool:
    """!
    Internal helper function for determining if a pixel shares a
    standard deviation value with any points within a given distance.

    This helper function is necessary in order to multiprocess this check.

    @param xy (List[int]): [x,y] coordinates of the pixel to check
    @param ptIndex (sps.KDTree): index of all pixels that are edges,
      for finding nearest edge neighbors for a given pixel
    @param ptVals (List[int]): standard deviation values of all edge pixels
    @param sigmaMap (np.array): standard deviation map of the image
    @param kdist (float): distance to check for edge pixels neighbors
    @return (bool): True if the pixel shares a standard deviation value
      with an edge pixel within kdist, False otherwise
    """
    nearVals = ptIndex.query_ball_point(xy, kdist, workers=-1)
    for val in nearVals:
        if np.isclose(ptVals[val], sigmaMap[xy], atol=0.1):
            return True
    return False


def crop_rover(
    image: np.ndarray, canny: np.ndarray, sigmaMap: np.ndarray, xydist: float = 50
) -> np.ndarray:
    """!
    Crop the rover out of the image.

    This function operates by determining if a pixel shares a standard deviation range with *any*
    edge pixels within a given distance. If it does, then it is considered to be part of the rover.

    @param image (np.ndarray): Image array: 2d array of pixel values
    @param canny (np.ndarray): Canny edge detection map
    @param sigmaMap (np.ndarray): Standard deviation map of the image
    @param xydist (int, optional): Max distance to edge pixels to be considered part of the rover.
      Defaults to 50.

    @return (np.ndarray): Image array same size of the original image,
      but with all non-rover pixels set to 0
    """
    rows, cols = image.shape
    edgeIdxs = [x for x in zip(*np.nonzero(canny))]

    # get the distance of every point to an edge
    dt = distance_transform_edt(~canny)

    # only examine points within xydist of an edge
    validIdxs = np.where(dt <= xydist)
    result = np.zeros((rows, cols), dtype=float)
    ptVals = [sigmaMap.item(*x) for x in edgeIdxs]
    ptIndex = spsp.KDTree(edgeIdxs)
    result = np.zeros((rows, cols), dtype=float)
    mapfun = functools.partial(
        shares_std_val_within_dist,
        ptIndex=ptIndex,
        ptVals=ptVals,
        sigmaMap=sigmaMap,
        kdist=xydist,
    )
    coords = list(zip(*validIdxs))
    # multiprocess the check (leads to a 2x-3x speedup)
    with Pool() as pool:
        res = pool.map(mapfun, coords)

    # reconstruct the result array from the multiprocessed results
    for i, resVal in enumerate(res):
        if resVal:
            result[coords[i]] = image[coords[i]]
    return result


def crop_rover_fast(image: np.ndarray, canny: np.ndarray, xydist: float = 50):
    """!
    Crop the rover out of the image.

    This function operates by determining if a pixel is within a pixel radius of an edge pixel.
    If it is, then it is considered to be part of the rover.
    This function is 10x-20x faster than crop_rover, and in most cases, produces similar results.

    @param image (np.ndarray): Image array: 2d array of pixel values
    @param canny (np.ndarray): Canny edge detection map
    @param xydist (int, optional): Max distance to edge pixels to be considered part of the rover.
      Defaults to 50.

    @return (np.ndarray): Image array same size of the original image,
      but with all non-rover pixels set to 0
    """
    rows, cols = image.shape
    # get the distance of every point to an edge
    dt = distance_transform_edt(~canny)
    # only examine points within xydist of an edge
    validIdxs = dt <= xydist
    result = np.zeros((rows, cols), dtype=float)
    result[validIdxs] = image[validIdxs]
    return result


def save_debugging_images(
    img: np.ndarray,
    sigmaMap: np.ndarray,
    edges: np.ndarray,
    rover: np.ndarray,
    outname: str,
    sig: float,
):
    """!
    Save the rover images to disk that can be useful for debugging:
    (1) the original image
    (2) the sigma map
    (3) the canny edge image
    (4) the cropped rover image

      @param img (np.ndarray): Image array: 2d array of pixel values
      @param sigmaMap (np.ndarray): Standard deviation map of the image
      @param edges (np.ndarray): Canny edge detection map
      @param rover (np.ndarray): Cropped image with only the rover pixels
      @param outname (str):
      @param sig (float):
    """
    # save the original image, the canny edge detection map, and the cropped image
    fig = plt.figure(figsize=(24, 12))
    ax1 = fig.add_subplot(141)
    im1 = ax1.imshow(img, cmap=cm.gray)
    ax1.set_title("Original Image")

    divider = make_axes_locatable(ax1)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im1, cax=cax, orientation="vertical")

    ax2 = fig.add_subplot(142)
    im2 = ax2.imshow(sigmaMap)
    ax2.set_title("Sigma From Mean")

    divider = make_axes_locatable(ax2)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im2, cax=cax, orientation="vertical")

    ax3 = fig.add_subplot(143)
    im3 = ax3.imshow(edges, cmap=cm.gray)
    ax3.set_title(f"Canny Edge - {sig} Sigma")

    divider = make_axes_locatable(ax3)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im3, cax=cax, orientation="vertical")

    ax4 = fig.add_subplot(144)
    im4 = ax4.imshow(rover, cmap=cm.gray)
    ax4.set_title("Rover Crop")

    divider = make_axes_locatable(ax4)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im4, cax=cax, orientation="vertical")

    plt.savefig(outname, dpi=200)


@click.command()
@click.option(
    "--input",
    "-i",
    "input_image",
    default=os.path.join(TLD, "images/pos/rover.jpg"),
    help="Input image to process",
)
@click.option(
    "--output",
    "-o",
    "output_img",
    default="./output/image_processing_progression.png",
    help="Output file for image progression results, image processing progression if debug=True,"
    "else the segmented image",
)
@click.option(
    "--debug",
    type=bool,
    default=True,
    help="Output the segmented image and image processing progression,"
    "rather than just the segmented image (if it has the rover in it)",
)
@click.option(
    "--gsigma",
    default=7.0,
    type=float,
    show_default=True,
    help="Std used for Gaussian blur prior to running Canny edge detection. "
    "Higher number results in fewer edges.",
)
@click.option(
    "--match_edges",
    is_flag=True,
    help="Segment the region where the std is quantized to the same region as any edge "
    "within --seg_npx pixels.",
)
@click.option(
    "--seg_npx",
    default=100,
    type=int,
    show_default=True,
    help="Segment the region within seg_npx pixels of any edge.",
)
@click.option(
    "--rover_npx_thresh",
    default=100,
    type=int,
    show_default=True,
    help="Count the rover as segmented if it has at least "
    "rover_npx_thresh edge pixels, else it's an empty image.",
)
def seg(**kwargs):
    """!
    Segment an image to only include the rover.

    This segmentation function operates under the assumption that the rover produces
    edges in the image, and that the edge regions are the only part of the image that we care about.

    Run `mra seg --help` to see all input options and consult README.md for more details.
    """
    startTime = time.time()

    img = mpimg.imread(kwargs["input_image"])
    # convert to rgb if color image
    if len(img.shape) == 3:
        img = rgb2gray(img)
    imgMean = img.mean()
    img_std = img.std()
    bins = [i * img_std for i in range(4)]
    # zero center the image so that stds are centered around 0 and
    # we can use abs() to determine sigma map
    sigmaMap = np.digitize(np.abs(img - imgMean), bins)
    edges = feature.canny(img, sigma=kwargs["gsigma"])

    if kwargs["debug"] or edges.sum() > kwargs["rover_npx_thresh"]:
        # set all "non-rover" pixels to 0
        if kwargs["match_edges"]:
            rover = crop_rover(img, edges, sigmaMap, kwargs["seg_npx"])
        else:
            rover = crop_rover_fast(img, edges, kwargs["seg_npx"])
    else:
        rover = np.zeros_like(img)

    runtime = time.time() - startTime
    console.log("Finished analysis.")
    console.log(f"Runtime: {runtime:.2f} seconds", style="bold yellow")

    # write the image progression to file
    console.log("Writing output to file.")

    make_dir_if_not_exist(os.path.dirname(kwargs["output_img"]))
    if kwargs["debug"]:
        save_debugging_images(
            img, sigmaMap, edges, rover, kwargs["output_img"], kwargs["gsigma"]
        )
    else:
        if rover.sum() > 0:
            plt.imsave(kwargs["output_img"], rover, cmap=cm.gray)
        else:
            console.log("Rover not found in image.", style="bold blue")
    console.log("Done.")

    return True
