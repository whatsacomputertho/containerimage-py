"""
Contains a base ContainerImageDescriptor class which is implemented by the
docker v2s2 and OCI specifications for layer, config, and blob descriptors
"""

import json
import re
from jsonschema             import  validate, ValidationError
from typing                 import  Dict, Any, Tuple, Union, List
from image.manifestschema   import  MANIFEST_DESCRIPTOR_SCHEMA
from image.regex            import  ANCHORED_DIGEST

class ContainerImageDescriptor:
    """
    Represents a descriptor defined by the OCI image specification. Descriptors
    simply describe some content stored by the registry, which include configs
    and layers.

    A ContainerImageDescriptor follows a JSON schema which is a superset of the
    v2s2 config & layer schemas, which are effectively just descriptors.  Hence,
    we reuse this class across both v2s2 layers / configs, and OCI descriptors.
    """
    @staticmethod
    def validate_static(descriptor: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates OCI descriptor metadata

        Args:
        layer (Dict[str, Any]): The descriptor metadata to validate

        Returns:
        Tuple[bool, str]: Whether the descriptor metadata is valid, error msg
        """
        # Validate against the descriptor JSON schema
        try:
            validate(
                instance=descriptor,
                schema=MANIFEST_DESCRIPTOR_SCHEMA
            )
        except Exception as e:
            return False, str(e)
        
        # Validate the digest
        digest_valid = bool(re.match(ANCHORED_DIGEST, descriptor["digest"]))
        if not digest_valid:
            return False, f"Invalid digest: {descriptor['digest']}"
        
        # If both are valid, the descriptor is valid
        return True, ""

    def __init__(self, descriptor: Dict[str, Any]):
        """
        Constructor for the ContainerImageDescriptor class

        Args:
        descriptor (Dict[str, Any]): The descriptor loaded into a dict
        """
        # Validate the descriptor, if invalid raise ValidationError
        valid, err = ContainerImageDescriptor.validate_static(
            descriptor
        )
        if not valid:
            raise ValidationError(err)
        
        # If valid, store the descriptor
        self.descriptor = descriptor

    def validate(self) -> Tuple[bool, str]:
        """
        Validates a ContainerImageDescriptor instance
        
        Args:
        None

        Returns:
        Tuple[bool, str]: Whether the descriptor metadata is valid, error msg
        """
        return ContainerImageDescriptor.validate_static(self.descriptor)

    def get_digest(self) -> str:
        """
        Returns the descriptor digest, validates the digest in the process

        Args:
        None

        Returns:
        str: The layer digest
        """
        digest = self.descriptor.get("digest")
        valid = bool(re.match(ANCHORED_DIGEST, digest))
        if not valid:
            raise ValidationError(f"Invalid digest: {digest}")
        return digest

    def get_size(self) -> int:
        """
        Returns the layer size in bytes

        Args:
        None

        Returns:
        int: The layer size
        """
        return int(self.descriptor.get("size"))
    
    def get_media_type(self) -> str:
        """
        Returns the layer mediaType

        Args:
        None

        Returns:
        str: The layer mediaType
        """
        media_type = self.descriptor.get("mediaType")
        if media_type == None:
            raise TypeError(f"Invalid mediaType: {media_type}")
        return media_type
    
    def get_urls(self) -> Union[List[str], None]:
        """
        Returns the descriptor URLs if found, else None

        Args:
        None

        Returns:
        Union[List[str], None]: The descriptor URLs or None
        """
        return self.descriptor.get("urls")
    
    def get_annotations(self) -> Union[Dict[str, Any], None]:
        """
        Returns the annotations if found, else None

        Args:
        None

        Returns:
        Union[Dict[str, Any], None]: The descriptor annotations or None
        """
        return self.descriptor.get("annotations")

    def __str__(self) -> str:
        """
        Stringifies a ContainerImageDescriptor instance

        Args:
        None

        Returns:
        str: The stringified descriptor
        """
        return json.dumps(self.descriptor, indent=2, sort_keys=False)

    def __json__(self) -> Dict[str, Any]:
        """
        JSONifies a ContainerImageDescriptor instance

        Args:
        None

        Returns:
        Dict[str, Any]: The JSONified descriptor
        """
        return self.descriptor
