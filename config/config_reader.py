import json
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def get_config():
    if os.path.isfile(f"{__location__}/config.json"):
        with open(os.path.join(__location__, "config.json"), "r") as file:
            config = json.load(file)
        return config
    else:
        raise FileNotFoundError("'config.json' not found. Edit config/config_example.json with your informations and rename it 'config.json'") 
