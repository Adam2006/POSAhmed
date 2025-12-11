"""
Admin authentication dialog
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import config


class AdminAuthDialog(QDialog):
    """Dialog for admin authentication"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Authentication")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(350)

        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Title
        title_label = QLabel("Enter Admin Password")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Password field
        password_label = QLabel("Password:")
        password_label.setFont(font)
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setFont(font)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter admin password")
        self.password_input.returnPressed.connect(self.validate_password)
        layout.addWidget(self.password_input)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setFont(font)
        self.error_label.setStyleSheet("color: #ff4444;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(font)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        login_btn = QPushButton("Login")
        login_btn.setProperty("class", "primary-button")
        login_btn.setFont(font)
        login_btn.setMinimumWidth(100)
        login_btn.clicked.connect(self.validate_password)
        button_layout.addWidget(login_btn)

        layout.addLayout(button_layout)

    def validate_password(self):
        """Validate entered password"""
        entered_password = self.password_input.text().strip()

        if entered_password == config.ADMIN_PASSWORD:
            self.accept()
        else:
            self.error_label.setText("Incorrect password!")
            self.password_input.clear()
            self.password_input.setFocus()
