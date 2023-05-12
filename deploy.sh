#!/bin/sh
# Deploy VertFlow to (Test)PyPI

TEST="${1}"

set -eux

pip install build
pip install twine

. ./VERSION
export VERTFLOW_VERSION

rm -rf dist

python -m build
twine check dist/*

if [[ $TEST == "--test" ]]; then
  twine upload \
    --non-interactive \
    --repository testpypi \
    -u __token__ \
    -p "$VERTFLOW_TESTPYPI_TOKEN" \
    dist/*

  sleep 10

  docker build \
    test/build_on_cloud_composer \
    --no-cache \
    --progress=plain \
    --build-arg VERTFLOW_VERSION="$VERTFLOW_VERSION"
else
  twine upload \
    --non-interactive \
    -u __token__ \
    -p "$VERTFLOW_PYPI_TOKEN" \
    dist/*
fi
