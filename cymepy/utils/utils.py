import toml
import os

def readToml(file_path):
    if os.path.exists(file_path):
        data = toml.load(open(file_path, "r"))
        return data
    else:
        raise Exception(f"File path does not exist: {file_path}")

def writeToml(file_path, data_dict):
    data = toml.dump(data_dict, open(file_path, "w"))