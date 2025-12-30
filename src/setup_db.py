import sqlite3
import os

# Set path to data folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'linksurfer.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create Tables based on your original schema
    c.execute('''CREATE TABLE IF NOT EXISTS Metadata 
                 (url TEXT, owner TEXT, heading TEXT, paragraph TEXT, date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS webpage 
                 (webpage_ID TEXT, url TEXT, summary TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Category 
                 (category TEXT, category_count INTEGER, webpage_ID TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Keywords 
                 (keyword TEXT, keyword_count INTEGER, webpage_ID TEXT)''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()