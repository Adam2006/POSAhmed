"""
Dialogs for editing products and categories
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QFormLayout, QCheckBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CategoryEditDialog(QDialog):
    """Dialog for adding/editing categories"""

    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.setWindowTitle("Edit Category" if category else "Add Category")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Category name
        self.name_input = QLineEdit()
        self.name_input.setFont(font)
        self.name_input.setPlaceholderText("Enter category name")
        if self.category:
            self.name_input.setText(self.category.name)
        form_layout.addRow("Category Name:", self.name_input)

        # Active status
        self.active_checkbox = QCheckBox("Active")
        self.active_checkbox.setFont(font)
        self.active_checkbox.setChecked(self.category.is_active if self.category else True)
        form_layout.addRow("Status:", self.active_checkbox)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(font)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFont(font)
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def get_data(self):
        """Get category data"""
        return {
            'name': self.name_input.text().strip(),
            'is_active': self.active_checkbox.isChecked()
        }


class ProductEditDialog(QDialog):
    """Dialog for adding/editing products"""

    def __init__(self, parent=None, category_id=None, product=None):
        super().__init__(parent)
        self.category_id = category_id
        self.product = product
        self.setWindowTitle("Edit Product" if product else "Add Product")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(450)

        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Product name
        self.name_input = QLineEdit()
        self.name_input.setFont(font)
        self.name_input.setPlaceholderText("Enter product name")
        if self.product:
            self.name_input.setText(self.product.name)
        form_layout.addRow("Product Name:", self.name_input)

        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setFont(font)
        self.price_input.setDecimals(2)
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(9999.99)
        self.price_input.setSuffix(" dt")
        if self.product:
            self.price_input.setValue(self.product.price)
        form_layout.addRow("Price:", self.price_input)

        # Active status
        self.active_checkbox = QCheckBox("Active")
        self.active_checkbox.setFont(font)
        self.active_checkbox.setChecked(self.product.is_active if self.product else True)
        form_layout.addRow("Status:", self.active_checkbox)

        layout.addLayout(form_layout)

        # Image path field
        image_label = QLabel("Image Path:")
        image_label.setFont(font)
        layout.addWidget(image_label)

        self.image_input = QLineEdit()
        self.image_input.setFont(font)
        self.image_input.setPlaceholderText("Enter image file path (optional)")
        if self.product and self.product.image_path:
            self.image_input.setText(self.product.image_path)
        layout.addWidget(self.image_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(font)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFont(font)
        save_btn.setMinimumWidth(120)
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def get_data(self):
        """Get product data"""
        return {
            'name': self.name_input.text().strip(),
            'price': self.price_input.value(),
            'is_active': self.active_checkbox.isChecked(),
            'image_path': self.image_input.text().strip()
        }
