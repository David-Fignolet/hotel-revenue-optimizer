#!/bin/bash
set -e

# Mettre à jour les paquets
apt-get update

# Installer Java (requis pour tabula-py)
apt-get install -y default-jre

# Vérifier l'installation de Java
java -version