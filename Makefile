.PHONY: doc
PYTHON ?= /usr/bin/python3
PYPI ?= testpypi

############
# Pre-commit recipes
#
# Install the pre-commit hooks for the project
pre-commit:
	$(PYTHON) -m pip install -r ci/requirements.precommit.txt
	$(PYTHON) -m pre_commit install

#########
# Testing recipes
#
# Install the required dependencies for the test recipe
test-dependencies:
	$(PYTHON) -m pip install -r ci/requirements.test.txt

# Execute the unit tests locally and in CI
test:
	$(PYTHON) -m tox

#######
# Build recipes
#
# Install the required dependencies for the build recipe
build-dependencies:
	$(PYTHON) -m pip install -r ci/requirements.build.txt

# Build the python distribution locally and in CI
build:
	$(PYTHON) -m build

#########
# Publish recipes
#
# Install the required dependencies for the publish recipe
publish-dependencies:
	$(PYTHON) -m pip install -r ci/requirements.publish.txt

# Publish the built python distribution
# Assumes the python distribution was already built using build recipe
publish:
	$(PYTHON) -m twine upload --repository $(PYPI) dist/*

#########
# Release recipes
#
# Install the required dependencies for the release recipe
release-dependencies: build-dependencies publish-dependencies

# Release the python distribution by building and publishing it
release: build publish

#####
# Doc recipes
#
# Install the required dependencies for the doc recipe
doc-dependencies:
	$(PYTHON) -m pip install -r ci/requirements.doc.txt

# Build the python docs locally and in CI
doc:
	$(PYTHON) -m sphinx.ext.apidoc -o ./doc/source/image . "tests/*"
	$(PYTHON) -m sphinx ./doc/source ./doc/sphinx

##########
# Security recipes
#
# Install required dependencies for the sec recipe
sec-dependencies:
	$(PYTHON) -m pip install -r ci/requirements.sec.txt

# Security scan locally and in CI
sec:
	$(PYTHON) -m detect_secrets.pre_commit_hook --baseline .secrets.baseline -v
	$(PYTHON) -m pip_audit -r requirements.txt
