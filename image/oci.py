import re
from typing                     import  Dict, Any, Tuple, Type
from jsonschema                 import  validate, ValidationError
from image.descriptor           import  ContainerImageDescriptor
from image.manifest             import  ContainerImageManifest
from image.manifestlistentry    import  ContainerImageManifestListEntry
from image.platform             import  ContainerImagePlatform
from image.regex                import  ANCHORED_DIGEST
from image.ocischema            import  MANIFEST_OCI_SCHEMA, \
                                        IMAGE_INDEX_ENTRY_OCI_SCHEMA

# A list of mediaTypes which are not supported by the OCI manifest spec
UNSUPPORTED_MEDIA_TYPES = [
    "application/vnd.docker.distribution.manifest.v2+json"
]

"""
ContainerImageManifestOCI class

Represents an arch manifest returned from the distribution registry API.
Contains validation logic and getters for manifest metadata following the
manifest OCI specification.
"""
class ContainerImageManifestOCI(ContainerImageManifest):
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
            validate(instance=manifest, schema=MANIFEST_OCI_SCHEMA)
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
        
        # If there is a mediaType, ensure it is not a v2s2 manifest
        if "mediaType" in manifest.keys():
            if manifest["mediaType"] in UNSUPPORTED_MEDIA_TYPES:
                return False, f"Unsupported mediaType: {manifest['mediaType']}"

        # If all are valid, return True with empty error message
        return True, ""

    @staticmethod
    def from_manifest(manifest: Type[ContainerImageManifest]):
        """
        Converts a generic ContainerImageManifest into an OCI manifst instance

        Args:
        manifest (Type[ContainerImageManifest]): The generic manifest

        Returns:
        ContainerImageManifestOCI: The OCI manifest instance
        """
        return ContainerImageManifestOCI(manifest.manifest)

    def __init__(self, manifest: Dict[str, Any]):
        """
        Constructor for the ContainerImageManifestOCI class

        Args:
        manifest (Dict[str, Any]): The manifest loaded into a dict
        """
        # Validate the image manifest
        valid, err = ContainerImageManifestOCI.validate_static(manifest)
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
        return ContainerImageManifestOCI.validate_static(self.manifest)

"""
ContainerImageIndexEntryOCI class

Represents an image index entry in an OCI image index response from the
distribution registry API. Contains validation logic and getters for entry
metadata following the OCI image index specification.
"""
class ContainerImageIndexEntryOCI(ContainerImageManifestListEntry):
    @staticmethod
    def validate_static(entry: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates an image index entry

        Args:
        entry (Dict[str, Any]): The index entry to validate

        Returns:
        Tuple[bool, str]: Whether the index entry is valid, error msg
        """
        # Validate the image index entry
        try:
            validate(instance=entry, schema=IMAGE_INDEX_ENTRY_OCI_SCHEMA)
        except Exception as e:
            return False, str(e)
        
        # Validate the image index entry digest
        digest_valid = bool(re.match(ANCHORED_DIGEST, entry["digest"]))
        if not digest_valid:
            return False, f"Invalid digest: {entry['digest']}"

        # Validate the index entry platform, if given
        if "platform" in entry.keys():
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
        Converts a generic ContainerImageManifestListEntry into an OCI image
        index entry

        Args:
        entry (Type[ContainerImageManifestListEntry]): The generic entry

        Returns:
        Type[ContainerImageIndexEntryOCI]: The OCI image index entry
        """
        return ContainerImageIndexEntryOCI(entry.entry)

    def __init__(self, entry: Dict[str, Any]):
        """
        Constructor for the ContainerImageIndexEntryOCI class

        Args:
        entry (Dict[str, Any]): The index entry loaded into a dict
        """
        # Validate the image index entry
        valid, err = ContainerImageIndexEntryOCI.validate_static(
            entry
        )
        if not valid:
            raise ValidationError(err)

        # If both valid, instantiate the index entry
        super().__init__(entry)

    def validate(self) -> Tuple[bool, str]:
        """
        Validates an image index entry instance

        Args:
        None

        Returns:
        Tuple[bool, str]: Whether the index entry is valid, error msg
        """
        # Validate the image index
        return ContainerImageIndexEntryOCI.validate_static(
            self.entry
        )
