# Mainteneurs du Projet

Ce document décrit les rôles et responsabilités des mainteneurs du projet Hotel Revenue Optimizer.

## Rôles et Responsabilités

### Mainteneurs Principaux
- Superviser la direction générale du projet
- Examiner et fusionner les pull requests
- Gérer les versions et les publications
- Prendre les décisions techniques importantes
- Maintenir la qualité du code et de la documentation

### Développeurs Actifs
- Réviser le code des autres contributeurs
- Aider à la résolution des problèmes
- Maintenir la documentation technique
- Participer aux discussions sur l'architecture

## Processus de Revue de Code

1. Toutes les modifications doivent passer par une Pull Request (PR)
2. Au moins un mainteneur doit approuver une PR avant la fusion
3. Les tests doivent tous passer avant la fusion
4. La couverture de code doit être maintenue ou améliorée
5. La documentation doit être mise à jour pour refléter les changements

## Gestion des Versions

Le projet suit le [Versionnage Sémantique](https://semver.org/) (SemVer) :

- **MAJEUR** : Changements incompatibles avec les versions précédentes
- **MINEUR** : Nouvelles fonctionnalités rétrocompatibles
- **PATCH** : Corrections de bugs rétrocompatibles

## Publication d'une Nouvelle Version

1. Mettre à jour le numéro de version dans `src/__version__.py`
2. Mettre à jour le fichier `CHANGELOG.md`
3. Créer un tag Git avec la version : `git tag -a vX.Y.Z -m "Version X.Y.Z"`
4. Pousser le tag : `git push origin vX.Y.Z`
5. Créer une release sur GitHub avec les notes de version

## Communication

- Les problèmes importants doivent être discutés dans les issues GitHub
- Les décisions techniques majeures doivent être documentées dans les ADR (Architecture Decision Records)
- La communication doit rester professionnelle et respectueuse

## Mainteneurs Actuels

- [David Michel-Larrieux](https://github.com/DavidMichelLarrieux) - Créateur et mainteneur principal

## Devenir Mainteneur

Les contributeurs réguliers peuvent être invités à devenir mainteneurs. Les critères incluent :
- Contributions significatives et de haute qualité
- Compréhension approfondie du codebase
- Engagement envers le projet à long terme
- Capacité à travailler en équipe et à aider les autres contributeurs
