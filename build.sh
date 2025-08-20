#!/bin/bash

# This script is run by Vercel during the build step.
# It's run from the repository root.

echo "--- Starting custom build script ---"

# Copy the entire 'music' directory into the 'server' directory.
# The 'server' directory is our Vercel "Root Directory".
cp -r music server/

echo "--- Successfully copied 'music' folder into 'server' folder ---"