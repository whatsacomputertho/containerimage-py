"""
Contains a base factory pattern implementation in which a generic manifest dict
can be passed in, and the factory can determine which manifest type to return
"""

import json
from image.errors   import  ContainerImageError
from image.oci      import  ContainerImageManifestOCI, \
                            ContainerImageIndexOCI
from image.v2s2     import  ContainerImageManifestV2S2, \
                            ContainerImageManifestListV2S2
from typing         import  Dict, Any, Union

class ContainerImageManifestFactory:
    """
    A factory pattern implementation.  Given a distribution registry manifest
    response, this class can instantiate any of the following types, based on the
    manifest's format
    - ContainerImageManifestListV2S2
    - ContainerImageManifestV2S2
    - ContainerImageIndexOCI
    - ContainerImageManifestOCI
    """
    def create_v2s2_manifest(manifest: Dict[str, Any]) -> ContainerImageManifestV2S2:
        """
        Given a manifest response from the distribution registry API, create
        a ContainerImageManifestV2S2, or raise an exception if it's invalid

        Args:
            manifest (Dict[str, Any]): A v2s2 manifest dict

        Returns:
            ContainerImageManifestV2S2: A v2s2 manifest object
        """
        return ContainerImageManifestV2S2(manifest)

    def create_v2s2_manifest_list(manifest_list: Dict[str, Any]) -> ContainerImageManifestListV2S2:
        """
        Given a manifest list response from the distribution registry API,
        create a ContainerImageManifestListV2S2, or raise an exception if it's
        invalid

        Args:
            manifest_list (Dict[str, Any]): A v2s2 manifest list dict

        Returns:
            ContainerImageManifestListV2S2: A v2s2 manifest list object
        """
        return ContainerImageManifestListV2S2(manifest_list)

    def create_oci_manifest(manifest: Dict[str, Any]) -> ContainerImageManifestOCI:
        """
        Given a manifest response from the distribution registry API,
        create a ContainerImageManifestOCI, or raise an exception if it's
        invalid

        Args:
            manifest (Dict[str, Any]): An OCI manifest dict

        Returns:
            ContainerImageManifestOCI: An OCI manifest object
        """
        return ContainerImageManifestOCI(manifest)

    def create_oci_image_index(index: Dict[str, Any]) -> ContainerImageIndexOCI:
        """
        Given an image index response from the distribution registry API,
        create a ContainerImageIndexOCI, or raise an exception if it's invalid

        Args:
            index (Dict[str, Any]): An OCI image index dict

        Returns:
            ContainerImageIndexOCI: An OCI image index object
        """
        return ContainerImageIndexOCI(index)

    def create(manifest_or_list: Dict[str, Any]) -> Union[
            ContainerImageManifestV2S2,
            ContainerImageManifestListV2S2,
            ContainerImageManifestOCI,
            ContainerImageIndexOCI
        ]:
        """
        Given a manifest response from the distribution registry API, create
        the appropriate type of manifest / manifest list object based on the
        response schema
        - ContainerImageManifestV2S2
        - ContainerImageManifestListV2S2
        - ContainerImageManifestOCI
        - ContainerImageIndexOCI

        Args:
            manifest_or_list (Dict[str, Any]): A manifest or manifest list dict

        Returns:
            Union[ContainerImageManifestV2S2,ContainerImageManifestListV2S2,ContainerImageManifestOCI,ContainerImageIndexOCI]: Manifest or manifest list objects for the OCI & v2s2 specs
        """
        # Validate whether this is a v2s2 manifest
        is_v2s2_manifest, vm_err = ContainerImageManifestV2S2.validate_static(
            manifest_or_list
        )
        if is_v2s2_manifest:
            return ContainerImageManifestV2S2(manifest_or_list)

        # If not, validate whether this is a v2s2 manifest list
        is_v2s2_list, l_err = ContainerImageManifestListV2S2.validate_static(
            manifest_or_list
        )
        if is_v2s2_list:
            return ContainerImageManifestListV2S2(manifest_or_list)
        
        # If not, validate whether this is an OCI manifest
        is_oci_manifest, om_err = ContainerImageManifestOCI.validate_static(
            manifest_or_list
        )
        if is_oci_manifest:
            return ContainerImageManifestOCI(manifest_or_list)

        # If not, validate whether this is an OCI image index
        is_oci_index, i_err = ContainerImageIndexOCI.validate_static(
            manifest_or_list
        )
        if is_oci_index:
            return ContainerImageIndexOCI(manifest_or_list)

        # If neither, raise a ValidationError
        raise ContainerImageError(
            "Invalid schema, not v2s2 or OCI manifest or list: " + \
                f"{json.dumps(manifest_or_list)}"
        )
