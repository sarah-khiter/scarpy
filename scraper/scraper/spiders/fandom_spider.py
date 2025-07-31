import scrapy
from ..items import CharacterItem
import re
from urllib.parse import urljoin, urlparse
from scrapy.exceptions import CloseSpider
import os
import json

class FandomSpider(scrapy.Spider):
    name = 'fandom'
    
    def __init__(self, fandom_url=None, *args, **kwargs):
        super(FandomSpider, self).__init__(*args, **kwargs)
        if not fandom_url:
            raise ValueError("L'URL du wiki Fandom est requise")
            
        # Nettoyer l'URL fournie
        self.fandom_url = fandom_url.strip()
        if not self.fandom_url.startswith(('http://', 'https://')):
            self.fandom_url = 'https://' + self.fandom_url
            
        # S'assurer que c'est une URL Fandom
        if 'fandom.com' not in self.fandom_url:
            raise ValueError("L'URL doit être une URL Fandom valide")
            
        # Extraire le nom du wiki de l'URL
        parsed_url = urlparse(self.fandom_url)
        self.wiki_name = parsed_url.netloc.split('.')[0]
        
        # Créer le dossier data s'il n'existe pas
        current_dir = os.path.dirname(os.path.abspath(__file__))  # dossier spiders
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # dossier racine
        self.data_dir = os.path.join(project_root, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Définir le chemin du fichier JSON
        self.json_file = os.path.join(self.data_dir, f'{self.wiki_name}_characters.json')
        print(f"\nLes données seront sauvegardées dans : {self.json_file}")
        
        self.start_urls = [self.fandom_url]
        self.visited_urls = set()
        self.character_count = 0
        self.character_limit = 50
        self.items = []  # Liste pour stocker les items avant sauvegarde

    def save_items(self):
        """Sauvegarde les items dans le fichier JSON"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
            print(f"\nDonnées sauvegardées dans {self.json_file}")

    def check_limit(self):
        if self.character_count >= self.character_limit:
            print(f"\nLimite de {self.character_limit} personnages atteinte. Arrêt du scraping.")
            self.save_items()  # Sauvegarde finale avant l'arrêt
            raise CloseSpider(f'Limite de {self.character_limit} personnages atteinte')

    def clean_image_url(self, url):
        if not url:
            return None
        if url.startswith('//'):
            url = 'https:' + url
        url = re.sub(r'/revision/latest.*$', '', url)
        url = re.sub(r'/scale-to-.*?(?=/|$)', '', url)
        url = url.split('?')[0]
        return url

    def parse(self, response):
        print("\nExploring page:", response.url)
        
        # Cherche le lien vers la catégorie des personnages
        character_links = response.css('a[href*="Category:Characters"]::attr(href), a[href*="Characters"]::attr(href)').getall()
        
        for link in character_links:
            if link and link not in self.visited_urls:
                self.visited_urls.add(link)
                absolute_url = urljoin(response.url, link)
                print(f"\nSuivant le lien vers la liste des personnages : {link}")
                yield response.follow(link, self.parse_character_list)

    def parse_character_list(self, response):
        print("\nExploring character list:", response.url)
        
        # Extraction des personnages depuis la structure spécifique de Fandom
        character_items = response.css('.category-page__member')
        print(f"\nTrouvé {len(character_items)} personnages potentiels")
        
        for item in character_items:
            # Vérifie si on a atteint la limite
            if self.character_count >= self.character_limit:
                return
            
            # Extraction des données du personnage directement depuis la liste
            character = CharacterItem()
            
            # Nom du personnage
            name = item.css('.category-page__member-link::text').get()
            if not name:
                continue
            character['name'] = name.strip()
            
            # URL du personnage
            char_url = item.css('.category-page__member-link::attr(href)').get()
            if char_url:
                character['url'] = urljoin(response.url, char_url)
            
            # Image du personnage
            image_url = item.css('.category-page__member-thumbnail::attr(src)').get()
            if not image_url:
                image_url = item.css('.category-page__member-thumbnail::attr(data-src)').get()
            
            if image_url:
                cleaned_url = self.clean_image_url(image_url)
                if cleaned_url:
                    character['image_url'] = cleaned_url
                    self.character_count += 1
                    
                    # Convertir l'item en dictionnaire et l'ajouter à la liste
                    item_dict = dict(character)
                    self.items.append(item_dict)
                    
                    # Sauvegarder après chaque nouvel item
                    self.save_items()
                    
                    print("\n" + "="*50)
                    print(f"Character #{self.character_count}/{self.character_limit}: {character['name']}")
                    print(f"URL: {character['url']}")
                    print(f"Image: {character['image_url']}")
                    print(f"Sauvegardé dans : {self.json_file}")
                    print("="*50)
                    
                    if self.character_count >= self.character_limit:
                        print(f"\nLimite de {self.character_limit} personnages atteinte!")
                    
                    yield character

        # Vérifie s'il y a une page suivante
        next_page = response.css('a.category-page__pagination-next::attr(href)').get()
        if next_page and self.character_count < self.character_limit:
            yield response.follow(next_page, self.parse_character_list)

    def closed(self, reason):
        # Sauvegarde finale
        self.save_items()
        
        if reason == f'Limite de {self.character_limit} personnages atteinte':
            print(f"\nScraping terminé : limite de {self.character_limit} personnages atteinte.")
        else:
            print(f"\nScraping terminé ! {self.character_count} personnages trouvés.")