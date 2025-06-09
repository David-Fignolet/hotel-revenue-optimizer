"""
Streamlit App for Hotel Revenue Optimization Dashboard
"""
import streamlit as st

# Configuration de la page - DOIT ÊTRE LA PREMIÈRE COMMANDE
st.set_page_config(
    page_title="Optimisateur de Revenu Hôtelier",
    page_icon="🏨",
    layout="wide"
)

# Imports standards
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import os
import re

# Import du tableau de bord
try:
    from src.dashboard import DashboardVisuals
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False

# Vérification de tabula
try:
    from tabula import read_pdf
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False

def clean_numeric_series(series):
    """Nettoie une série numérique en remplaçant les virgules par des points"""
    return series.astype(str).str.replace(',', '.').astype(float)

def parse_hotel_pdf(pdf_file):
    """Traite un fichier PDF d'hôtel et retourne un DataFrame nettoyé"""
    if not TABULA_AVAILABLE:
        st.error("Erreur: tabula-py n'est pas disponible. Impossible de traiter les fichiers PDF.")
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_file.getvalue())
        tmp_path = tmp.name
    
    try:
        # Lire le PDF avec des paramètres optimisés
        dfs = read_pdf(
            tmp_path,
            pages='all',
            multiple_tables=True,
            lattice=False,
            stream=True,
            pandas_options={'header': None},
            guess=False
        )
        
        if not dfs:
            st.error("Aucune donnée trouvée dans le PDF")
            return None
        
        # Concaténer et nettoyer les données
        df = pd.concat(dfs, ignore_index=True)
        df = df.dropna(how='all').reset_index(drop=True)
        
        # Nettoyer les données texte
        df = df.astype(str)
        df = df.apply(lambda x: x.str.strip())
        
        # Initialiser les données de sortie
        processed_data = {
            'date': [],
            'price': [],
            'occupancy_rate': [],
            'chambres_occupees': [],
            'chambres_totales': [],
            'ca_total': []
        }
        
        # Traiter chaque ligne
        for _, row in df.iterrows():
            row_str = ' '.join([str(cell) for cell in row if str(cell) != 'nan'])
            if not row_str.strip():
                continue
                
            # Chercher une date au format JJ.MM.AA
            date_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', row_str)
            if not date_match:
                continue
                
            try:
                date_str = date_match.group(1)
                date = datetime.strptime(date_str, '%d.%m.%y').date()
                
                # Extraire les nombres décimaux
                numbers = re.findall(r'(\d+[\.,]?\d*)', row_str)
                numbers = [float(n.replace(',', '.')) for n in numbers if n.replace(',', '').replace('.', '').isdigit()]
                
                if len(numbers) >= 12:  # Vérifier qu'on a assez de nombres
                    chambres_occupees = numbers[6]   # 7ème nombre
                    chambres_totales = numbers[7]    # 8ème nombre
                    taux_occupation = numbers[8]      # 9ème nombre
                    prix_moyen = numbers[10]          # 11ème nombre
                    ca_total = numbers[11]            # 12ème nombre
                    
                    # Ajouter aux données traitées
                    processed_data['date'].append(date)
                    processed_data['price'].append(prix_moyen)
                    processed_data['occupancy_rate'].append(taux_occupation / 100)
                    processed_data['chambres_occupees'].append(chambres_occupees)
                    processed_data['chambres_totales'].append(chambres_totales)
                    processed_data['ca_total'].append(ca_total)
                    
            except Exception as e:
                st.warning(f"Ligne ignorée: {row_str}")
                continue
                
        # Créer le DataFrame final
        result_df = pd.DataFrame(processed_data)
        
        if result_df.empty:
            st.error("Aucune donnée valide trouvée dans le PDF")
            return None
            
        # Nettoyer les colonnes numériques
        numeric_cols = ['price', 'occupancy_rate', 'chambres_occupees', 'chambres_totales', 'ca_total']
        for col in numeric_cols:
            if col in result_df.columns:
                result_df[col] = clean_numeric_series(result_df[col])
        
        # Trier par date
        result_df = result_df.sort_values('date').reset_index(drop=True)
        
        return result_df
        
    except Exception as e:
        st.error(f"Erreur lors du traitement du PDF : {str(e)}")
        return None
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def load_uploaded_file(uploaded_file):
    """Charge un fichier CSV ou PDF téléchargé"""
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.pdf'):
            return parse_hotel_pdf(uploaded_file)
        else:
            st.error("Format de fichier non supporté. Veuillez télécharger un fichier CSV ou PDF.")
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {str(e)}")
        return None

def generate_predictions(historical, days=30):
    """Génère des prédictions basées sur les données historiques"""
    # Implémentez votre logique de prédiction ici
    # Ceci est un exemple simplifié
    last_date = historical['date'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
    
    predictions = pd.DataFrame({
        'date': future_dates,
        'price': historical['price'].mean() * np.random.normal(1, 0.1, days),
        'occupancy_rate': np.clip(historical['occupancy_rate'].mean() * np.random.normal(1, 0.15, days), 0, 1)
    })
    
    return predictions

def display_metrics(historical, predictions=None):
    """Affiche les indicateurs clés"""
    if historical is None or historical.empty:
        return
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Prix moyen", f"{historical['price'].mean():.2f} €")
    
    with col2:
        st.metric("Taux d'occupation", f"{historical['occupancy_rate'].mean() * 100:.1f}%")
    
    with col3:
        if 'ca_total' in historical.columns:
            st.metric("CA Total", f"{historical['ca_total'].sum():.2f} €")
        else:
            st.metric("Prix moyen (7j)", f"{historical['price'].tail(7).mean():.2f} €")

def main():
    """Fonction principale de l'application"""
    st.title("🏨 Optimisateur de Revenu Hôtelier")
    
    # Vérification des dépendances
    if not TABULA_AVAILABLE:
        st.warning(
            "La fonctionnalité PDF est désactivée car tabula-py n'est pas correctement installé. "
            "Veuillez installer Java pour l'activer."
        )
    
    # Sidebar pour le téléchargement de fichiers
    st.sidebar.header("Chargement des données")
    uploaded_file = st.sidebar.file_uploader(
        "Téléchargez un fichier CSV ou PDF",
        type=["csv", "pdf"]
    )
    
    # Charger les données
    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)
    else:
        # Charger des données d'exemple
        data = pd.read_csv("exemple_donnees_historiques.csv")
        st.sidebar.info("Utilisation des données d'exemple. Téléchargez vos propres données pour commencer.")
    
    if data is not None:
        # Afficher les données brutes
        st.subheader("Aperçu des données")
        st.dataframe(data.head())
        
        # Afficher les métriques
        st.subheader("Indicateurs clés")
        display_metrics(data)
        
        # Générer des prédictions
        if len(data) > 30:  # Seulement si on a assez de données
            with st.spinner("Génération des prédictions..."):
                predictions = generate_predictions(data)
                
                if predictions is not None:
                    st.subheader("Prévisions des 30 prochains jours")
                    st.line_chart(predictions.set_index('date'))
        
        # Section d'analyse avancée
        if DASHBOARD_AVAILABLE:
            st.subheader("Analyse avancée")
            try:
                dashboard = DashboardVisuals(data)
                st.plotly_chart(dashboard.create_occupancy_forecast_chart(data))
            except Exception as e:
                st.error(f"Erreur lors du chargement du tableau de bord : {str(e)}")

if __name__ == "__main__":
    main()