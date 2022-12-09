#!/bin/bash
# Assumes user has a working version of python3.9 installed
# Create venv and activate it
python3.9 -m venv venv
source venv/bin/activate

# Install python dependancies
pip install -e .

# Install npm dependancies
cd mags/static
npm ci mags

# Download and extract stockfish
cd ../../
mkdir -p stockfish
cd stockfish
wget "https://stockfishchess.org/files/stockfish_15.1_linux_x64_avx2.zip"
unzip stockfish_15.1_linux_x64_avx2.zip
rm stockfish_15.1_linux_x64_avx2.zip
