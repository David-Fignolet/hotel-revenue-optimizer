import streamlit as st
from src.dashboard import main

# Configuration de la page
st.set_page_config(
    page_title="Hotel Revenue Optimizer",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Désactiver le warning PyplotGlobalUse
st.set_option('deprecation.showPyplotGlobalUse', False)

def main_app():
    """Fonction principale de l'application Streamlit"""
    # Afficher le dashboard
    main()

if __name__ == "__main__":
    main_app()
