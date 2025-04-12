import copy
import json
from jsonschema     import  ValidationError
from image.platform import  ContainerImagePlatform

# Ref: https://github.com/opencontainers/image-spec/blob/v1.0.1/image-index.md
OCI_PLATFORM_EXAMPLE = {
    "architecture": "amd64",
    "os": "linux"
}
OCI_PLATFORM_EXAMPLE_EXTENDED = {
    "architecture": "amd64",
    "os": "windows",
    "os.version": "10.0.14393.1066",
    "os.features": [
        "win32k"
    ]
}

"""
ContainerImagePlatform tests

Unit tests for the ContainerImagePlatform class
"""
def test_container_image_oci_platform_static_validation():
    # Empty dict should be invalid
    empty_dict_valid, err = ContainerImagePlatform.validate_static(
        {}
    )
    assert empty_dict_valid == False
    assert isinstance(err, str)
    assert len(err) > 0

    # Valid OCI example should be valid
    oci_example_mut = copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    oci_example_valid, err = ContainerImagePlatform.validate_static(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    )
    assert oci_example_valid == True
    assert isinstance(err, str)
    assert len(err) == 0

    # No os should be invalid
    oci_example_mut.pop("os")
    no_os_valid, err = ContainerImagePlatform.validate_static(
        oci_example_mut
    )
    assert no_os_valid == False
    assert isinstance(err, str)
    assert len(err) > 0

    # Invalid os type should be invalid
    oci_example_mut["os"] = 1234
    inv_os_valid, err = ContainerImagePlatform.validate_static(
        oci_example_mut
    )
    assert inv_os_valid == False
    assert isinstance(err, str)
    assert len(err) > 0
    oci_example_mut["os"] = copy.copy(OCI_PLATFORM_EXAMPLE["os"])

    # No architecture should be invalid
    oci_example_mut.pop("architecture")
    no_arch_valid, err = ContainerImagePlatform.validate_static(
        oci_example_mut
    )
    assert no_arch_valid == False
    assert isinstance(err, str)
    assert len(err) > 0

    # Invalid architecture type should be invalid
    oci_example_mut["architecture"] = 1234
    inv_arch_valid, err = ContainerImagePlatform.validate_static(
        oci_example_mut
    )
    assert inv_arch_valid == False
    assert isinstance(err, str)
    assert len(err) > 0
    oci_example_mut["architecture"] = copy.copy(
        OCI_PLATFORM_EXAMPLE["architecture"]
    )

    # Invalid os.version type should be invalid
    oci_example_mut["os.version"] = 1234
    inv_ver_valid, err = ContainerImagePlatform.validate_static(
        oci_example_mut
    )
    assert inv_ver_valid == False
    assert isinstance(err, str)
    assert len(err) > 0
    oci_example_mut.pop("os.version")

    # Invalid os.features type should be invalid
    oci_example_mut["os.features"] = ""
    inv_os_feat_valid, err = ContainerImagePlatform.validate_static(
        oci_example_mut
    )
    assert inv_os_feat_valid == False
    assert isinstance(err, str)
    assert len(err) > 0
    oci_example_mut.pop("os.features")

    # Invalid features type should be invalid
    oci_example_mut["features"] = ""
    inv_feat_valid, err = ContainerImagePlatform.validate_static(
        oci_example_mut
    )
    assert inv_feat_valid == False
    assert isinstance(err, str)
    assert len(err) > 0
    oci_example_mut.pop("features")

    # Invalid variant type should be invalid
    oci_example_mut["variant"] = 1234
    inv_var_valid, err = ContainerImagePlatform.validate_static(
        oci_example_mut
    )
    assert inv_var_valid == False
    assert isinstance(err, str)
    assert len(err) > 0

    # Valid OCI extended example should be valid
    oci_ext_plt_valid, err = ContainerImagePlatform.validate_static(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE_EXTENDED)
    )
    assert oci_ext_plt_valid == True
    assert isinstance(err, str)
    assert len(err) == 0

def test_container_image_oci_platform_instantiation():
    # Ensure exception is thrown on instantiation using invalid schema
    exc = None
    try:
        platform = ContainerImagePlatform({})
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, ValidationError)

    # Ensure ContainerImagePlatform is returned on instantiation using valid schema
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    )
    assert isinstance(platform, ContainerImagePlatform)

def test_container_image_oci_platform_get_architecture():
    # Ensure arch matches expected arch
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    )
    arch = platform.get_architecture()
    assert arch == OCI_PLATFORM_EXAMPLE["architecture"]

    # Ensure if we remove the os, a TypeError is thrown
    platform.platform.pop("architecture")
    exc = None
    try:
        arch = platform.get_architecture()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

def test_container_image_oci_platform_get_os():
    # Ensure os matches expected os
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    )
    os = platform.get_os()
    assert os == OCI_PLATFORM_EXAMPLE["os"]

    # Ensure if we remove the os, a TypeError is thrown
    platform.platform.pop("os")
    exc = None
    try:
        os = platform.get_os()
    except Exception as e:
        exc = e
    assert exc != None
    assert isinstance(exc, TypeError)

def test_container_image_oci_platform_get_os_version():
    # Ensure os matches expected version
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE_EXTENDED)
    )
    os_ver = platform.get_os_version()
    assert os_ver == OCI_PLATFORM_EXAMPLE_EXTENDED["os.version"]

    # Ensure if we remove the os version, it is None
    platform.platform.pop("os.version")
    os_ver = platform.get_os_version()
    assert os_ver == None

def test_container_image_oci_platform_get_os_features():
    # Ensure os features expected os features
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE_EXTENDED)
    )
    os_feat = platform.get_os_features()
    assert os_feat == OCI_PLATFORM_EXAMPLE_EXTENDED["os.features"]

    # Ensure if we remoe the os features, it is None
    platform.platform.pop("os.features")
    os_feat = platform.get_os_features()
    assert os_feat == None

def test_container_image_oci_platform_get_variant():
    # Ensure variant, if not set, is None
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE_EXTENDED)
    )
    variant = platform.get_variant()
    assert variant == None

    # Ensure variant matches expected variant when set
    platform.platform["variant"] = "v8"
    variant = platform.get_variant()
    assert variant == "v8"

def test_container_image_oci_platform_get_features():
    # Ensure features, when not set, is None
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    )
    features = platform.get_features()
    assert features == None

    # Ensure features matches expected features when set
    platform.platform["features"] = ["sse4"]
    features = platform.get_features()
    assert features == ["sse4"]

def test_container_image_oci_platform_to_string():
    # Ensure platform to string matches expected value when variant is not set
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    )
    assert str(platform) == f"{OCI_PLATFORM_EXAMPLE['os']}/" + \
        f"{OCI_PLATFORM_EXAMPLE['architecture']}"

    # Ensure platform to string matches expected value when variant is set
    platform.platform["variant"] = "v7"
    assert str(platform) == f"{OCI_PLATFORM_EXAMPLE['os']}/" + \
        f"{OCI_PLATFORM_EXAMPLE['architecture']}/v7"

def test_container_image_oci_platform_to_json():
    # Ensure JSON conversions match expected JSON conversions
    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    )
    assert json.dumps(platform) == json.dumps(OCI_PLATFORM_EXAMPLE)

    platform = ContainerImagePlatform(
        copy.deepcopy(OCI_PLATFORM_EXAMPLE)
    )
    assert json.dumps(platform) == json.dumps(OCI_PLATFORM_EXAMPLE)
