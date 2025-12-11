"""
Application configuration settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Application settings
RESTAURANT_NAME = "Woods"
RESTAURANT_PHONE = "99777197"
ADMIN_PASSWORD = ""

# Database settings
DATABASE_PATH = BASE_DIR / "data" / "restaurant.db"

# Display settings
CATEGORY_GRID_COLUMNS = 5
CATEGORY_GRID_ROWS = 3
PRODUCT_GRID_COLUMNS = 4
PRODUCT_GRID_ROWS = 3
PRODUCTS_PER_PAGE = 12

# Printer settings
ENABLE_PRINTING = True
PRINTER_NAME = "Microsoft Print to PDF"
KITCHEN_PRINTER_NAME = "Microsoft Print to PDF"

# Order settings
ORDER_RESET_TIME = "02:30"

# UI settings
WINDOW_TITLE = "Woods POS"
THEME_COLOR = "#252525"
ACCENT_COLOR = "#3a3a3a"
TEXT_COLOR = "#f0f8ff"
HIGHLIGHT_COLOR = "#5d5d5d"

# Assets paths
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
ICONS_DIR = ASSETS_DIR / "icons"
BACKUP_DIR = BASE_DIR / "data" / "backups"

# Create necessary directories
os.makedirs(DATABASE_PATH.parent, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)
