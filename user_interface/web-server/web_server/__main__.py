import logging
import argparse

import yaml
import pydash
import paho.mqtt.client as mqtt

from . import make_app

# -----------------------------------------------------------------------------
# YAML setup
# -----------------------------------------------------------------------------


def env_constructor(loader, node):
    return os.path.expandvars(node.value)


# !env expands all environment variables
yaml.SafeLoader.add_constructor("!env", env_constructor)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser("web_interface")
    args.add_argument(
        "--profile", "-p", required=True, help="Path to profile YAML file"
    )
    args, _ = parser.parse_known_args()

    # Read profile
    with open(args.profile, "r") as profile_file:
        profile = yaml.safe_load(yaml_file)

    # Run web server
    app = make_app(profile)
    app.run()
