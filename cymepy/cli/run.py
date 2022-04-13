"""
CLI to run a PyDSS project
"""

from cymepy.common import CORE_CYMEPY_PROJECT_FILES, CORE_CYMEPY_OPTIONAL_PROJECT_FILES
from cymepy.utils.utils import readToml
from cymepy.cymepy import cymeInstance
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

@click.option(
    "-p", "--profile-file",
    required=False,
    default = CORE_CYMEPY_OPTIONAL_PROJECT_FILES.PROFILES.value,
    show_default=True,
    help="scenario toml file to run (over rides default)",
)

@click.option(
    "-m", "--mapping-file",
    required=False,
    default = CORE_CYMEPY_OPTIONAL_PROJECT_FILES.MAPPING_FILE.value,
    show_default=True,
    help="scenario toml file to run (over rides default)",
)

@click.command()

def run(project_path, simulations_file, profile_file, mapping_file):
    file_path = os.path.join(project_path, simulations_file)
    settings = readToml(file_path)
    if profile_file:
        settings['profiles']['source'] = profile_file
    if mapping_file:
        settings['profiles']['mapping'] = mapping_file
    
    instance = cymeInstance(settings)
    instance.runSimulation()
    return

