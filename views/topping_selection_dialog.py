"""
Topping selection dialog for customizing products before adding to cart
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QScrollArea, QWidget, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models import ToppingGroup
from translations import TOPPINGS, COMMON


class ToppingSelectionDialog(QDialog):
    """Dialog for selecting toppings when adding a product to cart"""

    def __init__(self, product, category=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.category = category
        self.selected_toppings = {}  # {group_id: [option_id1, option_id2, ...]}
        self.setWindowTitle(f"{TOPPINGS['customize']}: {product.name}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Product name header
        product_label = QLabel(f"{TOPPINGS['customizing']}: {self.product.name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        product_label.setFont(title_font)
        product_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(product_label)

        # Base price
        price_label = QLabel(f"{TOPPINGS['base_price']}: {self.product.price:.2f} dt")
        price_label.setFont(font)
        price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(price_label)

        # Get topping groups for this product
        topping_groups = self.product.get_topping_groups()

        # If product doesn't have topping groups, check category
        if not topping_groups and self.category:
            topping_groups = self.category.get_topping_groups()

        if not topping_groups:
            # No toppings available - show message
            no_toppings_label = QLabel(TOPPINGS['no_options'])
            no_toppings_label.setFont(font)
            no_toppings_label.setAlignment(Qt.AlignCenter)
            no_toppings_label.setStyleSheet("color: #888;")
            layout.addWidget(no_toppings_label)
        else:
            # Scroll area for topping groups
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)

            # Create a group box for each topping group
            self.topping_buttons = {}  # {option_id: button}

            for group in topping_groups:
                group_box = QGroupBox(group.name)
                group_box.setFont(font)
                group_layout = QGridLayout(group_box)
                group_layout.setSpacing(10)

                # Get options for this group
                options = group.get_options(active_only=True)

                if options:
                    # Create buttons in a grid (2 columns)
                    for idx, option in enumerate(options):
                        # Create button with option name and price
                        price_text = f" (+{option.price:.2f} dt)" if option.price > 0 else ""
                        button = QPushButton(f"{option.name}{price_text}")
                        button.setFont(font)
                        button.setMinimumHeight(45)
                        button.setCheckable(True)
                        button.setStyleSheet("""
                            QPushButton {
                                background-color: #4b4b4b;
                                border: 2px solid #ccc;
                                border-radius: 5px;
                                padding: 5px;
                            }
                            QPushButton:checked {
                                background-color: #4CAF50;
                                color: white;
                                border: 2px solid #45a049;
                            }
                        """)

                        self.topping_buttons[option.id] = {
                            'button': button,
                            'group_id': group.id,
                            'option': option
                        }

                        # Add to grid (2 columns)
                        row = idx // 2
                        col = idx % 2
                        group_layout.addWidget(button, row, col)
                else:
                    no_options_label = QLabel("No options available")
                    no_options_label.setFont(font)
                    no_options_label.setStyleSheet("color: #888;")
                    group_layout.addWidget(no_options_label, 0, 0)

                scroll_layout.addWidget(group_box)

            scroll_layout.addStretch()
            scroll.setWidget(scroll_widget)
            layout.addWidget(scroll)

        # Total price label
        self.total_label = QLabel(f"{COMMON['total']}: {self.product.price:.2f} dt")
        total_font = QFont()
        total_font.setPointSize(14)
        total_font.setBold(True)
        self.total_label.setFont(total_font)
        self.total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_label)

        # Connect buttons to update total
        if topping_groups:
            for option_data in self.topping_buttons.values():
                option_data['button'].toggled.connect(self.update_total)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton(COMMON['cancel'])
        cancel_btn.setFont(font)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        add_btn = QPushButton(TOPPINGS['add_to_cart'])
        add_btn.setFont(font)
        add_btn.setMinimumHeight(40)
        add_btn.setMinimumWidth(150)
        add_btn.setProperty("class", "primary-button")
        add_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(add_btn)

        layout.addLayout(buttons_layout)

    def update_total(self):
        """Update the total price based on selected toppings"""
        total = self.product.price

        for option_data in self.topping_buttons.values():
            if option_data['button'].isChecked():
                total += option_data['option'].price

        self.total_label.setText(f"{COMMON['total']}: {total:.2f} dt")

    def get_selected_toppings(self):
        """Get dictionary of selected toppings grouped by group_id"""
        selected = {}

        for option_id, option_data in self.topping_buttons.items():
            if option_data['button'].isChecked():
                group_id = option_data['group_id']
                if group_id not in selected:
                    selected[group_id] = []
                selected[group_id].append({
                    'id': option_id,
                    'name': option_data['option'].name,
                    'price': option_data['option'].price
                })

        return selected

    def get_total_price(self):
        """Get the total price including toppings"""
        total = self.product.price

        for option_data in self.topping_buttons.values():
            if option_data['button'].isChecked():
                total += option_data['option'].price

        return total
