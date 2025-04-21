"""
Contains a base ContainerImageManifestListEntry class which is extended by the
docker v2s2 and OCI specifications for the entries in their respective manifest
list implementations
"""

import json
import re
from jsonschema     import  ValidationError
from typing         import  Dict, Any, Type
from image.regex    import  ANCHORED_DIGEST
from image.platform import  ContainerImagePlatform

class ContainerImageManifestListEntry:
    """
    Represents a manifest list entry in a manifest list response from the
    distribution registry API. This is a base class extended by the
    ContainerImageManifestListEntryV2S2 and ContainerImageIndexEntryOCI
    classes since the two specs are very similar, with the v2s2 spec being
    more restrictive than the OCI spec.
    """
    def __init__(self, entry: Dict[str, Any]):
        """
        Constructor for the ContainerImageManifestListEntry class

        Args:
            entry (Dict[str, Any]): The manifest list entry loaded into a dict
        """
        self.entry = entry
    
    def get_digest(self) -> str:
        """
        Returns the entry digest, validates the digest in the process

        Returns:
            str: The entry digest
        """
        digest = self.entry.get("digest")
        valid = bool(re.match(ANCHORED_DIGEST, digest))
        if not valid:
            raise ValidationError(f"Invalid digest: {digest}")
        return digest

    def get_size(self) -> int:
        """
        Returns the entry size in bytes

        Returns:
            int: The entry size in bytes
        """
        return int(self.entry.get("size"))

    def get_media_type(self) -> str:
        """
        Returns the entry mediaType

        Returns:
            str: The entry mediaType
        """
        media_type = self.entry.get("mediaType")
        if media_type == None:
            raise TypeError(f"Invalid mediaType: {media_type}")
        return media_type

    def get_platform(self) -> Type[ContainerImagePlatform]:
        """
        Returns the entry platform metadata as a ContainerImagePlatform

        Returns:
            Type[ContainerImagePlatform]: The platform metadata
        """
        platform = self.entry.get("platform")
        if platform == None:
            raise TypeError(f"Invalid platform: {platform}")
        return ContainerImagePlatform(platform)
    
    def __str__(self) -> str:
        """
        Formats the ContainerImageManifestListEntry as a string

        Returns:
            str: The ContainerImageManifestListEntry formatted as a string
        """
        return json.dumps(self.entry, indent=2, sort_keys=False)
    
    def __json__(self) -> Dict[str, Any]:
        """
        Formats the ContainerImageManifestListEntry as a JSON dictionary

        Returns:
            Dict[str, Any]: The ContainerImageManifestListEntry as a JSON dict
        """
        return self.entry
