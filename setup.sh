#!/bin/bash

# Créer le dossier .streamlit s'il n'existe pas
mkdir -p ~/.streamlit/

# Créer le fichier de configuration
cat > ~/.streamlit/config.toml << EOL
[server]
headless = true
port = 8501
enableCORS = false

[browser]
serverAddress = ""
serverPort = 8501

[theme]
base = "light"
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOL

echo "Configuration Streamlit terminée"
