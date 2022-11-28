"""!
Perform an exploratory correlation analysis of the input atmospheric data.

This subpackage contains functions for performing an exploratory correlation
analysis of the input atmospheric data. The main function for this subpackage is
corr(), which can be called from the command line as follows: `mra corr`;
see `mra corr --help` for more information.
"""

import os
import sys
import time
from contextlib import redirect_stderr

import click
import graphviz
import numpy as np
import pandas as pd
from rich.markdown import Markdown
from rich.table import Table
from sklearn import tree

from mranalyzer.util import (
    TLD,
    ErrorLogWrapper,
    combine_multiple_csvs_to_dataframe,
    console,
    make_dir_if_not_exist,
)


def run_decision_tree(
    X: pd.DataFrame, y: pd.DataFrame, randomSeed: int = 0
) -> tree.DecisionTreeClassifier:
    """!
    Fit a decision tree to the input data and return the classifier.

    @param X (pd.DataFrame): An input dataframe of covariates for the decision tree classifier.
    @param y (pd.DataFrame): An input dataframe of labels for the decision tree classifier.
    @param randomSeed (int, optional): Random seed for the decision tree classifier. Defaults to 0.
    @returns (tree.DecisionTreeClassifier): A trained decision tree classifier
    """
    clf = tree.DecisionTreeClassifier(random_state=randomSeed)
    clf = clf.fit(X, y)
    return clf


def plot_decision_tree(
    model: tree.DecisionTreeClassifier, featureNames: str, outdir: str
) -> None:
    r"""!
    Export the decision tree to a dot file and a rendered pdf into \p outdir.

    @param model (DecisionTreeClassifier): the decision tree model
    @param featureNames (str): the names of the features
    @param outdir (str): the output directory
    """
    dot_data = tree.export_graphviz(
        model,
        out_file=None,
        filled=True,
        rounded=True,
        special_characters=True,
        feature_names=featureNames,
    )
    graph = graphviz.Source(dot_data)
    outpath = os.path.join(outdir, "decision_tree")
    try:
        graph.render(outpath, overwrite_source=True)
    except PermissionError:
        # a strange permission error results if graphviz is installed via pip instead of conda
        console.print(
            "Unable to render decision tree. Did you install graphviz as follows? "
            "`conda install --channel conda-forge pygraphviz`",
            style="red",
        )
        sys.exit(1)
    console.log(f"Writing decision tree to {outpath} and {outpath}.pdf")


@click.command()
@click.option(
    "--output",
    "-o",
    "output_path",
    default="./output",
    help="Output directory for results",
)
# for some reason, doxygen wants to document this option as a variable. This cond comment hides it
##\cond # noqa: E265
@click.option(
    "--data",
    "data_path",
    default=os.path.join(TLD, "data/7500_data.csv"),
    type=click.Path(exists=True),
    show_default=True,
    help="Input atmopheric data csv file, see default for example",
)
@click.option(
    "--labels",
    "labels_path",
    default=os.path.join(TLD, "data/7500_labels.csv"),
    type=click.Path(exists=True),
    show_default=True,
    help="Input atmopheric data labels, see default for example",
)
##\endcond # noqa: E265
@click.option(
    "--min_lon",
    default=30.0,
    type=float,
    show_default=True,
    help="The minimum longitude to include in the analysis",
)
@click.option(
    "--max_lon",
    default=120.0,
    type=float,
    show_default=True,
    help="The maximum longitude to include in the analysis",
)
@click.option(
    "--min_lat",
    default=33.0,
    type=float,
    show_default=True,
    help="The minimum latitude to include in the analysis",
)
@click.option(
    "--max_lat",
    default=80.0,
    type=float,
    show_default=True,
    help="The maximum latitude to include in the analysis",
)
@click.option(
    "--random_seed",
    default=0,
    type=int,
    show_default=True,
    help="The random seed to use for the analysis",
)
def corr(**kwargs) -> None:
    """!
    Perform an exploratory correlation analysis of the input atmospheric data.

    Run `mra corr --help` to see all input options.
    """
    startTime = time.time()
    console.print(Markdown("# Starting correlation analysis"))
    console.print("Input settings: ")

    with (
        console.status("Loading data", spinner="dots")
        and redirect_stderr(
            ErrorLogWrapper(
                console,
                preamble="Data loading issue (inspect/clean your data at these lines to fix)",
            )
        )
    ):
        console.log("[bold underline]Loading data: ")
        # redirect errors so that they are more informative for the user / aligned in a pretty way
        # this is necessary because pandas prints to stderr instead of returning all info
        # about the error (i.e. the line number that did not process correctly)
        df = combine_multiple_csvs_to_dataframe(
            [kwargs["data_path"], kwargs["labels_path"]]
        )
        df.labels = df.labels.astype(np.int)

    # Summarize the input data
    minLat, maxLat = kwargs["min_lat"], kwargs["max_lat"]
    minLon, maxLon = kwargs["min_lon"], kwargs["max_lon"]
    assert (
        minLat < maxLat
        and minLat >= 0
        and maxLat <= 90
        and minLon < maxLon
        and minLon >= 0
        and maxLon <= 180
    ), f"Invalid lat/lon range: {minLat}, {maxLat}, {minLon}, {maxLon}"

    # take only the data of interest from the lat/lon spec
    refinedDF = df[
        df.retrieval_latitude.between(minLat, maxLat, inclusive="neither")
        & df.retrieval_longitude.between(minLon, maxLon, inclusive="neither")
    ]

    # create a pretty summary of the data
    table = Table(title="Data Summary")
    table.add_column("Description", justify="right", style="cyan", no_wrap=True)
    table.add_column("Counts", style="magenta")
    table.add_column("Percent of Total", style="magenta")
    table.add_row("All", str(len(df)), "100%")
    table.add_section()
    table.add_row(
        f"{minLat} < lat < {maxLat} and {minLon} < lon < {maxLon}",
        str(len(refinedDF)),
        f"{len(refinedDF)/len(df):.2%}",
    )
    for className, classCt in refinedDF.labels.value_counts().items():
        table.add_row(f"|-> Class {className}", f"{classCt}")
    console.log(table)

    # setup the output dir
    make_dir_if_not_exist(kwargs["output_path"])

    # specify inputs/labels and run decision tree
    X = refinedDF.drop("labels", axis=1)
    y = refinedDF.labels

    clf = run_decision_tree(X, y, kwargs["random_seed"])
    plot_decision_tree(clf, X.columns, kwargs["output_path"])

    runtime = time.time() - startTime
    console.log(f"Runtime: {runtime:.2f} seconds", style="bold yellow")
