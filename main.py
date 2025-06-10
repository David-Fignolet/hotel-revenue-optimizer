#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(str(Path(__file__).parent.absolute()))

def main():
    """Point d'entrée principal de l'application."""
    from app.streamlit_app import run_app
    run_app()

if __name__ == "__main__":
    main()