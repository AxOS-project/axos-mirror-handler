#!/bin/bash

DIR="$HOME/.local/bin/"

echo "Installing to '$DIR'"

echo "Creating directories..."
mkdir -p "$DIR"

echo "Verifying file..."
if [[ -f "mirror.py" ]]; then
    cp mirror.py "$DIR/axmirrors"
else
    echo "mirror.py does not exist!"
    exit 1
fi
