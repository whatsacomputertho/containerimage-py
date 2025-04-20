.PHONY: doc

PYTHON ?= /usr/bin/python3

# Execute the unit tests locally and in CI
test:
	$(PYTHON) -m pytest -vv

# Build the python distribution locally and in CI
build:
	$(PYTHON) -m build

# Build the python docs locally and in CI
doc:
	$(PYTHON) -m sphinx ./doc/source ./doc/sphinx
