#!/bin/sh
set -eu

rm -rf default.db

# install
python ./setup.py develop

# init database
piper-core ./config.example.yml --init "root@localhost ~/.ssh/id_rsa.pub"

# execute shell
piper-shell ./config.example.yml 1