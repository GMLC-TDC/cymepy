import enum


DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

class CORE_CYMEPY_PROJECT_FILES(enum.Enum):
    SIMULATION_FILE = "Settings.toml"
    PUBLICATION_FILE = "Publications.toml"
    SUBSCRIPTION_FILE = "Subscriptions.toml"
    PROFILE_MAPPING = "Mapping.toml"
    PROFILES = "Profiles.hdf5"

CYMEPY_FOLDER_STRUCTURE = ["model", "logs", "exports"]
