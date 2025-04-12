# Execute the unit tests locally and in CI
test:
	pytest -vv

# Build the python distribution locally and in CI
build:
	python3 -m build