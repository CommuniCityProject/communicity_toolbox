#!/bin/bash
set -e

url="${1:-https://github.com/edgarGracia/models/releases/download/v0.2.1/data.zip}"

echo "Downloading ${url}"
wget -q --show-progress "${url}" -O data.zip

echo "Extracting data"
unzip -o data.zip

rm data.zip

echo "Done"