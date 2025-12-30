import customtkinter as ctk
import os
import webbrowser
from PIL import Image
from src.database import DatabaseManager
from src.scraper import Scraper

# Configuration
FONT_TITLE = ('avenir', 18)
FONT_HEADER = ('hiragino sans', 30)
THEME_COLOR = '#47E5E5'
HOVER_COLOR = '#2443F0'

class LinkSurferGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('LinkSurfer')
        self.geometry('1600x1000')
        ctk.set_default_color_theme("blue")
        
        # Initialize Backend
        self.db = DatabaseManager()
        
        # Setup Directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.base_dir, 'assets')
        self.output_dir = os.path.join(self.base_dir, 'data', 'text_output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.show_home_page()

    def clear_frame(self):
        """Removes all widgets from the current view."""
        for widget in self.winfo_children():
            widget.place_forget()

    # --- Pages ---

    def show_home_page(self):
        self.clear_frame()
        
        # Logo
        logo_path = os.path.join(self.assets_dir, 'logo.png')
        if os.path.exists(logo_path):
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(500, 500))
            logo_label = ctk.CTkLabel(self, image=img, text="")
            logo_label.place(relx=0.3, rely=0.05, relheight=0.5, relwidth=0.45)
        else:
            # Fallback if image missing
            ctk.CTkLabel(self, text="LinkSurfer", font=("Arial", 60)).place(relx=0.4, rely=0.2)

        # Search Bar
        self.search_entry = ctk.CTkEntry(self, placeholder_text='Enter URL...', font=FONT_HEADER, width=400)
        self.search_entry.place(relx=0.35, rely=0.55, relheight=0.08, relwidth=0.3)

        # Search Button
        btn_search = ctk.CTkButton(self, text="Search", command=self.on_search, height=60, 
                                   fg_color=THEME_COLOR, text_color="black", hover_color=HOVER_COLOR)
        btn_search.place(relx=0.66, rely=0.55)
        
        # Index Button
        btn_index = ctk.CTkButton(self, text="START INDEXING", fg_color=THEME_COLOR, text_color="black", 
                                  font=(FONT_TITLE[0], 45), hover_color=HOVER_COLOR, command=self.on_manual_index)
        btn_index.place(relx=0.35, rely=0.65, relheight=0.1, relwidth=0.35)

        # Recents Dropdown
        recents_data = self.db.get_recent_files()
        recent_urls = [r[0] for r in recents_data] if recents_data else ["No History"]
        
        self.dropdown_var = ctk.StringVar(value='Recently Indexed')
        dropdown = ctk.CTkOptionMenu(self, variable=self.dropdown_var, values=recent_urls, 
                                     command=self.open_recent, width=200, height=50, fg_color=THEME_COLOR, text_color='black')
        dropdown.place(relx=0.1, rely=0.18)

    def show_results_page(self, query_url, results):
        self.clear_frame()
        
        # Main Menu Button
        btn_menu = ctk.CTkButton(self, text="Main Menu", command=self.show_home_page, 
                                 width=200, height=70, font=FONT_TITLE, fg_color=THEME_COLOR, text_color="black")
        btn_menu.place(relx=0.1, rely=0.1)
        
        # Title
        ctk.CTkLabel(self, text=f"Results for: {query_url}", font=FONT_HEADER).place(relx=0.35, rely=0.1)

        # List Results (Dynamic generation instead of hardcoded 1-5)
        start_y = 0.3
        if not results:
            ctk.CTkLabel(self, text="No related pages found in this category.", font=FONT_TITLE).place(relx=0.35, rely=0.3)
            return

        for i, res in enumerate(results[:5]): # Limit to top 5
            url = res[0]
            # Create a button for each result
            btn = ctk.CTkButton(self, text=url, command=lambda u=url: self.show_summary_page(u), 
                                width=600, height=60, fg_color=THEME_COLOR, text_color='black', font=FONT_TITLE)
            btn.place(relx=0.3, rely=start_y + (i * 0.1))

    def show_summary_page(self, url):
        self.clear_frame()
        self.selected_url = url
        
        summary_text = self.db.get_summary(url)
        keywords = self.db.get_keywords(url)
        
        # Header
        btn_menu = ctk.CTkButton(self, text="< Back", command=self.show_home_page, 
                                 width=150, height=50, fg_color=THEME_COLOR, text_color="black")
        btn_menu.place(relx=0.05, rely=0.05)
        
        ctk.CTkLabel(self, text=url, font=FONT_TITLE).place(relx=0.3, rely=0.05)

        # Summary Section
        summary_frame = ctk.CTkScrollableFrame(self, width=500, height=400, label_text="Summary")
        summary_frame.place(relx=0.1, rely=0.2)
        ctk.CTkLabel(summary_frame, text=summary_text, wraplength=480, font=("Arial", 16)).pack(pady=10, padx=10)

        # Keywords Section
        keyword_frame = ctk.CTkScrollableFrame(self, width=400, height=400, label_text="Top Keywords")
        keyword_frame.place(relx=0.5, rely=0.2)
        for kw in keywords[:20]: # Show top 20
            ctk.CTkLabel(keyword_frame, text=kw, font=("Arial", 14)).pack()

        # Action Buttons
        btn_open = ctk.CTkButton(self, text="Open in Browser", command=self.open_in_browser, width=300, height=50, fg_color=THEME_COLOR, text_color="black")
        btn_open.place(relx=0.2, rely=0.7)
        
        btn_save = ctk.CTkButton(self, text="Save to Text File", command=self.save_to_text, width=300, height=50, fg_color=THEME_COLOR, text_color="black")
        btn_save.place(relx=0.5, rely=0.7)

    # --- Logic Handlers ---

    def on_search(self):
        url = self.search_entry.get()
        if not url: return
        
        # 1. Check if we know this URL
        if not self.db.check_link_exists(url):
            # It's new, let's scrape it first
            print("URL not found in DB. Scraping now...")
            scraper = Scraper(url, recursive=False)
            scraper.run()
        
        # 2. Get the primary category of this URL
        categories = self.db.get_categories_by_url(url)
        if categories:
            primary_cat = categories[0][0]
            # 3. Find other URLs in this category
            results = self.db.get_urls_by_category(primary_cat)
            self.show_results_page(url, results)
        else:
            # Fallback if no categories found
            self.show_results_page(url, [])

    def on_manual_index(self):
        # Starts indexing from a default seed or user input
        url = self.search_entry.get()
        if not url:
            url = "https://www.bbc.co.uk" # Default seed
        
        scraper = Scraper(url, recursive=True)
        scraper.run()
        print("Manual indexing finished.")

    def open_recent(self, choice):
        self.show_summary_page(choice)

    def open_in_browser(self):
        webbrowser.open(self.selected_url)

    def save_to_text(self):
        # Create a safe filename
        safe_name = self.selected_url.replace("https://", "").replace("http://", "").replace("/", "_") + ".txt"
        path = os.path.join(self.output_dir, safe_name)
        
        summary_text = self.db.get_summary(self.selected_url)
        
        try:
            with open(path, "w") as f:
                f.write(f"URL: {self.selected_url}\n\n")
                f.write(f"SUMMARY:\n{summary_text}")
            print(f"Saved to {path}")
        except Exception as e:
            print(f"Error saving file: {e}")