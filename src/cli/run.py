"""
CLI to run a PyDSS project
"""

from src.common import CORE_CYMEPY_PROJECT_FILES
from src.utils.utils import readToml
from src.cymepy import cymeInstance
import logging
import click

import os

logger = logging.getLogger(__name__)

@click.argument(
    "project-path",
)

@click.option(
    "-s", "--simulations-file",
    required=False,
    default = CORE_CYMEPY_PROJECT_FILES.SIMULATION_FILE.value,
    show_default=True,
    help="scenario toml file to run (over rides default)",
)

@click.command()

def run(project_path, simulations_file):
    file_path = os.path.join(project_path, simulations_file)
    settings = readToml(file_path)
    instance = cymeInstance(settings)
    instance.runSimulation()
    return

