#!/bin/bash

pelican -s pelicanconf.py

python3 -m http.server --directory output/
