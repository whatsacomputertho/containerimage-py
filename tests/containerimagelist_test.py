from image.byteunit             import  ByteUnit
from image.containerimage       import  ContainerImageList, \
                                        ContainerImage, \
                                        ContainerImageListDiff
from tests.registryclientmock   import  MOCK_IMAGE_NAME, \
                                        MOCK_REGISTRY_CREDS, \
                                        REDHAT_MANIFEST_LIST_EXAMPLE, \
                                        REDHAT_MANIFEST_LIST_EXAMPLE_DUP, \
                                        REDHAT_AMD64_MANIFEST, \
                                        REDHAT_AMD64_MANIFEST_DUP, \
                                        REDHAT_ARM64_MANIFEST, \
                                        REDHAT_PPC64LE_MANIFEST, \
                                        REDHAT_S390X_MANIFEST, \
                                        mock_get_manifest

EXPECTED_DIFF_UPDATED_STR_1 = """Updated
this.is.an/image-1:and-a-different-tag
this.is.an/image-3@sha256:39c59a30e3ecae689c23b27e54a81e03d9a5db22d11890edaf6bb16bac783e8b"""

EXPECTED_DIFF_UPDATED_STR_2 = """Updated
this.is.an/image-3@sha256:39c59a30e3ecae689c23b27e54a81e03d9a5db22d11890edaf6bb16bac783e8b
this.is.an/image-1:and-a-different-tag"""

EXPECTED_DIFF_STR = """Summary
Added:\t1
Removed:\t1
Updated:\t2
Common:\t1

Added
this.is.a/new-image-5:and-tag

Removed
this.is.an/old-image-4:and-tag

{}

Common
this.is.an/image-2:and-tag"""

def test_container_image_list_instantiation():
    # Ensure the ContainerImageList and its properties are of the expected types
    img_list = ContainerImageList()
    assert isinstance(img_list, ContainerImageList)
    assert isinstance(img_list.images, list)

def test_container_image_list_append():
    # Ensure the ContainerImageList is of the expected length after appending one
    img_list = ContainerImageList()
    img_list.append(
        ContainerImage(
            "this.is/my/image:and-my-tag"
        )
    )
    assert len(img_list) == 1

def test_container_image_list_get_size(mocker):
    mocker.patch(
        "image.containerimage.ContainerImageRegistryClient.get_manifest",
        mock_get_manifest
    )

    # Ensure the ContainerImageList size matches the expected size
    img_list = ContainerImageList()
    img_list.append(
        ContainerImage(
            f"{MOCK_IMAGE_NAME}:latest"
        )
    )
    img_list.append(
        ContainerImage(
            f"{MOCK_IMAGE_NAME}:latest-dup"
        )
    )
    img_list.append(
        ContainerImage(
            f"{MOCK_IMAGE_NAME}@" + \
            "sha256:39c59a30e3ecae689c23b27e54a81e03d9a5db22d11890edaf6bb16bac783e8b"
        )
    )
    expected_size = REDHAT_MANIFEST_LIST_EXAMPLE["manifests"][0]["size"] + \
                    REDHAT_MANIFEST_LIST_EXAMPLE["manifests"][1]["size"] + \
                    REDHAT_MANIFEST_LIST_EXAMPLE["manifests"][2]["size"] + \
                    REDHAT_MANIFEST_LIST_EXAMPLE["manifests"][3]["size"] + \
                    REDHAT_MANIFEST_LIST_EXAMPLE_DUP["manifests"][0]["size"] + \
                    REDHAT_MANIFEST_LIST_EXAMPLE_DUP["manifests"][1]["size"] + \
                    REDHAT_MANIFEST_LIST_EXAMPLE_DUP["manifests"][2]["size"] + \
                    REDHAT_MANIFEST_LIST_EXAMPLE_DUP["manifests"][3]["size"] + \
                    REDHAT_AMD64_MANIFEST["config"]["size"] + \
                    REDHAT_AMD64_MANIFEST["layers"][0]["size"] + \
                    REDHAT_AMD64_MANIFEST_DUP["config"]["size"] + \
                    REDHAT_AMD64_MANIFEST_DUP["layers"][0]["size"] + \
                    REDHAT_ARM64_MANIFEST["config"]["size"] + \
                    REDHAT_ARM64_MANIFEST["layers"][0]["size"] + \
                    REDHAT_PPC64LE_MANIFEST["config"]["size"] + \
                    REDHAT_PPC64LE_MANIFEST["layers"][0]["size"] + \
                    REDHAT_S390X_MANIFEST["config"]["size"] + \
                    REDHAT_S390X_MANIFEST["layers"][0]["size"]
    size = img_list.get_size(MOCK_REGISTRY_CREDS)
    formatted = img_list.get_size_formatted(MOCK_REGISTRY_CREDS)
    assert size == expected_size
    assert formatted == ByteUnit.format_size_bytes(expected_size)

def test_container_image_list_delete(mocker):
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.delete", return_value=mock_response)

    # Ensure no exceptions are raised when images are successfully deleted
    img_list = ContainerImageList()
    img_list.append(
        ContainerImage(
            f"{MOCK_IMAGE_NAME}:latest"
        )
    )
    img_list.append(
        ContainerImage(
            f"{MOCK_IMAGE_NAME}:latest-dup"
        )
    )
    img_list.append(
        ContainerImage(
            f"{MOCK_IMAGE_NAME}@" + \
            "sha256:39c59a30e3ecae689c23b27e54a81e03d9a5db22d11890edaf6bb16bac783e8b"
        )
    )
    exc = None
    try:
        img_list.delete(MOCK_REGISTRY_CREDS)
    except Exception as e:
        exc = e
    assert exc == None

def test_container_image_list_diff():
    #Ensure the image list diff matches the expected diff
    img_list_1 = ContainerImageList()
    img_list_1.append(
        ContainerImage(
            "this.is.an/image-1:and-tag"
        )
    )
    img_list_1.append(
        ContainerImage(
            "this.is.an/image-2:and-tag"
        )
    )
    img_list_1.append(
        ContainerImage(
            "this.is.an/image-3@sha256:f5d2c6a1e0c86e4234ea601552dbabb4ced0e013a1efcbfb439f1f6a7a9275b0"
        )
    )
    img_list_1.append(
        ContainerImage(
            "this.is.an/old-image-4:and-tag"
        )
    )
    img_list_2 = ContainerImageList()
    img_list_2.append(
        ContainerImage(
            "this.is.an/image-1:and-a-different-tag"
        )
    )
    img_list_2.append(
        ContainerImage(
            "this.is.an/image-2:and-tag"
        )
    )
    img_list_2.append(
        ContainerImage(
            "this.is.an/image-3@sha256:39c59a30e3ecae689c23b27e54a81e03d9a5db22d11890edaf6bb16bac783e8b"
        )
    )
    img_list_2.append(
        ContainerImage(
            "this.is.a/new-image-5:and-tag"
        )
    )
    diff = img_list_2.diff(img_list_1)
    diff_str = str(diff)
    assert isinstance(diff, ContainerImageListDiff)
    assert len(diff.added) == 1
    assert len(diff.removed) == 1
    assert len(diff.updated) == 2
    assert len(diff.common) == 1
    assert "this.is.a/new-image-5:and-tag" in [ str(x) for x in diff.added ]
    assert "this.is.an/old-image-4:and-tag" in [ str(x) for x in diff.removed ]
    assert "this.is.an/image-3@sha256:39c59a30e3ecae689c23b27e54a81e03d9a5db22d11890edaf6bb16bac783e8b" in \
        [ str(x) for x in diff.updated ]
    assert "this.is.an/image-1:and-a-different-tag" in \
        [ str(x) for x in diff.updated ]
    assert "this.is.an/image-2:and-tag" in [ str(x) for x in diff.common ]
    assert (diff_str == EXPECTED_DIFF_STR.format(EXPECTED_DIFF_UPDATED_STR_1)) \
            or (diff_str == EXPECTED_DIFF_STR.format(EXPECTED_DIFF_UPDATED_STR_2))
