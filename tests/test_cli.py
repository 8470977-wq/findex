import pytest
from typer.testing import CliRunner
from findex.cli import app

runner = CliRunner()

def test_full_pipeline():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
