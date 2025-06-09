"""
Streamlit App for Hotel Revenue Optimization Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from src.dashboard import DashboardVisuals

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
    """Main function to run the Streamlit app"""
    st.title("🏨 Hotel Revenue Optimizer")
    st.markdown("### Tableau de bord d'optimisation des revenus")
    
    # Load data with caching
    with st.spinner('Chargement des données...'):
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
            selected_dates = st.date_input(
                "Sélectionnez la plage de dates",
                value=st.session_state.date_range,
                min_value=min_date,
                max_value=max_date,
                key="date_range_selector"
            )
            
            # Update session state if valid date range selected
            if len(selected_dates) == 2 and selected_dates[0] <= selected_dates[1]:
                st.session_state.date_range = selected_dates
            else:
                st.warning("Veuillez sélectionner une plage de dates valide")
                
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