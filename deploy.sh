#!/bin/sh

set -eux

pip install build
pip install twine

python -m build
twine check dist/*

twine upload \
  --non-interactive \
  -u __token__ \
  -p $VERTFLOW_PYPI_TOKEN \
  dist/*
