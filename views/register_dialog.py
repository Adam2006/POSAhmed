"""
Dialogs for opening and closing registers
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QDoubleSpinBox, QTextEdit, QRadioButton,
    QButtonGroup, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models import Register
from translations import REGISTER, COMMON


class OpenRegisterDialog(QDialog):
    """Dialog for opening a new register"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(REGISTER['open_register'])
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Title
        title_label = QLabel(REGISTER['open_register'])
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Employee name
        self.employee_input = QLineEdit()
        self.employee_input.setFont(font)
        self.employee_input.setPlaceholderText(REGISTER['employee_name'])
        form_layout.addRow(REGISTER['employee_name'] + ":", self.employee_input)

        # Shift type
        shift_label = QLabel(REGISTER['shift_type'] + ":")
        shift_label.setFont(font)
        form_layout.addRow(shift_label)

        shift_widget = QWidget()
        shift_layout = QHBoxLayout(shift_widget)
        shift_layout.setContentsMargins(0, 0, 0, 0)

        self.shift_group = QButtonGroup()
        self.morning_radio = QRadioButton(REGISTER['morning'])
        self.morning_radio.setFont(font)
        self.morning_radio.setChecked(True)
        self.shift_group.addButton(self.morning_radio)
        shift_layout.addWidget(self.morning_radio)

        self.evening_radio = QRadioButton(REGISTER['evening'])
        self.evening_radio.setFont(font)
        self.shift_group.addButton(self.evening_radio)
        shift_layout.addWidget(self.evening_radio)

        shift_layout.addStretch()
        form_layout.addRow(shift_widget)

        # Opening amount
        self.opening_amount_input = QDoubleSpinBox()
        self.opening_amount_input.setFont(font)
        self.opening_amount_input.setDecimals(2)
        self.opening_amount_input.setMinimum(0)
        self.opening_amount_input.setMaximum(999999.99)
        self.opening_amount_input.setSuffix(" dt")
        self.opening_amount_input.setValue(0.0)
        form_layout.addRow(REGISTER['opening_amount'] + ":", self.opening_amount_input)

        layout.addLayout(form_layout)

        # Note
        note_label = QLabel("Note: This will start a new shift session. All sales will be tracked under this register.")
        note_label.setFont(QFont("Arial", 10))
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #ff9900; padding: 10px; background-color: #3a3a3a; border-radius: 5px;")
        layout.addWidget(note_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton(COMMON['cancel'])
        cancel_btn.setFont(font)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        open_btn = QPushButton(REGISTER['open'])
        open_btn.setProperty("class", "primary-button")
        open_btn.setFont(font)
        open_btn.setMinimumWidth(150)
        open_btn.setMinimumHeight(40)
        open_btn.clicked.connect(self.accept)
        button_layout.addWidget(open_btn)

        layout.addLayout(button_layout)

    def get_data(self):
        """Get register data"""
        return {
            'employee_name': self.employee_input.text().strip(),
            'shift_type': 'morning' if self.morning_radio.isChecked() else 'evening',
            'opening_amount': self.opening_amount_input.value()
        }


class CloseRegisterDialog(QDialog):
    """Dialog for closing a register"""

    def __init__(self, register, parent=None):
        super().__init__(parent)
        self.register = register
        self.setWindowTitle(REGISTER['close_register'])
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Title
        shift_type = REGISTER['morning'] if self.register.shift_type == 'morning' else REGISTER['evening']
        title_label = QLabel(f"{REGISTER['close_register']} - {shift_type}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Register info
        info_label = QLabel(f"{REGISTER['employee_name']}: {self.register.employee_name}\n{COMMON['date']}: {self.register.opened_at}")
        info_label.setFont(font)
        info_label.setStyleSheet("padding: 10px; background-color: #3a3a3a; border-radius: 5px;")
        layout.addWidget(info_label)

        # Sales summary
        total_sales = self.register.get_total_sales()
        orders_count = self.register.get_orders_count()
        expected_amount = self.register.get_expected_amount()

        summary_label = QLabel(
            f"Total Orders: {orders_count}\n"
            f"Total Sales: {total_sales:.2f} dt\n"
            f"{REGISTER['opening_amount']}: {self.register.opening_amount:.2f} dt\n"
            f"{REGISTER['expected_amount']}: {expected_amount:.2f} dt"
        )
        summary_font = QFont()
        summary_font.setPointSize(13)
        summary_font.setBold(True)
        summary_label.setFont(summary_font)
        summary_label.setStyleSheet("color: #2d5016; padding: 15px; background-color: #3a3a3a; border-radius: 5px;")
        layout.addWidget(summary_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Actual closing amount
        self.closing_amount_input = QDoubleSpinBox()
        self.closing_amount_input.setFont(font)
        self.closing_amount_input.setDecimals(2)
        self.closing_amount_input.setMinimum(0)
        self.closing_amount_input.setMaximum(999999.99)
        self.closing_amount_input.setSuffix(" dt")
        self.closing_amount_input.setValue(expected_amount)
        self.closing_amount_input.valueChanged.connect(self.update_difference)
        form_layout.addRow(REGISTER['closing_amount'] + ":", self.closing_amount_input)

        # Difference
        self.difference_label = QLabel("0.00 dt")
        self.difference_label.setFont(font)
        form_layout.addRow(REGISTER['difference'] + ":", self.difference_label)

        layout.addLayout(form_layout)

        # Notes
        notes_label = QLabel(REGISTER['notes'] + ":")
        notes_label.setFont(font)
        layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setFont(font)
        self.notes_input.setPlaceholderText(REGISTER['notes'] + "...")
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(self.notes_input)

        # Update difference initially
        self.update_difference()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton(COMMON['cancel'])
        cancel_btn.setFont(font)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        close_btn = QPushButton(REGISTER['close_and_save'])
        close_btn.setProperty("class", "danger-button")
        close_btn.setFont(font)
        close_btn.setMinimumWidth(150)
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.validate_and_close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def update_difference(self):
        """Update the difference label"""
        expected = self.register.get_expected_amount()
        actual = self.closing_amount_input.value()
        difference = actual - expected

        color = "#2d5016" if difference >= 0 else "#8d2020"
        sign = "+" if difference > 0 else ""
        self.difference_label.setText(f"{sign}{difference:.2f} dt")
        self.difference_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def validate_and_close(self):
        """Validate and confirm closing"""
        expected = self.register.get_expected_amount()
        actual = self.closing_amount_input.value()
        difference = actual - expected

        if abs(difference) > 0.01:  # If there's a difference
            msg = f"{REGISTER['difference']}: {difference:.2f} dt\n\n"
            msg += f"{COMMON['confirm']}?"

            reply = QMessageBox.question(
                self,
                REGISTER['close_register'],
                msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        self.accept()

    def get_data(self):
        """Get closing data"""
        return {
            'closing_amount': self.closing_amount_input.value(),
            'notes': self.notes_input.toPlainText().strip()
        }
