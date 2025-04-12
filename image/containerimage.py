from __future__ import annotations
import hashlib
import json
import re
import requests
import urllib.parse
from requests.adapters          import  HTTPAdapter, Retry
from jsonschema                 import  validate, ValidationError
from typing                     import  List, Dict, Any, \
                                        Tuple, Union, Type, Iterator
from image.byteunit             import  ByteUnit
from image.config               import  ContainerImageConfig
from image.descriptor           import  ContainerImageDescriptor
from image.manifest             import  ContainerImageManifest
from image.manifestlistentry    import  ContainerImageManifestListEntry
from image.platform             import  ContainerImagePlatform
from image.v2s2                 import  ContainerImageManifestV2S2, \
                                        ContainerImageManifestListEntryV2S2
from image.v2s2schema           import  MANIFEST_LIST_V2_SCHEMA
from image.oci                  import  ContainerImageIndexEntryOCI, \
                                        ContainerImageManifestOCI
from image.ocischema            import  IMAGE_INDEX_OCI_SCHEMA
from image.regex                import  REFERENCE_PAT, \
                                        ANCHORED_DIGEST, \
                                        ANCHORED_NAME, \
                                        ANCHORED_TAG, \
                                        ANCHORED_DOMAIN

#########################################
# Classes for managing container images #
#########################################

# Override the default JSON encoder function to enable
# serializing classes as JSON
def wrapped_default(self, obj):
    return getattr(obj.__class__, "__json__", wrapped_default.default)(obj)
wrapped_default.default = json.JSONEncoder().default
json.JSONEncoder.original_default = json.JSONEncoder.default
json.JSONEncoder.default = wrapped_default

# Unsupported mediaTypes for the OCI and v2s2 manifest list classes
UNSUPPORTED_OCI_MEDIA_TYPES = [
    "application/vnd.docker.distribution.manifest.list.v2+json"
]
UNSUPPORTED_V2S2_MEDIA_TYPES = [
    "application/vnd.oci.image.index.v1+json"
]

"""
ContainerImageManifestList class

Represents a manifest list returned from the distribution registry API.
This is a base class extended by the ContainerImageManifestListV2S2 and
ContainerImageManifestListOCI since the two specs are very similar, with the
v2s2 spec being more restrictive than the OCI spec.
"""
class ContainerImageManifestList:
    def __init__(self, manifest_list: Dict[str, Any]):
        """
        Constructor for the ContainerImageManifestList class

        Args:
        manifest_list (Dict[str, Any]): The manifest list loaded into a dict
        """
        self.manifest_list = manifest_list

    def get_entries(self) -> List[Type[ContainerImageManifestListEntry]]:
        """
        Returns the manifest list entries as ContainerImageManifestListEntry
        instances

        Args:
        None

        Returns:
        List[Type[ContainerImageManifestListEntry]]: The entries
        """
        # Loop through each entry in the manifest list and append to the list
        entries = []
        manifest_entries = list(self.manifest_list.get("manifests"))
        for entry in manifest_entries:
            entries.append(
                ContainerImageManifestListEntry(entry)
            )
        
        # Return the list of manifest list entries
        return entries

    def get_entry_sizes(self) -> int:
        """
        Returns the combined size of each of the entries in the list

        Args:
        None

        Returns:
        int: The combined size of each of the entries in the list
        """
        # Loop through each entry in the manifest list and add its size
        # into the total
        size = 0
        entries = self.get_entries()
        for entry in entries:
            size += entry.get_size()
        return size

    def get_manifests(self, name: str, auth: Dict[str, Any]) -> List[
            Type[ContainerImageManifest]
        ]:
        """
        Fetches the arch manifests from the distribution registry API

        Args:
        name (str): A valid image name, the name of the manifest
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        List[Type[ContainerImageManifest]]: The arch manifests
        """
        # Validate the image name
        valid = bool(re.match(ANCHORED_NAME, name))
        if not valid:
            return False, f"Invalid name: {name}"

        # Loop through each manifest in the manifest list
        manifests = []
        manifest_entries = self.get_entries()
        for entry in manifest_entries:
            # Construct and validate the arch image ref
            manifest_digest = entry.get_digest()
            ref = f"{name}@{manifest_digest}"

            # Get the arch image's manifest from the registry, append to list
            manifest_dict = ContainerImageRegistryClient.get_manifest(
                ref, auth
            )
            manifest = ContainerImageManifest(manifest_dict)
            manifests.append(manifest)
        
        # Return the list of manifests
        return manifests

    def get_layer_descriptors(self, name: str, auth: Dict[str, Any]) -> List[
            ContainerImageDescriptor
        ]:
        """
        Retrieves the layer descriptors for each manifest image combined
        into a list

        Args:
        name (str): A valid image name, the name of the manifest
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        int: The list of layer descriptors across each of the manifests
        """
        layers = []
        manifests = self.get_manifests(name, auth)
        for manifest in manifests:
            layers.extend(
                manifest.get_layer_descriptors()
            )
        return layers

    def get_config_descriptors(self, name: str, auth: Dict[str, Any]) -> List[
            ContainerImageDescriptor
        ]:
        """
        Retrieves the config descriptors for each manifest image combined
        into a list

        Args:
        name (str): A valid image name, the name of the manifest
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        List[ContainerImageDescriptor]: The list of config descriptors across
            each of the manifests
        """
        configs = []
        manifests = self.get_manifests(name, auth)
        for manifest in manifests:
            configs.append(manifest.get_config_descriptor())
        return configs
    
    def get_media_type(self) -> str:
        """
        Returns the mediaType of the container image manifest list

        Args:
        None

        Returns:
        str: The container image manifest list mediaType
        """
        return str(self.manifest_list.get("mediaType"))

    def get_size(self, name: str, auth: Dict[str, Any]) -> int:
        """
        Calculates the size of the image using the distribution registry API

        Args:
        name (str): A valid image name, the name of the manifest
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        int: The size of the manifest list in bytes
        """
        # Validate the image name
        valid = bool(re.match(ANCHORED_NAME, name))
        if not valid:
            return False, f"Invalid name: {name}"

        # Loop through each manifest in the manifest list
        configs = {}
        layers = {}
        entry_sizes = 0
        manifest_entries = self.get_entries()
        for entry in manifest_entries:
            # Get the manifest list entry size
            entry_sizes += entry.get_size()

            # Construct and validate the arch image ref
            manifest_digest = entry.get_digest()
            ref = f"{name}@{manifest_digest}"

            # Get the arch image's manifest from the registry
            manifest_dict = ContainerImageRegistryClient.get_manifest(
                ref, auth
            )
            manifest = ContainerImageManifest(manifest_dict)

            # Get the arch image's layer and config descriptors
            manifest_layers = manifest.get_layer_descriptors()
            manifest_config = manifest.get_config_descriptor()

            # Append config to configs dict
            config_digest = manifest_config.get_digest()
            config_size = manifest_config.get_size()
            configs[config_digest] = config_size

            # Append layers to layers dict
            for layer in manifest_layers:
                layer_digest = layer.get_digest()
                layer_size = layer.get_size()
                layers[layer_digest] = layer_size

        # Sum the deduplicated size
        manifest_list_size = entry_sizes
        for digest in configs.keys():
            manifest_list_size += configs[digest]
        for digest in layers.keys():
            manifest_list_size += layers[digest]
        
        # Return the list of manifests
        return manifest_list_size

    def __str__(self) -> str:
        """
        Formats the ContainerImageManifestListV2S2 as a string

        Args:
        None

        Returns:
        str: The ContainerImageManifestListV2S2 formatted as a string
        """
        return json.dumps(self.manifest_list, indent=2, sort_keys=False)

    def __json__(self) -> Dict[str, Any]:
        """
        Formats the ContainerImageManifestListV2S2 as a JSON dict

        Args:
        None

        Returns:
        Dict[str, Any]: The ContainerImageManifestListV2S2 formatted as a JSON dict
        """
        return self.manifest_list

"""
ContainerImageManifestListV2S2 class

Represents a manifest list returned from the distribution registry API.
Contains validation logic and getters for manifest list metadata following the
manifest v2s2 specification.
"""
class ContainerImageManifestListV2S2(ContainerImageManifestList):
    @staticmethod
    def validate_static(manifest_list: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates an image manifest list

        Args:
        manifest_list (Dict[str, Any]): The manifest list to validate

        Returns:
        Tuple[bool, str]: Whether the manifest list is valid, error message
        """
        # Validate the image manifest list
        try:
            validate(instance=manifest_list, schema=MANIFEST_LIST_V2_SCHEMA)
        except Exception as e:
            return False, str(e)
        
        # Validate the manifest list entries
        for entry in manifest_list["manifests"]:
            entry_valid, err = ContainerImageManifestListEntryV2S2.validate_static(
                entry
            )
            if not entry_valid:
                return entry_valid, err
        
        # Validate the mediaType, if unsupported then error
        if manifest_list["mediaType"] in UNSUPPORTED_V2S2_MEDIA_TYPES:
            return False, f"Unsupported mediaType: {manifest_list['mediaType']}"

        # Success if both valid
        return True, ""
    
    @staticmethod
    def from_manifest_list(
            manifest_list: Type[ContainerImageManifestList]
        ) -> ContainerImageManifestListV2S2:
        """
        Convert a ContainerImageManifestList to a v2s2 manifest list instance

        Args:
        manifest_list Type[ContainerImageManifestList]: The generic manifest
            list instance
        
        Returns:
        ContainerImageManifestListV2S2: The v2s2 manifest list instance
        """
        return ContainerImageManifestListV2S2(manifest_list.manifest_list)

    def __init__(self, manifest_list: Dict[str, Any]):
        """
        Constructor for the ContainerImageManifestListV2S2 class

        Args:
        manifest_list (Dict[str, Any]): The manifest list loaded into a dict
        """
        # Validate the image manifest list
        valid, err = ContainerImageManifestListV2S2.validate_static(manifest_list)
        if not valid:
            raise ValidationError(err)

        # If both valid, instantiate the manifest list
        super().__init__(manifest_list)

    def validate(self) -> Tuple[bool, str]:
        """
        Validates an image manifest list instance

        Args:
        None

        Returns:
        Tuple[bool, str]: Whether the manifest list is valid, error message
        """
        # Validate the image manifest list
        return ContainerImageManifestListV2S2.validate_static(
            self.manifest_list
        )

    def get_v2s2_entries(self) -> List[
            Type[ContainerImageManifestListEntryV2S2]
        ]:
        """
        Returns the manifest list entries as ContainerImageManifestListEntryV2S2
        instances

        Args:
        None

        Returns:
        List[Type[ContainerImageManifestListEntryV2S2]]: The entries
        """
        entries = self.get_entries()
        for i in range(len(entries)):
            # Convert each entry to a v2s2 entry
            entries[i] = ContainerImageManifestListEntryV2S2.from_manifest_list_entry(
                entries[i]
            )
        return entries

    def get_v2s2_manifests(
            self, name: str, auth: Dict[str, Any]
        ) -> List[Type[ContainerImageManifestV2S2]]:
        """
        Fetches the arch manifests from the distribution registry API and
        returns as a list of ContainerImageManifestV2S2s

        Args:
        name (str): A valid image name, the name of the manifest
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        List[Type[ContainerImageManifestV2S2]]: The arch manifests
        """
        manifests = self.get_manifests(name, auth)
        for i in range(len(manifests)):
            # Convert each manifest to a v2s2 manifest
            manifests[i] = ContainerImageManifestV2S2.from_manifest(
                manifests[i]
            )
        return manifests

"""
ContainerImageIndexOCI class

Represents an OCI image index returned from the distribution registry API.
Contains validation logic and getters for image index metadata following the
OCI image index specification.
"""
class ContainerImageIndexOCI(ContainerImageManifestList):
    @staticmethod
    def validate_static(manifest_list: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates an OCI image index

        Args:
        manifest_list (Dict[str, Any]): The image index to validate

        Returns:
        Tuple[bool, str]: Whether the image index valid, error message
        """
        # Validate the image index
        try:
            validate(instance=manifest_list, schema=IMAGE_INDEX_OCI_SCHEMA)
        except Exception as e:
            return False, str(e)
        
        # Validate the image index entries
        for entry in manifest_list["manifests"]:
            entry_valid, err = ContainerImageIndexEntryOCI.validate_static(
                entry
            )
            if not entry_valid:
                return entry_valid, err
        
        # Validate the mediaType, if unsupported then error
        if "mediaType" in manifest_list.keys():
            if manifest_list["mediaType"] in UNSUPPORTED_OCI_MEDIA_TYPES:
                return False, f"Unsupported mediaType: {manifest_list['mediaType']}"

        # Success if both valid
        return True, ""
    
    @staticmethod
    def from_manifest_list(
            manifest_list: Type[ContainerImageManifestList]
        ) -> ContainerImageIndexOCI:
        """
        Convert a ContainerImageManifestList to an OCI image index instance

        Args:
        manifest_list Type[ContainerImageManifestList]: The generic manifest
            list instance
        
        Returns:
        ContainerImageIndexOCI: The OCI image index instance
        """
        return ContainerImageIndexOCI(manifest_list.manifest_list)

    def __init__(self, index: Dict[str, Any]):
        """
        Constructor for the ContainerImageIndexOCI class

        Args:
        manifest_list (Dict[str, Any]): The image index loaded into a dict
        """
        # Validate the image index
        valid, err = ContainerImageIndexOCI.validate_static(index)
        if not valid:
            raise ValidationError(err)

        # If both valid, instantiate the image index
        super().__init__(index)

    def validate(self) -> Tuple[bool, str]:
        """
        Validates an OCI image index instance

        Args:
        None

        Returns:
        Tuple[bool, str]: Whether the image index is valid, error message
        """
        # Validate the image manifest list
        return ContainerImageIndexOCI.validate_static(
            self.manifest_list
        )

    def get_oci_entries(self) -> List[
            Type[ContainerImageIndexEntryOCI]
        ]:
        """
        Returns the manifest list entries as ContainerImageIndexEntryOCI
        instances

        Args:
        None

        Returns:
        List[Type[ContainerImageIndexEntryOCI]]: The entries
        """
        entries = self.get_entries()
        for i in range(len(entries)):
            # Convert each entry to an OCI entry
            entries[i] = ContainerImageIndexEntryOCI.from_manifest_list_entry(
                entries[i]
            )
        return entries

    def get_oci_manifests(
            self, name: str, auth: Dict[str, Any]
        ) -> List[Type[ContainerImageManifestOCI]]:
        """
        Fetches the arch manifests from the distribution registry API and
        returns as a list of ContainerImageManifestOCI instances

        Args:
        name (str): A valid image name, the name of the manifest
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        List[Type[ContainerImageManifestOCI]]: The arch manifests
        """
        manifests = self.get_manifests(name, auth)
        for i in range(len(manifests)):
            # Convert each manifest to an OCI manifest
            manifests[i] = ContainerImageManifestOCI.from_manifest(
                manifests[i]
            )
        return manifests

"""
ContainerImageManifestFactory class

A factory pattern implementation.  Given a distribution registry manifest
response, this class can instantiate any of the following types, based on the
manifest's format
- ContainerImageManifestListV2S2
- ContainerImageManifestV2S2
- ContainerImageIndexOCI
- ContainerImageManifestOCI
"""
class ContainerImageManifestFactory:
    def create_v2s2_manifest(manifest: Dict[str, Any]) -> Type[
            ContainerImageManifestV2S2
        ]:
        """
        Given a manifest response from the distribution registry API, create
        a ContainerImageManifestV2S2, or raise an exception if it's invalid

        Args:
        manifest (Dict[str, Any]): A v2s2 manifest dict

        Returns:
        Type[ContainerImageManifestV2S2]: A v2s2 manifest object
        """
        return ContainerImageManifestV2S2(manifest)

    def create_v2s2_manifest_list(manifest_list: Dict[str, Any]) -> Type[
            ContainerImageManifestListV2S2
        ]:
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

    def create_oci_manifest(manifest: Dict[str, Any]) -> Type[
            ContainerImageManifestOCI
        ]:
        """
        Given a manifest response from the distribution registry API,
        create a ContainerImageManifestOCI, or raise an exception if it's
        invalid

        Args:
        manifest (Dict[str, Any]): An OCI manifest dict

        Returns:
        Type[ContainerImageManifestOCI]: An OCI manifest object
        """
        return ContainerImageManifestOCI(manifest)

    def create_oci_image_index(index: Dict[str, Any]) -> Type[
            ContainerImageIndexOCI
        ]:
        """
        Given an image index response from the distribution registry API,
        create a ContainerImageIndexOCI, or raise an exception if it's invalid

        Args:
        index (Dict[str, Any]): An OCI image index dict

        Returns:
        Type[ContainerImageIndexOCI]: An OCI image index object
        """
        return ContainerImageIndexOCI(index)

    def create(manifest_or_list: Dict[str, Any]) -> Union[
            Type[ContainerImageManifestV2S2],
            Type[ContainerImageManifestListV2S2],
            Type[ContainerImageManifestOCI],
            Type[ContainerImageIndexOCI]
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
        Union[
            Type[ContainerImageManifestV2S2],
            Type[ContainerImageManifestListV2S2],
            Type[ContainerImageManifestOCI],
            Type[ContainerImageIndexOCI]
        ]: Manifest or manifest list objects for the OCI & v2s2 specs
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
        raise ValidationError(
            "Invalid schema, not v2s2 or OCI manifest or list: " + \
                f"{json.dumps(manifest_or_list)}"
        )

"""
ContainerImageRegistryClient class

A CNCF distribution registry API client
"""
class ContainerImageRegistryClient:
    @staticmethod
    def get_registry_base_url(ref_or_img: Union[str, ContainerImage]) -> str:
        """
        Constructs the distribution registry API base URL from the image
        reference.
        
        For example:
        - quay.io/ibm/software/cloudpak/hello-world:latest
        
        Would become:
        - https://quay.io/v2/ibm/software/cloudpak/hello-world

        Args:
        ref_or_img (Union[str, ContainerImage]): A valid image ref, or ContainerImage

        Returns:
        str: The distribution registry API base URL
        """
        # If the ref or image is a string (ref), load it into a ContainerImage
        image = ref_or_img
        if isinstance(image, str):
            image = ContainerImage(ref_or_img)
        
        # Split reference into slash-separated components
        # Get domain, it is the first element of the list
        # Join all but the first and last components into the path
        domain_components = image.ref.split('/')
        domain = domain_components[0]
        path = "/".join(domain_components[1:-1])

        # Get name, it is the last element of the list
        # But if tag and/or digest, those must be parsed out of the name
        name = domain_components[-1].split("@")[0].split(":")[0]

        # If the domain is docker.io, then convert it to registry-1.docker.io
        if domain == 'docker.io':
            domain = 'registry-1.docker.io'

        # Format and return the registry URL base image
        return f"https://{domain}/v2/{path}/{name}"
    
    @staticmethod
    def get_registry_auth(ref_or_img: Union[str, ContainerImage], auth: Dict[str, Any]) -> Tuple[
            str,
            bool
        ]:
        """
        Gets the registry auth from a docker config JSON matching the registry
        for this image

        Args:
        ref_or_img (Union[str, ContainerImage]): A valid image ref, or ContainerImage
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        Tuple[str, bool]: The auth, and whether an auth was found
        """
        # If the ref or image is a string (ref), load it into a ContainerImage
        image = ref_or_img
        if isinstance(image, str):
            image = ContainerImage(ref_or_img)

        # Track the last matching registry
        last_match = ""
        match_found = False

        # Loop through the registries in the auth
        auths = auth.get("auths", {})
        for registry in auths.keys():
            # Check if the registry is a leading substring of the image ref
            reg_str = str(registry)
            if not image.ref.startswith(reg_str):
                continue

            # If the registry path is longer than the last match, save it
            if len(reg_str) > len(last_match):
                last_match = reg_str
                match_found = True

        # If no match was found, then return
        if not match_found:
            return "", False

        # Get the auth for the matching registry
        # Error if the auth key is not given, otherwise return it
        reg_auth_dict = auths.get(last_match, {})
        if "auth" not in reg_auth_dict:
            raise Exception(f"No auth key for registry {last_match}")
        return reg_auth_dict["auth"], True
    
    @staticmethod
    def get_auth_token(
            res: Type[requests.Response],
            reg_auth: str
        ) -> Tuple[str, str]:
        """
        The response from the distribution registry API, which MUST be a 401
        response, and MUST include the www-authenticate header

        Args:
        res (Type[requests.Response]): The response from the registry API
        reg_auth (str): The auth retrieved for the registry

        Returns:
        Tuple[str, str]:
            - The auth scheme for the token
            - The token retrieved from the auth service
        """
        # Get the www-authenticate header, split into components
        www_auth_header = res.headers['www-authenticate']
        auth_components = www_auth_header.split(" ")

        # Parse the auth scheme from the header
        auth_scheme = auth_components[0]

        # Parse each key-value pair into a dict
        query_params = {}
        query_param_components = auth_components[1].split(",")
        for param in query_param_components:
            param_components = param.split("=")
            query_params[param_components[0]] = param_components[1].replace("\"", "")
        
        # Pop the realm value out of the dict and encode as a query string
        # Format into the auth service URL to request
        realm = query_params.pop("realm")
        query_string = urllib.parse.urlencode(query_params)
        auth_url = f"{realm}?{query_string}"

        # Send the request to the auth service, parse the token from the
        # response
        headers = {
            'Authorization': f"Basic {reg_auth}"
        }
        token_res = requests.get(auth_url, headers=headers)
        token_res.raise_for_status()
        token_json = token_res.json()
        token = token_json['token']
        return auth_scheme, token
    
    @staticmethod
    def query_blob(
            ref_or_img: Union[str, ContainerImage],
            desc: Type[ContainerImageDescriptor],
            auth: Dict[str, Any]
        ) -> Type[requests.Response]:
        """
        Fetches a blob from the registry API and returns as a requests response
        object

        Args:
        ref_or_img (Union[str, ContainerImage]): The image to construct the url
        desc (Type[ContainerImageDescriptor]): A blob descriptor
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        Type[requests.Response]: The registry API blob response
        """
        # If the ref or image is a string (ref), load it into a ContainerImage
        image = ref_or_img
        if isinstance(image, str):
            image = ContainerImage(ref_or_img)

        # Construct the API URL for querying the blob
        api_base_url = ContainerImageRegistryClient.get_registry_base_url(
            image
        )
        digest = desc.get_digest()
        api_url = f'{api_base_url}/blobs/{digest}'

        # Construct the headers for querying the image manifest
        headers = {}

        # Get the matching auth for the image from the docker config JSON
        reg_auth, found = ContainerImageRegistryClient.get_registry_auth(
            image,
            auth
        )
        if found:
            headers['Authorization'] = f'Basic {reg_auth}'
        
        # Send the request to the distribution registry API
        # If it fails with a 401 response code and auth given, do OAuth dance
        res = requests.get(api_url, headers=headers)
        if res.status_code == 401 and found and \
            'www-authenticate' in res.headers.keys():
            # Do Oauth dance if basic auth fails
            # Ref: https://distribution.github.io/distribution/spec/auth/token/
            scheme, token = ContainerImageRegistryClient.get_auth_token(
                res, reg_auth
            )
            headers['Authorization'] = f'{scheme} {token}'
            res = requests.get(api_url, headers=headers)

        # Raise exceptions on error status codes
        res.raise_for_status()
        return res
    
    @staticmethod
    def get_config(
            ref_or_img: Union[str, ContainerImage],
            config_desc: Type[ContainerImageDescriptor],
            auth: Dict[str, Any]
        ) -> Dict[str, Any]:
        """
        Fetches a config blob from the registry API and returns as a dict

        Args:
        ref_or_img (Union[str, ContainerImage]): The image to construct the url
        desc (Type[ContainerImageDescriptor]): A blob descriptor
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        Dict[str, Any]: The config as a dict
        """
        # Query the blob, get the manifest response
        res = ContainerImageRegistryClient.query_blob(
            ref_or_img, config_desc, auth
        )

        # Load the manifest into a dict and return
        config = res.json()
        return config
    
    @staticmethod
    def query_manifest(ref_or_img: Union[str, ContainerImage], auth: Dict[str, Any]) -> Type[
            requests.Response
        ]:
        """
        Fetches the manifest from the registry API and returns as a requests
        response object

        Args:
        ref_or_img (Union[str, ContainerImage]): A valid image ref, or ContainerImage
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        Type[requests.Response]: The registry API response
        """
        # If the ref or image is a string (ref), load it into a ContainerImage
        image = ref_or_img
        if isinstance(image, str):
            image = ContainerImage(ref_or_img)

        # Construct the API URL for querying the image manifest
        api_base_url = ContainerImageRegistryClient.get_registry_base_url(
            image
        )
        image_identifier = image.get_identifier()
        api_url = f'{api_base_url}/manifests/{image_identifier}'

        # Construct the headers for querying the image manifest
        headers = {}

        # Get the matching auth for the image from the docker config JSON
        reg_auth, found = ContainerImageRegistryClient.get_registry_auth(
            image,
            auth
        )
        if found:
            headers['Authorization'] = f'Basic {reg_auth}'
        
        # Send the request to the distribution registry API
        # If it fails with a 401 response code and auth given, do OAuth dance
        res = requests.get(api_url, headers=headers)
        if res.status_code == 401 and found and \
            'www-authenticate' in res.headers.keys():
            # Do Oauth dance if basic auth fails
            # Ref: https://distribution.github.io/distribution/spec/auth/token/
            scheme, token = ContainerImageRegistryClient.get_auth_token(
                res, reg_auth
            )
            headers['Authorization'] = f'{scheme} {token}'
            res = requests.get(api_url, headers=headers)

        # Raise exceptions on error status codes
        res.raise_for_status()
        return res

    @staticmethod
    def get_manifest(ref_or_img: Union[str, ContainerImage], auth: Dict[str, Any]) -> Dict[
            str, Any
        ]:
        """
        Fetches the manifest from the registry API and returns as a dict

        Args:
        ref_or_img (Union[str, ContainerImage]): A valid image ref, or ContainerImage
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        Dict[str, Any]: The manifest loaded into a dict
        """
        # Query the manifest, get the manifest response
        res = ContainerImageRegistryClient.query_manifest(
            ref_or_img, auth
        )

        # Load the manifest into a dict and return
        manifest = res.json()
        return manifest
    
    @staticmethod
    def get_digest(ref_or_img: Union[str, ContainerImage], auth: Dict[str, Any]) -> str:
        """
        Fetches the digest from the registry API

        Args:
        ref_or_img (Union[str, ContainerImage]): A valid image ref, or ContainerImage
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        str: The image digest
        """
        # Query the manifest, get the manifest response
        res = ContainerImageRegistryClient.query_manifest(
            ref_or_img, auth
        )

        # Load the digest header if given, otherwise compute the digest
        digest = ""
        digest_header = 'Docker-Content-Digest'
        if digest_header in res.headers.keys():
            digest = str(res.headers['Docker-Content-Digest'])
        else:
            manifest = res.json()
            # Indent 3 is required to compute the correct digest
            # Important that this is not changed as the digest would change
            encoded_manifest = json.dumps(manifest, indent=3).encode('utf-8')
            digest = hashlib.sha256(encoded_manifest).hexdigest()

        # Validate the digest, return if valid
        if not bool(re.match(ANCHORED_DIGEST, digest)):
            raise ValidationError(
                f"Invalid digest: {digest}"
            )
        return digest

    @staticmethod
    def delete(ref_or_img: Union[str, ContainerImage], auth: Dict[str, Any]):
        """
        Deletes the reference from the registry using the registry API

        Args:
        ref_or_img (Union[str, ContainerImage]): A valid image ref, or ContainerImage
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        None
        """
        # If the ref or image is a string (ref), load it into a ContainerImage
        image = ref_or_img
        if isinstance(image, str):
            image = ContainerImage(ref_or_img)

        # Construct the API URL for querying the image manifest
        api_base_url = ContainerImageRegistryClient.get_registry_base_url(
            image
        )
        image_identifier = image.get_identifier()
        api_url = f'{api_base_url}/manifests/{image_identifier}'

        # Construct the headers for querying the image manifest
        headers = {}

        # Get the matching auth for the image from the docker config JSON
        reg_auth, found = ContainerImageRegistryClient.get_registry_auth(
            image,
            auth
        )
        if found:
            headers['Authorization'] = f'Basic {reg_auth}'
        
        # Send the request to the distribution registry API
        # If it fails with a 401 response code and auth given, do OAuth dance
        res = requests.delete(api_url, headers=headers)
        if res.status_code == 401 and found and \
            'www-authenticate' in res.headers.keys():
            # Do Oauth dance if basic auth fails
            # Ref: https://distribution.github.io/distribution/spec/auth/token/
            scheme, token = ContainerImageRegistryClient.get_auth_token(
                res, reg_auth
            )
            headers['Authorization'] = f'{scheme} {token}'
            res = requests.delete(api_url, headers=headers)

        # Raise exceptions on error status codes
        res.raise_for_status()

"""
ContainerImage class

Represents a container image. Contains validation logic for container image
references, and logic for managing container images in remote registries.
"""
class ContainerImage:
    @staticmethod
    def validate_static(ref: str) -> Tuple[bool, str]:
        """
        Validates an image reference

        Args:
        ref (str): The image reference

        Returns:
        Tuple[bool, str]: Whether the reference is valid, error message
        """
        valid = bool(re.match(REFERENCE_PAT, ref))
        if not valid:
            return False, f"Invalid reference: {ref}"
        return True, ""
    
    @staticmethod
    def is_manifest_list_static(
            manifest: Union[
                Type[ContainerImageManifestV2S2],
                Type[ContainerImageManifestListV2S2],
                Type[ContainerImageManifestOCI],
                Type[ContainerImageIndexOCI]
            ]
        ) -> bool:
        """
        Determine if an arbitrary manifest object is a manifest list

        Args:
        manifest (
            Union[
                Type[ContainerImageManifestV2S2],
                Type[ContainerImageManifestListV2S2],
                Type[ContainerImageManifestOCI],
                Type[ContainerImageIndexOCI]
            ]
        ): The manifest object, generally from get_manifest method

        Returns:
        bool: Whether the manifest object is a list or single-arch
        """
        return isinstance(manifest, ContainerImageManifestList)
    
    @staticmethod
    def is_oci_static(
            manifest: Union[
                Type[ContainerImageManifestV2S2],
                Type[ContainerImageManifestListV2S2],
                Type[ContainerImageManifestOCI],
                Type[ContainerImageIndexOCI]
            ]
        ) -> bool:
        """
        Determine if an arbitrary manifest object is an OCI manifest or image
        index.

        Args:
        manifest (
            Union[
                Type[ContainerImageManifestV2S2],
                Type[ContainerImageManifestListV2S2],
                Type[ContainerImageManifestOCI],
                Type[ContainerImageIndexOCI]
            ]
        ): The manifest object, generally from get_manifest method

        Returns:
        bool: Whether the manifest object is in the OCI format
        """
        return isinstance(manifest, ContainerImageManifestOCI) or \
                isinstance(manifest, ContainerImageIndexOCI)
    
    def __init__(self, ref: str):
        """
        Constructor for the ContainerImage class

        Args:
        ref (str): The image reference
        """
        # Validate the image reference
        valid, err = ContainerImage.validate_static(ref)
        if not valid:
            raise ValidationError(err)

        # Set the image reference property
        self.ref = ref
    
    def validate(self) -> bool:
        """
        Validates an image reference

        Args:
        None

        Returns:
        bool: Whether the ContainerImage's reference is valid
        """
        return ContainerImage.validate_static(self.ref)
    
    def is_digest_ref(self) -> bool:
        """
        Determines if the image reference is a digest reference

        Args:
        None

        Returns:
        bool: Whether the image is a digest reference
        """
        # Ensure the ref is valid, if not raise an exception
        valid, err = self.validate()
        if not valid:
            raise ValidationError(err)
        
        # Check for an "@" character, if not found then it is not a digest ref
        if "@" not in self.ref:
            return False
        
        # Parse out the digest and validate it, if valid then its a digest ref
        digest = self.ref.split("@")[-1]
        return bool(re.match(ANCHORED_DIGEST, digest))
    
    def get_digest(self, auth: Dict[str, Any]) -> str:
        """
        Parses the digest from the reference if digest reference, or fetches
        it from the registry if tag reference

        Args:
        auth (Dict[str, Any]): A valid docker config JSON

        Returns:
        str: The image digest
        """
        if self.is_digest_ref():
            return self.get_identifier()
        return ContainerImageRegistryClient.get_digest(self, auth)
    
    def get_platforms(self, auth: Dict[str, Any]) -> List[
            Type[ContainerImagePlatform]
        ]:
        """
        Returns the supported platform(s) for the image as a list of
        ContainerImagePlatforms

        Args:
        auth (Dict[str, Any]): A valid docker config JSON

        Returns:
        List[Type[ContainerImagePlatform]]: The supported platforms
        """
        # If manifest, get the config and get its platform
        manifest = self.get_manifest(auth)
        platforms = []
        if not ContainerImage.is_manifest_list_static(manifest):
            config_desc = manifest.get_config_descriptor()
            config_dict = ContainerImageRegistryClient.get_config(
                self,
                config_desc,
                auth
            )
            config = ContainerImageConfig(config_dict)
            platforms = [ config.get_platform() ]
        else:
            for entry in manifest.get_entries():
                platforms.append(entry.get_platform())
        return platforms
    
    def is_tag_ref(self) -> bool:
        """
        Determine if the image reference is a tag reference

        Args:
        None

        Returns:
        bool: Whether the image is a tag referenece
        """
        # Ensure the ref is valid, if not raise an exception
        valid, err = self.validate()
        if not valid:
            raise ValidationError(err)

        # If the image is a digest ref, then it is not a tag ref
        if self.is_digest_ref():
            return False

        # Parse out the tag and validate it, if valdi then it is a tag ref
        tag = "latest"
        if ":" in self.ref:
            tag = self.ref.split(":")[-1]
        return bool(re.match(ANCHORED_TAG, tag))
    
    def get_identifier(self) -> str:
        """
        Gets the image identifier, which can be either a tag or a digest,
        based on whether the image is a tag or digest ref

        Args:
        None

        Returns:
        str: The image identifier, either a tag or digest
        """
        # Ensure the ref is valid, if not raise an exception
        valid, err = self.validate()
        if not valid:
            raise ValidationError(err)

        # Get either the tag or digest as the identifier for the image
        # Raise an exception if neither a valid tag or digest is found
        if self.is_digest_ref():
            return self.ref.split("@")[-1]
        elif self.is_tag_ref():
            if ":" in self.ref:
                return self.ref.split(":")[-1]
            return "latest"
        else:
            raise Exception(f"Not a valid tag or digest ref: {self.ref}")

    def get_name(self) -> str:
        """
        Gets the image name, which is the image registry and path but without
        an identifier (tag or digest)

        Args:
        None

        Returns:
        str: The image name
        """
        # Ensure the ref is valid, if not raise an exception
        valid, err = self.validate()
        if not valid:
            raise ValidationError(err)
        
        # Parse out any digests or tags
        digestless = self.ref.split("@")[0]
        tagless = digestless.split(":")[0]

        # Validate the image name, if valid then return
        valid = bool(re.match(ANCHORED_NAME, tagless))
        if not valid:
            raise ValidationError(f"Invalid name: {tagless}")
        return tagless
    
    def get_registry(self) -> str:
        """
        Gets the image registry domain from the image reference

        Args:
        None

        Returns:
        str: The image registry domain
        """
        # Get the image name
        name = self.get_name()

        # Split the path off and isolate the registry domain
        registry = name.split("/")[0]

        # Validate the registry domain, return if valid
        valid = bool(re.match(ANCHORED_DOMAIN, registry))
        if not valid:
            raise ValidationError(f"Invalid domain: {registry}")
        return registry
    
    def get_path(self) -> str:
        """
        Gets the image path from the image name.  This is the path only,
        with no inclusion of the registry domain.

        Args:
        None

        Returns:
        str: The image path
        """
        # Get the image name
        name = self.get_name()

        # Split the path off and isolate the path
        name_comp = name.split("/")
        name_comp.pop(0) # Remove the registry

        # Reconstruct and return the path
        return "/".join(name_comp)

    def get_short_name(self) -> str:
        """
        Gets the image short name, which is the component of the image name
        following the final forward slash.  For example, for image name
        "ingress-nginx/controller", the image short name is just "controller"

        Args:
        None

        Returns:
        str: The image short name
        """
        return self.get_name().split("/")[-1]

    def get_manifest(self, auth: Dict[str, Any]) -> Union[
            Type[ContainerImageManifestV2S2],
            Type[ContainerImageManifestListV2S2],
            Type[ContainerImageManifestOCI],
            Type[ContainerImageIndexOCI]
        ]:
        """
        Fetches the manifest from the distribution registry API

        Args:
        auth (Dict[str, Any]): A valid docker config JSON with auth into this
            image's registry

        Returns:
        Union[
            Type[ContainerImageManifestV2S2],
            Type[ContainerImageManifestListV2S2],
            Type[ContainerImageManifestOCI],
            Type[ContainerImageIndexOCI]
        ]: The manifest or manifest list response from the registry API
        """
        # Ensure the ref is valid, if not raise an exception
        valid, err = self.validate()
        if not valid:
            raise ValidationError(err)
        
        # Use the container image registry client to get the manifest
        return ContainerImageManifestFactory.create(
            ContainerImageRegistryClient.get_manifest(self, auth)
        )
    
    def exists(self, auth: Dict[str, Any]) -> bool:
        """
        Determine if the image reference corresponds to an image in the remote
        registry.

        Args:
        auth (Dict[str, Any]): A valid docker config JSON with auth into this
            image's registry
        
        Returns:
        bool: Whether the image exists in the registry
        """
        try:
            ContainerImageRegistryClient.get_manifest(self, auth)
        except requests.HTTPError as he:
            if he.response.status_code == 404:
                return False
            else:
                raise he
        return True

    def is_manifest_list(self, auth: Dict[str, Any]) -> bool:
        """
        Determine if the image is a manifest list

        Args:
        auth (Dict[str, Any]): A valid docker config JSON with auth into this
            image's registry

        Returns:
        bool: Whether the image is a manifest list or single-arch
        """
        return ContainerImage.is_manifest_list_static(self.get_manifest(auth))

    def is_oci(self, auth: Dict[str, Any]) -> bool:
        """
        Determine if the image is in the OCI format

        Args:
        auth (Dict[str, Any]): A valid docker config JSON with auth into this
            image's registry
        
        Returns:
        bool: Whether the image is in the OCI format
        """
        return ContainerImage.is_oci_static(self.get_manifest(auth))

    def get_media_type(self, auth: Dict[str, Any]) -> str:
        """
        Gets the image's mediaType from its manifest

        Args:
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        str: The image's mediaType
        """
        return self.get_manifest(auth).get_media_type()

    def get_size(self, auth: Dict[str, Any]) -> int:
        """
        Calculates the size of the image by fetching its manifest metadata
        from the registry.

        Args:
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        int: The size of the image in bytes
        """
        # Get the manifest and calculate its size
        manifest = self.get_manifest(auth)
        if ContainerImage.is_manifest_list_static(manifest):
            return manifest.get_size(self.get_name(), auth)
        else:
            return manifest.get_size()

    def get_size_formatted(self, auth: Dict[str, Any]) -> str:
        """
        Calculates the size of the image by fetching its manifest metadata
        from the registry.  Formats as a human readable string (e.g. 3.14 KB)

        Args:
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        str: The size of the image in bytes in human readable format (1.25 GB)
        """
        return ByteUnit.format_size_bytes(self.get_size(auth))
    
    def delete(self, auth: Dict[str, Any]):
        """
        Deletes the image from the registry.

        Args:
        auth (Dict[str, Any]): A valid docker config JSON loaded into a dict

        Returns:
        None
        """
        # Ensure the ref is valid, if not raise an exception
        valid, err = self.validate()
        if not valid:
            raise ValidationError(err)
        
        ContainerImageRegistryClient.delete(self, auth)

    def __str__(self) -> str:
        """
        Formats the ContainerImage as a string

        Args:
        None

        Returns:
        str: The ContainerImage as a string
        """
        return self.ref

    def __json__(self) -> Dict[str, Any]:
        """
        Formats the ContainerImage as a JSON dict

        Args:
        None

        Returns:
        Dict[str, Any]: The ContainerImage as a JSON dict
        """
        return { "ref": self.ref }

"""
ContainerImageList class

Represents a list of ContainerImages. Enables performing bulk actions against
many container images at once.
"""
class ContainerImageList:
    def __init__(self):
        """
        Constructor for ContainerImageList class

        Args:
        None
        """
        self.images = []
    
    def __len__(self) -> int:
        """
        Returns the length of the ContainerImageList

        Args:
        None

        Returns:
        int: The length of the ContainerImageList
        """
        return len(self.images)
    
    def __iter__(self) -> Iterator[ContainerImage]:
        """
        Returns an iterator over the ContainerImageList

        Args:
        None

        Returns:
        Iterator[ContainerImage]: The iterator over the ContainerImageList
        """
        return iter(self.images)
    
    def append(self, image: Type[ContainerImage]):
        """
        Append a new ContainerImage to the ContainerImageList

        Args:
        image (Type[ContainerImage]): The ContainerImage to add

        Returns:
        None
        """
        self.images.append(image)

    def get_size(self, auth: Dict[str, Any]) -> int:
        """
        Get the deduplicated size of all container images in the list

        Args:
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        int: The deduplicated size of all container images in the list
        """
        # Aggregate all layer and config digests, sum manifest list entries
        entry_sizes = 0
        layers = {}
        configs = {}

        # Loop through each image in the list
        for image in self.images:
            # Get the image's manifest
            manifest = image.get_manifest(auth)

            # If a manifest list, get its configs, entry sizes, layers
            image_layers = []
            image_configs = []
            if ContainerImage.is_manifest_list_static(manifest):
                entry_sizes += manifest.get_entry_sizes()
                image_layers = manifest.get_layer_descriptors(image.get_name(), auth)
                image_configs = manifest.get_config_descriptors(image.get_name(), auth)
            # If an arch manifest, get its config, layers
            else:
                image_configs = [manifest.get_config_descriptor()]
                image_layers = manifest.get_layer_descriptors()
            
            # Append the configs & layers to the aggregated dicts
            for image_config in image_configs:
                config_digest = image_config.get_digest()
                config_size = image_config.get_size()
                configs[config_digest] = config_size
            for image_layer in image_layers:
                layer_digest = image_layer.get_digest()
                layer_size = image_layer.get_size()
                layers[layer_digest] = layer_size
        
        # Calculate the layer and config sizes
        layer_sizes = 0
        config_sizes = 0
        for digest in layers.keys():
            layer_sizes += layers[digest]
        for digest in configs.keys():
            config_sizes += configs[digest]
        
        # Return the summed size
        return layer_sizes + config_sizes + entry_sizes
    
    def get_size_formatted(self, auth: Dict[str, Any]) -> str:
        """
        Get the deduplicated size of all container images in the list,
        formatted as a human readable string (e.g. 3.14 MB)

        Args:
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        str: List size in bytes formatted to nearest unit (ex. "1.23 MB")
        """
        return ByteUnit.format_size_bytes(self.get_size(auth))
    
    def delete(self, auth: Dict[str, Any]):
        """
        Delete all of the container images in the list from the registry

        Args:
        auth (Dict[str, Any]): A valid docker config JSON dict

        Returns:
        None
        """
        for image in self.images:
            image.delete(auth)

    def diff(self, previous: Type[ContainerImageList]) -> Type[ContainerImageListDiff]:
        """
        Compare this ContainerImageList with another and identify images which
        were added, removed, updated, and common across both instances.  Here,
        the receiver ContainerImageList is viewed as the current version, while
        the argument ContainerImageList is viewed as the previous version.

        Args:
        previous (Type[ContainerImageList]): The "previous" ContainerImageList

        Returns:
        Type[ContainerImageListDiff]: The diff between the ContainerImageLists
        """
        # Initialize a ContainerImageListDiff
        diff = ContainerImageListDiff()

        # Construct a mapping of image name to current and prev image instance
        images = {}
        for image in self.images:
            image_name = image.get_name()
            if image_name not in images:
                images[image_name] = {}
            images[image_name]['current'] = image
        for image in previous.images:
            image_name = image.get_name()
            if image_name not in images:
                images[image_name] = {}
            images[image_name]['previous'] = image

        # Use the mapping to populate the diff
        for image_name, keys in images.items():
            if 'current' in keys and 'previous' in keys:
                current_identifier = images[image_name]['current'].get_identifier()
                previous_identifier = images[image_name]['previous'].get_identifier()
                if current_identifier == previous_identifier:
                    diff.common.append(images[image_name]['current'])
                    continue
                diff.updated.append(images[image_name]['current'])
            elif 'current' in images[image_name]:
                diff.added.append(images[image_name]['current'])
            elif 'previous' in images[image_name]:
                diff.removed.append(images[image_name]['previous'])
        return diff

"""
ContainerImageListDiff class

Represents a diff between two ContainerImageLists
"""
class ContainerImageListDiff:
    def __init__(self):
        """
        Constructor for the ContainerImageListDiff class

        Args:
        None
        """
        self.added = ContainerImageList()
        self.removed = ContainerImageList()
        self.updated = ContainerImageList()
        self.common = ContainerImageList()

    def __str__(self) -> str:
        """
        Formats a ContainerImageListDiff as a string

        Args:
        None

        Returns:
        str: The ContainerImageListDiff formatted as a string
        """
        # Format the summary
        summary =   f"Added:\t{len(self.added)}\n" + \
                    f"Removed:\t{len(self.removed)}\n" + \
                    f"Updated:\t{len(self.updated)}\n" + \
                    f"Common:\t{len(self.common)}"
        
        # Format the added, removed, updated, and common sections
        added = "\n".join([str(img) for img in self.added])
        removed = "\n".join([str(img) for img in self.removed])
        updated = "\n".join([str(img) for img in self.updated])
        common = "\n".join([str(img) for img in self.common])

        # Format the stringified diff
        diff_str =  f"Summary\n{summary}\n\nAdded\n{added}\n\n" + \
                    f"Removed\n{removed}\n\nUpdated\n{updated}\n\n" + \
                    f"Common\n{common}"
        return diff_str
