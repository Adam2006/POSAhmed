"""
Client management view for admin - manage credit/monthly payment customers
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QDoubleSpinBox, QTextEdit, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from models import Client


class AddClientDialog(QDialog):
    """Dialog for adding/editing client"""

    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle("Add Client" if not client else "Edit Client")
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
        title_label = QLabel("Add Client" if not self.client else "Edit Client")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Client name
        self.name_input = QLineEdit()
        self.name_input.setFont(font)
        self.name_input.setPlaceholderText("Enter client name")
        if self.client:
            self.name_input.setText(self.client.name)
        form_layout.addRow("Name:", self.name_input)

        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setFont(font)
        self.phone_input.setPlaceholderText("Enter phone number")
        if self.client:
            self.phone_input.setText(self.client.phone or '')
        form_layout.addRow("Phone:", self.phone_input)

        # Address
        self.address_input = QLineEdit()
        self.address_input.setFont(font)
        self.address_input.setPlaceholderText("Enter address")
        if self.client:
            self.address_input.setText(self.client.address or '')
        form_layout.addRow("Address:", self.address_input)

        # Credit limit
        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setFont(font)
        self.credit_limit_input.setDecimals(2)
        self.credit_limit_input.setMinimum(0)
        self.credit_limit_input.setMaximum(999999.99)
        self.credit_limit_input.setSuffix(" dt")
        if self.client:
            self.credit_limit_input.setValue(self.client.credit_limit)
        else:
            self.credit_limit_input.setValue(0.0)
        form_layout.addRow("Credit Limit:", self.credit_limit_input)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setFont(font)
        self.notes_input.setPlaceholderText("Enter notes (optional)")
        self.notes_input.setMaximumHeight(80)
        if self.client:
            self.notes_input.setPlainText(self.client.notes or '')
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)

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
        save_btn.clicked.connect(self.save_client)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def save_client(self):
        """Validate and save client"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a client name.")
            return

        self.accept()

    def get_data(self):
        """Get client data"""
        return {
            'name': self.name_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'address': self.address_input.text().strip(),
            'credit_limit': self.credit_limit_input.value(),
            'notes': self.notes_input.toPlainText().strip()
        }


class ClientView(QWidget):
    """View for managing clients"""

    client_view_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clients = []
        self.setup_ui()
        self.load_clients()

    def setup_ui(self):
        """Setup client view UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        font = QFont()
        font.setPointSize(11)

        # Header with close button
        header_layout = QHBoxLayout()

        title_label = QLabel("Client Management")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setFont(font)
        close_btn.clicked.connect(self.client_view_closed.emit)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Summary section
        self.summary_label = QLabel()
        self.summary_label.setFont(font)
        self.summary_label.setStyleSheet("background-color: #2d5016; color: white; padding: 15px; border-radius: 5px;")
        layout.addWidget(self.summary_label)

        # Clients table
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(4)
        self.clients_table.setHorizontalHeaderLabels([
            "Name", "Phone", "Address", "Credit Limit (dt)"
        ])
        self.clients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.clients_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.clients_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.clients_table.verticalHeader().setVisible(False)
        self.clients_table.setFont(font)
        self.clients_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.clients_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.clients_table)

        # Action buttons layout
        action_buttons_layout = QHBoxLayout()

        add_client_btn = QPushButton("Add Client")
        add_client_btn.setProperty("class", "primary-button")
        add_client_btn.setFont(font)
        add_client_btn.setMinimumHeight(40)
        add_client_btn.clicked.connect(self.add_client)
        action_buttons_layout.addWidget(add_client_btn)

        edit_client_btn = QPushButton("Edit Client")
        edit_client_btn.setFont(font)
        edit_client_btn.setMinimumHeight(40)
        edit_client_btn.clicked.connect(self.edit_client)
        action_buttons_layout.addWidget(edit_client_btn)

        delete_client_btn = QPushButton("Delete Client")
        delete_client_btn.setStyleSheet("background-color: #8d2020;")
        delete_client_btn.setFont(font)
        delete_client_btn.setMinimumHeight(40)
        delete_client_btn.clicked.connect(self.delete_client)
        action_buttons_layout.addWidget(delete_client_btn)

        layout.addLayout(action_buttons_layout)

    def load_clients(self):
        """Load clients from database"""
        self.clients = Client.get_all(active_only=True)
        self.refresh_table()
        self.update_summary()

    def refresh_table(self):
        """Refresh the clients table"""
        self.clients_table.setRowCount(len(self.clients))

        for row, client in enumerate(self.clients):
            # Name
            self.clients_table.setItem(row, 0, QTableWidgetItem(client.name))

            # Phone
            self.clients_table.setItem(row, 1, QTableWidgetItem(client.phone or ''))

            # Address
            self.clients_table.setItem(row, 2, QTableWidgetItem(client.address or ''))

            # Credit limit
            credit_limit_item = QTableWidgetItem(f"{client.credit_limit:.2f}")
            credit_limit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.clients_table.setItem(row, 3, credit_limit_item)

    def update_summary(self):
        """Update summary statistics"""
        if not self.clients:
            self.summary_label.setText("No clients found")
            return

        total_clients = len(self.clients)
        total_credit_limit = sum(client.credit_limit for client in self.clients)

        summary_text = (
            f"Total Clients: {total_clients}  |  "
            f"Total Credit Limit: {total_credit_limit:.2f} dt"
        )
        self.summary_label.setText(summary_text)

    def add_client(self):
        """Add new client"""
        dialog = AddClientDialog(parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            # Create new client
            client = Client(
                name=data['name'],
                phone=data['phone'],
                address=data['address'],
                credit_limit=data['credit_limit'],
                notes=data['notes']
            )

            try:
                client.save()
                QMessageBox.information(self, "Success", f"Client '{client.name}' has been added successfully.")
                self.load_clients()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add client:\n{str(e)}")

    def edit_client(self):
        """Edit selected client"""
        selected_rows = self.clients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a client to edit.")
            return

        row = selected_rows[0].row()
        client = self.clients[row]

        dialog = AddClientDialog(client=client, parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            # Update client
            client.name = data['name']
            client.phone = data['phone']
            client.address = data['address']
            client.credit_limit = data['credit_limit']
            client.notes = data['notes']

            try:
                client.save()
                QMessageBox.information(self, "Success", f"Client '{client.name}' has been updated successfully.")
                self.load_clients()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update client:\n{str(e)}")

    def delete_client(self):
        """Delete selected client (soft delete)"""
        selected_rows = self.clients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a client to delete.")
            return

        row = selected_rows[0].row()
        client = self.clients[row]

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete client '{client.name}'?\n\n"
            f"Current Balance: {client.current_balance:.2f} dt\n\n"
            "This action will deactivate the client (soft delete).",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                client.delete()
                QMessageBox.information(self, "Success", f"Client '{client.name}' has been deleted.")
                self.load_clients()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete client:\n{str(e)}")
