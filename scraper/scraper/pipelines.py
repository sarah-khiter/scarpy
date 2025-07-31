# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from scrapy.exceptions import DropItem
from urllib.parse import urlparse
import aiohttp
import asyncio
import logging
from itemadapter import ItemAdapter
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor
import re


class ScraperPipeline:
    def process_item(self, item, spider):
        return item

class ValidationPipeline:
    """Pipeline pour valider les données de base"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Vérifications rapides sans appel réseau
        if not adapter.get('name') or not adapter.get('url'):
            raise DropItem(f"Item incomplet trouvé: {item}")
        
        # Validation basique d'URL sans appel réseau
        if not adapter['url'].startswith(('http://', 'https://')):
            raise DropItem(f"URL invalide trouvée: {adapter['url']}")
            
        return item

class OptimizedImagePipeline:
    """Pipeline optimisé pour valider les URLs d'images"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Cache pour stocker les résultats de validation d'image (TTL de 1 heure)
        self.image_cache = TTLCache(maxsize=1000, ttl=3600)
        # Expressions régulières compilées
        self.image_pattern = re.compile(r'\.(jpg|jpeg|png|gif)$', re.I)
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if not adapter.get('image_url'):
            raise DropItem(f"Item sans image trouvé: {adapter['name']}")
        
        image_url = adapter['image_url']
        
        # Vérification rapide du format de l'URL
        if not image_url.startswith(('http://', 'https://')):
            raise DropItem(f"URL d'image invalide pour {adapter['name']}")
        
        # Vérification rapide de l'extension
        if not self.image_pattern.search(image_url):
            # Si pas d'extension, vérifier si c'est une URL de Fandom connue
            if not any(x in image_url.lower() for x in ['/render', '/portrait', '/image']):
                raise DropItem(f"Format d'image non reconnu pour {adapter['name']}")
        
        # Utiliser le cache si disponible
        if image_url in self.image_cache:
            if not self.image_cache[image_url]:
                raise DropItem(f"Image précédemment invalide pour {adapter['name']}")
            return item
        
        # Marquer l'image comme valide dans le cache
        self.image_cache[image_url] = True
        return item

class DuplicatesPipeline:
    """Pipeline pour éliminer les doublons"""
    
    def __init__(self):
        self.seen = set()
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Créer une clé unique combinant nom et URL
        item_key = f"{adapter['name']}::{adapter['url']}"
        
        if item_key in self.seen:
            raise DropItem(f"Doublon trouvé: {adapter['name']}")
            
        self.seen.add(item_key)
        return item

class CleaningPipeline:
    """Pipeline pour nettoyer les données"""
    
    def __init__(self):
        # Compiler les expressions régulières une seule fois
        self.character_suffix = re.compile(r'\s*\(Character\)\s*$')
        self.url_params = re.compile(r'\?.*$')
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Nettoyer le nom
        if adapter.get('name'):
            name = adapter['name'].strip()
            name = self.character_suffix.sub('', name)
            adapter['name'] = name
        
        # Nettoyer les URLs
        if adapter.get('url'):
            adapter['url'] = self.url_params.sub('', adapter['url'])
        
        if adapter.get('image_url'):
            adapter['image_url'] = spider.clean_image_url(adapter['image_url'])
            
        return item
