"""
Regex patterns used for validating container image references, ported to
python from official containers/image go module.

Ref: https://github.com/containers/image/blob/main/docker/reference/regexp.go
"""

import re
from typing import List

# See doc comments below
ALPHA_NUMERIC = r"[a-z0-9]+"
"""
Defines the alpha numeric atom, typically a component of names. This only
allows lower case characters and digits.

Ported to python from official containers/image go module

Ref: https://github.com/containers/image/blob/main/docker/reference/regexp.go
"""

# See doc comments below
SEPARATOR = r"(?:[._]|__|[-]*)"
"""
Defines the separators allowed to be embedded in name components. This allows
one period, one or two underscore and multiple dashes. Repeated dashes and
underscores are intentionally treated differently. In order to support valid
hostnames as name components, supporting repeated dash was added. Additionally
double underscore is now allowed as a separator to loosen the restriction for
previously supported names.
"""

# See doc comments below
DOMAIN_COMPONENT = r"(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])"
"""
Repository name to start with a component as defined by DOMAIN and followed by
an optional port.
"""

# See doc comments below
TAG_PAT = r"[\w][\w.-]{0,127}"
"""
Matches valid tag names. From the docker/docker library's graph/tags.go source
file
"""

# See doc comments below
DIGEST_PAT = r"[A-Za-z][A-Za-z0-9]*(?:[-_+.][A-Za-z][A-Za-z0-9]*)*:[0-9a-fA-F]{32,}"
"""
The string counterpart for DIGEST_REGEXP.
"""

# See doc comments below
IDENTIFIER = r"([a-f0-9]{64})"
"""
The string counterpart for IDENTIFIER_REGEXP.
"""

# See doc comments below
SHORT_IDENTIFIER = r"([a-f0-9]{6,64})"
"""
The string counterpart for SHORT_IDENTIFIER_REGEXP.
"""

def literal(s: str) -> str:
    """
    Compiles s into a literal regular expression, escaping any regexp reserved
    characters

    Args:
        s (str): The literal to convert to a regular expression

    Returns:
        str: The converted regular expression literal
    """
    return re.escape(s)

def expression(res: List[str]) -> str:
    """
    Defines a full expression, where each regular expression must follow the
    previous

    Args:
        res (List[str]): The regular expressions to combine

    Returns:
        str: The combined regular expressions
    """
    return r"".join(res)

def optional(res: List[str]) -> str:
    """
    Wraps the expression in a non-capturing group and makes the production
    optional

    Args:
        res (List[str]): The regular expressions to make optional

    Returns:
        str: The regular expressions made optional
    """
    return group([expression(res)]) + r"?"

def repeated(res: List[str]) -> str:
    """
    Wraps the regexp in a non-capturing group to get one or more matches

    Args:
        res (List[str]): The regular expressions to repeat

    Returns:
        str: The repeated regular expressions
    """
    return group([expression(res)]) + r"+"

def group(res: List[str]) -> str:
    """
    Wraps the regexp in a non-capturing group.

    Args:
        res (List[str]): The regular expressions to group

    Returns:
        str: The grouped regular expressions
    """
    return r"(?:" + expression(res) + r")"

def capture(res: List[str]) -> str:
    """
    Wraps the expression in a capturing group.

    Args:
        res (List[str]): The regular expressions to capture

    Returns:
        str: The captured regular expressions
    """
    return r"(" + expression(res) + r")"

def anchored(res: List[str]) -> str:
    """
    Anchors the regular expression by adding start and end delimiters.

    Args:
        res (List[str]): The regular expressions to anchor

    Returns:
        str: The anchored regular expression
    """
    return r"^" + expression(res) + r"$"

# See doc comments below
NAME_COMPONENT = expression(
    [
        ALPHA_NUMERIC,
        optional(
            repeated(
                [
                    SEPARATOR,
                    ALPHA_NUMERIC
                ]
            )
        )
    ]
)
"""
Restricts registry path component names to start with at least one letter or
number, with following parts able to be separated by one period, one or two
underscore and multiple dashes.
"""

# See doc comments below
DOMAIN = expression(
    [
        DOMAIN_COMPONENT,
        optional(
            repeated(
                [
                    literal("."),
                    DOMAIN_COMPONENT
                ]
            )
        ),
        optional(
            [
                literal(":"),
                r"[0-9]+"
            ]
        )
    ]
)
"""
Defines the structure of potential domain components that may be part of image
names. This is purposely a subset of what is allowed by DNS to ensure backwards
compatibility with Docker image names.
"""

# See doc comments below
ANCHORED_DOMAIN = anchored(DOMAIN)
"""
Matches valid domains, anchored at the start and end of the matched string.
"""

# See doc comments below
ANCHORED_TAG = anchored(TAG_PAT)
"""
Matches valid tag names, anchored at the start and end of the matched string.
"""

# See doc comments below
ANCHORED_DIGEST = anchored(DIGEST_PAT)
"""
Matches valid digests, anchored at the start and end of the matched string.
"""

# See doc comments below
NAME_PAT = expression(
	[
        optional(
            [
                DOMAIN,
                literal("/")
            ]
        ),
        NAME_COMPONENT,
        optional(
            repeated(
                [
                    literal("/"),
                    NAME_COMPONENT
                ]
            )
        )
    ]
)
"""
The format for the name component of references. The regexp has capturing
groups for the domain and name part omitting the separating forward slash from
either.
"""

# See doc comments below
ANCHORED_NAME = anchored(
    [
        optional(
            [
                capture(
                    DOMAIN
                ),
                literal("/")
            ]
        ),
        capture(
            [
                NAME_COMPONENT,
                optional(
                    repeated(
                        [
                            literal("/"),
                            NAME_COMPONENT
                        ]
                    )
                )
            ]
        )
    ]
)
"""
Used to parse a name value, capturing the domain and trailing components.
"""

# See doc comments below
REFERENCE_PAT = anchored(
    [
        capture(
            NAME_PAT
        ),
        optional(
            [
                literal(":"),
                capture(TAG_PAT)
            ]
        ),
        optional(
            [
                literal("@"),
                capture(DIGEST_PAT)
            ]
        )
    ]
)
"""
The full supported format of a reference. The regexp is anchored and has
capturing groups for name, tag, and digest components.
"""
