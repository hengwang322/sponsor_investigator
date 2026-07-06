#!/bin/bash
set -euo
uv pip install \
    --target ./site-packages \
    --python-platform x86_64-manylinux_2_28 \
    --python-version 3.14 \
    --only-binary=:all: \
    -r requirements.txt
    
zip -r lambda.zip . -x "__pycache__/*"
