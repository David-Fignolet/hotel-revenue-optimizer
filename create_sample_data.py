# create_sample_data.py
import pandas as pd
import numpy as np

# Créer des données historiques
dates = pd.date_range(start='2023-01-01', periods=90)
base_price = np.random.normal(120, 20, 90).clip(80, 200).round(2)
price_variation = np.random.normal(0, 10, 90).round(2)
occupancy_trend = np.random.beta(3, 2, 90).clip(0.3, 0.95).round(4)
historical = pd.DataFrame({
    'date': dates,
    'price': (base_price + price_variation).clip(80, 200).round(2),
    'occupancy_rate': (occupancy_trend + np.random.normal(0, 0.05, 90)).clip(0.3, 0.95).round(4)
})

# Enregistrer les données
output_file = 'exemple_donnees_historiques.csv'
historical[['date', 'price', 'occupancy_rate']].to_csv(output_file, index=False)
print("Fichier d'exemple créé : exemple_donnees_historiques.csv")