"""
Tests unitaires pour le module dashboard.py
"""
import sys
import unittest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dashboard import DashboardVisuals
from src.config import PLOT_PARAMS

class TestDashboardVisuals(unittest.TestCase):
    """Classe de tests pour DashboardVisuals"""
    
    @classmethod
    def setUpClass(cls):
        """Configuration avant tous les tests"""
        # Créer des données de test
        cls.create_test_data()
    
    @classmethod
    def create_test_data(cls):
        """Créer des données de test pour les visualisations"""
        # Créer une plage de dates pour les 30 prochains jours
        end_date = datetime.now() + timedelta(days=30)
        dates = pd.date_range(end=end_date, periods=30, freq='D')
        
        # Données de prédiction
        np.random.seed(42)
        predictions = np.clip(0.4 + 0.4 * np.sin(2 * np.pi * np.arange(30) / 15) + 
                            np.random.normal(0, 0.1, 30), 0, 1)
        
        # Créer le DataFrame de prédictions
        cls.predictions_df = pd.DataFrame({
            'date': dates,
            'predicted_occupancy_rate': predictions,
            'lower_bound': np.clip(predictions - 0.1, 0, 1),
            'upper_bound': np.clip(predictions + 0.1, 0, 1)
        })
        
        # Données historiques (6 mois)
        hist_dates = pd.date_range(end=dates[0] - timedelta(days=1), periods=180, freq='D')
        hist_occupancy = np.clip(0.4 + 0.4 * np.sin(2 * np.pi * np.arange(180) / 30) + 
                                np.random.normal(0, 0.1, 180), 0, 1)
        
        cls.historical_df = pd.DataFrame({
            'date': hist_dates,
            'occupancy_rate': hist_occupancy,
            'price': 100 + 50 * np.sin(2 * np.pi * np.arange(180) / 60) + 
                    np.random.normal(0, 10, 180)
        })
        
        # Données de sensibilité aux prix
        prices = np.linspace(80, 250, 20)
        demands = np.clip(1.5 - 0.002 * prices + np.random.normal(0, 0.05, 20), 0.2, 1.2)
        
        cls.price_sensitivity_df = pd.DataFrame({
            'price': prices,
            'demand': demands,
            'revenue': prices * demands
        })
    
    def test_create_occupancy_forecast_chart(self):
        """Teste la création du graphique de prévision d'occupation"""
        # Créer le graphique
        fig = DashboardVisuals.create_occupancy_forecast_chart(
            self.predictions_df,
            'Prévision du taux d\'occupation',
            'rgba(30, 136, 229, 0.8)',
            'rgba(30, 136, 229, 0.2)'
        )
        
        # Vérifier le type de retour
        self.assertIsInstance(fig, go.Figure)
        
        # Vérifier les données du graphique
        self.assertEqual(len(fig.data), 3)  # Ligne principale + deux bandes d'incertitude
        
        # Vérifier les titres
        self.assertIn('Prévision du taux d\'occupation', fig.layout.title.text)
        self.assertEqual(fig.layout.xaxis.title.text, 'Date')
        self.assertEqual(fig.layout.yaxis.title.text, 'Taux d\'occupation')
        
        # Vérifier les couleurs
        self.assertIn('rgba(30, 136, 229, 0.8)', str(fig.to_dict()))
    
    def test_create_price_sensitivity_chart(self):
        """Teste la création du graphique de sensibilité aux prix"""
        # Créer le graphique
        fig = DashboardVisuals.create_price_sensitivity_chart(
            self.price_sensitivity_df,
            'Sensibilité de la demande au prix',
            'Prix',
            'Demande'
        )
        
        # Vérifier le type de retour
        self.assertIsInstance(fig, go.Figure)
        
        # Vérifier les données du graphique
        self.assertGreater(len(fig.data), 0)
        
        # Vérifier les titres
        self.assertEqual(fig.layout.title.text, 'Sensibilité de la demande au prix')
        self.assertEqual(fig.layout.xaxis.title.text, 'Prix')
        self.assertEqual(fig.layout.yaxis.title.text, 'Demande')
    
    def test_create_historical_trends_chart(self):
        """Teste la création du graphique des tendances historiques"""
        # Créer le graphique
        fig = DashboardVisuals.create_historical_trends_chart(
            self.historical_df,
            'Tendances historiques du taux d\'occupation',
            'Taux d\'occupation',
            'rgba(30, 136, 229, 0.8)'
        )
        
        # Vérifier le type de retour
        self.assertIsInstance(fig, go.Figure)
        
        # Vérifier les données du graphique
        self.assertEqual(len(fig.data), 1)
        
        # Vérifier les titres
        self.assertEqual(fig.layout.title.text, 'Tendances historiques du taux d\'occupation')
        self.assertEqual(fig.layout.xaxis.title.text, 'Date')
        self.assertEqual(fig.layout.yaxis.title.text, 'Taux d\'occupation')
    
    def test_create_weekly_heatmap(self):
        """Teste la création de la heatmap hebdomadaire"""
        # Créer la heatmap
        fig = DashboardVisuals.create_weekly_heatmap(
            self.historical_df,
            'Heatmap du taux d\'occupation par jour de la semaine',
            'Taux d\'occupation moyen'
        )
        
        # Vérifier le type de retour
        self.assertIsInstance(fig, go.Figure)
        
        # Vérifier les dimensions de la heatmap
        self.assertEqual(len(fig.data), 1)
        
        # Vérifier les titres
        self.assertEqual(fig.layout.title.text, 'Heatmap du taux d\'occupation par jour de la semaine')
        self.assertEqual(fig.layout.xaxis.title.text, 'Jour de la semaine')
        self.assertEqual(fig.layout.yaxis.title.text, 'Heure de la journée')
    
    def test_create_price_occupancy_scatter(self):
        """Teste la création du nuage de points prix/occupation"""
        # Créer le graphique
        fig = DashboardVisuals.create_price_occupancy_scatter(
            self.historical_df,
            'Relation entre le prix et le taux d\'occupation',
            'Prix (€)',
            'Taux d\'occupation'
        )
        
        # Vérifier le type de retour
        self.assertIsInstance(fig, go.Figure)
        
        # Vérifier les données du graphique
        self.assertEqual(len(fig.data), 1)
        
        # Vérifier les titres
        self.assertEqual(fig.layout.title.text, 'Relation entre le prix et le taux d\'occupation')
        self.assertEqual(fig.layout.xaxis.title.text, 'Prix (€)')
        self.assertEqual(fig.layout.yaxis.title.text, 'Taux d\'occupation')
    
    def test_create_revenue_forecast_chart(self):
        """Teste la création du graphique de prévision de revenus"""
        # Créer le graphique
        fig = DashboardVisuals.create_revenue_forecast_chart(
            self.predictions_df,
            self.historical_df,
            'Prévision des revenus',
            'Revenu (€)'
        )
        
        # Vérifier le type de retour
        self.assertIsInstance(fig, go.Figure)
        
        # Vérifier les données du graphique
        self.assertGreater(len(fig.data), 0)
        
        # Vérifier les titres
        self.assertEqual(fig.layout.title.text, 'Prévision des revenus')
        self.assertEqual(fig.layout.yaxis.title.text, 'Revenu (€)')

if __name__ == '__main__':
    unittest.main()
