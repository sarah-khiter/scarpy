from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
import re
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def get_wiki_name(url):
    """Extrait le nom du wiki de l'URL"""
    parsed_url = urlparse(url)
    return parsed_url.netloc.split('.')[0]

def validate_fandom_url(url):
    """Valide et nettoie l'URL Fandom"""
    if not url:
        return None, "L'URL est requise"
        
    # Nettoyer l'URL
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    # Vérifier que c'est une URL valide
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return None, "URL invalide"
    except:
        return None, "URL mal formée"
        
    # Vérifier que c'est une URL Fandom
    if 'fandom.com' not in url:
        return None, "L'URL doit être une URL Fandom valide"
        
    return url, None

def ensure_data_directory():
    """Crée le dossier data s'il n'existe pas"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    logger.info(f"Data directory ensured at: {data_dir}")
    return data_dir

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        logger.info("Received scrape request")
        data = request.json
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400
            
        url = data.get('url')
        logger.info(f"Processing URL: {url}")
        
        # Valider l'URL
        clean_url, error = validate_fandom_url(url)
        if error:
            logger.error(f"URL validation error: {error}")
            return jsonify({'error': error}), 400
            
        # Préparer le dossier de données
        data_dir = ensure_data_directory()
        wiki_name = get_wiki_name(clean_url)
        json_path = os.path.join(data_dir, f'{wiki_name}_characters.json')
        logger.info(f"Will save to: {json_path}")
        
        # Vérifier que le dossier scraper existe
        if not os.path.exists('scraper'):
            logger.error("Scraper directory not found")
            return jsonify({
                'error': 'Configuration error',
                'details': 'Scraper directory not found'
            }), 500
        
        # Configurer et exécuter le spider
        spider_cmd = [
            'scrapy', 'crawl', 'fandom',
            '-a', f'fandom_url={clean_url}',
            '--nolog'  # Éviter la pollution des logs
        ]
        
        logger.info(f"Executing command: {' '.join(spider_cmd)}")
        
        process = subprocess.Popen(
            spider_cmd,
            cwd='scraper',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        # Log the output
        if stdout:
            logger.info(f"Spider stdout: {stdout}")
        if stderr:
            logger.error(f"Spider stderr: {stderr}")
        
        # Gérer les erreurs de scraping
        if process.returncode != 0:
            error_msg = stderr.strip()
            logger.error(f"Scraping failed with return code {process.returncode}")
            return jsonify({
                'error': 'Erreur lors du scraping',
                'details': error_msg
            }), 500
            
        # Vérifier et lire les résultats
        if not os.path.exists(json_path):
            logger.error(f"JSON file not found at: {json_path}")
            return jsonify({
                'error': 'Aucune donnée générée',
                'details': 'Le fichier JSON n\'a pas été créé'
            }), 404
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                characters = json.load(f)
                
            if not characters:
                logger.warning("No characters found in JSON file")
                return jsonify({
                    'error': 'Aucun personnage trouvé',
                    'details': 'Le scraping n\'a trouvé aucun personnage'
                }), 404
                
            logger.info(f"Successfully scraped {len(characters)} characters")
            return jsonify({
                'success': True,
                'message': f'{len(characters)} personnages trouvés',
                'data': characters,
                'wiki_name': wiki_name
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return jsonify({
                'error': 'Erreur de lecture JSON',
                'details': str(e)
            }), 500
            
    except Exception as e:
        logger.exception("Unexpected error occurred")
        return jsonify({
            'error': 'Erreur inattendue',
            'details': str(e)
        }), 500

@app.route('/wikis', methods=['GET'])
def get_wikis():
    """Retourne la liste des wikis déjà scrapés"""
    try:
        data_dir = ensure_data_directory()
        wiki_files = [f for f in os.listdir(data_dir) if f.endswith('_characters.json')]
        wikis = []
        
        for file in wiki_files:
            wiki_name = file.replace('_characters.json', '')
            with open(os.path.join(data_dir, file), 'r', encoding='utf-8') as f:
                characters = json.load(f)
                wikis.append({
                    'name': wiki_name,
                    'character_count': len(characters)
                })
                
        return jsonify({
            'success': True,
            'wikis': wikis
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Erreur lors de la récupération des wikis',
            'details': str(e)
        }), 500

@app.route('/wiki/<wiki_name>', methods=['GET'])
def get_wiki_data(wiki_name):
    """Retourne les données d'un wiki spécifique"""
    try:
        data_dir = ensure_data_directory()
        json_path = os.path.join(data_dir, f'{wiki_name}_characters.json')
        
        if not os.path.exists(json_path):
            return jsonify({
                'error': 'Wiki non trouvé',
                'details': f'Aucune donnée pour le wiki {wiki_name}'
            }), 404
            
        with open(json_path, 'r', encoding='utf-8') as f:
            characters = json.load(f)
            
        return jsonify({
            'success': True,
            'wiki_name': wiki_name,
            'character_count': len(characters),
            'data': characters
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Erreur lors de la récupération des données',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 