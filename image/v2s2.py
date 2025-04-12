import re
from typing import Dict, Any, Tuple, Type
from jsonschema import validate, ValidationError
from image.descriptor           import  ContainerImageDescriptor
from image.manifest             import  ContainerImageManifest
from image.manifestlistentry    import  ContainerImageManifestListEntry
from image.platform             import  ContainerImagePlatform
from image.regex                import  ANCHORED_DIGEST
from image.v2s2schema           import  MANIFEST_V2_SCHEMA, \
                                        MANIFEST_LIST_V2_ENTRY_SCHEMA

# A list of mediaTypes which are not supported by the v2s2 manifest spec
UNSUPPORTED_MEDIA_TYPES = [
    "application/vnd.oci.image.manifest.v1+json"
]

"""
ContainerImageManifestV2S2 class

Represents an arch manifest returned from the distribution registry API.
Contains validation logic and getters for manifest metadata following the
manifest v2s2 specification.
"""
class ContainerImageManifestV2S2(ContainerImageManifest):
    @staticmethod
    def validate_static(manifest: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates an image manifest

        Args:
        manifest (Dict[str, Any]): The manifest to validate

        Returns:
        Tuple[bool, str]: Whether the manifest is valid, error message
        """
        # Validate the image manifest
        try:
            validate(instance=manifest, schema=MANIFEST_V2_SCHEMA)
        except Exception as e:
            return False, str(e)
        
        # Validate the image manifest config
        config_valid, err = ContainerImageDescriptor.validate_static(
            manifest["config"]
        )
        if not config_valid:
            return config_valid, err

        # Validate the image layers
        for layer in manifest["layers"]:
            layer_valid, err = ContainerImageDescriptor.validate_static(layer)
            if not layer_valid:
                return layer_valid, err
        
        # Validate the mediaType
        if manifest["mediaType"] in UNSUPPORTED_MEDIA_TYPES:
            return False, f"Unsupported mediaType: {manifest['mediaType']}"

        # If all are valid, return True with empty error message
        return True, ""
    
    @staticmethod
    def from_manifest(manifest: Type[ContainerImageManifest]):
        """
        Convert a ContainerImageManifest to a v2s2 manifest instance

        Args:
        manifest_list Type[ContainerImageManifest]: The generic manifest
            instance
        
        Returns:
        ContainerImageManifestV2S2: The v2s2 manifest instance
        """
        return ContainerImageManifestV2S2(manifest.manifest)

    def __init__(self, manifest: Dict[str, Any]):
        """
        Constructor for the ContainerImageManifestV2S2 class

        Args:
        manifest (Dict[str, Any]): The manifest loaded into a dict
        """
        # Validate the image manifest
        valid, err = ContainerImageManifestV2S2.validate_static(manifest)
        if not valid:
            raise ValidationError(err)

        # If valid, instantiate the manifest
        super().__init__(manifest)

    def validate(self) -> Tuple[bool, str]:
        """
        Validates an image manifest instance

        Args:
        None

        Returns:
        Tuple[bool, str]: Whether the manifest is valid, error message
        """
        # Validate the image manifest
        return ContainerImageManifestV2S2.validate_static(self.manifest)

"""
ContainerImageManifestListEntryV2S2 class

Represents a manifest list entry in a manifest list response from the
distribution registry API. Contains validation logic and getters for entry
metadata following the manifest v2s2 specification.
"""
class ContainerImageManifestListEntryV2S2(ContainerImageManifestListEntry):
    @staticmethod
    def validate_static(entry: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates an image manifest list entry

        Args:
        entry (Dict[str, Any]): The manifest list entry to validate

        Returns:
        Tuple[bool, str]: Whether the manifest list entry is valid, error msg
        """
        # Validate the image manifest list entry
        try:
            validate(instance=entry, schema=MANIFEST_LIST_V2_ENTRY_SCHEMA)
        except Exception as e:
            return False, str(e)
        
        # Validate the image manifest list entry digest
        digest_valid = bool(re.match(ANCHORED_DIGEST, entry["digest"]))
        if not digest_valid:
            return False, f"Invalid digest: {entry['digest']}"

        # Validate the manifest list entry platform
        platform_valid, err = ContainerImagePlatform.validate_static(
            entry["platform"]
        )
        if not platform_valid:
            return platform_valid, err
        
        # If the mediaType is unsupported, then error
        if entry["mediaType"] in UNSUPPORTED_MEDIA_TYPES:
            return False, f"Unsupported mediaType: {entry['mediaType']}"

        # Valid if all of the above are valid
        return True, ""

    @staticmethod
    def from_manifest_list_entry(entry: Type[ContainerImageManifestListEntry]):
        """
        Convert a ContainerImageManifestListEntry to a v2s2 manifest list entry
        instance

        Args:
        manifest_list Type[ContainerImageManifestList]: The generic manifest
            list entry instance
        
        Returns:
        ContainerImageManifestListEntryV2S2: The v2s2 manifest list entry
            instance
        """
        return ContainerImageManifestListEntryV2S2(entry.entry)

    def __init__(self, entry: Dict[str, Any]):
        """
        Constructor for the ContainerImageManifestListEntryV2S2 class

        Args:
        entry (Dict[str, Any]): The manifest list entry loaded into a dict
        """
        # Validate the image manifest list entry
        valid, err = ContainerImageManifestListEntryV2S2.validate_static(
            entry
        )
        if not valid:
            raise ValidationError(err)

        # If both valid, instantiate the manifest list entry
        super().__init__(entry)

    def validate(self) -> Tuple[bool, str]:
        """
        Validates an image manifest list entry instance

        Args:
        None

        Returns:
        Tuple[bool, str]: Whether the manifest list entry is valid, error msg
        """
        # Validate the image manifest list
        return ContainerImageManifestListEntryV2S2.validate_static(
            self.entry
        )
