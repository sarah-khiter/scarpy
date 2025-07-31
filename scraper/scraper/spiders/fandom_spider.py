import scrapy
from ..items import CharacterItem
import json
import re
from scrapy.exporters import JsonItemExporter
import urllib.parse
import os

class FandomSpider(scrapy.Spider):
    name = 'fandom'
    
    # Default URL for League of Legends Wiki
    DEFAULT_FANDOM_URL = "https://leagueoflegends.fandom.com/wiki/League_of_Legends_Wiki"
    
    custom_settings = {
        'FEEDS': {
            '../data/characters.json': {  # Changed path to data directory
                'format': 'json',
                'encoding': 'utf8',
                'indent': 2,
                'overwrite': True,
            },
        },
    }
    
    def __init__(self, fandom_url=None, *args, **kwargs):
        super(FandomSpider, self).__init__(*args, **kwargs)
        self.start_urls = [fandom_url if fandom_url else self.DEFAULT_FANDOM_URL]
        self.visited_urls = set()
        self.character_count = 0
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)

    def clean_image_url(self, url):
        if not url:
            return None
            
        # Ensure we have a full URL
        if url.startswith('//'):
            url = 'https:' + url
            
        # Remove any scaling parameters but keep the original image
        url = re.sub(r'/scale-to-width-down/\d+', '', url)
        url = re.sub(r'/scale-to-height-down/\d+', '', url)
        url = re.sub(r'/scale-to-width/\d+', '', url)
        url = re.sub(r'/scale-to-height/\d+', '', url)
        
        # Remove revision part if present while keeping the image path
        url = re.sub(r'/revision/latest.*$', '', url)
        
        # Remove any query parameters
        url = url.split('?')[0]
        
        return url

    def parse(self, response):
        print("\nExploring page:", response.url)
        # First find all gallery items
        gallery_links = response.css('div.wikia-gallery-item a.link-internal::attr(href)').getall()
        
        if gallery_links:
            print(f"Found {len(gallery_links)} gallery links")
        
        # Follow each gallery link
        for link in gallery_links:
            if link and link not in self.visited_urls:
                self.visited_urls.add(link)
                # If it's a champion/character link, follow it to the list page
                if any(keyword in link.lower() for keyword in ['/champion', '/character', '/heroes']):
                    print(f"Following character list link: {link}")
                    yield response.follow(link, self.parse_character_list)
                else:
                    yield response.follow(link, self.parse)

    def parse_character_list(self, response):
        print("\nExploring character list:", response.url)
        # Look for links to individual character pages
        character_links = response.css('div.article-table a::attr(href), table.sortable a::attr(href), div.character-grid a::attr(href)').getall()
        
        if character_links:
            print(f"Found {len(character_links)} character links")
        
        # Also check for category links that might contain character pages
        category_links = response.css('a[href*="Category:Characters"]::attr(href)').getall()
        
        # Follow character links
        for link in character_links:
            if link and link not in self.visited_urls:
                self.visited_urls.add(link)
                yield response.follow(link, self.parse_character)
                
        # Follow category links
        for link in category_links:
            if link and link not in self.visited_urls:
                self.visited_urls.add(link)
                yield response.follow(link, self.parse_category)

    def parse_category(self, response):
        print("\nExploring category:", response.url)
        # Extract character links from category page
        character_links = response.css('div.category-page__members a::attr(href)').getall()
        
        if character_links:
            print(f"Found {len(character_links)} characters in category")
            
        for link in character_links:
            if link and link not in self.visited_urls:
                self.visited_urls.add(link)
                yield response.follow(link, self.parse_character)

    def parse_character(self, response):
        if not self.is_character_page(response):
            return

        item = CharacterItem()
        
        # Extract name
        item['name'] = response.css('h1.page-header__title::text').get() or \
                      response.css('h1::text').get()
        if item['name']:
            item['name'] = item['name'].strip()
        else:
            return None

        # Store source URL
        item['url'] = response.url
        
        # Extract image URL directly from the page
        character_name = item['name'].split('(')[0].strip()
        
        # Try different image selectors
        image_selectors = [
            f'img[alt*="{character_name} Render"]::attr(src)',
            f'img[alt*="{character_name} Portrait"]::attr(src)',
            'figure.pi-image img::attr(src)',
            '.infobox-image img::attr(src)',
            '.champion-image img::attr(src)',
            '.character-image img::attr(src)',
            'aside.portable-infobox img::attr(src)'
        ]
        
        for selector in image_selectors:
            image_url = response.css(selector).get()
            if image_url:
                cleaned_url = self.clean_image_url(image_url)
                if cleaned_url:
                    item['image_url'] = cleaned_url
                    self.character_count += 1
                    print("\n" + "="*50)
                    print(f"Character #{self.character_count}: {item['name']}")
                    print(f"URL: {item['url']}")
                    print(f"Image: {item['image_url']}")
                    print("="*50)
                    yield item
                    break
        
        if not item.get('image_url'):
            print(f"Warning: No valid image found for {item['name']}")

    def is_character_page(self, response):
        # More robust character page detection
        indicators = [
            # Check for character infobox
            response.css('.portable-infobox'),
            # Check for common character information labels
            response.css('.pi-data-label:contains("Status")'),
            response.css('.pi-data-label:contains("Species")'),
            response.css('.pi-data-label:contains("Gender")'),
            response.css('.pi-data-label:contains("Occupation")'),
            response.css('.pi-data-label:contains("Affiliation")'),
            # Check URL patterns that often indicate character pages
            'characters/' in response.url.lower(),
            '/character/' in response.url.lower(),
            '/champion/' in response.url.lower(),
            '/hero/' in response.url.lower()
        ]
        # Page is likely a character page if it has at least 2 indicators
        return sum(bool(i) for i in indicators) >= 2

    def closed(self, reason):
        print(f"\nScraping finished! Found {self.character_count} characters.")