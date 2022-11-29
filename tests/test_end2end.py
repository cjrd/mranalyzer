from click.testing import CliRunner

from mranalyzer.cli import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_cli_corr():
    runner = CliRunner()
    result = runner.invoke(cli, ["--profile", "corr"])
    assert result.exit_code == 0


def test_cli_seg():
    runner = CliRunner()
    result = runner.invoke(cli, ["seg"])
    assert result.exit_code == 0


def test_cli_seg_match_edges():
    runner = CliRunner()
    result = runner.invoke(cli, ["seg", "--match_edges"])
    assert result.exit_code == 0
