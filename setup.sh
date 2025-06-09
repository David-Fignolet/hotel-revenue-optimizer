#!/bin/bash
set -e
apt-get update
apt-get install -y default-jre
java -version