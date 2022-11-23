"""Common utility functions.
"""
import os
import io
import pandas as pd
from typing import List
from rich.console import Console


# Shared logging console object
console = Console()

# TLD dir
TLD = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def make_dir_if_not_exist(pth: str) -> None:
  """Make a directory if it does not exist.
  @param pth<str>: Path to directory to make.
  """
  assert os.path.isdir(pth) or not os.path.exists(pth), f"Path {pth} exists but is not a directory."
  if not os.path.exists(pth):
      os.makedirs(pth)


def combine_multiple_csvs_to_dataframe(
    csvPaths: List[str], sep: str = ","
) -> pd.DataFrame:
    """
    Combine multiple csvs into a single dataframe.
    
    This function is useful for combining multiple csvs into a single dataframe,
    where each csv should have the same number of columns and rows, where if a 
    given row in a particular csv can not be parsed, then that row is not parsed
    for all csvs, thereby keeping all csvs aligned in the output dataframe.
    
    @param csvPaths<List[str]>: List of paths to csvs to combine.
    @param sep<str>: Separator to use when parsing csvs.
    @return <pd.DataFrame>: Dataframe containing all data from all csvs.
    """
    # loop over all csvs and combine into a single dataframe
    allData = []
    for csvFile in csvPaths:
        with open(csvFile) as reader:
            data = reader.readlines()

        # make sure all data files are the same length and non-empty
        lenData = len(data)
        if lenData == 0:
            raise ValueError(f"Empty Data File: {csvFile}")

        # if not first file, compare with first file and make sure 
        # it has the same number of rows and columns
        if len(allData) > 0:
            lenFirstData = len(allData[0])
            if lenData != lenFirstData:
                raise ValueError(
                    "Data files are not the same length."
                    f"\n\tData file ({lenFirstData} rows): {csvPaths[0]}."
                    f"\n\tData file ({lenData} rows): {csvFile}."
                )
        allData.append(data)

    # recombine the data in memory as a big string we'll put into a dataframe
    # this makes sure that the data will stay aligned,
    # e.g. if one row has errors than that entire row will be dropped across all files
    combinedDataText = "\n".join(
        [sep.join([fields.strip() for fields in dataset]) for dataset in zip(*allData)]
    )

    # combine the data/labels by line number
    # it will warn the user if there are any lines that are not parsed
    return pd.read_csv(io.StringIO(combinedDataText), sep=sep, on_bad_lines="warn")



class ErrorLogWrapper:
    """Wrapper for rich.console.Console that logs errors with a colorful preamble.
    """
    preamble: str = ""

    def __init__(self, console: Console, preamble:str="") -> None:
      self.console = console
      self.preamble = preamble

    def write(self, msg: str):
        if msg.strip() != "":
            self.console.log(
                f"[red]{self.preamble}:[/red]\n\t" + msg.replace("\n", "\n\t"),
                style="bold yellow",
            )
