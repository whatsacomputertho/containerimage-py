"""
Contains docker v2s2-specific JSON schema constants for v2s2 manifests,
manifest list entries, and manifest lists
"""

from image.manifestschema   import  MANIFEST_DESCRIPTOR_SCHEMA, \
                                    IMAGE_INDEX_ENTRY_PLATFORM_SCHEMA

"""
The JSON schema for validating v2s2 manifest list entries (manifests)
Ref: https://distribution.github.io/distribution/spec/manifest-v2-2/

:meta hide-value:
"""
MANIFEST_LIST_V2_ENTRY_SCHEMA = {
    "type": "object",
    "description": "Manifests for specific platforms",
    "required": [ "mediaType", "size", "digest", "platform" ],
    "additionalProperties": False,
    "properties": {
        "mediaType": {
            "type": "string",
            "description": "The MIME type of the referenced object. " + \
                "This will generally be " +
                "application/vnd.docker.distribution.manifest.v2+json."
        },
        "size": {
            "type": "integer",
            "description": "The size in bytes of the object. This field " + \
                "exists so that a client will have an expected size for " + \
                "the content before validating. If the length of the " + \
                "retrieved content does not match the specified length, " + \
                "the content should not be trusted."
        },
        "digest": {
            "type": "string",
            "description": "The digest of the content, as defined by the " + \
                "Registry V2 HTTP API Specification."
        },
        "platform": IMAGE_INDEX_ENTRY_PLATFORM_SCHEMA
    }
}

"""
The JSON schema for validating v2s2 manifest lists
Ref: https://distribution.github.io/distribution/spec/manifest-v2-2/

:meta hide-value:
"""
MANIFEST_LIST_V2_SCHEMA = {
    "type": "object",
    "description": "The manifest list is the fat manifest which points to " + \
        "specific image manifests for one or more platforms. Its use is " + \
        "optional, and relatively few images will use one of these " + \
        "manifests. A client will distinguish a manifest list from an image " + \
        "manifest based on the Content-Type returned in the HTTP response.",
    "required" : [ "mediaType", "schemaVersion", "manifests" ],
    "additionalProperties": False,
    "properties": {
        "mediaType": {
            "type": "string",
            "description": "The MIME type of the manifest list. This should " + \
                "be set to " + 
                "application/vnd.docker.distribution.manifest.list.v2+json."
        },
        "schemaVersion": {
            "type": "integer",
            "description": "This field specifies the image manifest schema" + \
                " version as an integer. This schema uses the version 2."
        },
        "manifests": {
            "type": "array",
            "description": "The manifests field contains a list of manifests" + \
                " for specific platforms.",
            "items": MANIFEST_LIST_V2_ENTRY_SCHEMA
        }
    }
}

"""
The JSON schema for validaing v2s2 manifests
Ref: https://distribution.github.io/distribution/spec/manifest-v2-2/

:meta hide-value:
"""
MANIFEST_V2_SCHEMA = {
    "type": "object",
    "description": "The image manifest provides a configuration and a set " + \
        "of layers for a container image. It is the direct replacement for " + \
        "the schema-1 manifest.",
    "required": [ "schemaVersion", "mediaType", "config", "layers" ],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": {
            "type": "integer",
            "description": "This field specifies the image manifest schema " + \
                "version as an integer. This schema uses version 2."
        },
        "mediaType": {
            "type": "string",
            "description": "The MIME type of the manifest. This should be " + \
                "set to application/vnd.docker.distribution.manifest.v2+json."
        },
        "config": MANIFEST_DESCRIPTOR_SCHEMA,
        "layers": {
            "type": "array",
            "description": "The layer list is ordered starting from the " + \
                "base image (opposite order of schema1).",
            "items": MANIFEST_DESCRIPTOR_SCHEMA
        }
    }
}
