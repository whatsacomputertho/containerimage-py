"""
Contains OCI-specific JSON schema constants for OCI image indices, index
entries, and manifests
"""

from image.manifestschema   import  MANIFEST_DESCRIPTOR_SCHEMA, \
                                    IMAGE_INDEX_ENTRY_PLATFORM_SCHEMA

# See doc comments below
IMAGE_INDEX_ENTRY_OCI_SCHEMA = {
    "type": "object",
    "description": "Each object in manifests includes a set of descriptor " + \
        "properties with the following additional properties and restrictions.",
    "required": [ "mediaType", "digest", "size" ],
    "additionalProperties": False,
    "properties": {
        "mediaType": {
            "type": "string",
            "description": "This descriptor property has additional " + \
                "restrictions for manifests. Implementations MUST support " + \
                "at least the application/vnd.oci.image.manifest.v1+json " + \
                "media type.  Image indexes concerned with portability " + \
                "SHOULD use one of the aforementioned media type. Future " + \
                "versions of the spec MAY use a different mediatype " + \
                "(i.e. a new versioned format). An encountered mediaType " + \
                "that is unknown SHOULD be safely ignored."
        },
        "digest": {
            "type": "string",
            "description": "This REQUIRED property is the digest of the " + \
                "targeted content, conforming to the requirements outlined " + \
                "in Digests. Retrieved content SHOULD be verified against " + \
                "this digest when consumed via untrusted sources."
        },
        "size": {
            "type": "integer",
            "description": "This REQUIRED property specifies the size, " + \
                "in bytes, of the raw content. This property exists so " + \
                "that a client will have an expected size for the " + \
                "content before processing. If the length of the " + \
                "retrieved content does not match the specified length, " + \
                "the content SHOULD NOT be trusted."
        },
        "platform": IMAGE_INDEX_ENTRY_PLATFORM_SCHEMA,
        "annotations": {
            "type": "object",
            "description": "This OPTIONAL property contains arbitrary " + \
                "metadata for the image index. This OPTIONAL property " + \
                "MUST use the annotation rules."
        }
    }
}
"""
The JSON schema for validating OCI image index entries
Ref: https://github.com/opencontainers/image-spec/blob/v1.0.1/image-index.md

:meta hide-value:
"""

# See doc comments below
IMAGE_INDEX_OCI_SCHEMA = {
    "type": "object",
    "description": "The image index is a higher-level manifest which " + \
        "points to specific image manifests, ideal for one or more " + \
        "platforms. While the use of an image index is OPTIONAL for " + \
        "image providers, image consumers SHOULD be prepared to process them.",
    "required": [ "schemaVersion", "manifests" ],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": {
            "type": "integer",
            "description": "This REQUIRED property specifies the image " + \
                "manifest schema version. For this version of the " + \
                "specification, this MUST be 2 to ensure backward " + \
                "compatibility with older versions of Docker. The value of " + \
                "this field will not change. This field MAY be removed in " + \
                "a future version of the specification."
        },
        "mediaType": {
            "type": "string",
            "description": "This property is reserved for use, to maintain " + \
                "compatibility. When used, this field contains the media " + \
                "type of this document, which differs from the descriptor " + \
                "use of mediaType."
        },
        "manifests": {
            "type": "array",
            "description": "This REQUIRED property contains a list of " + \
                "manifests for specific platforms. While this property " + \
                "MUST be present, the size of the array MAY be zero.",
            "items": IMAGE_INDEX_ENTRY_OCI_SCHEMA
        },
        "annotations": {
            "type": "object",
            "description": "This OPTIONAL property contains arbitrary " + \
                "metadata for the image index. This OPTIONAL property " + \
                "MUST use the annotation rules."
        }
    }
}
"""
The JSON schema for validating OCI image indexes
Ref: https://github.com/opencontainers/image-spec/blob/v1.0.1/image-index.md

:meta hide-value:
"""

# See doc comments below
MANIFEST_OCI_SCHEMA = {
    "type": "object",
    "description": "The JSON schema for " + \
        "application/vnd.oci.image.manifest.v1+json mediaType manifests",
    "required": [ "schemaVersion", "config", "layers" ],
    "additionalProperties": False,
    "properties": {
        "schemaVersion": {
            "type": "integer",
            "description": "This REQUIRED property specifies the image " + \
                "manifest schema version. For this version of the " + \
                "specification, this MUST be 2 to ensure backward " + \
                "compatibility with older versions of Docker. The " + \
                "value of this field will not change. This field MAY be " + \
                "removed in a future version of the specification."
        },
        "mediaType": {
            "type": "string",
            "description": "This property is reserved for use, to maintain " + \
                "compatibility. When used, this field contains the media " + \
                "type of this document, which differs from the descriptor " + \
                "use of mediaType."
        },
        "config": MANIFEST_DESCRIPTOR_SCHEMA,
        "layers": {
            "type": "array",
            "description": "Each item in the array MUST be a descriptor. " + \
                "The array MUST have the base layer at index 0. Subsequent " + \
                "layers MUST then follow in stack order (i.e. from layers[0] " + \
                "to layers[len(layers)-1]). The final filesystem layout MUST " + \
                "match the result of applying the layers to an empty directory. " + \
                "The ownership, mode, and other attributes of the initial " + \
                "empty directory are unspecified.",
            "items": MANIFEST_DESCRIPTOR_SCHEMA
        },
        "annotations": {
            "type": "object",
            "description": "This OPTIONAL property contains arbitrary " + \
                "metadata for the image manifest. This OPTIONAL property " + \
                "MUST use the annotation rules."
        }
    }
}
"""
The JSON schema for validating OCI manifests
Ref: https://github.com/opencontainers/image-spec/blob/v1.0.1/manifest.md

:meta hide-value:
"""
