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