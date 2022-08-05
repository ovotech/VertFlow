#!/bin/sh
#Install VertFlow on the Cloud Composer image to confirm that it is compatible.

set -ex

PYTHON=python3

echo "Installing Cloud Composer requirements..."
${PYTHON} -m pip install -r requirements.txt

echo "Installing VertFlow..."
#First install from TestPyPI always fails, so ignore and repeat.
for i in 1 2; do
  ${PYTHON} -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ VertFlow=="$VERTFLOW_VERSION" || true
done

${PYTHON} -m pip check
