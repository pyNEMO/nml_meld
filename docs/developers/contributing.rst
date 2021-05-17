Contributing
************

Documentation
=============

- The documentation consists of two parts: the docstrings in the code itself
  and the docs in this folder ``nml_meld/docs/``.

- The documentation is written in `reStructuredText <http://sphinx-doc.org/>`_
  and built using `Sphinx <http://sphinx-doc.org/>`_.

- The docstrings follow the `Numpy Docstring Standard
  <https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard>`_.

How to build the documentation:

.. code-block:: sh

    # Create and activate the docs environment
    conda env create -f nml_meld/ci/docs.yml
    conda activate nmlmeld_docs

    # Navigate to the docs directory
    cd nml_meld/docs/

    # If you want to do a full clean build
    make clean

    # Build the documentation
    make html


Tests
=====

- All tests go into this folder ``nml_meld/nmlmeld/tests``.

- We are using `pytest <http://doc.pytest.org/en/latest/>`_ for testing.

Test functions should look like this:

.. code-block:: python

    def add_one(x):
        return x + 1


    def test_add_one():
        expected = 2
        actual = add_one(1)
        assert expected == actual

How to run the tests:

.. code-block:: sh

    # Create and activate the test environment
    conda env create -f nml_meld/ci/environment.yml
    conda activate nmlmeld_test

    # Navigate to the root directory and run pytest
    cd nml_meld
    pytest


Pre-commit formatting
=====================

We are using several tools to ensure that code and docs are well formatted:

- `isort <https://github.com/timothycrosley/isort>`_
  for standardized order in imports.
- `Black <https://black.readthedocs.io/en/stable/>`_
  for standardized code formatting.
- `blackdoc <https://blackdoc.readthedocs.io/en/stable/>`_
  for standardized code formatting in documentation.
- `Flake8 <http://flake8.pycqa.org/en/latest/>`_ for general code quality.
- `Darglint <https://github.com/terrencepreilly/darglint>`_ for docstring quality.
- `mypy <http://mypy-lang.org/>`_ for static type checking on
  `type hints <https://docs.python.org/3/library/typing.html>`_.
- `doc8 <https://github.com/PyCQA/doc8>`_ for reStructuredText documentation quality.

Setup `pre-commit <https://pre-commit.com/>`_ hooks to automatically run all
the above tools every time you make a git commit:

.. code-block:: sh

    # Install the pre-commit package manager.
    conda install -c conda-forge pre-commit

    # Set up the git hook scripts.
    cd nml_meld
    pre-commit install

    # Now pre-commit will run automatically on the changed files on ``git commit``
    # Alternatively, you can manually run all the hooks with:
    pre-commit run --all

    # You can skip the pre-commit checks with:
    git commit --no-verify

