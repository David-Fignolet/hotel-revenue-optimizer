"""
Configuration de l'application Hotel Revenue Optimizer
"""
from pathlib import Path
import os

# Chemins des répertoires
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
MODELS_DIR = ROOT_DIR / 'models' / 'saved_models'
ASSETS_DIR = ROOT_DIR / 'app' / 'assets'

# Création des répertoires s'ils n'existent pas
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, ASSETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Chemins des fichiers de données
PATHS = {
    'raw_data': str(RAW_DATA_DIR / 'sample_hotel_data.csv'),
    'processed_data': str(PROCESSED_DATA_DIR / 'processed_hotel_data.pkl'),
    'demand_model': str(MODELS_DIR / 'demand_forecaster.joblib'),
    'pricing_model': str(MODELS_DIR / 'pricing_engine.joblib'),
    'logo': str(ASSETS_DIR / 'logo.png')
}

# Paramètres du modèle de prédiction de demande
DEMAND_MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1
}

# Paramètres du moteur de tarification
PRICING_PARAMS = {
    'base_price': 120.0,
    'min_price': 80.0,
    'max_price': 300.0,
    'price_step': 5.0,
    'elasticity': -1.5,  # Élasticité-prix de la demande
    'competitor_weight': 0.3  # Poids des prix des concurrents
}

# Paramètres temporels
TIME_PARAMS = {
    'date_format': '%Y-%m-%d',
    'prediction_horizon': 90,  # jours
    'train_months': 12  # nombre de mois de données d'entraînement
}

# Paramètres de l'interface utilisateur
UI_PARAMS = {
    'theme': {
        'primary_color': '#1E88E5',
        'background_color': '#FFFFFF',
        'secondary_background_color': '#F0F2F6',
        'text_color': '#262730',
        'font': 'sans serif'
    },
    'page_config': {
        'page_title': 'Hotel Revenue Optimizer',
        'page_icon': '🏨',
        'layout': 'wide',
        'initial_sidebar_state': 'expanded'
    }
}

# Paramètres des graphiques
PLOT_PARAMS = {
    'template': 'plotly_white',
    'colors': {
        'primary': '#1E88E5',
        'secondary': '#FFC107',
        'success': '#4CAF50',
        'danger': '#F44336',
        'warning': '#FF9800',
        'info': '#00BCD4'
    },
    'margin': dict(l=50, r=50, t=50, b=50),
    'height': 400
}

# Paramètres de journalisation
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(ROOT_DIR / 'app.log'),
            'formatter': 'standard',
            'level': 'DEBUG'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Paramètres de l'API (exemple avec OpenWeatherMap)
API_KEYS = {
    'openweathermap': os.getenv('OPENWEATHERMAP_API_KEY', 'your_api_key_here'),
    'google_maps': os.getenv('GOOGLE_MAPS_API_KEY', 'your_api_key_here')
}

# Paramètres de déploiement
DEPLOYMENT = {
    'host': '0.0.0.0',
    'port': 8501,
    'debug': True,
    'use_reloader': True
}

def get_config():
    """Retourne la configuration sous forme de dictionnaire"""
    return {
        'paths': PATHS,
        'demand_model': DEMAND_MODEL_PARAMS,
        'pricing': PRICING_PARAMS,
        'time': TIME_PARAMS,
        'ui': UI_PARAMS,
        'plots': PLOT_PARAMS,
        'logging': LOGGING_CONFIG,
        'api_keys': API_KEYS,
        'deployment': DEPLOYMENT
    }
