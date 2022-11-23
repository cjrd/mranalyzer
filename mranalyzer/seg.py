import functools
import os
import time
from multiprocessing.pool import Pool

import click
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial as spsp
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.ndimage import distance_transform_edt
from skimage import feature

from mranalyzer.util import TLD, console, make_dir_if_not_exist


def _sharesStdVal(xy, ptIndex, ptVals, sigmaMap, kdist):
    nearVals = ptIndex.query_ball_point(xy, kdist, workers=-1)
    for val in nearVals:
        if ptVals[val] == sigmaMap[xy]:
            return True
    return False


def crop_rover(image, canny, sigmaMap, xydist=50):
    """_summary_

    Args:
        image (_type_): _description_
        canny (_type_): _description_
        sigmaMap (_type_): _description_
        xydist (int, optional): _description_. Defaults to 50.

    Returns:
        _type_: _description_
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
        _sharesStdVal, ptIndex=ptIndex, ptVals=ptVals, sigmaMap=sigmaMap, kdist=xydist
    )
    coords = list(zip(*validIdxs))
    with Pool() as pool:
        res = pool.map(mapfun, coords)
    for i, resVal in enumerate(res):
        if resVal:
            result[coords[i]] = image[coords[i]]
    return result


def crop_rover_fast(image, canny, xydist=50):
    """_summary_

    Args:
        image (_type_): _description_
        canny (_type_): _description_
        xydist (int, optional): _description_. Defaults to 50.

    Returns:
        _type_: _description_
    """
    rows, cols = image.shape
    # get the distance of every point to an edge
    dt = distance_transform_edt(~canny)
    # only examine points within xydist of an edge
    validIdxs = dt <= xydist
    result = np.zeros((rows, cols), dtype=float)
    result[validIdxs] = image[validIdxs]
    return result


@click.command()
@click.option(
    "--outimage",
    "-o",
    "output_path",
    default="./output/image_processing_progression.png",
    help="Output file for image progression results",
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
    "--input",
    "-i",
    "input_image",
    default=os.path.join(TLD, "images/pos/rover.jpg"),
    help="Input image to process",
)
def seg(**kwargs):
    startTime = time.time()

    img = mpimg.imread(kwargs["input_image"])
    imgMean = img.mean()
    img_std = img.std()
    bins = [i * img_std for i in range(4)]
    # zero center the image so that stds are centered around 0 and
    # we can use abs() to determine sigma map
    sigmaMap = np.digitize(np.abs(img - imgMean), bins)

    edges = feature.canny(img, sigma=kwargs["gsigma"])

    # set all "non-rover" pixels to 0
    if kwargs["match_edges"]:
        rover = crop_rover(img, edges, sigmaMap, kwargs["seg_npx"])
    else:
        rover = crop_rover_fast(img, edges, kwargs["seg_npx"])

    runtime = time.time() - startTime
    console.log("Finished analysis.")
    console.log(f"Runtime: {runtime:.2f} seconds", style="bold yellow")

    # write the image progression to file
    console.log("Writing output to file.")

    make_dir_if_not_exist(os.path.dirname(kwargs["output_path"]))
    save_rover_images(
        img, sigmaMap, edges, rover, kwargs["output_path"], kwargs["gsigma"]
    )
    console.log("Done.")

    return True


def save_rover_images(img, sigmaMap, edges, rover, outname: str, sig: float):
    """Save the rover images to disk that show the original image,
    the sigma map, the edges, and the rover.

    Args:
        img (_type_): _description_
        sigmaMap (_type_): _description_
        edges (_type_): _description_
        rover (_type_): _description_
        outname (str): _description_
    """
    # save the original image, the canny edge detection map, and the cropped image
    fig = plt.figure(figsize=(16, 12))
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
