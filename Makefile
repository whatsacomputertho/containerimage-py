.PHONY: doc
PYTHON ?= /usr/bin/python3

#########
# Testing recipes
#
# Install the required dependencies for the test recipe
test-dependencies:
	$(PYTHON) -m pip install -r requirements.test.txt

# Execute the unit tests locally and in CI
test:
	$(PYTHON) -m tox

#######
# Build recipes
#
# Install the required dependencies for the build recipe
build-dependencies:
	$(PYTHON) -m pip install -r requirements.build.txt

# Build the python distribution locally and in CI
build:
	$(PYTHON) -m build

#####
# Doc recipes
#
# Install the required dependencies for the doc recipe
doc-dependencies:
	$(PYTHON) -m pip install -r requirements.doc.txt

# Build the python docs locally and in CI
doc:
	$(PYTHON) -m sphinx.ext.apidoc -o ./doc/source/image . "tests/*"
	$(PYTHON) -m sphinx ./doc/source ./doc/sphinx

##########
# Security recipes
#
# Install required dependencies for the sec recipe
sec-dependencies:
	$(PYTHON) -m pip install -r requirements.sec.txt
	$(PYTHON) -m pre_commit install

# Security scan locally and in CI
sec:
	$(PYTHON) -m detect_secrets.pre_commit_hook --baseline .secrets.baseline -v
	$(PYTHON) -m pip_audit -r requirements.txt
