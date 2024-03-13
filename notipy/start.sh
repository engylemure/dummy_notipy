#!/bin/bash


# Special case probably on docker with volume mapped
if [ ! -d .venv ]; then
    source "$HOME/.rye/env" && rye sync -f
fi

source .venv/bin/activate && python src/notipy
