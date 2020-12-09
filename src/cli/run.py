"""
CLI to run a PyDSS project
"""

import ast
import logging
import os
import sys

import click

from PyDSS.pydss_project import PyDssProject
from PyDSS.loggers import setup_logging
from PyDSS.utils.utils import get_cli_string, make_human_readable_size
from PyDSS.common import SIMULATION_SETTINGS_FILENAME


logger = logging.getLogger(__name__)


@click.argument(
    "project-path",
)

@click.option(
    "-s", "--simulations-file",
    required=False,
    default = SIMULATION_SETTINGS_FILENAME,
    show_default=True,
    help="scenario toml file to run (over rides default)",
)

@click.command()

def run(project_path, simulations_file=None):
   return

