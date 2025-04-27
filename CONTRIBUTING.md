# Contributing to containerimage-py

> Thank you for your interest in contributing into `containerimage-py`!  Here are some basic instructions and background information on how to do so.

## Contents

- Tooling Setup
- Version Control

## Tooling Setup

> Discusses how to set up the project's pre-commit hooks, and install dependencies for the project's various make recipes

### Pre-Commit Hooks

> [!IMPORTANT]  
> All `containerimage-py` contributors should install the project's pre-commit hooks to ensure all incoming changes are secure, linted, and properly formatted

To install the project's pre-commit hooks, simply execute the following from the root of this repository
```sh
make pre-commit
```

### Other Make Recipes

You may need to execute other make recipes in contributing to the project, such as
- `make build`: To ensure the project can still successfully build into a python distribution
- `make doc`: To ensure the project's documentation can be generated without warnings
- `make sec`: To ensure the source code contains no new secrets, to ensure project dependencies contain no known vulnerabilities
- `make test`: To execute the unit tests across multiple python versions

For each of these recipes, we have recipes for installing their dependencies.  For each, this simply involves appending `-dependencies` onto the recipe name.  For example,
```sh
make build-dependencies
```

The default python interpreter used by each recipe is `/usr/bin/python3`, but you may override this for your system by setting the `PYTHON` value like so
```sh
PYTHON=/my/custom/python make build
```

> [!WARNING]
> The `make test-dependencies` recipe DOES NOT install all the required python interpreter for `tox`.  You must install each python interpreter expected by `tox` beforehand.  Because this process is dependent on the system you are developing on, we do not have a straightforward `make` recipe written for this.

## Version Control

> [!TIP]
> Any `containerimage-py` contributor should be familiar with the project's version control practices to ensure they contribute into the correct branches of the project, and understand how to include their changes in a project release

The `containerimage-py` project makes use of the following version control strategy.
1. The `main` branch represents the latest developments that are considered potentially shippable
    - The `main` branch MAY incur API breaking changes at any time
    - Releases of `containerimage-py` MUST NOT be produced from the `main` branch
2. For each release, we create a `release-x.y` branch, where `x.y` is the Major.Minor version of the release
    - The `release-x.y` branch MUST NOT incur API breaking changes
    - Any release of `containerimage-py` with Major.Minor version `x.y` MUST be produced from the `release-x.y` branch
        - Including the initial `x.y.0` release, `x.y.z` patch releases, and pre-releases (`x.y.z-prerelease`)
    - Any release of `containerimage-py` MUST be accompanied by a git tag and GitHub release
3. All new development MUST first be contributed into the `main` branch, then cherry-picked (using `git cherry-pick`) into the `release-x.y` branch for its corresponding release
    - Any exception to this rule (such as backports to significantly old versions) MUST be approved by project maintainers
