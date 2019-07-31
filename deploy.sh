#!/usr/bin/env bash

python -m unittest discover .\tests || exit $?
rm dist/*
python setup.py bdist_wheel
python -m twine upload dist/*
