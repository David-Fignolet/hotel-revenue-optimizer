"""
Tests unitaires pour le module demand_forecasting.py
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

from src.demand_forecasting import DemandForecaster
from src.data_processor import HotelDataProcessor
from src.config import PATHS, DEMAND_MODEL_PARAMS

class TestDemandForecaster(unittest.TestCase):
    """Classe de tests pour DemandForecaster"""
    
    @classmethod
    def setUpClass(cls):
        """Configuration avant tous les tests"""
        # Créer un jeu de données de test
        cls.create_test_data()
        
        # Initialiser le processeur de données
        cls.processor = HotelDataProcessor(country='FR')
        
        # Préparer les données
        cls.prepare_data()
        
    @classmethod
    def create_test_data(cls):
        """Créer un jeu de données de test"""
        # Créer des dates pour une année complète
        end_date = datetime.now().replace(day=1) - timedelta(days=1)  # Fin du mois dernier
        start_date = end_date - timedelta(days=365)  # 1 an de données
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Créer un DataFrame avec des données simulées
        np.random.seed(42)  # Pour la reproductibilité
        
        # Données de base
        data = {
            'date': dates,
            'room_type': np.random.choice(['Standard', 'Deluxe', 'Suite'], size=len(dates)),
            'occupancy_rate': np.clip(0.4 + 0.4 * np.sin(2 * np.pi * np.arange(len(dates)) / 30) + 
                               np.random.normal(0, 0.1, len(dates)), 0, 1),
            'price': np.clip(100 + 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 180) + 
                          np.random.normal(0, 10, len(dates)), 80, 300)
        }
        
        df = pd.DataFrame(data)
        
        # Ajouter des caractéristiques temporelles
        cls.processor = HotelDataProcessor(country='FR')
        df = cls.processor.create_calendar_features(df, 'date')
        
        # Ajouter des décalages temporels
        for room_type in df['room_type'].unique():
            mask = df['room_type'] == room_type
            df.loc[mask] = cls.processor.create_lag_features(
                df[mask], 'occupancy_rate', lags=[1, 7, 30], group_col=None
            )
        
        # Sauvegarder les données de test
        df.to_csv(PATHS['raw_data'], index=False)
        
        return df
    
    @classmethod
    def prepare_data(cls):
        """Préparer les données pour les tests"""
        # Charger les données brutes
        df = pd.read_csv(PATHS['raw_data'], parse_dates=['date'])
        
        # Filtrer pour une seule catégorie de chambre pour simplifier
        cls.test_room_type = 'Standard'
        df = df[df['room_type'] == cls.test_room_type].copy()
        
        # Trier par date
        df = df.sort_values('date').reset_index(drop=True)
        
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
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Réinitialiser le modèle avant chaque test
        self.model = DemandForecaster(**DEMAND_MODEL_PARAMS)
    
    def test_model_initialization(self):
        """Teste l'initialisation du modèle"""
        self.assertIsNotNone(self.model.model)
        self.assertEqual(self.model.model.n_estimators, DEMAND_MODEL_PARAMS['n_estimators'])
        self.assertEqual(self.model.model.max_depth, DEMAND_MODEL_PARAMS['max_depth'])
    
    def test_feature_engineering(self):
        """Teste la création des caractéristiques"""
        X, y = self.model._prepare_features(
            self.train_data, 
            self.feature_columns, 
            self.target_column
        )
        
        # Vérifier les dimensions
        self.assertEqual(len(X), len(self.train_data) - 30)  # A cause du lag de 30 jours
        self.assertEqual(len(X), len(y))
        
        # Vérifier les colonnes
        self.assertEqual(len(X.columns), len(self.feature_columns))
        self.assertTrue(all(col in X.columns for col in self.feature_columns))
    
    def test_train_model(self):
        """Teste l'entraînement du modèle"""
        # Entraîner le modèle
        mae = self.model.train(
            self.train_data,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            room_type=self.test_room_type,
            save_model=False
        )
        
        # Vérifier que le MAE est un nombre raisonnable
        self.assertIsInstance(mae, float)
        self.assertGreater(mae, 0.0)
        self.assertLess(mae, 0.3)  # MAE devrait être inférieur à 30%
    
    def test_predict(self):
        """Teste les prédictions du modèle"""
        # Entraîner d'abord le modèle
        self.model.train(
            self.train_data,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            room_type=self.test_room_type,
            save_model=False
        )
        
        # Faire des prédictions sur l'ensemble de test
        X_test, y_test = self.model._prepare_features(
            self.test_data, 
            self.feature_columns, 
            self.target_column
        )
        
        predictions = self.model.model.predict(X_test)
        
        # Vérifier les dimensions des prédictions
        self.assertEqual(len(predictions), len(X_test))
        
        # Vérifier que les prédictions sont dans la plage attendue (0-1 pour un taux d'occupation)
        self.assertTrue(all(0 <= p <= 1.5 for p in predictions))  # Tolérance pour les valeurs légèrement > 1
    
    def test_save_load_model(self, tmp_path):
        """Teste la sauvegarde et le chargement du modèle"""
        # Créer un modèle et l'entraîner
        self.model.train(
            self.train_data,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            room_type=self.test_room_type,
            save_model=False
        )
        
        # Chemin temporaire pour le test
        model_path = tmp_path / 'test_model.joblib'
        
        # Sauvegarder le modèle
        self.model.save_model(str(model_path))
        
        # Vérifier que le fichier a été créé
        self.assertTrue(model_path.exists())
        
        # Créer un nouveau modèle et charger le modèle sauvegardé
        new_model = DemandForecaster()
        new_model.load_model(str(model_path))
        
        # Vérifier que le modèle chargé fait les mêmes prédictions
        X_test, _ = self.model._prepare_features(
            self.test_data.head(10), 
            self.feature_columns, 
            self.target_column
        )
        
        original_preds = self.model.model.predict(X_test)
        loaded_preds = new_model.model.predict(X_test)
        
        self.assertTrue(np.allclose(original_preds, loaded_preds, rtol=1e-5))
    
    def test_predict_future(self):
        """Teste la prédiction future"""
        # Entraîner le modèle
        self.model.train(
            self.train_data,
            feature_columns=self.feature_columns,
            target_column=self.target_column,
            room_type=self.test_room_type,
            save_model=False
        )
        
        # Prédire pour les 30 prochains jours
        future_dates = pd.date_range(
            start=self.test_data['date'].max() + pd.Timedelta(days=1),
            periods=30,
            freq='D'
        )
        
        # Créer un DataFrame pour les futures dates
        future_data = pd.DataFrame({'date': future_dates})
        
        # Ajouter les caractéristiques temporelles
        future_data = self.processor.create_calendar_features(future_data, 'date')
        
        # Ajouter le type de chambre
        future_data['room_type'] = self.test_room_type
        
        # Faire des prédictions
        predictions = self.model.predict(
            future_data,
            feature_columns=self.feature_columns,
            room_type=self.test_room_type
        )
        
        # Vérifier les dimensions
        self.assertEqual(len(predictions), 30)
        
        # Vérifier que les prédictions sont dans la plage attendue
        self.assertTrue(all(0 <= p <= 1.5 for p in predictions['predicted_occupancy_rate']))
        
        # Vérifier que les intervalles de confiance sont cohérents
        self.assertTrue(all(
            lower <= pred <= upper
            for lower, pred, upper in zip(
                predictions['lower_bound'],
                predictions['predicted_occupancy_rate'],
                predictions['upper_bound']
            )
        ))

if __name__ == '__main__':
    unittest.main()
