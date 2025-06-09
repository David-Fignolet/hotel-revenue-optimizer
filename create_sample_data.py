# create_sample_data.py
import pandas as pd
import numpy as np

# Créer des données historiques
dates = pd.date_range(start='2023-01-01', periods=90)
historical = pd.DataFrame({
    'date': dates[:-30],
    'prix': np.random.normal(120, 20, 60).clip(80, 200).round(2),
    'taux_occupation': np.random.beta(3, 2, 60).clip(0.3, 0.95).round(4)
})

# Enregistrer les données
historical.to_csv('exemple_donnees_historiques.csv', index=False)
print("Fichier d'exemple créé : exemple_donnees_historiques.csv")