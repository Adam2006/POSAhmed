"""
Dialogs for editing products and categories
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QFormLayout, QCheckBox, QDoubleSpinBox,
    QGroupBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models import ToppingGroup


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

        # Topping groups section
        topping_group_box = QGroupBox("Available Topping Groups")
        topping_group_box.setFont(font)
        topping_layout = QVBoxLayout(topping_group_box)

        # Get all topping groups
        all_groups = ToppingGroup.get_all(active_only=True)

        # Get current category's topping groups
        current_group_ids = []
        if self.category and self.category.id:
            current_groups = self.category.get_topping_groups()
            current_group_ids = [g.id for g in current_groups]

        # Create checkboxes for each topping group
        self.topping_checkboxes = {}
        if all_groups:
            for group in all_groups:
                checkbox = QCheckBox(group.name)
                checkbox.setFont(font)
                checkbox.setChecked(group.id in current_group_ids)
                self.topping_checkboxes[group.id] = checkbox
                topping_layout.addWidget(checkbox)
        else:
            no_groups_label = QLabel("No topping groups available. Create them in Settings > Toppings.")
            no_groups_label.setFont(font)
            no_groups_label.setStyleSheet("color: #888;")
            topping_layout.addWidget(no_groups_label)

        layout.addWidget(topping_group_box)

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

    def get_selected_topping_groups(self):
        """Get list of selected topping group IDs"""
        selected_ids = []
        for group_id, checkbox in self.topping_checkboxes.items():
            if checkbox.isChecked():
                selected_ids.append(group_id)
        return selected_ids


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

        # Topping groups section
        topping_group_box = QGroupBox("Available Topping Groups")
        topping_group_box.setFont(font)
        topping_layout = QVBoxLayout(topping_group_box)

        # Get all topping groups
        all_groups = ToppingGroup.get_all(active_only=True)

        # Get current product's topping groups
        current_group_ids = []
        if self.product and self.product.id:
            current_groups = self.product.get_topping_groups()
            current_group_ids = [g.id for g in current_groups]

        # Create checkboxes for each topping group
        self.topping_checkboxes = {}
        if all_groups:
            for group in all_groups:
                checkbox = QCheckBox(group.name)
                checkbox.setFont(font)
                checkbox.setChecked(group.id in current_group_ids)
                self.topping_checkboxes[group.id] = checkbox
                topping_layout.addWidget(checkbox)
        else:
            no_groups_label = QLabel("No topping groups available. Create them in Settings > Toppings.")
            no_groups_label.setFont(font)
            no_groups_label.setStyleSheet("color: #888;")
            topping_layout.addWidget(no_groups_label)

        layout.addWidget(topping_group_box)

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

    def get_selected_topping_groups(self):
        """Get list of selected topping group IDs"""
        selected_ids = []
        for group_id, checkbox in self.topping_checkboxes.items():
            if checkbox.isChecked():
                selected_ids.append(group_id)
        return selected_ids
