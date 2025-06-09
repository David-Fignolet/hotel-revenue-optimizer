"""
Module de traitement des données pour l'application Hotel Revenue Optimizer
"""
import pandas as pd
import numpy as np

class DataProcessor:
    @staticmethod
    def clean_data(df):
        """Nettoie les données brutes du DataFrame"""
        # Faire une copie pour éviter les modifications inattendues
        df_clean = df.copy()
        
        # Nettoyage des colonnes numériques
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
        # Nettoyage des dates
        if 'date' in df_clean.columns:
            df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
            
        return df_clean

    @staticmethod
    def calculate_metrics(df):
        """Calcule les métriques clés à partir des données nettoyées"""
        metrics = {}
        
        if 'price' in df.columns:
            metrics['avg_price'] = df['price'].mean()
            metrics['max_price'] = df['price'].max()
            metrics['min_price'] = df['price'].min()
            
        if 'occupancy_rate' in df.columns:
            metrics['avg_occupancy'] = df['occupancy_rate'].mean()
            
        return metrics