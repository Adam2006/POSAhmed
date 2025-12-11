"""
Settings view for managing system configuration
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QCheckBox, QPushButton, QFormLayout,
    QSpinBox, QMessageBox, QGroupBox, QScrollArea, QTableWidget,
    QTableWidgetItem, QComboBox, QDoubleSpinBox, QHeaderView, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import config
from models import Category, Product


class SettingsView(QWidget):
    """Settings page with admin access only"""

    settings_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.settings_closed.emit)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Tab widget for different settings sections
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Arial", 11))

        # General settings tab
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "General")

        # Display settings tab
        self.display_tab = self.create_display_tab()
        self.tab_widget.addTab(self.display_tab, "Display")

        # Printer settings tab
        self.printer_tab = self.create_printer_tab()
        self.tab_widget.addTab(self.printer_tab, "Printer")

        # Products management tab
        self.products_tab = self.create_products_tab()
        self.tab_widget.addTab(self.products_tab, "Products")

        # Data management tab
        self.data_tab = self.create_data_tab()
        self.tab_widget.addTab(self.data_tab, "Data")

        layout.addWidget(self.tab_widget)

    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        form = QFormLayout()

        font = QFont()
        font.setPointSize(11)

        # Restaurant info
        group = QGroupBox("Restaurant Information")
        group.setFont(font)
        group_layout = QFormLayout()

        self.restaurant_name = QLineEdit(config.RESTAURANT_NAME)
        self.restaurant_name.setFont(font)
        group_layout.addRow("Restaurant Name:", self.restaurant_name)

        self.restaurant_phone = QLineEdit(config.RESTAURANT_PHONE)
        self.restaurant_phone.setFont(font)
        group_layout.addRow("Phone Number:", self.restaurant_phone)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Admin password
        group2 = QGroupBox("Security")
        group2.setFont(font)
        group2_layout = QFormLayout()

        self.admin_password = QLineEdit(config.ADMIN_PASSWORD)
        self.admin_password.setFont(font)
        self.admin_password.setEchoMode(QLineEdit.Password)
        group2_layout.addRow("Admin Password:", self.admin_password)

        group2.setLayout(group2_layout)
        layout.addWidget(group2)

        layout.addStretch()

        # Save button
        save_btn = QPushButton("Save General Settings")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFont(font)
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_general_settings)
        layout.addWidget(save_btn)

        return scroll

    def create_display_tab(self):
        """Create display settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        font = QFont()
        font.setPointSize(11)

        # Grid settings
        group = QGroupBox("Grid Layout")
        group.setFont(font)
        group_layout = QFormLayout()

        self.category_columns = QSpinBox()
        self.category_columns.setFont(font)
        self.category_columns.setMinimum(2)
        self.category_columns.setMaximum(8)
        self.category_columns.setValue(config.CATEGORY_GRID_COLUMNS)
        group_layout.addRow("Category Columns:", self.category_columns)

        self.product_columns = QSpinBox()
        self.product_columns.setFont(font)
        self.product_columns.setMinimum(2)
        self.product_columns.setMaximum(8)
        self.product_columns.setValue(config.PRODUCT_GRID_COLUMNS)
        group_layout.addRow("Product Columns:", self.product_columns)

        self.product_rows = QSpinBox()
        self.product_rows.setFont(font)
        self.product_rows.setMinimum(2)
        self.product_rows.setMaximum(6)
        self.product_rows.setValue(config.PRODUCT_GRID_ROWS)
        group_layout.addRow("Product Rows:", self.product_rows)

        group.setLayout(group_layout)
        layout.addWidget(group)

        layout.addStretch()

        # Save button
        save_btn = QPushButton("Save Display Settings")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFont(font)
        save_btn.setMinimumWidth(20)
        save_btn.clicked.connect(self.save_display_settings)
        layout.addWidget(save_btn)

        return tab

    def create_printer_tab(self):
        """Create printer settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        font = QFont()
        font.setPointSize(11)

        # Get available printers
        available_printers = self.get_available_printers()

        # Printer settings
        group = QGroupBox("Printer Configuration")
        group.setFont(font)
        group_layout = QFormLayout()

        self.enable_printing = QCheckBox()
        self.enable_printing.setChecked(config.ENABLE_PRINTING)
        group_layout.addRow("Enable Printing:", self.enable_printing)

        # Customer printer dropdown
        self.printer_name = QComboBox()
        self.printer_name.setFont(font)
        self.printer_name.addItems(available_printers)
        if config.PRINTER_NAME in available_printers:
            self.printer_name.setCurrentText(config.PRINTER_NAME)
        group_layout.addRow("Customer Printer:", self.printer_name)

        # Kitchen printer dropdown
        self.kitchen_printer_name = QComboBox()
        self.kitchen_printer_name.setFont(font)
        self.kitchen_printer_name.addItems(available_printers)
        if config.KITCHEN_PRINTER_NAME in available_printers:
            self.kitchen_printer_name.setCurrentText(config.KITCHEN_PRINTER_NAME)
        group_layout.addRow("Kitchen Printer:", self.kitchen_printer_name)

        group.setLayout(group_layout)
        layout.addWidget(group)

        layout.addStretch()

        # Save button
        save_btn = QPushButton("Save Printer Settings")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFont(font)
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_printer_settings)
        layout.addWidget(save_btn)

        return tab

    def get_available_printers(self):
        """Get list of available printers from Windows"""
        try:
            import win32print
            printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            return printers if printers else ["No printers found"]
        except ImportError:
            return ["win32print not available"]
        except Exception as e:
            return [f"Error: {str(e)}"]

    def create_products_tab(self):
        """Create products management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        font = QFont()
        font.setPointSize(11)

        # Category selection
        category_layout = QHBoxLayout()

        category_label = QLabel("Category:")
        category_label.setFont(font)
        category_layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.setFont(font)
        self.category_combo.setMinimumWidth(200)
        self.category_combo.currentIndexChanged.connect(self.load_products_for_category)
        category_layout.addWidget(self.category_combo)

        category_layout.addStretch()

        # Add/Edit/Delete Category buttons
        add_category_btn = QPushButton("+ New Category")
        add_category_btn.setFont(font)
        add_category_btn.clicked.connect(self.add_category)
        category_layout.addWidget(add_category_btn)

        edit_category_btn = QPushButton("Edit Category")
        edit_category_btn.setFont(font)
        edit_category_btn.clicked.connect(self.edit_category)
        category_layout.addWidget(edit_category_btn)

        delete_category_btn = QPushButton("Delete Category")
        delete_category_btn.setProperty("class", "danger-button")
        delete_category_btn.setFont(font)
        delete_category_btn.clicked.connect(self.delete_category)
        category_layout.addWidget(delete_category_btn)

        layout.addLayout(category_layout)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Product Name", "Price (dt)", "Status", "Actions"])
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.products_table.setColumnWidth(0, 200)  # Set fixed width for name column
        self.products_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.products_table.verticalHeader().setDefaultSectionSize(60)  # Set row height to 60px
        self.products_table.setFont(font)
        layout.addWidget(self.products_table)

        # Add product button
        add_product_btn = QPushButton("+ Add New Product")
        add_product_btn.setProperty("class", "primary-button")
        add_product_btn.setFont(font)
        add_product_btn.setMinimumHeight(40)
        add_product_btn.clicked.connect(self.add_product)
        layout.addWidget(add_product_btn)

        # Load categories
        self.refresh_categories()

        return tab

    def refresh_categories(self):
        """Refresh category dropdown"""
        self.category_combo.clear()
        categories = Category.get_all(active_only=False)
        for category in categories:
            status_text = " (Inactive)" if not category.is_active else ""
            self.category_combo.addItem(f"{category.name}{status_text}", category.id)

        if self.category_combo.count() > 0:
            self.load_products_for_category()

    def load_products_for_category(self):
        """Load products for selected category"""
        if self.category_combo.count() == 0:
            return

        category_id = self.category_combo.currentData()
        if category_id is None:
            return

        products = Product.get_by_category(category_id, active_only=False)

        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            # Product name
            name_item = QTableWidgetItem(product.name)
            self.products_table.setItem(row, 0, name_item)

            # Price
            price_item = QTableWidgetItem(f"{product.price:.2f}")
            self.products_table.setItem(row, 1, price_item)

            # Status
            status_item = QTableWidgetItem("Active" if product.is_active else "Inactive")
            self.products_table.setItem(row, 2, status_item)

            # Actions buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(15)

            edit_btn = QPushButton("Edit")
            edit_btn.setMinimumHeight(30)
            edit_btn.setMaximumHeight(30)
            edit_btn.setMinimumWidth(80)
            edit_btn.setStyleSheet("padding: 5px 15px; font-size: 13px;")
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            actions_layout.addWidget(edit_btn)

            toggle_btn = QPushButton("Deactivate" if product.is_active else "Activate")
            toggle_btn.setMinimumHeight(30)
            toggle_btn.setMaximumHeight(30)
            toggle_btn.setMinimumWidth(80)
            toggle_btn.setStyleSheet("padding: 5px 15px; font-size: 13px;")
            toggle_btn.clicked.connect(lambda checked, p=product: self.toggle_product_status(p))
            actions_layout.addWidget(toggle_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger-button")
            delete_btn.setMinimumHeight(30)
            delete_btn.setMaximumHeight(30)
            delete_btn.setMinimumWidth(80)
            delete_btn.setStyleSheet("padding: 5px 15px; font-size: 13px;")
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
            actions_layout.addWidget(delete_btn)

            actions_layout.addStretch()

            self.products_table.setCellWidget(row, 3, actions_widget)

    def add_category(self):
        """Add new category"""
        from .product_edit_dialog import CategoryEditDialog
        dialog = CategoryEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            category = Category(
                name=data['name'],
                is_active=data['is_active']
            )
            category.save()
            self.refresh_categories()
            QMessageBox.information(self, "Success", "Category added successfully!")

    def edit_category(self):
        """Edit selected category"""
        category_id = self.category_combo.currentData()
        if category_id is None:
            return

        category = Category.get_by_id(category_id)
        if not category:
            return

        from .product_edit_dialog import CategoryEditDialog
        dialog = CategoryEditDialog(self, category)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            category.name = data['name']
            category.is_active = data['is_active']
            category.save()
            self.refresh_categories()
            QMessageBox.information(self, "Success", "Category updated successfully!")

    def add_product(self):
        """Add new product"""
        category_id = self.category_combo.currentData()
        if category_id is None:
            QMessageBox.warning(self, "No Category", "Please select a category first.")
            return

        from .product_edit_dialog import ProductEditDialog
        dialog = ProductEditDialog(self, category_id)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            product = Product(
                category_id=category_id,
                name=data['name'],
                price=data['price'],
                is_active=data['is_active'],
                image_path=data['image_path']
            )
            product.save()
            self.load_products_for_category()
            QMessageBox.information(self, "Success", "Product added successfully!")

    def edit_product(self, product):
        """Edit existing product"""
        from .product_edit_dialog import ProductEditDialog
        dialog = ProductEditDialog(self, product.category_id, product)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            product.name = data['name']
            product.price = data['price']
            product.is_active = data['is_active']
            product.image_path = data['image_path']
            product.save()
            self.load_products_for_category()
            QMessageBox.information(self, "Success", "Product updated successfully!")

    def toggle_product_status(self, product):
        """Toggle product active status"""
        product.is_active = not product.is_active
        product.save()
        self.load_products_for_category()

    def delete_product(self, product):
        """Delete a product"""
        reply = QMessageBox.question(
            self,
            "Delete Product",
            f"Are you sure you want to delete '{product.name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            product.delete()
            self.load_products_for_category()
            QMessageBox.information(self, "Success", "Product deleted successfully!")

    def delete_category(self):
        """Delete selected category"""
        category_id = self.category_combo.currentData()
        if category_id is None:
            return

        category = Category.get_by_id(category_id)
        if not category:
            return

        # Check if category has products
        products = Product.get_by_category(category_id, active_only=False)

        if products:
            # Ask if user wants to delete category with all its products
            reply = QMessageBox.question(
                self,
                "Delete Category with Products",
                f"Category '{category.name}' has {len(products)} product(s).\n\n"
                f"Do you want to delete the category and ALL its products?\n"
                f"This action cannot be undone!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                category.delete(delete_products=True)
                self.refresh_categories()
                QMessageBox.information(self, "Success", f"Category and {len(products)} product(s) deleted successfully!")
        else:
            # Category has no products, simple deletion
            reply = QMessageBox.question(
                self,
                "Delete Category",
                f"Are you sure you want to delete category '{category.name}'?\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                category.delete()
                self.refresh_categories()
                QMessageBox.information(self, "Success", "Category deleted successfully!")

    def create_data_tab(self):
        """Create data management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        font = QFont()
        font.setPointSize(11)

        # Database info
        group = QGroupBox("Database Information")
        group.setFont(font)
        group_layout = QVBoxLayout()

        # Count categories and products
        categories = Category.get_all(active_only=False)
        products = Product.get_all(active_only=False)

        info_label = QLabel(
            f"Categories: {len(categories)}\n"
            f"Products: {len(products)}\n"
            f"Database: {config.DATABASE_PATH}"
        )
        info_label.setFont(font)
        group_layout.addWidget(info_label)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Data operations
        group2 = QGroupBox("Data Operations")
        group2.setFont(font)
        group2_layout = QVBoxLayout()

        # Import button
        import_btn = QPushButton("Import from menu.json")
        import_btn.setFont(font)
        import_btn.setMinimumHeight(40)
        import_btn.clicked.connect(self.import_from_json)
        group2_layout.addWidget(import_btn)

        # Create sample data button
        sample_btn = QPushButton("Create Sample Data")
        sample_btn.setFont(font)
        sample_btn.setMinimumHeight(40)
        sample_btn.clicked.connect(self.create_sample_data)
        group2_layout.addWidget(sample_btn)

        group2.setLayout(group2_layout)
        layout.addWidget(group2)

        layout.addStretch()

        return tab

    def save_general_settings(self):
        """Save general settings to config file"""
        try:
            # Update config values
            config.RESTAURANT_NAME = self.restaurant_name.text().strip()
            config.RESTAURANT_PHONE = self.restaurant_phone.text().strip()
            config.ADMIN_PASSWORD = self.admin_password.text().strip()

            # Write to config.py
            self.update_config_file()

            QMessageBox.information(self, "Success", "General settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def save_display_settings(self):
        """Save display settings to config file"""
        try:
            config.CATEGORY_GRID_COLUMNS = self.category_columns.value()
            config.PRODUCT_GRID_COLUMNS = self.product_columns.value()
            config.PRODUCT_GRID_ROWS = self.product_rows.value()
            config.PRODUCTS_PER_PAGE = config.PRODUCT_GRID_COLUMNS * config.PRODUCT_GRID_ROWS

            self.update_config_file()

            QMessageBox.information(
                self, "Success",
                "Display settings saved!\nPlease restart the application for changes to take effect."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def save_printer_settings(self):
        """Save printer settings to config file"""
        try:
            config.ENABLE_PRINTING = self.enable_printing.isChecked()
            config.PRINTER_NAME = self.printer_name.currentText().strip()
            config.KITCHEN_PRINTER_NAME = self.kitchen_printer_name.currentText().strip()

            self.update_config_file()

            QMessageBox.information(self, "Success", "Printer settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def update_config_file(self):
        """Update the config.py file with current values"""
        config_path = "config.py"

        config_content = f'''"""
Application configuration settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Application settings
RESTAURANT_NAME = "{config.RESTAURANT_NAME}"
RESTAURANT_PHONE = "{config.RESTAURANT_PHONE}"
ADMIN_PASSWORD = "{config.ADMIN_PASSWORD}"

# Database settings
DATABASE_PATH = BASE_DIR / "data" / "restaurant.db"

# Display settings
CATEGORY_GRID_COLUMNS = {config.CATEGORY_GRID_COLUMNS}
CATEGORY_GRID_ROWS = {config.CATEGORY_GRID_ROWS}
PRODUCT_GRID_COLUMNS = {config.PRODUCT_GRID_COLUMNS}
PRODUCT_GRID_ROWS = {config.PRODUCT_GRID_ROWS}
PRODUCTS_PER_PAGE = {config.PRODUCTS_PER_PAGE}

# Printer settings
ENABLE_PRINTING = {config.ENABLE_PRINTING}
PRINTER_NAME = "{config.PRINTER_NAME}"
KITCHEN_PRINTER_NAME = "{config.KITCHEN_PRINTER_NAME}"

# Order settings
ORDER_RESET_TIME = "{config.ORDER_RESET_TIME}"

# UI settings
WINDOW_TITLE = "{config.RESTAURANT_NAME} POS"
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
'''

        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)

    def import_from_json(self):
        """Import data from menu.json"""
        try:
            from utils.migrate_data import migrate_from_json
            import os

            if os.path.exists("menu.json"):
                reply = QMessageBox.question(
                    self, "Confirm Import",
                    "This will import data from menu.json. Continue?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    migrate_from_json("menu.json")
                    QMessageBox.information(
                        self, "Success",
                        "Data imported successfully!\nPlease restart the application."
                    )
            else:
                QMessageBox.warning(self, "File Not Found", "menu.json not found in application directory.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import data: {e}")

    def create_sample_data(self):
        """Create sample data"""
        try:
            from utils.migrate_data import create_sample_data

            reply = QMessageBox.question(
                self, "Confirm",
                "This will create sample data. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                create_sample_data()
                QMessageBox.information(
                    self, "Success",
                    "Sample data created successfully!\nPlease restart the application."
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create sample data: {e}")
