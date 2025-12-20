## Contribution Guide

Welcome to `drawpyo`! We're always interested in new contributors. This document contains information on the project goals and infrastructure.

### Working with the Project

Contributions can be made in one of two areas. `src/drawpyo` contains the core logic for generating any arbitrary Draw.io diagram. `src/drawpyo/diagram_types` contains subfunctions that use those core functions to automate the generation of common diagram types. A good first contribution is implementing a diagram_type before modifying the core functionality. Issues related to this are labeled with [the 'diagramType' tag](https://github.com/MerrimanInd/drawpyo/issues?q=is%3Aissue%20state%3Aopen%20label%3AdiagramType).

We prioritize keeping the absolute minimum dependencies. Currently we only have one dependency and that's the `toml` library. TOML reading functionality was added to the standard library in Python 3.11 so once we end support for 3.10 and 3.11 is the MRV we'll hopefully go down to zero dependencies!

### Working with the Codebase

We recommend [uv](https://docs.astral.sh/uv/) for working with the codebase. This cargo-like package and build manager handles creating venvs, downloading dependencies, and running scripts all in one tool. Prepending most commands (including `pip`) with `uv run` will run that command in the local uv-controlled venv and dependencies. `uv` checks the `pyproject.toml` file for dependencies and configuration, including both the package's dependencies and the development dependencies for building docs, testing, or deploying.

#### Docs

The docs are generated with `mkdocs`. To launch a docs server enter into your terminal:

```shell
uv run mkdocs serve
```

This will start a localhost instance of the documentation that will watch the `docs/` folder and update with any file changes. Make sure to update the docs with any new features added!

#### Testing

Drawpyo uses [tox](https://tox.wiki/) as a test manager. This creates virtual environments for each Python version and runs pytest in each one. The `tox.ini` file configures the testing workflow, including all the Python versions to test against. It also runs the [black](https://pypi.org/project/black/) formatter against the library to format the files.

To run the test suite enter in your terminal:

```shell
uv run tox
```

#### Building

Building can also be done with `uv`! The build system (flit) is specified in the `pyproject.toml` file and should have been installed automatically by `uv`. To build the wheels enter in your terminal:

```shell
uv build
```

All builds and publishing to PyPI is handled by GitHub Actions through Trusted Publishing. So builds need only be ran locally as verification.

#### Publishing

Drawpyo has GitHub Actions set up to automatically publish any commit to the main branch to TestPyPI and publish any tagged commit in main to the production PyPI instance, with approval from a maintainer.

#### Manual Publishing

For those with access to the PyPI repository and a valid API key, a manual upload to PyPI can be performed when there's a CD pipeline failure. `twine` handles the upload.

First, test the upload on TestPyPI with the command:

`uv run twine upload --repository testpypi dist/* -u "__token__" -p [TEST_API_TOKEN]"`

Once that's done, upload to the main PyPI instance:

`uv run twine upload --repository pypi dist/* -u "__token__" -p [API_TOKEN]"`

Likewise, a manual docs build and upload can be performed using the `gh` CLI:

`uv run mkdocs gh-deploy --force`

Note that your GitHub user account needs to have the correct access to the repo for this, making copying a token into the command unnecessary.
