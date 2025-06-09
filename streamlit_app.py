"""
Streamlit App for Hotel Revenue Optimization Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from src.dashboard import DashboardVisuals
import tempfile
import os
import re

try:
    from tabula import read_pdf
    TABULA_AVAILABLE = True
except ImportError:
    st.error("Erreur: tabula-py n'est pas installé. Veuillez installer Java et réessayer.")
    TABULA_AVAILABLE = False

# Configuration de la page
st.set_page_config(
    page_title="Optimisateur de Revenu Hôtelier",
    page_icon="🏨",
    layout="wide"
)

def clean_numeric_series(series):
    """Nettoie une série numérique en remplaçant les virgules par des points"""
    return series.astype(str).str.replace(',', '.').astype(float)

def parse_hotel_pdf(pdf_file):
    """Traite un fichier PDF d'hôtel et retourne un DataFrame nettoyé"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_file.getvalue())
        tmp_path = tmp.name
    
    try:
        # Lire le PDF avec des paramètres optimisés
        dfs = tabula.read_pdf(
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
    """Charge un fichier CSV téléchargé"""
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                st.error("Veuillez télécharger un fichier CSV")
                return None
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {str(e)}")
        return None

def generate_predictions(historical, days=30):
    """Génère des prédictions basées sur les données historiques"""
    last_date = historical['date'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)
    
    # Simulation simple basée sur la moyenne mobile
    avg_occupancy = historical['occupancy_rate'].mean()
    std_occupancy = historical['occupancy_rate'].std()
    
    predictions = pd.DataFrame({
        'date': future_dates,
        'predicted_occupancy': np.random.normal(avg_occupancy, std_occupancy/3, days).clip(0.3, 0.95),
        'lower_bound': 0,
        'upper_bound': 0
    })
    
    # Ajouter des bornes pour l'intervalle de confiance
    predictions['lower_bound'] = (predictions['predicted_occupancy'] * 0.9).clip(0.3, 0.95)
    predictions['upper_bound'] = (predictions['predicted_occupancy'] * 1.1).clip(0.3, 0.95)
    
    return predictions

def generate_scenarios(historical):
    """Génère des scénarios de tarification basés sur les données historiques"""
    avg_price = historical['price'].mean()
    min_price = max(50, avg_price * 0.6)
    max_price = min(300, avg_price * 1.5)
    
    scenarios = pd.DataFrame({
        'price': np.linspace(min_price, max_price, 25).round(2),
    })
    
    # Modèle de sensibilité aux prix simplifié
    scenarios['occupancy_rate'] = 1 / (1 + np.exp(0.03 * (scenarios['price'] - avg_price))) * 0.8 + 0.1
    scenarios['revpar'] = scenarios['price'] * scenarios['occupancy_rate']
    
    return scenarios

def display_metrics(historical, occupancy_threshold, price_threshold):
    """Affiche les indicateurs clés avec des seuils d'alerte"""
    if historical.empty:
        st.warning("Aucune donnée historique disponible")
        return
        
    # S'assurer que nous avons les bonnes colonnes
    has_occupancy = 'occupancy_rate' in historical.columns or 'taux_occupation' in historical.columns
    has_price = 'price' in historical.columns or 'prix_moyen' in historical.columns
    
    if not has_occupancy or not has_price:
        st.error("Les données ne contiennent pas toutes les colonnes requises")
        return
    
    # Utiliser les noms de colonnes appropriés
    occupancy_col = 'taux_occupation' if 'taux_occupation' in historical.columns else 'occupancy_rate'
    price_col = 'prix_moyen' if 'prix_moyen' in historical.columns else 'price'
    
    # Calculer les métriques
    current_occupancy = historical[occupancy_col].iloc[-1] * 100  # Convertir en pourcentage
    avg_price = historical[price_col].mean()
    
    # Calculer le RevPAR (Revenu par chambre disponible)
    if 'ca_total' in historical.columns and 'chambres_totales' in historical.columns:
        avg_revpar = (historical['ca_total'] / historical['chambres_totales']).mean()
    else:
        avg_revpar = avg_price * (current_occupancy / 100)
    
    # Vérifier les seuils d'alerte
    occupancy_alert = current_occupancy < occupancy_threshold
    price_alert = avg_price < price_threshold
    
    # Afficher les métriques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Taux d'occupation actuel", 
            f"{current_occupancy:.1f}%",
            delta=None,
            delta_color="inverse" if occupancy_alert else "normal",
            help=f"Seuil d'alerte: {occupancy_threshold}%"
        )
    
    with col2:
        st.metric(
            "Prix moyen", 
            f"€{avg_price:.2f}",
            delta=None,
            delta_color="inverse" if price_alert else "normal",
            help=f"Seuil minimum: €{price_threshold:.2f}"
        )
    
    with col3:
        st.metric("RevPAR moyen", f"€{avg_revpar:.2f}")

def main():
    """Fonction principale pour exécuter l'application Streamlit"""
    st.title("🏨 Optimisateur de Revenu Hôtelier")
    st.markdown("### Tableau de bord d'optimisation des revenus")
    
    # Section de téléchargement de fichier
    st.sidebar.header("Charger des données")
    
    # Option pour choisir entre CSV et PDF
    data_source = st.sidebar.radio(
        "Source des données",
        ["Données d'exemple", "Fichier CSV", "Fichier PDF"]
    )
    
    if data_source == "Fichier PDF":
        uploaded_file = st.sidebar.file_uploader(
            "Téléchargez votre fichier PDF",
            type=["pdf"],
            help="Sélectionnez un fichier PDF d'extraction hôtelière"
        )
        
        if uploaded_file is not None:
            with st.spinner('Traitement du PDF...'):
                historical = parse_hotel_pdf(uploaded_file)
                if historical is not None and not historical.empty:
                    st.success("Données chargées avec succès depuis le PDF !")
                    st.dataframe(historical.head())
                    
                    # Afficher des statistiques
                    st.subheader("Statistiques des données chargées")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Période", f"{historical['date'].min().strftime('%d/%m/%Y')} - {historical['date'].max().strftime('%d/%m/%Y')}")
                    with col2:
                        st.metric("Prix moyen", f"€{historical['price'].mean():.2f}")
                    with col3:
                        st.metric("Taux d'occupation moyen", f"{historical['occupancy_rate'].mean()*100:.1f}%")
                    
                    # Générer des prédictions
                    predictions = generate_predictions(historical)
                    scenarios = generate_scenarios(historical)
                else:
                    st.warning("Impossible de lire le PDF. Utilisation des données d'exemple.")
                    historical, predictions, scenarios = load_data()
        else:
            st.info("Veuillez télécharger un fichier PDF ou sélectionner une autre source de données.")
            return
            
    elif data_source == "Fichier CSV":
        uploaded_file = st.sidebar.file_uploader(
            "Téléchargez votre fichier CSV",
            type=["csv"],
            help="Le fichier doit contenir des colonnes pour la date, le prix et le taux d'occupation"
        )
        
        if uploaded_file is not None:
            historical = load_uploaded_file(uploaded_file)
            if historical is None or historical.empty:
                st.warning("Utilisation des données d'exemple")
                historical, predictions, scenarios = load_data()
            else:
                # Vérifier les colonnes requises
                required_columns = {'date', 'price', 'occupancy_rate'}
                if not required_columns.issubset(historical.columns):
                    st.error("Le fichier doit contenir les colonnes: date, price, occupancy_rate")
                    st.stop()
                    
                # Créer des prédictions basées sur les données chargées
                predictions = generate_predictions(historical)
                scenarios = generate_scenarios(historical)
        else:
            st.info("Aucun fichier chargé. Utilisation des données d'exemple.")
            historical, predictions, scenarios = load_data()
            
    else:  # Données d'exemple
        st.info("Utilisation des données d'exemple.")
        historical, predictions, scenarios = load_data()
    
    # Afficher les métriques
    st.sidebar.subheader("Seuils d'alerte")
    occupancy_threshold = st.sidebar.slider(
        "Seuil d'occupation critique (%)",
        min_value=0,
        max_value=100,
        value=60,
        step=5
    )
    
    price_threshold = st.sidebar.slider(
        "Seuil de prix minimum (€)",
        min_value=50,
        max_value=200,
        value=100,
        step=5
    )
    
    # Afficher les indicateurs clés
    display_metrics(historical, occupancy_threshold, price_threshold)
    
    # Créer les visualisations
    dashboard = DashboardVisuals()
    
    # Afficher les graphiques
    if not historical.empty:
        st.subheader("Évolution des indicateurs clés")
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique d'évolution du prix
            fig_price = px.line(
                historical, 
                x='date', 
                y='price',
                title='Évolution du prix moyen',
                labels={'price': 'Prix (€)', 'date': 'Date'}
            )
            st.plotly_chart(fig_price, use_container_width=True)
            
        with col2:
            # Graphique d'évolution du taux d'occupation
            fig_occ = px.line(
                historical, 
                x='date', 
                y='occupancy_rate',
                title="Taux d'occupation",
                labels={'occupancy_rate': "Taux d'occupation", 'date': 'Date'}
            )
            fig_occ.update_yaxes(tickformat=".0%")
            st.plotly_chart(fig_occ, use_container_width=True)
        
        # Graphique de prévisions
        if predictions is not None and not predictions.empty:
            st.subheader("Prévisions d'occupation")
            fig_forecast = go.Figure()
            
            # Ajouter les données historiques
            fig_forecast.add_trace(go.Scatter(
                x=historical['date'],
                y=historical['occupancy_rate'],
                name='Historique',
                mode='lines+markers'
            ))
            
            # Ajouter les prévisions
            fig_forecast.add_trace(go.Scatter(
                x=predictions['date'],
                y=predictions['predicted_occupancy'],
                name='Prévision',
                mode='lines+markers',
                line=dict(color='orange')
            ))
            
            # Ajouter l'intervalle de confiance
            fig_forecast.add_trace(go.Scatter(
                x=pd.concat([predictions['date'], predictions['date'][::-1]]),
                y=pd.concat([predictions['upper_bound'], predictions['lower_bound'][::-1]]),
                fill='toself',
                fillcolor='rgba(255,165,0,0.2)',
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip"
            ))
            
            fig_forecast.update_layout(
                yaxis_title="Taux d'occupation",
                yaxis_tickformat=".0%",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Graphique de sensibilité des prix
        if scenarios is not None and not scenarios.empty:
            st.subheader("Analyse de sensibilité des prix")
            fig_sensitivity = px.line(
                scenarios, 
                x='price', 
                y=['occupancy_rate', 'revpar'],
                title="Impact du prix sur l'occupation et le revenu",
                labels={'value': 'Valeur', 'price': 'Prix (€)'}
            )
            
            fig_sensitivity.update_layout(
                yaxis2=dict(
                    title="Revenu par chambre (€)",
                    overlaying="y",
                    side="right",
                    showgrid=False
                ),
                yaxis=dict(
                    title="Taux d'occupation",
                    side="left",
                    tickformat=".0%"
                )
            )
            
            st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    else:
        st.warning("Aucune donnée à afficher")

if __name__ == "__main__":
    main()