#!/bin/sh
mkdir -p $HOME/.pythonvenv
python3 -m venv $HOME/.pythonvenv/flashfeed
source $HOME/.pythonvenv/flashfeed/bin/activate
export PATH="$HOME/.pythonvenv/flashfeed/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
