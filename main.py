"""
Main entry point for the Restaurant POS System
"""
import sys
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from utils.styles import get_main_stylesheet
from models import get_db
import config


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)

    # Apply stylesheet
    app.setStyleSheet(get_main_stylesheet())

    # Initialize database
    db = get_db()

    # Check if we need to migrate data
    from models import Category
    categories = Category.get_all(active_only=False)

    if not categories:
        print("No data found in database.")
        print("Attempting to migrate from menu.json or create sample data...")

        from utils.migrate_data import migrate_from_json, create_sample_data
        import os

        if os.path.exists("menu.json"):
            migrate_from_json("menu.json")
        else:
            print("No menu.json found. Creating sample data...")
            create_sample_data()

    # Create and show main window
    window = MainWindow()
    window.showMaximized()

    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
