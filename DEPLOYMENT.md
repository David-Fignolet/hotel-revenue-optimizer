# Guide de Déploiement

Ce document fournit des instructions pour déployer l'application Hotel Revenue Optimizer dans différents environnements.

## Table des Matières

1. [Environnements](#environnements)
2. [Prérequis](#prérequis)
3. [Déploiement Local](#déploiement-local)
4. [Déploiement avec Docker](#déploiement-avec-docker)
5. [Déploiement sur un Serveur Linux](#déploiement-sur-un-serveur-linux)
6. [Déploiement sur le Cloud](#déploiement-sur-le-cloud)
7. [Configuration du Reverse Proxy](#configuration-du-reverse-proxy)
8. [Mise à Jour](#mise-à-jour)
9. [Dépannage](#dépannage)

## Environnements

- **Développement** : Pour le développement local
- **Staging** : Pour les tests d'intégration
- **Production** : Environnement de production

## Prérequis

- Python 3.8+
- pip
- git
- (Optionnel) Docker et Docker Compose
- (Optionnel) Nginx (pour le reverse proxy)

## Déploiement Local

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/hotel-revenue-optimizer.git
cd hotel-revenue-optimizer
```

### 2. Créer et activer un environnement virtuel

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
# Modifier .env selon vos besoins
```

### 5. Lancer l'application

```bash
streamlit run app/streamlit_app.py
```

L'application sera disponible à l'adresse : http://localhost:8501

## Déploiement avec Docker

### 1. Construire l'image Docker

```bash
docker build -t hotel-revenue-optimizer .
```

### 2. Lancer le conteneur

```bash
docker run -d --name hotel-app -p 8501:8501 hotel-revenue-optimizer
```

### 3. Utiliser Docker Compose (recommandé)

Créez un fichier `docker-compose.yml` :

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    restart: unless-stopped
```

Puis lancez :

```bash
docker-compose up -d
```

## Déploiement sur un Serveur Linux

### 1. Mettre à jour le système

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Installer les dépendances système

```bash
sudo apt install -y python3-pip python3-venv nginx
```

### 3. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/hotel-revenue-optimizer.git
cd hotel-revenue-optimizer
```

### 4. Configurer l'environnement

Suivez les étapes 2 à 4 de la section [Déploiement Local](#déploiement-local).

### 5. Configurer Gunicorn (optionnel)

Pour une meilleure performance en production :

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8501 app.streamlit_app:main
```

### 6. Configurer Nginx comme reverse proxy

Créez un fichier de configuration Nginx :

```bash
sudo nano /etc/nginx/sites-available/hotel-app
```

Avec le contenu :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Activez le site :

```bash
sudo ln -s /etc/nginx/sites-available/hotel-app /etc/nginx/sites-enabled/
sudo nginx -t  # Tester la configuration
sudo systemctl restart nginx
```

### 7. Configurer HTTPS avec Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

## Déploiement sur le Cloud

### Sur Heroku

1. Installez l'interface en ligne de commande Heroku
2. Connectez-vous : `heroku login`
3. Créez une nouvelle application : `heroku create nom-de-votre-app`
4. Définissez les variables d'environnement :
   ```bash
   heroku config:set STREAMLIT_SERVER_PORT=$PORT
   # Ajoutez d'autres variables d'environnement
   ```
5. Déployez : `git push heroku main`

### Sur AWS Elastic Beanstalk

1. Installez l'interface en ligne de commande EB
2. Initialisez l'application : `eb init -p python-3.8 hotel-app`
3. Créez un environnement : `eb create hotel-app-env`
4. Définissez les variables d'environnement via la console AWS
5. Déployez : `eb deploy`

## Configuration du Reverse Proxy

### Nginx

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }
}
```

### Apache

```apache
<VirtualHost *:80>
    ServerName votre-domaine.com
    
    ProxyPreserveHost On
    ProxyPass / http://localhost:8501/
    ProxyPassReverse / http://localhost:8501/
    
    # Pour WebSocket
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} =websocket [NC]
    RewriteRule /(.*) ws://localhost:8501/$1 [P,L]
    
    # Timeout pour les requêtes longues
    ProxyTimeout 300
</VirtualHost>
```

## Mise à Jour

### Mise à jour du Code

```bash
git pull origin main
pip install -r requirements.txt
# Redémarrer l'application
```

### Mise à jour des Données

1. Arrêter l'application
2. Sauvegarder les données existantes
3. Mettre à jour les données
4. Redémarrer l'application

## Dépannage

### Problèmes Courants

#### L'application ne démarre pas
- Vérifiez les logs : `docker logs nom-du-conteneur` ou `journalctl -u nom-du-service`
- Vérifiez que le port n'est pas déjà utilisé : `sudo lsof -i :8501`
- Vérifiez les variables d'environnement

#### Problèmes de Connexion
- Vérifiez les paramètres du pare-feu
- Vérifiez que le port est correctement exposé
- Vérifiez les logs d'erreur de Nginx/Apache

#### Problèmes de Performances
- Augmentez les ressources allouées au conteneur/service
- Optimisez les requêtes de base de données
- Mettez en cache les résultats coûteux

### Surveillance

- **Logs** : `docker logs -f nom-du-conteneur`
- **Ressources** : `htop`, `docker stats`
- **Réseau** : `netstat -tuln`

## Sécurité

- Mettez toujours à jour les dépendances
- Utilisez HTTPS
- Limitez l'accès aux ports sensibles
- Ne stockez pas de données sensibles dans le code source
- Utilisez des mots de passe forts et des clés d'API sécurisées

## Sauvegarde et Récupération

### Sauvegarde des Données

```bash
# Données
rsync -avz /chemin/vers/le/projet/data/ /chemin/de/sauvegarde/data_$(date +%Y%m%d)

# Modèles
rsync -avz /chemin/vers/le/projet/models/ /chemin/de/sauvegarde/models_$(date +%Y%m%d)

# Base de données (si applicable)
pg_dump -U utilisateur -d nom_de_la_base > backup_$(date +%Y%m%d).sql
```

### Récupération après Désastre

1. Restaurer les données à partir de la sauvegarde
2. Reconstruire l'environnement
3. Restaurer la base de données (si applicable)
4. Tester l'application
5. Mettre à jour le DNS si nécessaire
