"""
Module de prédiction de demande hôtelière
Auteur: David Michel-Larrieux
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import joblib
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DemandForecaster:
    """
    Prédicteur de demande hôtelière basé sur Random Forest
    
    Utilise les features temporelles, événements locaux et météo
    pour prédire le taux d'occupation futur.
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.features = None
        self.is_trained = False
        
    def create_features(self, df):
        """
        Création des features temporelles et contextuelles
        
        Args:
            df (pd.DataFrame): Données brutes avec colonnes date, occupancy_rate
            
        Returns:
            pd.DataFrame: DataFrame avec features engineered
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Features temporelles
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_summer'] = ((df['month'] >= 6) & (df['month'] <= 8)).astype(int)
        df['is_winter'] = ((df['month'] == 12) | (df['month'] <= 2)).astype(int)
        
        # Features cycliques
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Lag features (données historiques)
        for lag in [1, 7, 14, 30]:
            df[f'occupancy_lag_{lag}'] = df['occupancy_rate'].shift(lag)
            
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'occupancy_ma_{window}'] = df['occupancy_rate'].rolling(window=window).mean()
            df[f'occupancy_std_{window}'] = df['occupancy_rate'].rolling(window=window).std()
            
        # Features événements (simulées)
        df['has_event'] = np.random.choice([0, 1], size=len(df), p=[0.8, 0.2])
        df['event_impact'] = df['has_event'] * np.random.uniform(0.1, 0.3, len(df))
        
        # Features météo (simulées)
        df['temperature'] = 15 + 10 * np.sin(2 * np.pi * df['month'] / 12) + np.random.normal(0, 3, len(df))
        df['is_rain'] = np.random.choice([0, 1], size=len(df), p=[0.7, 0.3])
        
        return df.dropna()
    
    def prepare_features(self, df):
        """Prépare les features pour l'entraînement/prédiction"""
        feature_cols = [
            'day_of_week', 'month', 'week_of_year', 'is_weekend', 
            'is_summer', 'is_winter', 'day_sin', 'day_cos', 
            'month_sin', 'month_cos', 'occupancy_lag_1', 'occupancy_lag_7',
            'occupancy_lag_14', 'occupancy_lag_30', 'occupancy_ma_7',
            'occupancy_ma_14', 'occupancy_ma_30', 'occupancy_std_7',
            'occupancy_std_14', 'occupancy_std_30', 'has_event',
            'event_impact', 'temperature', 'is_rain'
        ]
        
        self.features = feature_cols
        return df[feature_cols], df['occupancy_rate']
    
    def train(self, df):
        """
        Entraîne le modèle de prédiction de demande
        
        Args:
            df (pd.DataFrame): Données d'entraînement
        """
        print("🔄 Création des features...")
        df_features = self.create_features(df)
        
        print("📊 Préparation des données...")
        X, y = self.prepare_features(df_features)
        
        print("🤖 Entraînement du modèle...")
        # Validation croisée temporelle
        tscv = TimeSeriesSplit(n_splits=5)
        mae_scores = []
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_val)
            mae = mean_absolute_error(y_val, y_pred)
            mae_scores.append(mae)
        
        # Entraînement final sur toutes les données
        self.model.fit(X, y)
        self.is_trained = True
        
        print(f"✅ Modèle entraîné - MAE moyen: {np.mean(mae_scores):.4f}")
        return np.mean(mae_scores)
    
    def predict_demand(self, start_date, days=30, room_type='Standard'):
        """
        Prédit la demande pour les prochains jours
        
        Args:
            start_date (str): Date de début (YYYY-MM-DD)
            days (int): Nombre de jours à prédire
            room_type (str): Type de chambre
            
        Returns:
            pd.DataFrame: Prédictions avec intervalles de confiance
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné. Utilisez train() d'abord.")
        
        # Création des dates futures
        start = pd.to_datetime(start_date)
        dates = pd.date_range(start, periods=days, freq='D')
        
        # Simulation des données futures (à remplacer par vraies données)
        future_data = []
        for date in dates:
            # Valeurs de base simulées
            base_occupancy = 0.70 + 0.15 * np.sin(2 * np.pi * date.month / 12)
            
            future_data.append({
                'date': date,
                'occupancy_rate': base_occupancy,  # Sera mise à jour itérativement
                'room_type': room_type
            })
        
        df_future = pd.DataFrame(future_data)
        
        # Création des features
        df_future = self.create_features(df_future)
        X_future, _ = self.prepare_features(df_future)
        
        # Prédictions
        predictions = self.model.predict(X_future)
        
        # Calcul des intervalles de confiance (approximation)
        std_pred = np.std(predictions) * 0.1  # Estimation simplifiée
        
        results = pd.DataFrame({
            'date': dates,
            'predicted_occupancy': predictions,
            'lower_bound': np.maximum(0, predictions - 1.96 * std_pred),
            'upper_bound': np.minimum(1, predictions + 1.96 * std_pred),
            'room_type': room_type
        })
        
        return results
    
    def get_feature_importance(self):
        """Retourne l'importance des features"""
        if not self.is_trained:
            return None
            
        importance_df = pd.DataFrame({
            'feature': self.features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def save_model(self, filepath):
        """Sauvegarde le modèle"""
        joblib.dump({
            'model': self.model,
            'features': self.features,
            'is_trained': self.is_trained
        }, filepath)
        print(f"💾 Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath):
        """Charge un modèle pré-entraîné"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.features = data['features']
        self.is_trained = data['is_trained']
        print(f"📂 Modèle chargé: {filepath}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Génération de données d'exemple
    from datetime import datetime, timedelta
    
    dates = pd.date_range('2022-01-01', '2023-12-31', freq='D')
    np.random.seed(42)
    
    # Simulation de données réalistes
    occupancy_data = []
    for date in dates:
        # Tendance saisonnière
        seasonal = 0.65 + 0.20 * np.sin(2 * np.pi * date.month / 12)
        # Effet week-end
        weekend_boost = 0.15 if date.weekday() >= 5 else 0
        # Bruit aléatoire
        noise = np.random.normal(0, 0.05)
        
        occupancy = np.clip(seasonal + weekend_boost + noise, 0.1, 0.98)
        
        occupancy_data.append({
            'date': date,
            'occupancy_rate': occupancy,
            'room_type': 'Standard'
        })
    
    df = pd.DataFrame(occupancy_data)
    
    # Test du modèle
    forecaster = DemandForecaster()
    mae = forecaster.train(df)
    
    # Prédiction
    predictions = forecaster.predict_demand('2024-01-01', days=30)
    print("\n📈 Prédictions de demande:")
    print(predictions.head(10))
    
    # Importance des features
    print("\n🔍 Importance des features:")
    print(forecaster.get_feature_importance().head(10))
