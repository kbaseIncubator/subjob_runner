#!/bin/bash

# Exit on any error
set -e

# This is run when the server exits, including on Ctrl-C
function cleanup {
  echo 'Deactivating env..'
  deactivate
}
trap cleanup EXIT

echo '---'
echo 'Setting up and activating environment..'
python -m venv env
source env/bin/activate

echo '---'
echo 'Running tests..'
python -m unittest discover src/test $1
