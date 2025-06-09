# Guide de contribution

Merci de votre intérêt pour contribuer à Hotel Revenue Optimizer ! Voici comment vous pouvez nous aider à améliorer ce projet.

## Comment contribuer

### Signaler des bugs
1. Vérrez si le bug n'a pas déjà été signalé dans les [issues](https://github.com/votre-username/hotel-revenue-optimizer/issues).
2. Si ce n'est pas le cas, créez une nouvelle issue avec un titre clair et une description détaillée du problème.
3. Incluez des étapes pour reproduire le bug, le résultat attendu et le résultat réel.

### Proposer des améliorations
1. Vérrez si l'amélioration n'a pas déjà été proposée.
2. Créez une nouvelle issue pour discuter de votre proposition avant de commencer à coder.
3. Une fois approuvée, vous pouvez soumettre une pull request.

### Soumettre du code
1. Forkez le dépôt et créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-nouvelle-fonctionnalite`).
2. Committez vos changements avec des messages clairs et concis.
3. Poussez vos modifications vers votre fork (`git push origin feature/ma-nouvelle-fonctionnalite`).
4. Ouvrez une Pull Request vers la branche `main` du dépôt original.

## Normes de code

### Style de code
- Suivez le style de code existant dans le projet.
- Utilisez `black` pour le formatage du code Python.
- Vérifiez votre code avec `flake8` avant de soumettre.
- Ajoutez des tests pour les nouvelles fonctionnalités.

### Structure du projet
```
hotel-revenue-optimizer/
├── app/                    # Application Streamlit
│   ├── assets/             # Fichiers statiques (images, CSS, etc.)
│   └── streamlit_app.py    # Point d'entrée de l'application
├── data/                    # Données
│   ├── processed/          # Données traitées
│   └── raw/                # Données brutes
├── docs/                   # Documentation
├── models/                 # Modèles entraînés
│   └── saved_models/
├── notebooks/              # Notebooks Jupyter
├── src/                    # Code source
│   ├── __init__.py
│   ├── config.py           # Configuration
│   ├── dashboard.py        # Visualisations
│   ├── data_processor.py   # Prétraitement
│   ├── demand_forecasting.py # Prédiction
│   └── pricing_engine.py   # Tarification
└── tests/                  # Tests unitaires et d'intégration
```

## Configuration de l'environnement de développement

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-username/hotel-revenue-optimizer.git
   cd hotel-revenue-optimizer
   ```

2. Créez un environnement virtuel :
   ```bash
   # Sur Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Sur MacOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Créez un fichier `.env` à partir du modèle :
   ```bash
   cp .env.example .env
   ```
   Puis modifiez les valeurs selon votre configuration.

## Exécution des tests

```bash
# Exécuter tous les tests
pytest

# Exécuter les tests avec couverture de code
pytest --cov=src

# Exécuter un fichier de test spécifique
pytest tests/test_demand_forecasting.py -v

# Exécuter un test spécifique
pytest tests/test_demand_forecasting.py::TestDemandForecaster::test_train_model -v
```

## Processus de revue de code

1. Les PR doivent passer tous les tests et vérifications de code.
2. Au moins un mainteneur doit approuver la PR avant la fusion.
3. Les commits doivent être atomiques et bien décrits.
4. La branche `main` est protégée - les modifications doivent passer par une PR.

## Communication

- Pour les questions générales, utilisez les discussions GitHub.
- Pour les problèmes spécifiques, créez une issue.
- Soyez respectueux et professionnel dans toutes les communications.

## Code de conduite

Ce projet et tous ceux qui y participent sont régis par notre [Code de Conduite](CODE_OF_CONDUCT.md). En participant, vous êtes tenu de respecter ce code.

## Licence

En contribuant, vous acceptez que vos contributions soient sous la même licence que celle du projet.
