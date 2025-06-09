"""
Streamlit App for Hotel Revenue Optimization Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.dashboard import DashboardVisuals

# Page configuration
st.set_page_config(
    page_title="Hotel Revenue Optimizer",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
    .metric-card { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def generate_sample_data():
    """Generate sample data for demonstration"""
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
    base_price = 120
    scenarios = pd.DataFrame({
        'price': np.linspace(80, 200, 25),
    })
    scenarios['occupancy_rate'] = 1 / (1 + np.exp(0.03 * (scenarios['price'] - 140))) * 0.8 + 0.1
    scenarios['revpar'] = scenarios['price'] * scenarios['occupancy_rate']
    
    return historical, predictions, scenarios

def main():
    """Main function to run the Streamlit app"""
    st.title("🏨 Hotel Revenue Optimizer")
    st.markdown("### Tableau de bord d'optimisation des revenus")
    
    # Generate sample data
    historical, predictions, scenarios = generate_sample_data()
    
    # Create dashboard visualizations
    dashboard = DashboardVisuals()
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux d'occupation actuel", f"{historical['occupancy_rate'].iloc[-1]:.1%}")
    with col2:
        st.metric("Prix moyen", f"€{historical['price'].mean():.2f}")
    with col3:
        st.metric("RevPAR moyen", f"€{(historical['price'] * historical['occupancy_rate']).mean():.2f}")
    
    # Main charts
    st.markdown("### Prévisions d'occupation")
    st.plotly_chart(
        dashboard.create_occupancy_forecast_chart(predictions),
        use_container_width=True
    )
    
    st.markdown("### Analyse de sensibilité des prix")
    st.plotly_chart(
        dashboard.create_price_sensitivity_chart(scenarios),
        use_container_width=True
    )
    
    st.markdown("### Tendances historiques")
    st.plotly_chart(
        dashboard.create_historical_trends_chart(historical),
        use_container_width=True
    )
    
    # Sidebar with filters
    with st.sidebar:
        st.header("Paramètres")
        st.subheader("Période d'analyse")
        date_range = st.date_input(
            "Sélectionnez la plage de dates",
            value=(
                datetime.now().date() - timedelta(days=90),
                datetime.now().date()
            ),
            min_value=datetime(2023, 1, 1).date(),
            max_value=datetime(2024, 12, 31).date(),
            format="DD/MM/YYYY"
        )
        
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

if __name__ == "__main__":
    main()
