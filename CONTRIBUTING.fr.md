# Guide du Contributeur

Merci de votre intérêt pour contribuer à Hotel Revenue Optimizer ! Ce guide vous aidera à contribuer efficacement au projet.

## Table des Matières

1. [Code de Conduite](#code-de-conduite)
2. [Comment Contribuer](#comment-contribuer)
   - [Signaler un Problème](#signaler-un-problème)
   - [Proposer une Amélioration](#proposer-une-amélioration)
   - [Soumettre du Code](#soumettre-du-code)
3. [Environnement de Développement](#environnement-de-développement)
4. [Tests](#tests)
5. [Style de Code](#style-de-code)
6. [Revue de Code](#revue-de-code)
7. [Questions](#questions)

## Code de Conduite

Ce projet et tous les participants sont régis par notre [Code de Conduite](CODE_OF_CONDUCT.md). En participant, vous êtes tenu de respecter ce code. Merci de signaler tout comportement inacceptable à [EMAIL].

## Comment Contribuer

### Signaler un Problème

Avant de signaler un problème :

1. Vérifiez que le problème n'a pas déjà été signalé dans les [problèmes existants](https://github.com/votre-utilisateur/hotel-revenue-optimizer/issues).
2. Si le problème n'existe pas, créez-en un nouveau avec :
   - Un titre clair et descriptif
   - Une description détaillée du problème
   - Les étapes pour reproduire le problème
   - Le comportement attendu
   - Captures d'écran ou exemples de code si nécessaire
   - Version du projet et configuration système

### Proposer une Amélioration

1. Vérifiez que l'amélioration n'a pas déjà été proposée.
2. Ouvrez une issue pour discuter de votre idée avant de commencer à coder.
3. Une fois l'idée approuvée, vous pouvez commencer à travailler dessus.

### Soumettre du Code

1. **Forkez** le dépôt et créez une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```

2. **Commitez** vos changements avec des messages clairs :
   ```bash
   git commit -m "Ajouter une nouvelle fonctionnalité"
   ```

3. **Poussez** vos changements vers votre fork :
   ```bash
   git push origin feature/nouvelle-fonctionnalite
   ```

4. **Ouvrez une Pull Request** vers la branche `main` du dépôt principal.

## Environnement de Développement

### Prérequis

- Python 3.8+
- pip
- git

### Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/hotel-revenue-optimizer.git
   cd hotel-revenue-optimizer
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   # Sur Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Sur macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Configurez les variables d'environnement :
   ```bash
   cp .env.example .env
   # Modifiez .env selon vos besoins
   ```

## Tests

Avant de soumettre votre code, assurez-vous que tous les tests passent :

```bash
# Exécuter tous les tests
pytest

# Exécuter les tests avec couverture
pytest --cov=src

# Vérifier la qualité du code
flake8 src/
black --check src/
isort --check-only src/
```

## Style de Code

- Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez des noms de variables et de fonctions descriptifs
- Ajoutez des docstrings pour les fonctions et les classes
- Écrivez des tests pour les nouvelles fonctionnalités

### Formatage Automatique

Nous utilisons des outils pour maintenir une cohérence du code :

```bash
# Formater le code avec black
black src/

# Trier les imports avec isort
isort src/
```

## Revue de Code

- Toutes les modifications doivent passer par une Pull Request
- Au moins un mainteneur doit approuver la PR avant la fusion
- Les tests doivent tous passer avant la fusion
- La couverture de code doit être maintenue ou améliorée

## Questions

Pour toute question, vous pouvez :
- Ouvrir une discussion dans la section [Discussions](https://github.com/votre-utilisateur/hotel-revenue-optimizer/discussions)
- Nous contacter à [EMAIL]

---
*Merci de contribuer à Hotel Revenue Optimizer !*
