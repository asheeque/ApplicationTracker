# application_tracker/config.py

import os
import json

# Get the environment from the ENV variable, default to "local" if not set
current_env = os.environ.get("ENV", "local")

# Given the relative path, the actual location of the `config.json` will be at the root of the project.
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')

try:
    # Load configurations from the JSON file
    with open(config_file_path, "r") as file:
        config_data = json.load(file)

    # Get the configuration for the current environment
    config = config_data.get(current_env, {})

    if not config:
        raise ValueError(f"No configuration found for environment: {current_env}")

except (IOError, json.JSONDecodeError) as e:
    raise Exception(f"Error loading configuration: {e}")

