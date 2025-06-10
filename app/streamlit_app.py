"""
Application Streamlit pour l'optimisation des revenus hôteliers
"""
import os
import re
import tempfile
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Configuration de la page - DOIT ÊTRE LA PREMIÈRE COMMANDE
st.set_page_config(
    page_title="Optimisateur de Revenu Hôtelier",
    page_icon="🏨",
    layout="wide"
)

# Vérification des dépendances
try:
    from tabula import read_pdf
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    st.warning("La fonctionnalité PDF est désactivée. Installez tabula-py pour l'activer.")

# Vérification du tableau de bord
try:
    from src.dashboard import DashboardVisuals
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    DASHBOARD_AVAILABLE = False
    st.warning(f"Tableau de bord non disponible : {str(e)}")

def clean_numeric_series(series):
    """Nettoie une série numérique en remplaçant les virgules par des points."""
    if pd.api.types.is_numeric_dtype(series):
        return series
    return pd.to_numeric(
        series.astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    )

def parse_hotel_pdf(pdf_file):
    """Traite un fichier PDF d'hôtel et retourne un DataFrame nettoyé."""
    if not TABULA_AVAILABLE:
        st.error("Erreur: tabula-py n'est pas disponible. Impossible de traiter les fichiers PDF.")
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_file.getvalue())
        tmp_path = tmp.name
    
    try:
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
        
        df = pd.concat(dfs, ignore_index=True)
        df = df.dropna(how='all').reset_index(drop=True)
        
        processed_data = {
            'date': [],
            'price': [],
            'occupancy_rate': [],
            'chambres_occupees': [],
            'chambres_totales': [],
            'ca_total': []
        }
        
        for _, row in df.iterrows():
            row_str = ' '.join([str(cell) for cell in row if str(cell) != 'nan'])
            if not row_str.strip():
                continue
                
            date_match = re.search(r'(\d{2}\.\d{2}\.\d{2,4})', row_str)
            if not date_match:
                continue
                
            try:
                date_str = date_match.group(1)
                date = pd.to_datetime(date_str, dayfirst=True).date()
                
                numbers = re.findall(r'(\d+[\.,]?\d*)', row_str)
                numbers = [float(n.replace(',', '.')) for n in numbers if n.replace(',', '').replace('.', '').isdigit()]
                
                if len(numbers) >= 12:
                    processed_data['date'].append(date)
                    processed_data['chambres_occupees'].append(numbers[6])
                    processed_data['chambres_totales'].append(numbers[7])
                    processed_data['occupancy_rate'].append(numbers[8] / 100)  # Convertir en décimal
                    processed_data['price'].append(numbers[10])
                    processed_data['ca_total'].append(numbers[11])
                    
            except Exception as e:
                print(f"Ligne ignorée: {row_str}")
                continue
                
        result_df = pd.DataFrame(processed_data)
        
        if result_df.empty:
            st.error("Aucune donnée valide trouvée dans le PDF")
            return None
            
        return result_df
        
    except Exception as e:
        st.error(f"Erreur lors du traitement du PDF : {str(e)}")
        return None
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def load_uploaded_file(uploaded_file):
    """Charge un fichier CSV ou PDF téléchargé."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
                df = df.dropna(subset=['date'])
            return df
        elif uploaded_file.name.endswith('.pdf'):
            return parse_hotel_pdf(uploaded_file)
        else:
            st.error("Format de fichier non supporté. Veuillez télécharger un fichier CSV ou PDF.")
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {str(e)}")
        return None

def generate_predictions(historical, days=30):
    """Génère des prédictions basées sur les données historiques."""
    try:
        df = historical.copy()
        
        required_cols = ['date', 'price', 'occupancy_rate']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colonnes manquantes : {', '.join(missing_cols)}")
            
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if df['date'].isnull().any():
            st.warning("Certaines dates n'ont pas pu être converties")
            df = df.dropna(subset=['date'])
            
        if df.empty:
            raise ValueError("Aucune date valide trouvée")
            
        df = df.sort_values('date')
        last_date = df['date'].max()
        
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=days,
            name='date'
        )
        
        avg_price = df['price'].mean()
        std_price = max(df['price'].std() * 0.15, avg_price * 0.05)
        
        avg_occupancy = df['occupancy_rate'].mean()
        std_occupancy = min(0.1, avg_occupancy * 0.3)
        
        np.random.seed(42)
        
        trend_window = min(7, len(df))
        price_trend = df['price'].iloc[-trend_window:].pct_change().mean() or 0
        occupancy_trend = df['occupancy_rate'].iloc[-trend_window:].diff().mean() or 0
        
        price_pred = []
        occupancy_pred = []
        
        for i in range(days):
            trend_factor = 1 + (price_trend * (i + 1) / days)
            price = np.random.normal(avg_price * trend_factor, std_price)
            price = max(avg_price * 0.5, min(price, avg_price * 2))
            price_pred.append(price)
            
            trend = occupancy_trend * (i + 1) / days
            occupancy = np.random.normal(avg_occupancy + trend, std_occupancy)
            occupancy = max(0.05, min(0.99, occupancy))
            occupancy_pred.append(occupancy)
        
        predictions = pd.DataFrame({
            'date': future_dates,
            'price': price_pred,
            'occupancy_rate': occupancy_pred
        })
        
        predictions['date'] = pd.to_datetime(predictions['date'])
        return predictions
        
    except Exception as e:
        st.error(f"Erreur lors de la génération des prédictions : {str(e)}")
        return None

def display_metrics(historical):
    """Affiche les indicateurs clés."""
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

def run_app():
    """Fonction principale de l'application."""
    st.title("🏨 Optimisateur de Revenu Hôtelier")
    
    # Sidebar pour le téléchargement de fichiers
    with st.sidebar:
        st.header("Chargement des données")
        uploaded_file = st.file_uploader(
            "Téléchargez un fichier CSV ou PDF",
            type=["csv", "pdf"]
        )
    
    # Charger les données
    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)
    else:
        # Charger des données d'exemple
        try:
            data = pd.read_csv("exemple_donnees_historiques.csv")
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'], errors='coerce')
                data = data.dropna(subset=['date'])
            st.sidebar.info("Utilisation des données d'exemple. Téléchargez vos propres données pour commencer.")
        except Exception as e:
            st.error(f"Erreur lors du chargement des données d'exemple : {str(e)}")
            return
    
    if data is not None and not data.empty:
        st.subheader("Aperçu des données")
        st.dataframe(data.head())
        
        st.subheader("Indicateurs clés")
        display_metrics(data)
        
        if len(data) > 7:
            with st.spinner("Génération des prédictions..."):
                predictions = generate_predictions(data)
                
                if predictions is not None and not predictions.empty:
                    st.subheader("Prévisions des 30 prochains jours")
                    
                    # Créer un graphique avec deux axes y
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    
                    # Ajouter les prédictions de prix
                    fig.add_trace(
                        go.Scatter(
                            x=predictions['date'],
                            y=predictions['price'],
                            name='Prix moyen (€)',
                            line=dict(color='blue')
                        ),
                        secondary_y=False
                    )
                    
                    # Ajouter les prédictions de taux d'occupation
                    fig.add_trace(
                        go.Scatter(
                            x=predictions['date'],
                            y=predictions['occupancy_rate'] * 100,
                            name="Taux d'occupation (%)",
                            line=dict(color='red')
                        ),
                        secondary_y=True
                    )
                    
                    # Mise en forme du graphique
                    fig.update_layout(
                        title="Prévisions des prix et du taux d'occupation",
                        xaxis_title="Date",
                        yaxis_title="Prix moyen (€)",
                        yaxis2_title="Taux d'occupation (%)",
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    # Configuration des axes
                    fig.update_yaxes(
                        title_font=dict(color="blue"),
                        tickfont=dict(color="blue"),
                        secondary_y=False
                    )
                    fig.update_yaxes(
                        title_font=dict(color="red"),
                        tickfont=dict(color="red"),
                        secondary_y=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # Section d'analyse avancée
        if DASHBOARD_AVAILABLE:
            st.subheader("Analyse avancée")
            try:
                if 'occupancy_rate' in data.columns:
                    dashboard_data = data[['date', 'occupancy_rate']].copy()
                    dashboard_data = dashboard_data.rename(columns={'occupancy_rate': 'predicted_occupancy'})
                    
                    mean_occ = dashboard_data['predicted_occupancy'].mean()
                    std_occ = dashboard_data['predicted_occupancy'].std()
                    
                    dashboard_data['lower_bound'] = dashboard_data['predicted_occupancy'] - std_occ * 0.5
                    dashboard_data['upper_bound'] = dashboard_data['predicted_occupancy'] + std_occ * 0.5
                    
                    dashboard = DashboardVisuals()
                    st.plotly_chart(dashboard.create_occupancy_forecast_chart(dashboard_data))
            except Exception as e:
                st.error(f"Erreur lors du chargement du tableau de bord : {str(e)}")
    else:
        st.warning("Aucune donnée à afficher. Veuillez charger un fichier valide.")

if __name__ == "__main__":
    run_app()