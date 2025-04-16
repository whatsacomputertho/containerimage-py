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

# Load auth file into auth dict
AUTH = {}
if os.path.exists(AUTH_FILE_PATH):
    with open(AUTH_FILE_PATH, 'r') as auth_file:
        try:
            AUTH = json.load(auth_file)
        except json.JSONDecodeError as jde:
            raise UserWarning(
                f"Auth file {AUTH_FILE_PATH} contains invalid JSON, " + \
                "proceeding without auth credentials."
            )
