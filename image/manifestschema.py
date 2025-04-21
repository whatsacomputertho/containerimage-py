"""
Contains various JSON schema constants which together form the overarching
container image manifest schema
"""

# See doc comments below
MANIFEST_DESCRIPTOR_SCHEMA = {
    "type": "object",
    "description": "An OCI image consists of several different " + \
        "components, arranged in a Merkle Directed Acyclic Graph (DAG). " + \
        "References between components in the graph are expressed through " + \
        "Content Descriptors. A Content Descriptor (or simply Descriptor) " + \
        "describes the disposition of the targeted content.",
    "required": [ "mediaType", "size", "digest" ],
    "additionalProperties": False,
    "properties": {
        "mediaType": {
            "type": "string",
            "description": "This REQUIRED property contains the media " + \
                "type of the referenced content. Values MUST comply with " + \
                "RFC 6838, including the naming requirements in its " + \
                "section 4.2."
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
        "urls": {
            "type": "array",
            "description": "This OPTIONAL property specifies a list of " + \
                "URIs from which this object MAY be downloaded. Each entry " + \
                "MUST conform to RFC 3986. Entries SHOULD use the http and " + \
                "https schemes, as defined in RFC 7230.",
            "items": {
                "type": "string",
                "description": "A URI from which this object MAY be downloaded"
            }
        },
        "annotations": {
            "type": "object",
            "description": "This OPTIONAL property contains arbitrary " + \
                "metadata for this descriptor. This OPTIONAL property MUST " + \
                "use the annotation rules."
        }
    }
}
"""
The JSON schema for validating manifest descriptors
Ref: https://github.com/opencontainers/image-spec/blob/v1.0.1/descriptor.md

This JSON schema is a superset of the v2s2 config & layer schemas, which
are effectively just descriptors.  Hence, we reuse this schema across both
v2s2 layers / configs, and OCI descriptors
Ref: https://distribution.github.io/distribution/spec/manifest-v2-2/

:meta hide-value:
"""

# See doc comments below
IMAGE_INDEX_ENTRY_PLATFORM_SCHEMA = {
    "type": "object",
    "description": "This OPTIONAL property describes the minimum " + \
        "runtime requirements of the image. This property SHOULD " + \
        "be present if its target is platform-specific.",
    "required": [ "os", "architecture" ],
    "additionalProperties": False,
    "properties": {
        "architecture": {
            "type": "string",
            "description": "This REQUIRED property specifies the CPU " + \
                "architecture. Image indexes SHOULD use, and implementations " + \
                "SHOULD understand, values listed in the Go Language document " + \
                "for GOARCH."
        },
        "os": {
            "type": "string",
            "description": "This REQUIRED property specifies the operating " + \
                "system. Image indexes SHOULD use, and implementations " + \
                "SHOULD understand, values listed in the Go Language " + \
                "document for GOOS."
        },
        "os.version": {
            "type": "string",
            "description": "This OPTIONAL property specifies the version of " + \
                "the operating system targeted by the referenced blob. " + \
                "Implementations MAY refuse to use manifests where os.version " + \
                "is not known to work with the host OS version. Valid values " + \
                "are implementation-defined. e.g. 10.0.14393.1066 on windows."
        },
        "os.features": {
            "type": "array",
            "description": "This OPTIONAL property specifies an array of " + \
                "strings, each specifying a mandatory OS feature. When os is " + \
                "windows, image indexes SHOULD use, and implementations SHOULD " + \
                "understand the following values: win32k: image requires " + \
                "win32k.sys on the host (Note: win32k.sys is missing on Nano " + \
                "Server) When os is not windows, values are implementation-defined " + \
                "and SHOULD be submitted to this specification for standardization.",
            "items": {
                "type": "string",
                "description": "The mandatory OS feature"
            }
        },
        "variant": {
            "type": "string",
            "description": "This OPTIONAL property specifies the variant of " + \
                "the CPU. Image indexes SHOULD use, and implementations " + \
                "SHOULD understand, values listed in the following table. " + \
                "When the variant of the CPU is not listed in the table, " + \
                "values are implementation-defined and SHOULD be submitted " + \
                "to this specification for standardization."
        },
        "features": {
            "type": "array",
            "description": "This property is RESERVED for future versions of " + \
            "the specification."
        }
    }
}
"""
The JSON schema for validating OCI image index entry platforms
Ref: https://github.com/opencontainers/image-spec/blob/v1.0.1/image-index.md

This JSON schema is identical to the v2s2 platform JSON schema for manifest
list entries.  Hence, we reuse this schema across both v2s2 manifest lists,
and OCI image indexes.
Ref: https://distribution.github.io/distribution/spec/manifest-v2-2/

:meta hide-value:
"""