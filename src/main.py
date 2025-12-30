import sys
import os

# Add the project root directory to Python's path
# This ensures that 'from src.gui import...' works regardless of where you run the script from
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui import LinkSurferGUI

if __name__ == "__main__":
    app = LinkSurferGUI()
    app.mainloop()