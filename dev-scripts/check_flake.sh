#!/bin/bash
echo "Kontrola flake8..."

flake8 . --max-line-length 120
