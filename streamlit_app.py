"""
Streamlit App for Hotel Revenue Optimization Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from src.dashboard import DashboardVisuals

# Configuration de la page
st.set_page_config(
    page_title="Optimisateur de Revenu Hôtelier",
    page_icon="🏨",
    layout="wide"
)

def load_uploaded_file(uploaded_file):
    """Charge un fichier CSV téléchargé"""
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                # Convertir la colonne date en datetime si elle existe
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

# Enable caching for better performance
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def load_data():
    return generate_sample_data()

def generate_sample_data():
    """Generate sample data for demonstration with error handling"""
    try:
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=90)
        
        # Historical data
        historical = pd.DataFrame({
            'date': dates[:-30],
            'price': np.random.normal(120, 20, 60).clip(80, 200),
            'occupancy_rate': np.random.beta(3, 2, 60).clip(0.3, 0.95)
        })
        
        # Predictions
        future_dates = pd.date_range(start=dates[-30], periods=30)
        predictions = pd.DataFrame({
            'date': future_dates,
            'predicted_occupancy': np.linspace(0.7, 0.9, 30) + np.random.normal(0, 0.05, 30),
            'lower_bound': np.linspace(0.6, 0.85, 30) + np.random.normal(0, 0.03, 30),
            'upper_bound': np.linspace(0.8, 0.95, 30) + np.random.normal(0, 0.03, 30)
        })
        
        # Price sensitivity scenarios
        scenarios = pd.DataFrame({
            'price': np.linspace(80, 200, 25),
        })
        scenarios['occupancy_rate'] = 1 / (1 + np.exp(0.03 * (scenarios['price'] - 140))) * 0.8 + 0.1
        scenarios['revpar'] = scenarios['price'] * scenarios['occupancy_rate']
        
        return historical, predictions, scenarios
        
    except Exception as e:
        st.error(f"Error generating sample data: {str(e)}")
        # Return empty dataframes in case of error
        empty_df = pd.DataFrame()
        return empty_df, empty_df, empty_df

def display_metrics(historical, occupancy_threshold, price_threshold):
    """Display key metrics with threshold indicators"""
    if historical.empty:
        st.warning("No historical data available")
        return
        
    current_occupancy = historical['occupancy_rate'].iloc[-1]
    avg_price = historical['price'].mean()
    avg_revpar = (historical['price'] * historical['occupancy_rate']).mean()
    
    # Check thresholds
    occupancy_alert = current_occupancy < (occupancy_threshold / 100)
    price_alert = avg_price < price_threshold
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Taux d'occupation actuel", 
            f"{current_occupancy:.1%}",
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
            help=f"Seuil minimum: €{price_threshold}"
        )
    
    with col3:
        st.metric("RevPAR moyen", f"€{avg_revpar:.2f}")

def main():
    """Fonction principale pour exécuter l'application Streamlit"""
    st.title("🏨 Optimisateur de Revenu Hôtelier")
    st.markdown("### Tableau de bord d'optimisation des revenus")
    
    # Section de téléchargement de fichier
    st.sidebar.header("Charger des données")
    uploaded_file = st.sidebar.file_uploader(
        "Téléchargez votre fichier de données (CSV)",
        type=["csv"],
        help="Le fichier doit contenir des colonnes pour la date, le prix et le taux d'occupation"
    )
    
    # Charger les données (soit depuis le fichier, soit des données d'exemple)
    with st.spinner('Chargement des données...'):
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
    
    # Create dashboard visualizations
    dashboard = DashboardVisuals()
    
    # Sidebar with filters
    with st.sidebar:
        st.header("Paramètres")
        
        # Date range filter
        st.subheader("Période d'analyse")
        
        # Define date constants
        min_date = datetime(2023, 1, 1).date()
        max_date = datetime(2024, 12, 31).date()
        today = datetime.now().date()
        
        # Set default date range (last 90 days, but within min/max)
        default_start = max(min_date, today - timedelta(days=90))
        default_end = min(max_date, today)
        
        # Initialize session state for date range if not exists
        if 'date_range' not in st.session_state:
            st.session_state.date_range = (default_start, default_end)
        
        # Date input widget
        try:
            # Get the current date range from session state
            current_start, current_end = st.session_state.date_range
            
            # Ensure the current range is within bounds
            current_start = max(min_date, min(current_start, max_date))
            current_end = min(max_date, max(current_end, min_date))
            if current_start > current_end:
                current_start, current_end = default_start, default_end
            
            # Update session state with validated dates
            st.session_state.date_range = (current_start, current_end)
            
            # Create the date input with the validated range
            selected_dates = st.date_input(
                "Sélectionnez la plage de dates",
                value=st.session_state.date_range,
                min_value=min_date,
                max_value=max_date,
                key="date_range_selector"
            )
            
            # Update session state if valid date range selected
            if len(selected_dates) == 2:
                if selected_dates[0] <= selected_dates[1]:
                    st.session_state.date_range = selected_dates
                else:
                    st.warning("La date de fin doit être postérieure à la date de début")
                    st.session_state.date_range = (default_start, default_end)
            else:
                st.warning("Veuillez sélectionner une plage de dates valide")
                st.session_state.date_range = (default_start, default_end)
                
        except Exception as e:
            st.error(f"Erreur lors de la sélection de la date: {str(e)}")
            st.session_state.date_range = (default_start, default_end)
        
        # Use the date range from session state
        date_range = st.session_state.date_range
        
        st.subheader("Seuils d'alerte")
        occupancy_threshold = st.slider(
            "Seuil d'occupation critique (%)",
            min_value=50,
            max_value=100,
            value=80,
            step=5
        )
        
        price_threshold = st.slider(
            "Seuil de prix minimum (€)",
            min_value=50,
            max_value=200,
            value=100,
            step=5
        )
    
    # Display metrics with error handling
    try:
        display_metrics(historical, occupancy_threshold, price_threshold)
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des métriques: {str(e)}")
    
    # Display charts with error handling
    try:
        if not predictions.empty:
            st.markdown("### Prévisions d'occupation")
            st.plotly_chart(
                dashboard.create_occupancy_forecast_chart(predictions),
                use_container_width=True
            )
        
        if not scenarios.empty:
            st.markdown("### Analyse de sensibilité des prix")
            st.plotly_chart(
                dashboard.create_price_sensitivity_chart(scenarios),
                use_container_width=True
            )
        
        if not historical.empty:
            st.markdown("### Tendances historiques")
            st.plotly_chart(
                dashboard.create_historical_trends_chart(historical),
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des graphiques: {str(e)}")

if __name__ == "__main__":
    main()