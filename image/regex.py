import re
from typing import List

"""
Container image regexp validation

Ported to python from official containers/image go module
Ref: https://github.com/containers/image/blob/main/docker/reference/regexp.go
"""

"""
Container image regexp constants / atoms
"""

# ALPHA_NUMERIC defines the alpha numeric atom, typically a
# component of names. This only allows lower case characters and digits.
ALPHA_NUMERIC = r"[a-z0-9]+"

# SEPARATOR defines the separators allowed to be embedded in name
# components. This allow one period, one or two underscore and multiple
# dashes. Repeated dashes and underscores are intentionally treated
# differently. In order to support valid hostnames as name components,
# supporting repeated dash was added. Additionally double underscore is
# now allowed as a separator to loosen the restriction for previously
# supported names.
SEPARATOR = r"(?:[._]|__|[-]*)"

# repository name to start with a component as defined by DOMAIN and
# followed by an optional port.
DOMAIN_COMPONENT = r"(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])"

# matches valid tag names. From docker/docker:graph/tags.go.
TAG_PAT = r"[\w][\w.-]{0,127}"

# The string counterpart for DIGEST_REGEXP.
DIGEST_PAT = r"[A-Za-z][A-Za-z0-9]*(?:[-_+.][A-Za-z][A-Za-z0-9]*)*:[0-9a-fA-F]{32,}"

# The string counterpart for IDENTIFIER_REGEXP.
IDENTIFIER = r"([a-f0-9]{64})"

# The string counterpart for SHORT_IDENTIFIER_REGEXP.
SHORT_IDENTIFIER = r"([a-f0-9]{6,64})"

"""
Container image regexp helper functions
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

"""
Constructed container image regexp constants
"""

# NAME_COMPONENT restricts registry path component names to start with at
# least one letter or number, with following parts able to be separated by
# one period, one or two underscore and multiple dashes.
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

# DOMAIN defines the structure of potential domain components that may be part
# of image names. This is purposely a subset of what is allowed by DNS to
# ensure backwards compatibility with Docker image names.
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
ANCHORED_DOMAIN = anchored(DOMAIN)

# ANCHORED_TAG matches valid tag names, anchored at the start and end of the
# matched string.
ANCHORED_TAG = anchored(TAG_PAT)

# ANCHORED_DIGEST matches valid digests, anchored at the start and end of the
# matched string.
ANCHORED_DIGEST = anchored(DIGEST_PAT)

# NAME_PAT is the format for the name component of references. The regexp has
# capturing groups for the domain and name part omitting the separating forward
# slash from either.
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

# ANCHORED_NAME is used to parse a name value, capturing the domain and
# trailing components.
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

# REFERENCE_PAT is the full supported format of a reference. The regexp is
# anchored and has capturing groups for name, tag, and digest components.
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
