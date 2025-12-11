"""
Dialog for editing cart item (quantity, price, notes)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QDoubleSpinBox, QSpinBox, QPushButton, QHBoxLayout, QFormLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class EditItemDialog(QDialog):
    """Dialog for editing a cart item"""

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setWindowTitle("Edit Item")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(450)

        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(14)

        # Title showing product name
        title_label = QLabel(f"{self.item.get('category_name', '')} {self.item['name']}")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Quantity field
        self.quantity_input = QSpinBox()
        self.quantity_input.setFont(font)
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(99)
        self.quantity_input.setValue(self.item['quantity'])
        form_layout.addRow("Quantity:", self.quantity_input)

        # Unit price field
        self.price_input = QDoubleSpinBox()
        self.price_input.setFont(font)
        self.price_input.setDecimals(2)
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(9999.99)
        self.price_input.setValue(self.item['unit_price'])
        self.price_input.setSuffix(" dt")
        form_layout.addRow("Unit Price:", self.price_input)

        # Discount field
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setFont(font)
        self.discount_input.setDecimals(2)
        self.discount_input.setMinimum(0)
        self.discount_input.setMaximum(9999.99)
        self.discount_input.setValue(self.item['discount'])
        self.discount_input.setSuffix(" dt")
        form_layout.addRow("Discount:", self.discount_input)

        layout.addLayout(form_layout)

        # Notes field
        notes_label = QLabel("Notes:")
        notes_label.setFont(font)
        layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setFont(font)
        self.notes_input.setPlaceholderText("Enter special instructions...")
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setText(self.item.get('notes', ''))
        layout.addWidget(self.notes_input)

        # Final price preview
        self.final_price_label = QLabel()
        self.final_price_label.setProperty("class", "total-label")
        final_font = QFont()
        final_font.setPointSize(18)
        final_font.setBold(True)
        self.final_price_label.setFont(final_font)
        self.final_price_label.setAlignment(Qt.AlignCenter)
        self.update_final_price()
        layout.addWidget(self.final_price_label)

        # Connect signals to update final price
        self.quantity_input.valueChanged.connect(self.update_final_price)
        self.price_input.valueChanged.connect(self.update_final_price)
        self.discount_input.valueChanged.connect(self.update_final_price)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        btn_font = QFont()
        btn_font.setPointSize(14)
        cancel_btn.setFont(btn_font)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFont(btn_font)
        save_btn.setMinimumWidth(120)
        save_btn.setMinimumHeight(45)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def update_final_price(self):
        """Update the final price preview"""
        quantity = self.quantity_input.value()
        unit_price = self.price_input.value()
        discount = self.discount_input.value()
        final_price = (unit_price - discount) * quantity
        self.final_price_label.setText(f"Final Price: {final_price:.2f}dt")

    def get_data(self):
        """Get updated item data"""
        return {
            'quantity': self.quantity_input.value(),
            'unit_price': self.price_input.value(),
            'discount': self.discount_input.value(),
            'notes': self.notes_input.toPlainText().strip()
        }
