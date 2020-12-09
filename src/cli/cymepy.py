"""Main CLI command for PyDSS."""

import logging
import click

from src.cli.run import run


logger = logging.getLogger(__name__)


@click.group()
def cli():
    """PyDSS commands"""


cli.add_command(run)
