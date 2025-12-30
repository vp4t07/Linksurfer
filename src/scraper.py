import os
import json
import random
import ssl
import urllib.request as UR
from datetime import datetime
from src.database import DatabaseManager

# Dynamic Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYWORDS_PATH = os.path.join(BASE_DIR, 'data', 'keywords.json')

class KeywordManager:
    def __init__(self):
        self.word_dict = {}
        if os.path.exists(KEYWORDS_PATH):
            with open(KEYWORDS_PATH, 'r') as f:
                self.word_dict = json.load(f)
        else:
            print("Warning: keywords.json not found in data folder.")

    def get_category(self, keyword):
        # Case-insensitive lookup
        return self.word_dict.get(keyword) or self.word_dict.get(keyword.capitalize())

class WebParser:
    """
    Custom Lexical Analysis to extract content from HTML 
    without external libraries like BeautifulSoup.
    """
    def __init__(self, html_content):
        self.html = html_content
        self.paragraphs = []
        self.headings = []
        self.links = []

    def _extract_tag_content(self, tag_start):
        """Helper to extract content between <tag> and next <"""
        results = []
        j = 0
        while j < len(self.html):
            # Find start of tag, e.g. "<p"
            if self.html[j:j+len(tag_start)] == tag_start:
                # Find end of the opening tag ">"
                tag_close_idx = self.html.find('>', j)
                if tag_close_idx != -1:
                    # Content starts after ">"
                    content_start = tag_close_idx + 1
                    # Content ends at the next "<"
                    content_end = self.html.find('<', content_start)
                    if content_end != -1:
                        raw_text = self.html[content_start:content_end]
                        clean_text = self._clean_text(raw_text)
                        if clean_text:
                            results.append(clean_text)
                        j = content_end
            j += 1
        return results

    def extract_paragraphs(self):
        self.paragraphs = self._extract_tag_content('<p')
        return self.paragraphs

    def extract_headings(self):
        # Simplified to catch h1, h2, etc. logic could be expanded
        self.headings = self._extract_tag_content('<h')
        return self.headings

    def extract_links(self):
        j = 0
        while j < len(self.html):
            if self.html[j:j+4] == 'href':
                # Find first quote
                start_quote = self.html.find('"', j)
                if start_quote != -1:
                    # Find closing quote
                    end_quote = self.html.find('"', start_quote + 1)
                    if end_quote != -1:
                        link = self.html[start_quote+1:end_quote]
                        if link.startswith('http'):
                            self.links.append(link)
            j += 1
        return self.links

    @staticmethod
    def _clean_text(text):
        """Decodes common HTML entities."""
        return text.replace("&#x27;", "'").replace("&amp;", "&").replace('&quot;', '"').strip()

class Scraper:
    def __init__(self, url, recursive=False):
        self.url = url
        self.recursive = recursive
        self.db = DatabaseManager()
        self.keywords_manager = KeywordManager()
        
        # Bypass SSL verification for educational scraping
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def generate_web_id(self):
        """Generates a unique ID ensuring no collision in DB."""
        while True:
            web_id = str(random.randint(0, 10**15))
            # Check if exists
            exists = self.db.execute_read('SELECT webpage_ID FROM webpage WHERE webpage_ID=?', (web_id,))
            if not exists:
                return web_id

    def fetch_html(self):
        try:
            print(f"Fetching: {self.url}")
            # User-agent helps avoid some 403 errors
            req = UR.Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
            response = UR.urlopen(req, context=self.ctx)
            return str(response.read())
        except Exception as e:
            print(f"Error scraping {self.url}: {e}")
            return None

    def analyze_content(self, paragraphs):
        """
        Counts keyword frequency and generates a summary.
        """
        stats = {}
        summary_words = []
        
        full_text = " ".join(paragraphs)
        words = full_text.split(" ")
        
        for word in words:
            clean_word = word.strip().strip('.,;()[]"')
            if not clean_word:
                continue
            
            # Check if this word is in our dictionary
            cat = self.keywords_manager.get_category(clean_word)
            if cat:
                # It's a keyword, count it
                key = clean_word.capitalize()
                stats[key] = stats.get(key, 0) + 1
            
            # Build summary (take first ~50 valid words)
            if len(summary_words) < 50:
                summary_words.append(clean_word)

        summary_text = " ".join(summary_words) + "..."
        return stats, summary_text

    def run(self):
        # 1. Check uniqueness
        if self.db.check_link_exists(self.url):
            print("URL already indexed.")
            return

        # 2. Fetch
        html = self.fetch_html()
        if not html:
            return

        # 3. Parse
        parser = WebParser(html)
        paragraphs = parser.extract_paragraphs()
        headings = parser.extract_headings()
        links = parser.extract_links()

        if not paragraphs:
            print("No text content found.")
            return

        # 4. Analyze
        web_id = self.generate_web_id()
        keyword_stats, summary = self.analyze_content(paragraphs)
        
        # 5. Calculate Categories
        # Initialize 12 categories
        categories = {
            "Finance": 0, "Health": 0, "Science": 0, "Technology": 0,
            "UK_Politics": 0, "Military": 0, "America": 0, "History": 0,
            "Geography": 0, "Literature": 0, "Sport": 0, "Politics": 0
        }

        for word, count in keyword_stats.items():
            cat = self.keywords_manager.get_category(word)
            if cat and cat in categories:
                categories[cat] += count
            
            # Store keyword occurrence
            self.db.add_keyword_record(word, count, web_id)

        # 6. Store Data
        # Extract owner from URL (e.g. bbc.co.uk)
        try:
            owner = self.url.split('/')[2]
        except:
            owner = "Unknown"

        self.db.add_metadata_record(self.url, owner, ";".join(headings[:5]), ";".join(paragraphs[:5]), datetime.now())
        self.db.add_webpage_record(web_id, self.url, summary)
        
        for cat, count in categories.items():
            self.db.add_category_record(cat, count, web_id)

        print(f"Successfully indexed {self.url} with ID {web_id}")

        # 7. Recursive Crawl
        if self.recursive:
            print(f"Found {len(links)} links. Crawling first 5...")
            for link in links[:5]:
                # Recursive call
                crawler = Scraper(link, recursive=False)
                crawler.run()