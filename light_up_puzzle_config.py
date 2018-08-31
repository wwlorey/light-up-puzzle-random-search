import json

class LightUpPuzzleConfig:
    def __init__(self, config_file):
        """Initializes the light up puzzle config class.

        This class assumes JSON format for data in config_file.
        """

        with open(config_file, 'r') as file:
          self.settings = json.loads(file.read().replace('\n', ''))
