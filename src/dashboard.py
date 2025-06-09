"""
Module de visualisation pour le tableau de bord de revenue management
Auteur: David Michel-Larrieux
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

class DashboardVisuals:
    """
    Classe pour générer les visualisations du tableau de bord
    """
    
    @staticmethod
    def create_occupancy_forecast_chart(predictions):
        """
        Crée un graphique de prévision d'occupation avec intervalle de confiance
        
        Args:
            predictions (pd.DataFrame): DataFrame avec colonnes date, predicted_occupancy, lower_bound, upper_bound
            
        Returns:
            plotly.graph_objects.Figure: Figure Plotly
        """
        fig = go.Figure()
        
        # Zone de confiance
        fig.add_trace(go.Scatter(
            x=predictions['date'],
            y=predictions['upper_bound']*100,
            fill=None,
            mode='lines',
            line_color='rgba(0,100,80,0.2)',
            name='Borne supérieure',
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=predictions['date'],
            y=predictions['lower_bound']*100,
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,80,0.2)',
            name='Intervalle de confiance',
            fillcolor='rgba(31,119,180,0.2)'
        ))
        
        # Prédiction centrale
        fig.add_trace(go.Scatter(
            x=predictions['date'],
            y=predictions['predicted_occupancy']*100,
            mode='lines+markers',
            name='Occupation prédite',
            line=dict(color='#1f77b4', width=3)
        ))
        
        # Ligne à 80% d'occupation (seuil d'alerte)
        fig.add_hline(
            y=80,
            line_dash="dash",
            line_color="red",
            annotation_text="Seuil d'alerte (80%)",
            annotation_position="bottom right"
        )
        
        fig.update_layout(
            title="Prévision d'occupation sur 30 jours",
            xaxis_title="Date",
            yaxis_title="Taux d'occupation (%)",
            hovermode='x unified',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def create_price_sensitivity_chart(scenarios):
        """
        Crée un graphique de sensibilité prix/occupation/revpar
        
        Args:
            scenarios (pd.DataFrame): Résultats de l'analyse de scénarios
            
        Returns:
            plotly.graph_objects.Figure: Figure Plotly avec deux sous-graphiques
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('RevPAR vs Prix', 'Occupation vs Prix'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Graphique RevPAR
        fig.add_trace(
            go.Scatter(
                x=scenarios['price'],
                y=scenarios['revpar'],
                mode='lines+markers',
                name='RevPAR',
                line=dict(color='green', width=3)
            ),
            row=1, col=1
        )
        
        # Point de RevPAR maximum
        optimal_idx = scenarios['revpar'].idxmax()
        fig.add_trace(
            go.Scatter(
                x=[scenarios.loc[optimal_idx, 'price']],
                y=[scenarios.loc[optimal_idx, 'revpar']],
                mode='markers',
                marker=dict(size=15, color='red', symbol='star'),
                name='Optimum RevPAR'
            ),
            row=1, col=1
        )
        
        # Graphique Occupation
        fig.add_trace(
            go.Scatter(
                x=scenarios['price'],
                y=scenarios['occupancy_rate']*100,
                mode='lines+markers',
                name='Occupation %',
                line=dict(color='blue', width=3)
            ),
            row=1, col=2
        )
        
        # Mise en forme
        fig.update_xaxes(title_text="Prix (€)")
        fig.update_yaxes(title_text="RevPAR (€)", row=1, col=1)
        fig.update_yaxes(title_text="Occupation (%)", row=1, col=2)
        
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.1,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
    
    @staticmethod
    def create_historical_trends_chart(historical_data):
        """
        Crée un graphique des tendances historiques
        
        Args:
            historical_data (pd.DataFrame): Données historiques avec colonnes date, price, occupancy_rate
            
        Returns:
            plotly.graph_objects.Figure: Figure Plotly avec plusieurs sous-graphiques
        """
        df = historical_data.copy()
        df['revpar'] = df['price'] * df['occupancy_rate']
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Prix (€)', 'Occupation (%)', 'RevPAR (€)'),
            vertical_spacing=0.08,
            shared_xaxes=True
        )
        
        # Prix
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='lines',
                name='Prix',
                line=dict(color='green')
            ),
            row=1, col=1
        )
        
        # Ligne de moyenne mobile sur 7 jours pour le prix
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['price'].rolling(window=7).mean(),
                mode='lines',
                name='Moyenne mobile (7j)',
                line=dict(color='red', dash='dash')
            ),
            row=1, col=1
        )
        
        # Occupation
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['occupancy_rate']*100,
                mode='lines',
                name='Occupation',
                line=dict(color='blue')
            ),
            row=2, col=1
        )
        
        # Ligne de moyenne mobile sur 7 jours pour l'occupation
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['occupancy_rate'].rolling(window=7).mean()*100,
                mode='lines',
                name='Moyenne mobile (7j)',
                line=dict(color='orange', dash='dash'),
                showlegend=False
            ),
            row=2, col=1
        )
        
        # RevPAR
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['revpar'],
                mode='lines',
                name='RevPAR',
                line=dict(color='purple')
            ),
            row=3, col=1
        )
        
        # Ligne de moyenne mobile sur 7 jours pour le RevPAR
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['revpar'].rolling(window=7).mean(),
                mode='lines',
                name='Moyenne mobile (7j)',
                line=dict(color='red', dash='dash'),
                showlegend=False
            ),
            row=3, col=1
        )
        
        # Mise en forme
        fig.update_layout(
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Mise à jour des axes y
        fig.update_yaxes(title_text="Prix (€)", row=1, col=1)
        fig.update_yaxes(title_text="Occupation (%)", row=2, col=1)
        fig.update_yaxes(title_text="RevPAR (€)", row=3, col=1)
        
        return fig
    
    @staticmethod
    def create_weekly_heatmap(historical_data):
        """
        Crée une heatmap de l'occupation par jour de la semaine et par mois
        
        Args:
            historical_data (pd.DataFrame): Données historiques avec colonne date et occupancy_rate
            
        Returns:
            plotly.graph_objects.Figure: Figure Plotly
        """
        df = historical_data.copy()
        
        # Extraction du jour de la semaine et du mois
        df['day_of_week'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.month_name()
        
        # Ordre des jours et des mois
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        # Agrégation des données
        heatmap_data = df.groupby(['month', 'day_of_week'])['occupancy_rate'].mean().reset_index()
        heatmap_data['occupancy_pct'] = (heatmap_data['occupancy_rate'] * 100).round(1)
        
        # Création de la heatmap
        fig = px.imshow(
            heatmap_data.pivot(
                index='month', 
                columns='day_of_week', 
                values='occupancy_pct'
            ).reindex(index=month_order, columns=day_order),
            labels=dict(x="Jour de la semaine", y="Mois", color="Occupation (%)"),
            aspect="auto",
            color_continuous_scale='Viridis'
        )
        
        # Ajout des valeurs dans les cellules
        for i, row in enumerate(month_order):
            for j, col in enumerate(day_order):
                value = heatmap_data[
                    (heatmap_data['month'] == row) & 
                    (heatmap_data['day_of_week'] == col)
                ]['occupancy_pct'].values
                if len(value) > 0:
                    fig.add_annotation(
                        x=j, y=i,
                        text=f"{value[0]:.0f}%",
                        showarrow=False,
                        font=dict(color='white' if value[0] > 50 else 'black', size=10)
                    )
        
        # Mise en forme
        fig.update_layout(
            title="Heatmap d'occupation par jour et par mois",
            xaxis_title="Jour de la semaine",
            yaxis_title="Mois",
            height=600
        )
        
        return fig

# Exemple d'utilisation
if __name__ == "__main__":
    # Génération de données d'exemple
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    
    # Simulation de données réalistes
    data = []
    for date in dates:
        # Tendance saisonnière
        seasonal = 0.65 + 0.20 * np.sin(2 * np.pi * date.month / 12)
        # Effet week-end
        weekend_boost = 0.15 if date.weekday() >= 5 else 0
        # Bruit aléatoire
        noise = np.random.normal(0, 0.05)
        
        occupancy = np.clip(seasonal + weekend_boost + noise, 0.1, 0.98)
        base_price = 100 + 30 * seasonal + 20 * weekend_boost
        price = base_price + np.random.normal(0, 10)
        
        data.append({
            'date': date,
            'occupancy_rate': occupancy,
            'price': max(80, min(200, price))
        })
    
    df = pd.DataFrame(data)
    
    # Création des graphiques
    dashboard = DashboardVisuals()
    
    # Exemple de prévision (simulée)
    future_dates = pd.date_range('2024-01-01', periods=30, freq='D')
    predictions = pd.DataFrame({
        'date': future_dates,
        'predicted_occupancy': 0.7 + 0.1 * np.sin(np.linspace(0, 6, 30)),
        'lower_bound': 0.6 + 0.1 * np.sin(np.linspace(0, 6, 30)) - 0.1,
        'upper_bound': 0.6 + 0.1 * np.sin(np.linspace(0, 6, 30)) + 0.1
    })
    
    # Affichage des graphiques
    fig1 = dashboard.create_occupancy_forecast_chart(predictions)
    fig1.show()
    
    # Exemple d'analyse de scénarios (simulée)
    prices = np.linspace(80, 200, 50)
    scenarios = pd.DataFrame({
        'price': prices,
        'occupancy_rate': 0.9 * (1 - 0.5 * ((prices - 140) / 60) ** 2) + np.random.normal(0, 0.02, 50),
        'revpar': prices * (0.9 * (1 - 0.5 * ((prices - 140) / 60) ** 2) + np.random.normal(0, 0.02, 50))
    })
    
    fig2 = dashboard.create_price_sensitivity_chart(scenarios)
    fig2.show()
    
    fig3 = dashboard.create_historical_trends_chart(df)
    fig3.show()
    
    fig4 = dashboard.create_weekly_heatmap(df)
    fig4.show()
