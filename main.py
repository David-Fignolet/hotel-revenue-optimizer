#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(root_dir))

def main():
    """Point d'entrée principal de l'application."""
    from app.streamlit_app import run_app
    run_app()

if __name__ == "__main__":
    main()