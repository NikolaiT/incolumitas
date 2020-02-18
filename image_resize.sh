#!/bin/bash

find ./content/ -type f -name "*.md" -exec sed -i 's/"width: 800px"/"width: 100%"/g' {} +
