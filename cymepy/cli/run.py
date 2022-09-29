"""
CLI to run a PyDSS project
"""

from cymepy.common import CORE_CYMEPY_PROJECT_FILES, CORE_CYMEPY_OPTIONAL_PROJECT_FILES
from cymepy.utils.utils import readToml
from cymepy.cymepy import cymeInstance
import cymepy.logger as Logger
import logging
import click
import os

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
    default = None,
    show_default=True,
    help="Profilr toml file to run (over rides default)",
)

@click.option(
    "-m", "--mapping-file",
    required=False,
    default = None,
    show_default=True,
    help="Mapping toml file to run (over rides default)",
)

@click.option(
    "-i", "--subscription-file",
    required=False,
    default = None,
    show_default=True,
    help="subscription toml file to run (over rides default)",
)

@click.option(
    "-o", "--publication-file",
    required=False,
    default = None,
    show_default=True,
    help="Publication toml file to run (over rides default)",
)

@click.command()

def run(project_path, simulations_file, profile_file, mapping_file, subscription_file, publication_file):
    
    try:
        file_path = os.path.join(project_path, simulations_file)
        settings = readToml(file_path)
        
        LoggerTag = 'cymepy_' + str(settings['helics']['federate_name']).lower().replace('.sxst', '')
        logger = Logger.getLogger(
            LoggerTag,
            LoggerOptions=settings["logger"],
            logger_path=os.path.join(settings["project"]["project_path"], 'logs')
        )
        
        if profile_file:
            settings['profiles']['source'] = profile_file
        else:
            if not settings['profiles']['source']:
                settings['profiles']['source'] = CORE_CYMEPY_OPTIONAL_PROJECT_FILES.PROFILES.value
            
        if mapping_file:
            settings['profiles']['mapping'] = mapping_file
        else:
            if not settings['profiles']['mapping']:
                settings['profiles']['mapping'] = CORE_CYMEPY_OPTIONAL_PROJECT_FILES.MAPPING_FILE.value    
        
        if subscription_file:
            settings['helics']['subscription_file'] = subscription_file
        else:
            if not settings['helics']['subscription_file']:
                settings['helics']['subscription_file'] = CORE_CYMEPY_PROJECT_FILES.SUBSCRIPTION_FILE.value
            
        if publication_file:
            settings['helics']['publication_file'] = publication_file
        else:
            if not settings['helics']['subscription_file']:
                settings['helics']['publication_file'] = CORE_CYMEPY_PROJECT_FILES.PUBLICATION_FILE.value
        
        print(settings)
        
        instance = cymeInstance(settings)
        instance.runSimulation()
    except Exception as e:
        logger.error(e, exc_info=True)
    return

