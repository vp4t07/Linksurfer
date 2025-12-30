import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="linksurfer.db"):
        # Sets DB path relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, 'data', db_name)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        # Optional: Add table creation logic here if needed for a fresh install
        pass

    def execute_write(self, query, params=()):
        """Executes INSERT, UPDATE, DELETE queries safely."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def execute_read(self, query, params=(), fetch_all=False):
        """Executes SELECT queries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch_all:
                return cursor.fetchall()
            return cursor.fetchone()

    # --- Read Methods ---

    def get_recent_files(self, limit=10):
        query = 'SELECT url FROM Metadata ORDER BY date ASC LIMIT ?'
        return self.execute_read(query, (limit,), fetch_all=True)

    def check_link_exists(self, url):
        query = 'SELECT webpage_ID FROM webpage WHERE url=?'
        result = self.execute_read(query, (url,))
        return result is not None

    def get_web_id(self, url):
        result = self.execute_read('SELECT webpage_ID FROM webpage WHERE url=?', (url,))
        return result[0] if result else None

    def get_summary(self, url):
        result = self.execute_read('SELECT summary FROM webpage WHERE url=?', (url,))
        return result[0] if result else "No summary available."

    def get_keywords(self, url):
        web_id = self.get_web_id(url)
        if web_id:
            query = 'SELECT keyword FROM Keywords WHERE webpage_ID=? ORDER BY keyword_count DESC'
            results = self.execute_read(query, (web_id,), fetch_all=True)
            return [r[0] for r in results]
        return []

    def get_categories_by_url(self, url):
        web_id = self.get_web_id(url)
        if web_id:
            query = 'SELECT category FROM Category WHERE webpage_ID=? ORDER BY category_count DESC'
            return self.execute_read(query, (web_id,), fetch_all=True)
        return []

    def get_urls_by_category(self, category):
        # Joins tables to find URLs belonging to a specific category
        query = '''
            SELECT w.url 
            FROM webpage w
            JOIN Category c ON w.webpage_ID = c.webpage_ID
            WHERE c.category = ?
            ORDER BY c.category_count DESC
        '''
        return self.execute_read(query, (category,), fetch_all=True)

    # --- Write Methods ---

    def add_metadata_record(self, url, owner, heading, paragraph, date):
        query = "INSERT INTO Metadata VALUES (?, ?, ?, ?, ?)"
        self.execute_write(query, (url, owner, heading, paragraph, date))

    def add_webpage_record(self, web_id, url, summary):
        query = "INSERT INTO webpage VALUES (?, ?, ?)"
        self.execute_write(query, (web_id, url, summary))
        
    def add_category_record(self, category, count, web_id):
        query = "INSERT INTO Category VALUES (?, ?, ?)"
        self.execute_write(query, (category, count, web_id))

    def add_keyword_record(self, keyword, count, web_id):
        query = "INSERT INTO Keywords VALUES (?, ?, ?)"
        self.execute_write(query, (keyword, count, web_id))

    def update_metadata(self, headings, paragraphs, url):
        query = "UPDATE Metadata SET heading=?, paragraph=? WHERE url=?"
        self.execute_write(query, (headings, paragraphs, url))