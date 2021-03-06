# Archivar Dev Guide

## Getting started

Get started just like a normal setup:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements
export FLASK_APP=dmcp.py
flask db upgrade
flask run
```

Be sure to work on your own branch(es).

## Linting

You can setup automatic code linting as a git pre-commit hook using `./setup-pre-commit-hook.sh`.
You may need to install flake8 via `pip install flake8`.
If you want to integrate the linting into your IDE, toplevel has a .flake8 config file that can be used.

## Changes to the database

To make changes to the database, adjust the member elements of one or more of the model classes. Then run:

```bash
flask db migrate -m "very short description"
flask db upgrade
```

from within the venv.
This creates a migration file in migrations/version/$hash_very_short_description.py.
This file *must* be commited with the first commit that accesses the new model members.

## Installing additional packages

From within the venv, install additional packages with pip:

```bash
pip install $package-name(s)
```

After that, add the new packages to the requirements:

```bash
pip freeze | grep -v "pkg-resources" > requirements.txt
```

Note: the grep prevents a bug on some systems where pkg-resources=0.0.0 is erroneously added to the requirements-file.
The updates requirements.txt *must* be part of the commit that uses functions from the new packages.

## Running in Dev/Debug-Mode

Start `flask run` with FLASK_ENV=development to enter debug-mode.
It will provide a python debugger, automatic reload on code-change as well as some extra logging (and hints in the template that you are in dev-mode).
