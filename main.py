import os
import sys

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.streamlit_app import main

if __name__ == "__main__":
    main()