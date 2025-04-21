"""
Contains the AUTH constant which loads the user's default podman auth file.
"""

import json
import os
import sys

# Auth file constants & env vars
if sys.platform == "linux":
    AUTH_FILE_PATH_DEFAULT = os.path.expandvars(
        "$XDG_RUNTIME_DIR/containers/auth.json"
    )
else:
    AUTH_FILE_PATH_DEFAULT = os.path.expandvars(
        "$HOME/.config/containers/auth.json"
    )
AUTH_FILE_PATH = os.environ.get("AUTH_FILE_PATH", AUTH_FILE_PATH_DEFAULT)

# AUTH constant
AUTH = {}
"""
The AUTH constant contains the loaded contents from your default podman
auth file.  This is located at $XDG_RUNTIME_DIR/containers/auth.json on linux
and $HOME/.config/containers/auth.json on mac and windows

The AUTH constant remains an empty dict if the user has no auth file.  A
UserWarning is raised if the user's auth file does exist, but contains invalid
JSON.

:meta hide-value:
"""

# Load auth file into auth dict
if os.path.exists(AUTH_FILE_PATH):
    with open(AUTH_FILE_PATH, 'r') as auth_file:
        try:
            AUTH = json.load(auth_file)
        except json.JSONDecodeError as jde:
            raise UserWarning(
                f"Auth file {AUTH_FILE_PATH} contains invalid JSON, " + \
                "proceeding without auth credentials."
            )
