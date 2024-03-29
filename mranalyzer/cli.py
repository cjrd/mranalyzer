"""!
The command line interface for the Mars Rover Analyzer package.

See `mra --help` for more information.
"""

import atexit
import cProfile
import sys

import click

from mranalyzer import corr, seg
from mranalyzer.util import console


@click.group()
@click.option("--profile", is_flag=True, help="Profile the program.")
@click.option(
    "--profile-output",
    default="profile.out",
    help="Output file when profiling, else it's ignored.",
)
def cli(profile: bool, profile_output: str) -> None:
    """!
    This function provides the command line interface for the Mars Rover Analyzer package.

    See subcommand options with `mranalyzer --help` or `mranalyzer <subcommand> --help`.
    See click.group() for more information on the arguments.

    @param profile [bool]: Whether to profile the program or not.
    @param profile_output [str]: The output file when profiling, else it's ignored.

    @return None
    """
    # Profiling snippet modified from
    # https://stackoverflow.com/questions/55880601/how-to-use-profiler-with-click-cli-in-python
    if profile:
        console.log("Profiling...", style="bold yellow")
        pr = cProfile.Profile()
        pr.enable()

        def exit():
            pr.disable()
            pr.dump_stats(profile_output)
            console.log(
                "Profiling Complete. See profile.prof using snakeviz. `snakeviz profile.prof`",
                style="bold yellow",
            )

        atexit.register(exit)
    console.log("Beginning analysis...", style="bold yellow")


# Add the subcommands
cli.add_command(corr.corr)
cli.add_command(seg.seg)


if __name__ == "__main__":
    console.log("Use command line binary `mra`, see `mra --help`")
    sys.exit(1)
