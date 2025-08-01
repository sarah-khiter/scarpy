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
            
            # Extraction des données de base du personnage
            name = item.css('.category-page__member-link::text').get()
            if not name:
                continue
            
            char_url = item.css('.category-page__member-link::attr(href)').get()
            if char_url:
                absolute_url = urljoin(response.url, char_url)
                # Créer un dictionnaire pour stocker les informations de base
                character_info = {
                    'name': name.strip(),
                    'url': absolute_url,
                }
                
                # Image du personnage
                image_url = item.css('.category-page__member-thumbnail::attr(src)').get()
                if not image_url:
                    image_url = item.css('.category-page__member-thumbnail::attr(data-src)').get()
                if image_url:
                    character_info['image_url'] = self.clean_image_url(image_url)
                
                # Suivre le lien vers la page du personnage
                yield response.follow(
                    absolute_url,
                    self.parse_character_page,
                    cb_kwargs={'character_info': character_info}
                )

        # Vérifie s'il y a une page suivante
        next_page = response.css('a.category-page__pagination-next::attr(href)').get()
        if next_page and self.character_count < self.character_limit:
            yield response.follow(next_page, self.parse_character_list)

    def parse_character_page(self, response, character_info):
        if self.character_count >= self.character_limit:
            return

        character = CharacterItem()
        character.update(character_info)

        # Recherche des informations dans l'infobox ou les sections pertinentes
        infobox = response.css('.portable-infobox')
        if infobox:
            # Parcourir tous les labels de l'infobox
            labels = infobox.css('.pi-data-label')
            values = infobox.css('.pi-data-value')
            for label, value in zip(labels, values):
                label_text = label.css('::text').get('').strip().lower()
                value_text = ' '.join(value.css('::text').getall()).strip()

                # Mapper les labels aux champs correspondants
                if any(keyword in label_text for keyword in ['type', 'espèce', 'race', 'species']):
                    character['type'] = value_text
                elif any(keyword in label_text for keyword in ['role', 'occupation', 'métier', 'job']):
                    character['role'] = value_text
                elif any(keyword in label_text for keyword in ['class', 'classe']):
                    character['class_name'] = value_text
                elif any(keyword in label_text for keyword in ['origin', 'origine', 'from', 'birthplace']):
                    character['origin'] = value_text

        # Si l'image n'a pas été trouvée dans la liste, essayer de la trouver sur la page
        if 'image_url' not in character:
            image_url = response.css('.pi-image-thumbnail::attr(src)').get()
            if image_url:
                character['image_url'] = self.clean_image_url(image_url)

        if 'image_url' in character:
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
            if character.get('type'):
                print(f"Type: {character['type']}")
            if character.get('role'):
                print(f"Role: {character['role']}")
            if character.get('class_name'):
                print(f"Class: {character['class_name']}")
            if character.get('origin'):
                print(f"Origin: {character['origin']}")
            print(f"Sauvegardé dans : {self.json_file}")
            print("="*50)
            
            if self.character_count >= self.character_limit:
                print(f"\nLimite de {self.character_limit} personnages atteinte!")
            
            yield character

    def closed(self, reason):
        # Sauvegarde finale
        self.save_items()
        
        if reason == f'Limite de {self.character_limit} personnages atteinte':
            print(f"\nScraping terminé : limite de {self.character_limit} personnages atteinte.")
        else:
            print(f"\nScraping terminé ! {self.character_count} personnages trouvés.")