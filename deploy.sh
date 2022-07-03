#!/bin/sh

set -e

pip install build
pip install twine

python -m build
twine check dist/*

twine upload \
--non-interactive \
-u __token__ \
-p $(gcloud secrets versions access projects/714098496902/secrets/pypi-api-token-all-scopes-test/versions/1) \
dist/*
