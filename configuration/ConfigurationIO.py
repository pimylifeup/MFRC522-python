import json
import os

class ConfigurationIO:

    FILE_CONFIG = 'config.json'
    FULL_PATH = ''

    def __init__(self, base_path) -> None:
        self.FULL_PATH = os.path.join(base_path, self.FILE_CONFIG)
        print(self.FULL_PATH)
        pass

    def read_config(self):
        with open(self.FULL_PATH,"r") as read_file:
            return json.load(read_file)

    def write_config(self, obj):
        with open(self.FULL_PATH, "w") as write_file:
            json.dump(obj, write_file)

    
