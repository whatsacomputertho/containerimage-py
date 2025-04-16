######
# Hack
#
# Make sibling modules visible to this nested executable
import os, sys
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.realpath(__file__)
        )
    )
)
# End Hack
######

from image.auth import AUTH
from image.containerimage import ContainerImage
from image.descriptor import ContainerImageDescriptor
from typing import List, Tuple, Dict, Any

# Source and target image ref env vars
SOURCE_IMAGE_REF = os.environ.get(
    "SOURCE_IMAGE_REF",
    "registry.k8s.io/pause:3.5"
)
TARGET_IMAGE_REF = os.environ.get(
    "TARGET_IMAGE_REF",
    "registry.k8s.io/pause:3.9"
)

# Initialize source and target container image objects
source_image: ContainerImage = ContainerImage(SOURCE_IMAGE_REF)
target_image: ContainerImage = ContainerImage(TARGET_IMAGE_REF)

def get_manifest_diff(
        src: ContainerImage,
        tgt: ContainerImage,
        auth: Dict[str, Any]
    ) -> Tuple[
        List[ContainerImage], # Manifests unique to src
        List[ContainerImage], # Manifests unique to tgt
        List[ContainerImage]  # Common manifests
    ]:
    # Fetch and compare the source and target raw manifests
    src_mf = src.get_manifest(auth=auth)
    tgt_mf = tgt.get_manifest(auth=auth)

    # If one or the other is not a list, then raise exception
    if not ContainerImage.is_manifest_list_static(src_mf):
        raise Exception(f"Not a manifest list: {str(src)}")
    elif not ContainerImage.is_manifest_list_static(tgt_mf):
        raise Exception(f"Not a manifest list: {str(tgt)}")

    # Check if the manifest lists share any manifests in common
    src_unique_mfs = []
    tgt_unique_mfs = []
    common_mfs = []
    src_entries = src_mf.get_entries()
    tgt_entries = tgt_mf.get_entries()
    for src_entry in src_entries:
        src_entry_matches = False
        src_entry_digest = src_entry.get_digest()
        for tgt_entry in tgt_entries:
            if src_entry_digest != tgt_entry.get_digest():
                continue
            src_entry_matches = True
            common_mfs.append(
                ContainerImage(
                    f"{src.get_name()}@{src_entry_digest}"
                )
            )
        if not src_entry_matches:
            src_unique_mfs.append(
                ContainerImage(
                    f"{src.get_name()}@{src_entry_digest}"
                )
            )
    for tgt_entry in tgt_entries:
        tgt_entry_digest = tgt_entry.get_digest()
        if not any(tgt_entry_digest in str(mf) for mf in common_mfs):
            tgt_unique_mfs.append(
                ContainerImage(
                    f"{tgt.get_name()}@{tgt_entry_digest}"
                )
            )
    return src_unique_mfs, tgt_unique_mfs, common_mfs

def get_layer_diff(
        src: ContainerImage,
        tgt: ContainerImage,
        auth: Dict[str, Any]
    ) -> Tuple[
        List[ContainerImageDescriptor],
        List[ContainerImageDescriptor],
        List[ContainerImageDescriptor]
    ]:
    # Fetch and compare the source and target raw manifests
    src_mf = src.get_manifest(auth=auth)
    tgt_mf = tgt.get_manifest(auth=auth)

    # If one or the other is not a manifest, then raise exception
    if ContainerImage.is_manifest_list_static(src_mf):
        raise Exception(
            f"Got manifest list, expected manifest: {str(src)}"
        )
    elif ContainerImage.is_manifest_list_static(tgt_mf):
        raise Exception(
            f"Got manifest list, expected manifest: {str(tgt)}"
        )
    
    # 
    src_unique_layers = []
    tgt_unique_layers = []
    common_layers = []
    src_layers = src_mf.get_layer_descriptors()
    tgt_layers = tgt_mf.get_layer_descriptors()
    for src_layer in src_layers:
        src_layer_matches = False
        src_layer_digest = src_layer.get_digest()
        for tgt_layer in tgt_layers:
            if src_layer_digest != tgt_layer.get_digest():
                continue
            src_layer_matches = True
            common_layers.append(
                src_layer
            )
        if not src_layer_matches:
            src_unique_layers.append(
                src_layer
            )
    for tgt_layer in tgt_layers:
        tgt_layer_digest = tgt_layer.get_digest()
        if not any(tgt_layer_digest == l.get_digest() for l in common_layers):
            tgt_unique_layers.append(
                tgt_layer
            )
    return src_unique_layers, tgt_unique_layers, common_layers

# Fetch and compare the source and target raw manifests
source_manifest = source_image.get_manifest(auth=AUTH)
target_manifest = target_image.get_manifest(auth=AUTH)

# If one is a list and the other is a manifest, check for shared manifests
is_source_list: bool = ContainerImage.is_manifest_list_static(source_manifest)
is_target_list: bool = ContainerImage.is_manifest_list_static(target_manifest)
if ((not is_source_list) and is_target_list):
    print(
        f"{str(target_image)} is a manifest list but " + \
        f"{str(source_image)} is a manifest"
    )

    # TODO: Finish
elif (is_source_list and (not is_target_list)):
    print(
        f"{str(source_image)} is a manifest list but " + \
        f"{str(target_image)} is a manifest"
    )

    # TODO: Finish
elif is_source_list and is_target_list:
    print(
        f"{str(source_image)} and {str(target_image)} are " + \
        "both manifest lists"
    )

    # Diff across the manifests
    (
        source_unique_manifests,
        target_unique_manifests,
        common_manifests
    ) = get_manifest_diff(
        src=source_image,
        tgt=target_image,
        auth=AUTH
    )
    print("Common manifests:")
    for common_mf in common_manifests:
        print(f"- ({(str(common_mf.get_platforms(auth=AUTH)[0]))}) {str(common_mf)}")
    print()
    print(f"Manifests unique to {str(source_image)}:")
    for source_mf in source_unique_manifests:
        print(f"- ({(str(source_mf.get_platforms(auth=AUTH)[0]))}) {str(source_mf)}")
    print()
    print(f"Manifests unique to {str(target_image)}:")
    for target_mf in target_unique_manifests:
        print(f"- ({(str(target_mf.get_platforms(auth=AUTH)[0]))}) {str(target_mf)}")
else:
    print(
        f"{str(source_image)} and {str(target_image)} are " + \
        "both manifests"
    )

    # Diff across the manifest layers
    (
        source_unique_layers,
        target_unique_layers,
        common_layers
    ) = get_layer_diff(
        src=source_image,
        tgt=target_image,
        auth=AUTH
    )
    print("Common layers:")
    for common_layer in common_layers:
        print(f"{str(common_layer)}")
    print()
    print(f"Layers unique to {str(source_image)}:")
    for source_layer in source_unique_layers:
        print(f"{str(source_layer)}")
    print()
    print(f"Layers unique to {str(target_image)}:")
    for target_layer in target_unique_layers:
        print(f"{str(target_layer)}")
