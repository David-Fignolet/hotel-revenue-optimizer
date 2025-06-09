# Guide de Développement

Ce document fournit des informations essentielles pour les développeurs travaillant sur le projet Hotel Revenue Optimizer.

## Table des Matières

1. [Structure du Projet](#structure-du-projet)
2. [Configuration de l'Environnement](#configuration-de-lenvironnement)
3. [Workflow de Développement](#workflow-de-développement)
4. [Standards de Code](#standards-de-code)
5. [Tests](#tests)
6. [Documentation](#documentation)
7. [Déploiement](#déploiement)
8. [Dépannage](#dépannage)

## Structure du Projet

```
hotel-revenue-optimizer/
├── app/                    # Application Streamlit
│   ├── assets/            # Fichiers statiques (images, CSS, etc.)
│   └── streamlit_app.py   # Point d'entrée de l'application
├── data/                   # Données
│   ├── processed/         # Données traitées
│   └── raw/               # Données brutes
├── docs/                  # Documentation
├── models/                # Modèles entraînés
│   └── saved_models/
├── notebooks/             # Notebooks Jupyter
├── src/                   # Code source
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── dashboard.py       # Visualisations
│   ├── data_processor.py  # Prétraitement
│   ├── demand_forecasting.py # Prédiction
│   └── pricing_engine.py  # Tarification
└── tests/                 # Tests unitaires et d'intégration
```

## Configuration de l'Environnement

### Prérequis

- Python 3.8+
- pip
- git
- (Optionnel) Docker pour le développement conteneurisé

### Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/hotel-revenue-optimizer.git
   cd hotel-revenue-optimizer
   ```

2. Créer et activer un environnement virtuel :
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Modifier .env selon vos besoins
   ```

## Workflow de Développement

1. **Créer une branche** pour votre fonctionnalité/correction :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   # ou
   git checkout -b fix/nom-du-bug
   ```

2. **Développer** votre fonctionnalité en suivant les standards de code

3. **Tester** votre code :
   ```bash
   pytest
   ```

4. **Vérifier la qualité du code** :
   ```bash
   flake8 src/
   black --check src/
   isort --check-only src/
   mypy src/
   ```

5. **Formater le code** si nécessaire :
   ```bash
   black src/
   isort src/
   ```

6. **Pousser** vos changements :
   ```bash
   git add .
   git commit -m "Description claire et concise de vos changements"
   git push origin nom-de-votre-branche
   ```

7. **Ouvrir une Pull Request** vers la branche `main`

## Standards de Code

### Python

- Suivre [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utiliser des noms descriptifs pour les variables et fonctions
- Écrire des docstrings pour toutes les fonctions et classes
- Garder les fonctions courtes et focalisées
- Utiliser le typage des annotations de type Python

### Git

- Écrire des messages de commit clairs et descriptifs
- Un commit par fonctionnalité/correction
- Éviter les commits volumineux
- Utiliser le format de message de commit conventionnel :
  ```
  type(portée): description courte
  
  Description plus détaillée si nécessaire
  
  - Liste
  - Des
  - Points
  
  Fixes #issue-number
  ```
  
  Types possibles :
  - feat : Nouvelle fonctionnalité
  - fix : Correction de bug
  - docs : Modification de la documentation
  - style : Formatage, point-virgule manquant, etc. (pas de changement de code)
  - refactor : Refactoring du code
  - test : Ajout ou modification de tests
  - chore : Mise à jour des tâches de construction, configuration, etc.

## Tests

### Exécuter les tests

```bash
# Tous les tests
pytest

# Un fichier de test spécifique
pytest tests/test_fichier.py

# Un test spécifique
pytest tests/test_fichier.py::TestClass::test_method

# Avec couverture de code
pytest --cov=src --cov-report=term-missing
```

### Écrire des tests

- Un test par fonctionnalité
- Tester les cas limites et les erreurs
- Utiliser des fixtures pour les données de test courantes
- Garder les tests indépendants et isolés

## Documentation

### Documentation du code

- Utiliser des docstrings au format Google :
  ```python
  def fonction_exemple(param1: type, param2: type) -> type_retour:
      """Description courte de la fonction.
  
      Description détaillée si nécessaire.
  
      Args:
          param1: Description du premier paramètre.
          param2: Description du deuxième paramètre.
  
      Returns:
          Description de la valeur de retour.
  
      Raises:
          TypeError: Si les types des paramètres sont incorrects.
      """
  ```

### Documentation du projet

- Maintenir à jour le README.md
- Ajouter des exemples d'utilisation
- Documenter les décisions d'architecture importantes

## Déploiement

### Environnement de développement

```bash
streamlit run app/streamlit_app.py
```

### Production

1. Construire l'image Docker :
   ```bash
   docker build -t hotel-revenue-optimizer .
   ```

2. Exécuter le conteneur :
   ```bash
   docker run -p 8501:8501 hotel-revenue-optimizer
   ```

## Dépannage

### Problèmes courants

1. **Erreurs d'importation**
   - Vérifiez que votre PYTHONPATH est correctement défini
   - Assurez-vous que tous les packages sont installés

2. **Problèmes de dépendances**
   - Mettez à jour pip : `pip install --upgrade pip`
   - Réinstallez les dépendances : `pip install -r requirements.txt`

3. **Problèmes avec Streamlit**
   - Vérifiez que le port 8501 est disponible
   - Assurez-vous que toutes les variables d'environnement nécessaires sont définies

### Débogage

- Utilisez `print()` pour le débogage simple
- Pour un débogage plus avancé, utilisez le module `pdb` :
  ```python
  import pdb; pdb.set_trace()  # Point d'arrêt
  ```

## Ressources

- [Documentation Python](https://docs.python.org/3/)
- [Documentation Streamlit](https://docs.streamlit.io/)
- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
