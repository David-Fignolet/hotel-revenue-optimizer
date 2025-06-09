# 🏨 Hotel Revenue Optimizer

> **Intelligence artificielle appliquée au revenue management hôtelier**  
> Développé par David Michel-Larrieux - Data Analyst & Expert Hôtellerie (20 ans d'expérience)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-orange.svg)](https://scikit-learn.org)

## 🎯 Contexte Business

Dans l'industrie hôtelière, **optimiser les revenus** nécessite de prédire avec précision :
- La **demande future** (taux d'occupation)
- Le **prix optimal** par type de chambre
- L'**impact des événements** locaux et de la météo

Ce système combine **machine learning** et **expertise métier** pour automatiser ces décisions complexes.

## 🔧 Fonctionnalités

### 📊 Prédiction de Demande
- **Modèle ML** : Random Forest + features temporelles
- **Variables** : Saisonnalité, événements, météo, historique
- **Précision** : MAE < 5% sur les prédictions à 30 jours

### 💰 Algorithme de Pricing Dynamique
- **Prix optimal** basé sur la demande prédite
- **Segmentation** par type de chambre et clientèle
- **Contraintes business** : prix min/max, concurrence

### 📈 Dashboard Interactif
- **Visualisations temps réel** des KPIs revenue
- **Simulations "What-if"** : impact des changements de prix
- **Alertes automatiques** : opportunités de pricing

## 🚀 Démo Live

[**➡️ Tester l'application**](https://hotel-revenue-optimizer.streamlit.app) 
*(Déployée sur Streamlit Cloud)*

## 🛠 Installation & Utilisation

### Prérequis
- Python 3.9+
- pip (gestionnaire de paquets Python)

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-username/hotel-revenue-optimizer.git
   cd hotel-revenue-optimizer
   ```

2. **Créer un environnement virtuel** (recommandé)
   ```bash
   # Sur Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Sur MacOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

### Lancement de l'application

```bash
# Lancer le dashboard Streamlit
streamlit run app/streamlit_app.py
```

## 🧠 Modèle de Machine Learning

### Architecture
- **Prédiction de demande** : Random Forest Regressor
- **Sélection de caractéristiques** : Importance des features
- **Validation** : Time Series Cross-Validation
- **Métriques** : MAE, MAPE, R²

### Entraînement du modèle

```python
from src.demand_forecasting import DemandForecaster
import pandas as pd

# Charger les données
data = pd.read_csv('data/raw/sample_hotel_data.csv')

# Initialiser et entraîner le modèle
forecaster = DemandForecaster()
mae = forecaster.train(data)

# Faire des prédictions
predictions = forecaster.predict_demand(
    start_date='2024-01-01',
    days=30,
    room_type='Standard'
)
```

## 📊 Données

### Structure des données
- **Fichier source** : `data/raw/sample_hotel_data.csv`
- **Colonnes principales** :
  - `date` : Date de l'observation
  - `occupancy_rate` : Taux d'occupation (0-1)
  - `price` : Prix moyen par nuit (€)
  - `room_type` : Type de chambre
  - `reservations` : Nombre de réservations
  - `avg_daily_rate` : Prix moyen par chambre occupée (ADR)
  - `revenue` : Revenu total (€)
  - `weekend` : Indicateur de week-end (0/1)
  - `month` : Mois (1-12)
  - `day_of_week` : Jour de la semaine (0=lundi, 6=dimanche)
  - `special_event` : Événement spécial (si applicable)

## 📈 Améliorations Futures

- [ ] Intégration avec les systèmes PMS (Property Management System)
- [ ] Analyse des canaux de distribution
- [ ] Optimisation des restrictions de séjour (min stay, close to arrival)
- [ ] Détection automatique des motifs saisonniers
- [ ] Analyse des segments de clientèle

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Contact

Pour toute question ou suggestion, n'hésitez pas à me contacter :
- Email: contact@example.com
- LinkedIn: [linkedin.com/in/david-michel-larrieux](https://linkedin.com)
- Site web: [www.example.com](https://www.example.com)
