"""
Delivery order dialog
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QIntValidator


class DeliveryDialog(QDialog):
    """Dialog for entering delivery information"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delivery")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)

        # Try to set icon
        try:
            icon = QIcon("delivery.png")
            self.setWindowIcon(icon)
        except:
            pass

        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Address field
        address_label = QLabel("Delivery Address:")
        address_label.setFont(font)
        layout.addWidget(address_label)

        self.address_input = QLineEdit()
        self.address_input.setFont(font)
        self.address_input.setPlaceholderText("Enter customer address")
        layout.addWidget(self.address_input)

        # Phone field
        phone_label = QLabel("Phone Number:")
        phone_label.setFont(font)
        layout.addWidget(phone_label)

        self.phone_input = QLineEdit()
        self.phone_input.setFont(font)
        self.phone_input.setPlaceholderText("Enter phone number")
        # Set validator for numbers only
        validator = QIntValidator(0, 99999999)
        self.phone_input.setValidator(validator)
        layout.addWidget(self.phone_input)

        # Delivery price field
        price_label = QLabel("Delivery Price (dt):")
        price_label.setFont(font)
        layout.addWidget(price_label)

        self.price_input = QDoubleSpinBox()
        self.price_input.setFont(font)
        self.price_input.setDecimals(2)
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(999.99)
        self.price_input.setValue(2.0)
        layout.addWidget(self.price_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(font)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        done_btn = QPushButton("Done")
        done_btn.setProperty("class", "primary-button")
        done_btn.setFont(font)
        done_btn.setMinimumWidth(100)
        done_btn.setMaximumHeight(40)
        done_btn.clicked.connect(self.accept)
        button_layout.addWidget(done_btn)

        layout.addLayout(button_layout)

    def get_data(self):
        """Get delivery data"""
        return {
            'place': self.address_input.text().strip(),
            'num': self.phone_input.text().strip(),
            'price': self.price_input.value()
        }
