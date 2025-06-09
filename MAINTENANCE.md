# Guide de Maintenance

Ce document fournit des instructions pour la maintenance et la mise à jour du projet Hotel Revenue Optimizer.

## Table des Matières

1. [Mises à Jour des Dépendances](#mises-à-jour-des-dépendances)
2. [Gestion des Versions](#gestion-des-versions)
3. [Sauvegarde des Données](#sauvegarde-des-données)
4. [Surveillance](#surveillance)
5. [Maintenance Préventive](#maintenance-préventive)
6. [Dépannage](#dépannage)
7. [Sécurité](#sécurité)
8. [Documentation](#documentation)

## Mises à Jour des Dépendances

### Vérification des Mises à Jour

```bash
# Voir les packages obsolètes
pip list --outdated

# Mettre à jour pip
pip install --upgrade pip

# Mettre à jour un package spécifique
pip install --upgrade nom_du_package

# Mettre à jour tous les packages (à utiliser avec précaution)
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```

### Mise à Jour des Fichiers de Dépendances

Après la mise à jour des packages, mettez à jour les fichiers de dépendances :

```bash
# Générer un nouveau requirements.txt
pip freeze > requirements.txt

# Pour le développement
pip freeze | findstr -v "^#" > requirements-dev.txt
```

## Gestion des Versions

### Numérotation des Versions

Le projet suit le versionnage sémantique (SemVer) : `MAJEUR.MINEUR.PATCH`

- **MAJEUR** : Changements incompatibles avec les versions précédentes
- **MINEUR** : Nouvelles fonctionnalités rétrocompatibles
- **PATCH** : Corrections de bugs rétrocompatibles

### Processus de Publication

1. Mettre à jour le numéro de version dans `src/__version__.py`
2. Mettre à jour le fichier `CHANGELOG.md`
3. Créer un tag Git :
   ```bash
   git tag -a vX.Y.Z -m "Version X.Y.Z"
   ```
4. Pousser le tag :
   ```bash
   git push origin vX.Y.Z
   ```
5. Créer une release sur GitHub avec les notes de version

## Sauvegarde des Données

### Données Importantes à Sauvegarder

- Fichiers de configuration (`.env`)
- Modèles entraînés dans `models/saved_models/`
- Données brutes importantes dans `data/raw/`
- Base de données (si utilisée)

### Fréquence des Sauvegardes

- **Quotidienne** : Données de production
- **Hebdomadaire** : Modèles entraînés
- **Mensuelle** : Archives complètes

## Surveillance

### Métriques à Surveiller

- Utilisation de la mémoire et du CPU
- Temps de réponse de l'application
- Erreurs dans les logs
- Espace disque disponible
- État des sauvegardes

### Outils Recommandés

- **Logs** : Utiliser le module `logging` de Python
- **Surveillance** : Prometheus, Grafana
- **Alertes** : Sentry, Rollbar

## Maintenance Préventive

### Tâches Récurrentes

| Tâche | Fréquence | Description |
|-------|-----------|-------------|
| Nettoyage des logs | Hebdomadaire | Supprimer les anciens fichiers de log |
| Vérification de l'espace disque | Quotidienne | S'assurer qu'il reste suffisamment d'espace |
| Mise à jour des dépendances | Mensuelle | Mettre à jour les packages Python |
| Sauvegarde des données | Selon la politique | Voir section Sauvegarde |
| Revue des logs d'erreur | Quotidienne | Identifier les problèmes récurrents |

### Nettoyage

```bash
# Supprimer les fichiers .pyc et les dossiers __pycache__
find . -type d -name "__pycache__" -exec rm -r {} +
find . -name "*.pyc" -delete

# Nettoyer les fichiers temporaires
rm -rf .pytest_cache/
rm -rf .mypy_cache/
rm -rf .coverage
rm -rf htmlcov/
```

## Dépannage

### Problèmes Courants

#### L'application ne démarre pas
1. Vérifiez que tous les services requis sont en cours d'exécution
2. Vérifiez les logs d'erreur
3. Vérifiez que le port n'est pas déjà utilisé

#### Problèmes de Performances
1. Vérifiez l'utilisation des ressources (CPU, mémoire)
2. Optimisez les requêtes de base de données
3. Mettez en cache les résultats coûteux

#### Erreurs d'Importation
1. Vérifiez que l'environnement virtuel est activé
2. Vérifiez que toutes les dépendances sont installées
3. Vérifiez le PYTHONPATH

### Journalisation

Les logs sont essentiels pour le dépannage. Assurez-vous que :
- Les logs contiennent suffisamment d'informations
- Les niveaux de log sont correctement configurés
- Les fichiers de log sont correctement archivés

## Sécurité

### Mises à Jour de Sécurité

- Surveillez les vulnérabilités dans les dépendances avec `safety check`
- Abonnez-vous aux alertes de sécurité pour les packages utilisés
- Appliquez les correctifs de sécurité dès que possible

### Bonnes Pratiques

- Ne stockez jamais de données sensibles dans le code source
- Utilisez des variables d'environnement pour les informations sensibles
- Limitez les permissions aux fichiers et dossiers sensibles
- Mettez à jour régulièrement les clés et mots de passe

## Documentation

### Mise à Jour de la Documentation

La documentation doit être mise à jour à chaque :
- Ajout de nouvelles fonctionnalités
- Modification du comportement existant
- Correction de bugs importants
- Changement d'API

### Génération de la Documentation

Si vous utilisez Sphinx pour la documentation :

```bash
cd docs
make clean
make html
```

La documentation générée sera disponible dans `docs/_build/html/`.

## Ressources

- [Documentation Python](https://docs.python.org/3/)
- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
