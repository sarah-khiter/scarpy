# Fandom Wiki Scraper

Une application web permettant de scraper automatiquement les informations des personnages depuis n'importe quel wiki Fandom, avec une interface moderne pour visualiser et comparer les données.

## Fonctionnalités

### 1. Scraping Automatique
- Extraction des personnages depuis n'importe quel wiki Fandom
- Récupération des informations :
  - Nom du personnage
  - Image principale
  - Type/Race/Espèce
  - Rôle/Position
  - Classe/Classification
  - Origine/Nationalité
  - Affiliation
  - Occupation

### 2. Interface Utilisateur
- Design moderne avec thème sombre (violet et rouge)
- Affichage en grille des personnages
- Mode comparaison de personnages
- Liste des wikis déjà scrapés
- Feedback en temps réel pendant le scraping
- Gestion des erreurs avec messages explicites

### 3. Fonctionnalités Avancées
- Comparaison côte à côte de deux personnages
- Sauvegarde automatique des données par wiki
- Navigation entre les wikis scrapés
- Limitation à 50 personnages par wiki pour des performances optimales
- Gestion des images manquantes avec placeholder

## Architecture Technique

### Frontend (React)
- Interface responsive avec React
- Gestion d'état avec React Hooks
- Composants réutilisables
- Styles modulaires avec CSS personnalisé
- Animations et transitions fluides

### Backend (Flask)
- API RESTful avec Flask
- Endpoints :
  - `/scrape` : Lance le scraping d'un nouveau wiki
  - `/wikis` : Liste les wikis disponibles
  - `/wiki/<name>` : Récupère les données d'un wiki spécifique

### Scraper (Scrapy)
- Spider personnalisé pour les wikis Fandom
- Extraction intelligente des données
- Nettoyage des URLs d'images
- Gestion de la pagination
- Sauvegarde progressive des données

### Pipeline de Traitement
- **ValidationPipeline** : Vérifie l'intégrité des données extraites
- **OptimizedImagePipeline** :
  - Validation des URLs d'images
  - Nettoyage des URLs (suppression des paramètres de redimensionnement)
  - Cache des validations d'images pour optimiser les performances
- **DuplicatesPipeline** : Élimine les doublons basés sur le nom et l'URL
- **CleaningPipeline** :
  - Nettoyage des textes (espaces, caractères spéciaux)
  - Formatage cohérent des données
  - Validation des champs obligatoires

## Installation et Lancement

1. **Installation du Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

2. **Lancement du Backend**
   ```bash
   python server.py
   ```

3. **Accéder à l'Application**
   - Ouvrez votre navigateur
   - Accédez à `http://localhost:3000`

## Utilisation

1. **Scraper un Nouveau Wiki**
   - Collez l'URL d'un wiki Fandom dans la barre de recherche
   - Cliquez sur "Scraper"
   - Attendez que le scraping soit terminé

2. **Explorer les Données**
   - Parcourez la grille de personnages
   - Cliquez sur les cartes pour plus de détails
   - Utilisez le mode comparaison pour comparer deux personnages

3. **Naviguer Entre les Wikis**
   - Utilisez la liste des wikis scrapés
   - Cliquez sur un wiki pour charger ses données
   - Les données sont sauvegardées localement

## Structure des Données

Les données sont sauvegardées au format JSON :
```json
{
  "name": "Nom du Personnage",
  "url": "URL de la page",
  "image_url": "URL de l'image",
  "type": "Type/Race/Espèce",
  "role": "Rôle/Position",
  "class_name": "Classe",
  "origin": "Origine",
  "affiliation": "Affiliation",
  "occupation": "Occupation"
}
```

## Limitations Connues

- Maximum de 50 personnages par wiki
- Certaines informations peuvent être manquantes selon la structure du wiki
- Les images très grandes peuvent prendre du temps à charger
- Nécessite une connexion internet stable

## Améliorations Futures Possibles

- Support de plus de champs personnalisés
- Export des données en différents formats
- Filtres et recherche de personnages
- Mode sombre/clair
- Support multilingue
- Optimisation des performances de scraping