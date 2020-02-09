#!/bin/sh

pip3 install -r requirements.txt -r requirements-dev.txt -r requirements-tests.txt --user
pre-commit install
pre-commit autoupdate
