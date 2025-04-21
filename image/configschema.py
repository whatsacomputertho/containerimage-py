"""
Contains various JSON schema constants which together form the overarching
container image config schema
"""

# See doc comments below
CONTAINER_IMAGE_CONFIG_RUNTIME_CONFIG_SCHEMA = {
    "type": "object",
    "description": "The execution parameters which SHOULD be " + \
        "used as a base when running a container using the image. " + \
        "This field can be null, in which case any execution " + \
        "parameters should be specified at creation of the container.",
    "properties": {
        "User": {
            "type": "string",
            "description": "The username or UID which is a " + \
                "platform-specific structure that allows specific " + \
                "control over which user the process run as. This acts as " + \
                "a default value to use when the value is not specified " + \
                "when creating a container. For Linux based systems, all " + \
                "of the following are valid: user, uid, user:group, " + \
                "uid:gid, uid:group, user:gid. If group/gid is not " + \
                "specified, the default group and supplementary groups " + \
                "of the given user/uid in /etc/passwd and /etc/group from " + \
                "the container are applied. If group/gid is specified, " + \
                "supplementary groups from the container are ignored."
        },
        "ExposedPorts": {
            "type": "object",
            "description": "A set of ports to expose from a container " + \
                "running this image. Its keys can be in the format of: " + \
                "port/tcp, port/udp, port with the default protocol being " + \
                "tcp if not specified. These values act as defaults and are " + \
                "merged with any specified when creating a container. NOTE: " + \
                "This JSON structure value is unusual because it is a direct " + \
                "JSON serialization of the Go type map[string]struct and " + \
                "is represented in JSON as an object mapping its keys to an " + \
                "empty object."
        },
        "Env": {
            "type": "array",
            "description": "Entries are in the format of VARNAME=VARVALUE. " + \
                "These values act as defaults and are merged with any " + \
                "specified when creating a container.",
            "items": {
                "type": "string",
                "description": "An environment variable key-value pair in " + \
                    "the form VARNAME=VARVALUE"
            }
        },
        "Entrypoint": {
            "oneOf": [
                {
                    "type": "array",
                    "description": "A list of arguments to use as the command to " + \
                        "execute when the container starts. These values act as " + \
                        "defaults and may be replaced by an entrypoint specified " + \
                        "when creating a container.",
                    "items": {
                        "type": "string",
                        "description": "An argument to use as the command to execute " + \
                            "when the container starts."
                    },
                },
                {
                    "type": "null"
                }
            ]
        },
        "Cmd": {
            "oneOf": [
                {
                    "type": "array",
                    "description": "Default arguments to the entrypoint of the " + \
                        "container. These values act as defaults and may be replaced " + \
                        "by any specified when creating a container. If an Entrypoint " + \
                        "value is not specified, then the first entry of the Cmd array " + \
                        "SHOULD be interpreted as the executable to run.",
                    "items": {
                        "type": "string",
                        "description": "Default argument to the entrypoint of the " + \
                            "container."
                    }
                },
                {
                    "type": "null"
                }
            ]
        },
        "Volumes": {
            "oneOf": [
                {
                    "type": "object",
                    "description": "A set of directories describing where the " + \
                        "process is likely to write data specific to a container " + \
                        "instance. NOTE: This JSON structure value is unusual " + \
                        "because it is a direct JSON serialization of the Go type " + \
                        "map[string]struct and is represented in JSON as an " + \
                        "object mapping its keys to an empty object."
                },
                {
                    "type": "null"
                }
            ]
        },
        "WorkingDir": {
            "type": "string",
            "description": "Sets the current working directory of the " + \
                "entrypoint process in the container. This value acts as " + \
                "a default and may be replaced by a working directory " + \
                "specified when creating a container."
        },
        "Labels": {
            "oneOf": [
                {
                    "type": "object",
                    "description": "The field contains arbitrary metadata for the " + \
                        "container. This property MUST use the annotation rules."
                },
                {
                    "type": "null"
                }
            ]
        },
        "StopSignal": {
            "type": "string",
            "description": "The field contains the system call signal that " + \
                "will be sent to the container to exit. The signal can be " + \
                "a signal name in the format SIGNAME, for instance SIGKILL " + \
                "or SIGRTMIN+3."
        },
        "ArgsEscaped": {
            "type": "boolean",
            "description": "[Deprecated] - This field is present only for " + \
                "legacy compatibility with Docker and should not be used " + \
                "by new image builders. It is used by Docker for Windows " + \
                "images to indicate that the Entrypoint or Cmd or both, " + \
                "contains only a single element array, that is a pre-escaped, " + \
                "and combined into a single string CommandLine. If true the " + \
                "value in Entrypoint or Cmd should be used as-is to avoid " + \
                "double escaping. Note, the exact behavior of ArgsEscaped " + \
                "is complex and subject to implementation details in Moby " + \
                "project."
        },
        "Memory": {
            "type": "integer",
            "description": "This property is reserved for use, to maintain " + \
                "compatibility."
        },
        "MemorySwap": {
            "type": "integer",
            "description": "This property is reserved for use, to maintain " + \
                "compatibility."
        },
        "CpuShares": {
            "type": "integer",
            "description": "This property is reserved for use, to maintain " + \
                "compatibility."
        },
        "Healthcheck": {
            "type": "object",
            "description": "This property is reserved for use, to maintain " + \
                "compatibility."
        }
    }
}
"""
The JSON schema for the config property of a container image config

:meta hide-value:
"""

# See doc comments below
CONTAINER_IMAGE_CONFIG_ROOTFS_SCHEMA = {
    "type": "object",
    "description": "The rootfs key references the layer content addresses " + \
        "used by the image. This makes the image config hash depend on " + \
        "the filesystem hash.",
    "required": [ "type", "diff_ids" ],
    "properties": {
        "type": {
            "type": "string",
            "description": "MUST be set to layers. Implementations MUST " + \
                "generate an error if they encounter a unknown value while " + \
                "verifying or unpacking an image."
        },
        "diff_ids": {
            "type": "array",
            "description": "An array of layer content hashes (DiffIDs), " + \
                "in order from first to last.",
            "items": {
                "type": "string",
                "description": "A layer content hash (DiffID)"
            }
        }
    }
}
"""
The JSON schema for the rootfs property of a container image config

:meta hide-value:
"""

# See doc comments below
CONTAINER_IMAGE_CONFIG_HISTORY_SCHEMA = {
    "type": "object",
    "description": "Describes the history of each layer. The array is " + \
        "ordered from first to last.",
    "properties": {
        "created": {
            "type": "string",
            "description": "A combined date and time at which the layer " + \
                "was created, formatted as defined by RFC 3339, section 5.6."
        },
        "author": {
            "type": "string",
            "description": "The author of the build point."
        },
        "created_by": {
            "type": "string",
            "description": "The command which created the layer."
        },
        "comment": {
            "type": "string",
            "description": "A custom message set when creating the layer."
        },
        "empty_layer": {
            "type": "boolean",
            "description": "This field is used to mark if the history item " + \
                "created a filesystem diff. It is set to true if this " + \
                "history item doesn't correspond to an actual layer in the " + \
                "rootfs section (for example, Dockerfile's ENV command " + \
                "results in no change to the filesystem)."
        }
    }
}
"""
The JSON schema for the entries in the history list property in a container
image config

:meta hide-value:
"""

# See doc comments below
CONTAINER_IMAGE_CONFIG_SCHEMA = {
    "type": "object",
    "description": "An image is an ordered collection of root filesystem " + \
        "changes and the corresponding execution parameters for use " + \
        "within a container runtime. This specification outlines the JSON " + \
        "format describing images for use with a container runtime and " + \
        "execution tool and its relationship to filesystem changesets, " + \
        "described in Layers.",
    "required": [ "architecture", "os", "rootfs" ],
    "properties": {
        "created": {
            "type": "string",
            "description": "A combined date and time at which the image " + \
                "was created, formatted as defined by RFC 3339, section 5.6."
        },
        "author": {
            "type": "string",
            "description": "Gives the name and/or email address of the " + \
                "person or entity which created and is responsible for " + \
                "maintaining the image."
        },
        "architecture": {
            "type": "string",
            "description": "The CPU architecture which the binaries in " + \
                "this image are built to run on. Configurations SHOULD " + \
                "use, and implementations SHOULD understand, values " + \
                "listed in the Go Language document for GOARCH."
        },
        "os": {
            "type": "string",
            "description": "The name of the operating system which the " + \
                "image is built to run on. Configurations SHOULD use, and " + \
                "implementations SHOULD understand, values listed in the " + \
                "Go Language document for GOOS."
        },
        "os.version": {
            "type": "string",
            "description": "This OPTIONAL property specifies the version " + \
                "of the operating system targeted by the referenced blob. " + \
                "Implementations MAY refuse to use manifests where " + \
                "os.version is not known to work with the host OS version. " + \
                "Valid values are implementation-defined. e.g. " + \
                "10.0.14393.1066 on windows."
        },
        "os.features": {
            "type": "string",
            "description": "This OPTIONAL property specifies an array of " + \
                "strings, each specifying a mandatory OS feature. When os " + \
                "is windows, image indexes SHOULD use, and implementations " + \
                "SHOULD understand the following values: win32k: image " + \
                "requires win32k.sys on the host (Note: win32k.sys is " + \
                "missing on Nano Server)"
        },
        "variant": {
            "type": "string",
            "description": "The variant of the specified CPU architecture. " + \
                "Configurations SHOULD use, and implementations SHOULD " + \
                "understand, variant values listed in the Platform Variants " + \
                "table."
        },
        "config": CONTAINER_IMAGE_CONFIG_RUNTIME_CONFIG_SCHEMA,
        "rootfs": CONTAINER_IMAGE_CONFIG_ROOTFS_SCHEMA,
        "history": {
            "type": "array",
            "items": CONTAINER_IMAGE_CONFIG_HISTORY_SCHEMA
        }
    }
}
"""
The JSON schema for a container image config

:meta hide-value:
"""
