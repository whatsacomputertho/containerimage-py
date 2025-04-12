import copy
import json
from jsonschema                 import ValidationError
from image.manifestlistentry    import ContainerImageManifestListEntry

# An example manifest list entry from the CNCF manifest v2s2 spec
CNCF_MANIFEST_LIST_ENTRY_EXAMPLE = {
    "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
    "size": 7682,
    "platform": {
        "architecture": "amd64",
        "os": "linux",
        "features": [
            "sse4"
        ]
    }
}

# An example image index entry following the OCI spec
DOCKER_BUILDX_ATTESTATION_INDEX_ENTRY = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "sha256:61d78e5bc2772b75b97fc80f1e796594da4c5421957872be9302b39b1cf155b8",
    "size": 566,
    "annotations": {
        "vnd.docker.reference.digest": "sha256:d06586cc1e3a1f21052c2747237c2394917c8ab7d2e10c284ab975196eff0084",
        "vnd.docker.reference.type": "attestation-manifest"
    },
    "platform": {
        "architecture": "unknown",
        "os": "unknown"
    }
}

# An example manifest list entry from RedHat UBI 9
REDHAT_MANIFEST_LIST_ENTRY_EXAMPLE = {
    "digest": "sha256:96f4394d39e6edb69ca51f000f3e7dfb62990f55868134cfd83c82177651e848",
    "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
    "platform": {
        "architecture": "arm64",
        "os": "linux",
        "variant": "v8"
    },
    "size": 429
}

"""
ContainerImageManifestListEntry tests

Unit tests for the ContainerImageManifestListEntry class
"""
def test_container_image_manifest_list_entry_instantiation():
    # Ensure ContainerImageManifestListEntry is returned on instantiation
    # using v2s2 schema
    entry = ContainerImageManifestListEntry(
        CNCF_MANIFEST_LIST_ENTRY_EXAMPLE
    )
    assert isinstance(entry, ContainerImageManifestListEntry)

    # Ensure ContainerImageManifestListEntry is returned on instantiation
    # using OCI schema
    entry = ContainerImageManifestListEntry(
        DOCKER_BUILDX_ATTESTATION_INDEX_ENTRY
    )
    assert isinstance(entry, ContainerImageManifestListEntry)

def test_container_image_manifest_list_entry_get_digest():
    # Ensure digest matches expected digest
    entry = ContainerImageManifestListEntry(
        copy.deepcopy(CNCF_MANIFEST_LIST_ENTRY_EXAMPLE)
    )
    digest = entry.get_digest()
    assert digest == CNCF_MANIFEST_LIST_ENTRY_EXAMPLE["digest"]

    # Ensure if we modify the digest to be invalid type, a TypeError is thrown
    entry.entry["digest"] = 1234
    exc = None
    try:
        digest = entry.get_digest()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

    # Ensure if we remove the digest, a TypeError is thrown
    entry.entry.pop("digest")
    exc = None
    try:
        digest = entry.get_digest()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

    # Ensure if we modify the digest to be valid type with invalid value,
    # a ValidationError is thrown
    entry.entry["digest"] = "notadigest"
    exc = None
    try:
        digest = entry.get_digest()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, ValidationError)

def test_container_image_manifest_list_entry_get_size():
    # Ensure size matches expected size
    entry = ContainerImageManifestListEntry(
        copy.deepcopy(CNCF_MANIFEST_LIST_ENTRY_EXAMPLE)
    )
    size = entry.get_size()
    assert size == CNCF_MANIFEST_LIST_ENTRY_EXAMPLE["size"]

    # Ensure if we modify the size to be invalid type which cannot be converted
    # to an int, a ValueError is thrown
    entry.entry["size"] = "notanint"
    exc = None
    try:
        size = entry.get_size()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, ValueError)

    # Ensure if we remove the size, a TypeError is thrown
    entry.entry.pop("size")
    exc = None
    try:
        size = entry.get_size()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

def test_container_image_manifest_list_entry_get_media_type():
    # Ensure mediaType matches expected mediaType
    entry = ContainerImageManifestListEntry(
        copy.deepcopy(CNCF_MANIFEST_LIST_ENTRY_EXAMPLE)
    )
    media_type = entry.get_media_type()
    assert media_type == CNCF_MANIFEST_LIST_ENTRY_EXAMPLE["mediaType"]

    # Ensure if we remove the mediaType, a TypeError is thrown
    entry.entry.pop("mediaType")
    exc = None
    try:
        media_type = entry.get_media_type()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

def test_container_image_manifest_list_entry_get_platform():
    # Ensure platform matches expected platform
    entry = ContainerImageManifestListEntry(
        copy.deepcopy(CNCF_MANIFEST_LIST_ENTRY_EXAMPLE)
    )
    platform = entry.get_platform()
    assert platform.platform == CNCF_MANIFEST_LIST_ENTRY_EXAMPLE["platform"]

    # Ensure if we remove the platform, a TypeError is thrown
    entry.entry.pop("platform")
    exc = None
    try:
        platform = entry.get_platform()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

def test_container_image_manifest_list_entry_to_string():
    # Ensure the string conversion matches the expected string conversion
    entry_str = json.dumps(
        CNCF_MANIFEST_LIST_ENTRY_EXAMPLE, indent=2, sort_keys=False
    )
    entry = ContainerImageManifestListEntry(
        copy.deepcopy(CNCF_MANIFEST_LIST_ENTRY_EXAMPLE)
    )
    assert str(entry) == entry_str

def test_container_image_manifest_list_entry_to_json():
    # Ensure the JSON conversion matches the expected JSON conversion
    entry = ContainerImageManifestListEntry(
        copy.deepcopy(CNCF_MANIFEST_LIST_ENTRY_EXAMPLE)
    )
    assert json.dumps(entry) == json.dumps(CNCF_MANIFEST_LIST_ENTRY_EXAMPLE)
