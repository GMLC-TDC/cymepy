from src.common import DATE_FORMAT, CORE_CYMEPY_PROJECT_FILES, CYMEPY_FOLDER_STRUCTURE
from pydantic import BaseModel, validator, conint, confloat
from src.utils.utils import readToml
from datetime import datetime
from typing import List, Dict
from enum import Enum
import os
import re

class SIMULATION_TYPE(Enum):
    Static = "Static"
    QSTS = 'QSTS'

class LOGGING_LEVEL(Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    INFO = "INFO"

class HELICS_CORE_TYPE(Enum):
    Interprocess = "Interprocess"
    ZMQ_SS = "ZMQ_SS"
    TCP_SS = "TCP_SS"
    Test = "Test"
    ZMQ = "ZMQ"
    UDP = "UDP"
    TCP = "TCP"
    MPI = "MPI"

class Project_Settings(BaseModel):
    start_time: str
    sim_duration_min: conint(ge=1)
    time_step_min: conint(ge=1)
    max_iter: conint(ge=1, le=1000)
    error_tolerance: confloat(gt=0)
    simulation_type: SIMULATION_TYPE
    project_path: str
    mdb_file: str
    sxst_file: str
    cyme_installation_directory: str

    @validator('start_time')
    def validate_start_time(cls, v):
        try:
            Date = datetime.strptime(v, DATE_FORMAT)
        except:
            raise ValueError("'start_time' should be a datetime string with format {}".format( DATE_FORMAT  ))
        pass

    @validator('cyme_installation_directory')
    def validate_cyme_installation_directory(cls, v):
        if not os.path.exists(v):
            raise Exception(f"Project path: {v} does not exist")

    @validator('project_path')
    def validate_project_path(cls, v):
        if not v:
            raise Exception(f"Please provide a valid project path")
        if not os.path.exists(v):
            raise Exception(f"Cyme installation path: {v} does not exist")
        else:
            for fldr in CYMEPY_FOLDER_STRUCTURE:
                if not os.path.exists(os.path.join(v, fldr)):
                    raise Exception(f"A valid cymepy project should have a '{fldr}' folder")
            for file in CORE_CYMEPY_PROJECT_FILES:
                if not os.path.exists(os.path.join(v, file.value)):
                    raise Exception(f"A valid cymepy project should have a '{file.value}' file in the base path")

class Helics_Settings(BaseModel):
    cosimulation_mode: bool
    coiter_mode: bool
    coiter_error_tolerance: confloat(gt=0)
    max_coiter: conint(ge=1, le=1000)
    broker: str
    broker_port: conint(ge=1, le=65535)
    federate_name: str
    time_delta: confloat(gt=0.0)
    core_type: HELICS_CORE_TYPE
    uninterruptible: bool
    helics_logging_level: conint(ge=1, le=7)

class Logger_Settings(BaseModel):
    logging_level: LOGGING_LEVEL
    log_to_external_file: bool
    display_on_screen: bool
    clear_old_log_file: bool
    pre_configured_logging: bool

class Profile_Settings(BaseModel):
    use_profiles: bool
    use_internal_profile_manager: bool
    profile_database: str

class Cymepy_Settings(BaseModel):
    project: Project_Settings
    helics: Helics_Settings
    logger: Logger_Settings
    profiles: Profile_Settings

class PUBLICATION(BaseModel):
    regex_filter: str
    properties: List[str]

    @validator('regex_filter')
    def validate_regex_filter(cls, v):
        try:
            re.compile(v)
        except re.error as e:
            raise Exception(f"'{v}' is not a valid regular expression. Check https://docs.python.org/3/library/re.html")

class PUBLICATIONS(BaseModel):
    publication_dict: Dict[str, List[PUBLICATION]]

class SUBSCRIPTION(BaseModel):
    property: str
    subscription: str
    multiplier: float

class SUBSCRIPTIONS(BaseModel):
    subscription_dict: Dict[str, List[SUBSCRIPTION]]

def validate_settings(project_settings, sType):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(ROOT_DIR, "defaults", sType.value)
    default_settings = readToml(settings_path)
    default_settings.update(project_settings)
    if sType == CORE_CYMEPY_PROJECT_FILES.SIMULATION_FILE:
        Cymepy_Settings(**default_settings)
    elif sType == CORE_CYMEPY_PROJECT_FILES.PUBLICATION_FILE:
        PUBLICATIONS(publication_dict=default_settings)
    elif sType == CORE_CYMEPY_PROJECT_FILES.SUBSCRIPTION_FILE:
        SUBSCRIPTIONS(subscription_dict=default_settings)
    return default_settings


