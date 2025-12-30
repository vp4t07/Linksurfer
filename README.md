# LinkSurfer

LinkSurfer is a custom-built web crawler, search engine, and information retrieval system built with Python. It features a bespoke recursive indexing algorithm, a custom lexical analysis engine for HTML parsing, and a domain-specific categorization system.

![LinkSurfer GUI](assets/logo.png)

## 🚀 Features

* **Custom Web Crawler:** Recursively indexes web pages, extracting metadata, content, and outbound links.
* **Lexical Analysis Engine:** Implements a custom-built HTML parser (Lexer) to tokenize and extract headings, paragraphs, and links without relying on external scraping libraries like BeautifulSoup.
* **Keyword Categorization:** Utilizes a weighted dictionary approach to classify content into 12 distinct domains (Finance, Health, Science, Technology, UK Politics, Military, America, History, Geography, Literature, Sport, Politics).
* **Data Persistence:** Manages a relational database (SQLite) to store indexed URLs, keyword frequency, and categorization metrics.
* **Modern GUI:** Features a responsive user interface built with `CustomTkinter` for searching, viewing summaries, and managing the index.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/LinkSurfer.git](https://github.com/yourusername/LinkSurfer.git)
    cd LinkSurfer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python src/main.py
    ```

## 📂 Project Structure

* `src/scraper.py`: Core logic for the recursive crawler and custom HTML parser.
* `src/database.py`: Abstraction layer for SQLite database interactions.
* `src/gui.py`: Frontend user interface code.
* `data/keywords.json`: The categorization dictionary/dataset.
* `data/linksurfer.db`: Local SQLite database (generated upon first run).

## 💡 Usage

1.  **Indexing:** From the home screen, enter a seed URL (e.g., `https://www.bbc.co.uk`) and click **Start Indexing**. The system will crawl the page, extract keywords, and categorize the content.
2.  **Searching:** Enter a URL or keyword to retrieve indexed pages.
3.  **Summaries:** View a generated summary of indexed pages and export them to text files.

## 💻 Tech Stack

* **Language:** Python 3.9+
* **GUI Framework:** CustomTkinter
* **Database:** SQLite3
* **Networking:** urllib3 / SSL

## 📝 License

This project is open-source and available under the MIT License.