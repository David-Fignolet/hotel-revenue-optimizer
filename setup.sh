#!/bin/bash
set -e  # Exit on error

# Create .streamlit directory if it doesn't exist
mkdir -p ~/.streamlit/

# Create config.toml with production-ready settings
cat > ~/.streamlit/config.toml << EOL
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
enableWebsocketCompression = true

[browser]
serverAddress = ""
serverPort = 8501
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#1E88E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#262730"
font = "sans serif"

[runner]
# Optimize memory usage
magicEnabled = true

[logger]
level = "info"
messageFormat = "%(asctime)s %(levelname) -10s %(name)s %(funcName)s %(lineno)d: %(message)s"
textColor = "#262730"
font = "sans serif"
EOL

echo "Configuration Streamlit terminée"
