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
echo 'Installing requirements..'
pip install --upgrade pip
pip install -r requirements.txt
pip install -r dev-requirements.txt

echo "---"
echo 'Starting server..'
FLASK_APP=src/subjob_coordinator/server.py flask run --host=0.0.0.0
