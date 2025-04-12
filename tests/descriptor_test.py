import copy
import json
from jsonschema         import  ValidationError
from image.descriptor   import  ContainerImageDescriptor

# Ref: https://github.com/opencontainers/image-spec/blob/v1.0.1/descriptor.md
OCI_DESCRIPTOR_EXAMPLE = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270"
}

# Ref: https://github.com/opencontainers/image-spec/blob/v1.0.1/descriptor.md
OCI_DESCRIPTOR_EXAMPLE_EXTENDED = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
    "urls": [
        "https://example.com/example-manifest"
    ]
}

"""
ContainerImageDescriptor tests

Unit tests for the ContainerImageDescriptor class
"""
def test_container_image_oci_descriptor_static_validation():
    # Empty dict should be invalid
    empty_dict_valid, err = ContainerImageDescriptor.validate_static({})
    assert empty_dict_valid == False
    assert isinstance(err, str)

    # Just mediaType should be invalid
    mt_dict_valid, err = ContainerImageDescriptor.validate_static(
        {
            "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip"
        }
    )
    assert mt_dict_valid == False
    assert isinstance(err, str)

    # Just digest should be invalid
    d_dict_valid, err = ContainerImageDescriptor.validate_static(
        {
            "digest": "sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f"
        }
    )
    assert d_dict_valid == False
    assert isinstance(err, str)

    # Just size should be invalid
    s_dict_valid, err = ContainerImageDescriptor.validate_static(
        {
            "size": 1234
        }
    )
    assert s_dict_valid == False
    assert isinstance(err, str)

    # CNCF example should be valid
    oci_descriptor_mut = copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE)
    oci_desc_valid, err = ContainerImageDescriptor.validate_static(
        oci_descriptor_mut
    )
    assert oci_desc_valid == True
    assert isinstance(err, str)

    # Size as string should be invalid
    oci_descriptor_mut["size"] = "32654"
    oci_desc_valid, err = ContainerImageDescriptor.validate_static(
        oci_descriptor_mut
    )
    assert oci_desc_valid == False
    assert isinstance(err, str)
    oci_descriptor_mut["size"] = copy.copy(OCI_DESCRIPTOR_EXAMPLE["size"])

    # Digest as int should be invalid
    oci_descriptor_mut["digest"] = 1234
    oci_desc_valid, err = ContainerImageDescriptor.validate_static(
        oci_descriptor_mut
    )
    assert oci_desc_valid == False
    assert isinstance(err, str)
    oci_descriptor_mut["digest"] = copy.copy(OCI_DESCRIPTOR_EXAMPLE["digest"])

    # mediaType as int should be invalid
    oci_descriptor_mut["mediaType"] = 1234
    oci_desc_valid, err = ContainerImageDescriptor.validate_static(
        oci_descriptor_mut
    )
    assert oci_desc_valid == False
    assert isinstance(err, str)
    oci_descriptor_mut["mediaType"] = copy.copy(OCI_DESCRIPTOR_EXAMPLE["mediaType"])

    # Digest of valid type but invalid format should be invalid
    oci_descriptor_mut["digest"] = "notadigest"
    oci_desc_valid, err = ContainerImageDescriptor.validate_static(
        oci_descriptor_mut
    )
    assert oci_desc_valid == False
    assert isinstance(err, str)
    oci_descriptor_mut["digest"] = copy.copy(OCI_DESCRIPTOR_EXAMPLE["digest"])

    # With URLs should be valid
    oci_ext_desc_valid, err = ContainerImageDescriptor.validate_static(
        copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE_EXTENDED)
    )
    assert oci_ext_desc_valid == True
    assert isinstance(err, str)

def test_container_image_oci_descriptor_instantiation():
    # Ensure exception is thrown on instantiation using invalid schema
    exc = None
    try:
        desc = ContainerImageDescriptor({})
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, ValidationError)

    # Ensure ContainerImageDescriptor is returned on instantiation using valid schema
    desc = ContainerImageDescriptor(
        copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE)
    )
    assert isinstance(desc, ContainerImageDescriptor)

def test_container_image_oci_descriptor_instance_validation():
    # Ensure ContainerImageDescriptor instantiates and is valid post-instantiation
    desc = ContainerImageDescriptor(
        copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE)
    )
    valid, err = desc.validate()
    assert valid == True
    assert isinstance(err, str)

    # Ensure if we modify a property of the ContainerImageDescriptor to be invalid,
    # it becomes invalid
    desc.descriptor["digest"] = 1234
    valid, err = desc.validate()
    assert valid == False
    assert isinstance(err, str)

def test_container_image_oci_descriptor_get_digest():
    # Ensure digest matches expected digest
    desc = ContainerImageDescriptor(
        copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE)
    )
    digest = desc.get_digest()
    assert digest == "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270"

    # Ensure if we modify the digest to be invalid type, a TypeError is thrown
    desc.descriptor["digest"] = 1234
    exc = None
    try:
        digest = desc.get_digest()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

    # Ensure if we remove the digest, a TypeError is thrown
    desc.descriptor.pop("digest")
    exc = None
    try:
        digest = desc.get_digest()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

    # Ensure if we modify the digest to be valid type with invalid value,
    # a ValidationError is thrown
    desc.descriptor["digest"] = "notadigest"
    exc = None
    try:
        digest = desc.get_digest()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, ValidationError)

def test_container_image_oci_descriptor_get_size():
    # Ensure size matches expected size
    desc = ContainerImageDescriptor(
        copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE)
    )
    size = desc.get_size()
    assert size == 7682

    # Ensure if we modify the size to be invalid type which cannot be converted
    # to an int, a ValueError is thrown
    desc.descriptor["size"] = "notanint"
    exc = None
    try:
        size = desc.get_size()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, ValueError)

    # Ensure if we remove the size, a TypeError is thrown
    desc.descriptor.pop("size")
    exc = None
    try:
        size = desc.get_size()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

def test_container_image_oci_descriptor_get_media_type():
    # Ensure mediaType matches expected mediaType
    desc = ContainerImageDescriptor(
        copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE)
    )
    media_type = desc.get_media_type()
    assert media_type == "application/vnd.oci.image.manifest.v1+json"

    # Ensure if we remove the mediaType, a TypeError is thrown
    desc.descriptor.pop("mediaType")
    exc = None
    try:
        media_type = desc.get_media_type()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

def test_container_image_oci_descriptor_to_string():
    # Ensure stringified descriptor matches expected stringified contents
    desc_str = json.dumps(OCI_DESCRIPTOR_EXAMPLE, indent=2, sort_keys=False)
    desc = ContainerImageDescriptor(
        copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE)
    )
    assert str(desc) == desc_str

def test_container_image_oci_descriptor_to_json():
    # Ensure JSONified descriptor matches expected JSONified contents
    desc = ContainerImageDescriptor(
        copy.deepcopy(OCI_DESCRIPTOR_EXAMPLE)
    )
    assert json.dumps(desc) == json.dumps(OCI_DESCRIPTOR_EXAMPLE)
