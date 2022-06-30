#!/bin/sh

set -e

pip install build
pip install twine

python -m build
twine check dist/*

