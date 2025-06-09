"""
Configuration des fixtures pour les tests unitaires
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.demand_forecasting import DemandForecaster
from src.pricing_engine import PricingEngine
from src.data_processor import HotelDataProcessor
from src.config import PATHS, DEMAND_MODEL_PARAMS, PRICING_PARAMS

@pytest.fixture(scope="module")
def test_room_type():
    """Retourne le type de chambre de test"""
    return "Standard"

@pytest.fixture(scope="module")
def test_dates():
    """Retourne une plage de dates de test (1 an)"""
    end_date = datetime.now().replace(day=1) - timedelta(days=1)  # Fin du mois dernier
    start_date = end_date - timedelta(days=365)  # 1 an de données
    return pd.date_range(start=start_date, end=end_date, freq='D')

@pytest.fixture(scope="module")
def test_hotel_data(test_dates, test_room_type):
    """Crée un jeu de données hôtelières de test"""
    np.random.seed(42)  # Pour la reproductibilité
    
    # Données de base
    data = {
        'date': test_dates,
        'room_type': test_room_type,
        'occupancy_rate': np.clip(0.4 + 0.4 * np.sin(2 * np.pi * np.arange(len(test_dates)) / 30) + 
                           np.random.normal(0, 0.1, len(test_dates)), 0, 1),
        'price': np.clip(100 + 50 * np.sin(2 * np.pi * np.arange(len(test_dates)) / 180) + 
                      np.random.normal(0, 10, len(test_dates)), 80, 300)
    }
    
    return pd.DataFrame(data)

@pytest.fixture(scope="module")
def data_processor():
    """Retourne une instance de HotelDataProcessor"""
    return HotelDataProcessor(country='FR')

@pytest.fixture(scope="module")
def processed_test_data(data_processor, test_hotel_data):
    """Retourne des données traitées pour les tests"""
    # Ajouter des caractéristiques temporelles
    df = data_processor.create_calendar_features(test_hotel_data, 'date')
    
    # Ajouter des décalages temporels
    df = data_processor.create_lag_features(df, 'occupancy_rate', lags=[1, 7, 30])
    
    # Ajouter des statistiques mobiles
    df = data_processor.create_rolling_features(
        df, 
        'occupancy_rate', 
        windows=[7, 30],
        agg_funcs={'mean': np.mean, 'std': np.std}
    )
    
    return df

@pytest.fixture(scope="module")
def trained_demand_model(processed_test_data, test_room_type):
    """Retourne un modèle de demande entraîné sur les données de test"""
    # Colonnes de caractéristiques
    feature_columns = [
        'month_sin', 'month_cos', 'day_sin', 'day_cos',
        'is_weekend', 'is_holiday', 'is_school_holiday',
        'occupancy_rate_lag_1', 'occupancy_rate_lag_7', 'occupancy_rate_lag_30',
        'occupancy_rate_mean_7d', 'occupancy_rate_std_7d',
        'occupancy_rate_mean_30d', 'occupancy_rate_std_30d'
    ]
    
    # Colonne cible
    target_column = 'occupancy_rate'
    
    # Initialiser et entraîner le modèle
    model = DemandForecaster(**DEMAND_MODEL_PARAMS)
    model.train(
        processed_test_data,
        feature_columns=feature_columns,
        target_column=target_column,
        room_type=test_room_type,
        save_model=False
    )
    
    return model, feature_columns, target_column

@pytest.fixture(scope="module")
def pricing_engine(trained_demand_model):
    """Retourne une instance de PricingEngine avec un modèle de demande entraîné"""
    model, _, _ = trained_demand_model
    return PricingEngine(demand_model=model, **PRICING_PARAMS)

@pytest.fixture(scope="module")
def test_predictions(processed_test_data, trained_demand_model, test_room_type):
    """Retourne des prédictions de test"""
    model, feature_columns, _ = trained_demand_model
    
    # Sélectionner les 30 derniers jours pour la prédiction
    future_days = 30
    last_date = processed_test_data['date'].max()
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=future_days,
        freq='D'
    )
    
    # Créer un DataFrame pour les futures dates
    future_data = pd.DataFrame({'date': future_dates})
    
    # Ajouter des caractéristiques temporelles
    processor = HotelDataProcessor(country='FR')
    future_data = processor.create_calendar_features(future_data, 'date')
    
    # Ajouter le type de chambre
    future_data['room_type'] = test_room_type
    
    # Faire des prédictions
    predictions = model.predict(
        future_data,
        feature_columns=feature_columns,
        room_type=test_room_type
    )
    
    return predictions

@pytest.fixture(scope="module")
def test_historical_data(processed_test_data):
    """Retourne des données historiques pour les tests de visualisation"""
    # Sélectionner les 180 derniers jours de données historiques
    historical_data = processed_test_data.sort_values('date').tail(180).copy()
    
    # Ajouter une colonne de revenu simulée
    historical_data['revenue'] = historical_data['price'] * historical_data['occupancy_rate']
    
    return historical_data

@pytest.fixture(scope="module")
def test_price_sensitivity_data():
    """Retourne des données de sensibilité aux prix pour les tests"""
    np.random.seed(42)
    prices = np.linspace(80, 250, 20)
    demands = np.clip(1.5 - 0.002 * prices + np.random.normal(0, 0.05, 20), 0.2, 1.2)
    
    return pd.DataFrame({
        'price': prices,
        'demand': demands,
        'revenue': prices * demands
    })

@pytest.fixture(scope="module")
def dashboard_visuals():
    """Retourne une instance de DashboardVisuals"""
    from src.dashboard import DashboardVisuals
    return DashboardVisuals()
