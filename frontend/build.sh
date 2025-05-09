#!/bin/bash

# Install dependencies
npm install --legacy-peer-deps

# Build the application
npm run build

# Ensure the build directory exists
if [ ! -d "build" ]; then
    echo "Build directory not found!"
    exit 1
fi

# Ensure index.html exists in the build directory
if [ ! -f "build/index.html" ]; then
    echo "index.html not found in build directory!"
    exit 1
fi

echo "Build completed successfully!" 