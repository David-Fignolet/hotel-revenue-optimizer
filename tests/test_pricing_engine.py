"""
Tests unitaires pour le module pricing_engine.py
"""
import os
import sys
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pricing_engine import PricingEngine
from src.demand_forecasting import DemandForecaster
from src.data_processor import HotelDataProcessor
from src.config import PATHS, PRICING_PARAMS

class TestPricingEngine(unittest.TestCase):
    """Classe de tests pour PricingEngine"""
    
    @classmethod
    def setUpClass(cls):
        """Configuration avant tous les tests"""
        # Initialiser le processeur de données
        cls.processor = HotelDataProcessor(country='FR')
        
        # Créer des données de test pour les prédictions de demande
        cls.create_test_demand_data()
        
        # Initialiser le modèle de prévision de demande
        cls.demand_model = DemandForecaster()
        
        # Entraîner le modèle de demande sur les données de test
        cls.train_demand_model()
    
    @classmethod
    def create_test_demand_data(cls):
        """Créer des données de test pour les prédictions de demande"""
        # Créer des dates pour une année complète
        end_date = datetime.now().replace(day=1) - timedelta(days=1)  # Fin du mois dernier
        start_date = end_date - timedelta(days=365)  # 1 an de données
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Créer un DataFrame avec des données simulées
        np.random.seed(42)  # Pour la reproductibilité
        
        # Données de base
        cls.test_room_type = 'Standard'
        data = {
            'date': dates,
            'room_type': cls.test_room_type,
            'occupancy_rate': np.clip(0.4 + 0.4 * np.sin(2 * np.pi * np.arange(len(dates)) / 30) + 
                               np.random.normal(0, 0.1, len(dates)), 0, 1),
            'price': np.clip(100 + 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 180) + 
                          np.random.normal(0, 10, len(dates)), 80, 300)
        }
        
        df = pd.DataFrame(data)
        
        # Ajouter des caractéristiques temporelles
        df = cls.processor.create_calendar_features(df, 'date')
        
        # Ajouter des décalages temporels
        df = cls.processor.create_lag_features(df, 'occupancy_rate', lags=[1, 7, 30])
        
        # Sauvegarder les données de test
        df.to_csv(PATHS['raw_data'], index=False)
        
        # Diviser en ensembles d'entraînement et de test (80/20)
        split_idx = int(0.8 * len(df))
        cls.train_data = df.iloc[:split_idx].copy()
        cls.test_data = df.iloc[split_idx:].copy()
        
        # Colonnes à utiliser comme caractéristiques
        cls.feature_columns = [
            'month_sin', 'month_cos', 'day_sin', 'day_cos',
            'is_weekend', 'is_holiday', 'is_school_holiday',
            'occupancy_rate_lag_1', 'occupancy_rate_lag_7', 'occupancy_rate_lag_30'
        ]
        
        # Colonne cible
        cls.target_column = 'occupancy_rate'
    
    @classmethod
    def train_demand_model(cls):
        """Entraîner le modèle de demande sur les données de test"""
        cls.demand_model.train(
            cls.train_data,
            feature_columns=cls.feature_columns,
            target_column=cls.target_column,
            room_type=cls.test_room_type,
            save_model=False
        )
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Réinitialiser le moteur de tarification avant chaque test
        self.pricing_engine = PricingEngine(
            demand_model=self.demand_model,
            **PRICING_PARAMS
        )
    
    def test_initialization(self):
        """Teste l'initialisation du moteur de tarification"""
        self.assertIsNotNone(self.pricing_engine)
        self.assertEqual(self.pricing_engine.base_price, PRICING_PARAMS['base_price'])
        self.assertEqual(self.pricing_engine.min_price, PRICING_PARAMS['min_price'])
        self.assertEqual(self.pricing_engine.max_price, PRICING_PARAMS['max_price'])
        self.assertEqual(self.pricing_engine.price_step, PRICING_PARAMS['price_step'])
        self.assertEqual(self.pricing_engine.elasticity, PRICING_PARAMS['elasticity'])
    
    def test_demand_function(self):
        """Teste la fonction de demande"""
        # Tester avec le prix de base
        demand = self.pricing_engine.demand_function(PRICING_PARAMS['base_price'])
        self.assertAlmostEqual(demand, 1.0, places=2)  # La demande devrait être de 1.0 au prix de base
        
        # Tester avec un prix plus élevé (demande plus faible)
        higher_price = PRICING_PARAMS['base_price'] * 1.2  # +20%
        higher_demand = self.pricing_engine.demand_function(higher_price)
        self.assertLess(higher_demand, 1.0)
        
        # Tester avec un prix plus bas (demande plus élevée)
        lower_price = PRICING_PARAMS['base_price'] * 0.8  # -20%
        lower_demand = self.pricing_engine.demand_function(lower_price)
        self.assertGreater(lower_demand, 1.0)
    
    def test_revenue_function(self):
        """Teste la fonction de revenu"""
        # Tester avec le prix de base
        revenue = self.pricing_engine.revenue_function(PRICING_PARAMS['base_price'])
        expected_revenue = PRICING_PARAMS['base_price'] * 1.0  # Demande de 1.0 au prix de base
        self.assertAlmostEqual(revenue, expected_revenue, delta=0.01)
        
        # Tester avec un prix plus élevé
        higher_price = PRICING_PARAMS['base_price'] * 1.2  # +20%
        higher_revenue = self.pricing_engine.revenue_function(higher_price)
        
        # Tester avec un prix plus bas
        lower_price = PRICING_PARAMS['base_price'] * 0.8  # -20%
        lower_revenue = self.pricing_engine.revenue_function(lower_price)
        
        # Vérifier que le revenu suit la courbe attendue (parabole inversée)
        self.assertGreater(revenue, higher_revenue)
        self.assertGreater(revenue, lower_revenue)
    
    def test_find_optimal_price(self):
        """Teste la recherche du prix optimal"""
        # Trouver le prix optimal
        optimal_price = self.pricing_engine.find_optimal_price()
        
        # Vérifier que le prix est dans les limites autorisées
        self.assertGreaterEqual(optimal_price, PRICING_PARAMS['min_price'])
        self.assertLessEqual(optimal_price, PRICING_PARAMS['max_price'])
        
        # Vérifier que le prix est un multiple du pas de prix
        self.assertAlmostEqual(
            optimal_price % PRICING_PARAMS['price_step'],
            0,
            places=2
        )
    
    def test_optimize_price_for_demand(self):
        """Teste l'optimisation du prix pour une demande cible"""
        # Définir une demande cible (80% d'occupation)
        target_demand = 0.8
        
        # Optimiser le prix pour cette demande
        optimal_price = self.pricing_engine.optimize_price_for_demand(target_demand)
        
        # Vérifier que le prix est dans les limites autorisées
        self.assertGreaterEqual(optimal_price, PRICING_PARAMS['min_price'])
        self.assertLessEqual(optimal_price, PRICING_PARAMS['max_price'])
        
        # Vérifier que la demande prédite est proche de la cible
        predicted_demand = self.pricing_engine.demand_function(optimal_price)
        self.assertAlmostEqual(predicted_demand, target_demand, delta=0.05)  # Tolérance de 5%
    
    def test_scenario_analysis(self):
        """Teste l'analyse de scénarios"""
        # Définir des scénarios de prix à tester
        price_scenarios = [
            PRICING_PARAMS['base_price'] * 0.8,  # -20%
            PRICING_PARAMS['base_price'],         # Prix de base
            PRICING_PARAMS['base_price'] * 1.2    # +20%
        ]
        
        # Analyser les scénarios
        results = self.pricing_engine.scenario_analysis(price_scenarios)
        
        # Vérifier la structure des résultats
        self.assertIn('prices', results)
        self.assertIn('demands', results)
        self.assertIn('revenues', results)
        
        # Vérifier les dimensions
        self.assertEqual(len(results['prices']), len(price_scenarios))
        self.assertEqual(len(results['demands']), len(price_scenarios))
        self.assertEqual(len(results['revenues']), len(price_scenarios))
        
        # Vérifier que les prix sont dans le bon ordre
        self.assertEqual(results['prices'], sorted(price_scenarios))
        
        # Vérifier que la demande diminue avec l'augmentation du prix
        for i in range(len(results['prices']) - 1):
            self.assertGreater(results['demands'][i], results['demands'][i+1])
    
    def test_get_pricing_insights(self):
        """Teste la génération d'insights de tarification"""
        # Générer des insights
        insights = self.pricing_engine.get_pricing_insights()
        
        # Vérifier la structure des insights
        self.assertIn('optimal_price', insights)
        self.assertIn('current_price', insights)
        self.assertIn('price_change_pct', insights)
        self.assertIn('expected_demand', insights)
        self.assertIn('expected_revenue', insights)
        self.assertIn('revenue_change_pct', insights)
        
        # Vérifier que le prix optimal est dans les limites
        self.assertGreaterEqual(insights['optimal_price'], PRICING_PARAMS['min_price'])
        self.assertLessEqual(insights['optimal_price'], PRICING_PARAMS['max_price'])
        
        # Vérifier que la demande attendue est entre 0 et 1
        self.assertGreaterEqual(insights['expected_demand'], 0.0)
        self.assertLessEqual(insights['expected_demand'], 1.5)  # Tolérance pour les valeurs légèrement > 1
    
    def test_generate_business_recommendations(self):
        """Teste la génération de recommandations métier"""
        # Générer des recommandations
        recommendations = self.pricing_engine.generate_business_recommendations()
        
        # Vérifier que nous avons des recommandations
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Vérifier que chaque recommandation est une chaîne non vide
        for rec in recommendations:
            self.assertIsInstance(rec, str)
            self.assertGreater(len(rec.strip()), 0)

if __name__ == '__main__':
    unittest.main()
