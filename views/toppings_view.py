"""
Toppings management view for customizing products
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QLineEdit, QMessageBox, QDoubleSpinBox, QGroupBox, QCheckBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from models import ToppingGroup, ToppingOption, get_db
from translations import TOPPINGS, COMMON


class ToppingOptionDialog(QDialog):
    """Dialog for adding/editing topping options"""

    def __init__(self, group, option=None, parent=None):
        super().__init__(parent)
        self.group = group
        self.option = option
        self.setWindowTitle(TOPPINGS['add_option'] if not option else TOPPINGS['edit_option'])
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Name
        name_label = QLabel(TOPPINGS['option_name'] + ":")
        name_label.setFont(font)
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setFont(font)
        self.name_input.setPlaceholderText("e.g., Chicken, Marinara, Penne")
        if self.option:
            self.name_input.setText(self.option.name)
        layout.addWidget(self.name_input)

        # Price
        price_label = QLabel(TOPPINGS['extra_price'] + ":")
        price_label.setFont(font)
        layout.addWidget(price_label)

        self.price_input = QDoubleSpinBox()
        self.price_input.setFont(font)
        self.price_input.setDecimals(2)
        self.price_input.setMinimum(0.0)
        self.price_input.setMaximum(999.99)
        self.price_input.setSingleStep(0.5)
        if self.option:
            self.price_input.setValue(self.option.price)
        layout.addWidget(self.price_input)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton(COMMON['cancel'])
        cancel_btn.setFont(font)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton(COMMON['save'])
        save_btn.setFont(font)
        save_btn.setMinimumHeight(40)
        save_btn.setMinimumWidth(100)
        save_btn.setProperty("class", "primary-button")
        save_btn.clicked.connect(self.save_option)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def save_option(self):
        """Save the option"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, TOPPINGS['missing_info'], TOPPINGS['enter_option_name'])
            return

        price = self.price_input.value()

        if self.option:
            self.option.name = name
            self.option.price = price
        else:
            self.option = ToppingOption(
                group_id=self.group.id,
                name=name,
                price=price
            )

        self.option.save()
        self.accept()


class ToppingGroupDialog(QDialog):
    """Dialog for adding/editing topping groups"""

    def __init__(self, group=None, parent=None):
        super().__init__(parent)
        self.group = group
        self.setWindowTitle(TOPPINGS['add_group'] if not group else TOPPINGS['edit_group'])
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Name
        name_label = QLabel(TOPPINGS['group_name'] + ":")
        name_label.setFont(font)
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setFont(font)
        self.name_input.setPlaceholderText("e.g., Meat, Sauces, Pasta Type")
        if self.group:
            self.name_input.setText(self.group.name)
        layout.addWidget(self.name_input)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton(COMMON['cancel'])
        cancel_btn.setFont(font)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton(COMMON['save'])
        save_btn.setFont(font)
        save_btn.setMinimumHeight(40)
        save_btn.setMinimumWidth(100)
        save_btn.setProperty("class", "primary-button")
        save_btn.clicked.connect(self.save_group)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def save_group(self):
        """Save the group"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, TOPPINGS['missing_info'], TOPPINGS['enter_group_name'])
            return

        if self.group:
            self.group.name = name
        else:
            self.group = ToppingGroup(name=name)

        self.group.save()
        self.accept()


class ToppingsView(QWidget):
    """View for managing topping groups and options"""

    toppings_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups = []
        self.current_group = None
        self.setup_ui()
        self.load_groups()

    def setup_ui(self):
        """Setup toppings view UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        font = QFont()
        font.setPointSize(11)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel(TOPPINGS['manage_toppings'])
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        close_btn = QPushButton(COMMON['close'])
        close_btn.setMinimumWidth(100)
        close_btn.setFont(font)
        close_btn.clicked.connect(self.toppings_closed.emit)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Main content - split into two columns
        content_layout = QHBoxLayout()

        # Left column - Topping Groups
        left_group = QGroupBox(TOPPINGS['topping_groups'])
        left_group.setFont(font)
        left_layout = QVBoxLayout(left_group)

        # Groups table
        self.groups_table = QTableWidget()
        self.groups_table.setColumnCount(2)
        self.groups_table.setHorizontalHeaderLabels(["ID", "Group Name"])
        self.groups_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.groups_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.groups_table.verticalHeader().setVisible(False)
        self.groups_table.setFont(font)
        self.groups_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.groups_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.groups_table.itemSelectionChanged.connect(self.on_group_selected)
        left_layout.addWidget(self.groups_table)

        # Group buttons
        group_buttons_layout = QHBoxLayout()

        add_group_btn = QPushButton(TOPPINGS['add_group'])
        add_group_btn.setFont(font)
        add_group_btn.setMinimumHeight(35)
        add_group_btn.clicked.connect(self.add_group)
        group_buttons_layout.addWidget(add_group_btn)

        edit_group_btn = QPushButton(TOPPINGS['edit_group'])
        edit_group_btn.setFont(font)
        edit_group_btn.setMinimumHeight(35)
        edit_group_btn.clicked.connect(self.edit_group)
        group_buttons_layout.addWidget(edit_group_btn)

        delete_group_btn = QPushButton(TOPPINGS['delete_group'])
        delete_group_btn.setFont(font)
        delete_group_btn.setMinimumHeight(35)
        delete_group_btn.clicked.connect(self.delete_group)
        group_buttons_layout.addWidget(delete_group_btn)

        left_layout.addLayout(group_buttons_layout)

        content_layout.addWidget(left_group, stretch=1)

        # Right column - Options for selected group
        right_group = QGroupBox(TOPPINGS['options'] + " (" + TOPPINGS['select_group'] + ")")
        right_group.setFont(font)
        self.right_group_box = right_group
        right_layout = QVBoxLayout(right_group)

        # Options table
        self.options_table = QTableWidget()
        self.options_table.setColumnCount(3)
        self.options_table.setHorizontalHeaderLabels(["ID", TOPPINGS['option_name'], TOPPINGS['extra_price']])
        self.options_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.options_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.options_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.options_table.verticalHeader().setVisible(False)
        self.options_table.setFont(font)
        self.options_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.options_table.setSelectionBehavior(QTableWidget.SelectRows)
        right_layout.addWidget(self.options_table)

        # Option buttons
        option_buttons_layout = QHBoxLayout()

        add_option_btn = QPushButton(TOPPINGS['add_option'])
        add_option_btn.setFont(font)
        add_option_btn.setMinimumHeight(35)
        add_option_btn.clicked.connect(self.add_option)
        self.add_option_btn = add_option_btn
        self.add_option_btn.setEnabled(False)
        option_buttons_layout.addWidget(add_option_btn)

        edit_option_btn = QPushButton(TOPPINGS['edit_option'])
        edit_option_btn.setFont(font)
        edit_option_btn.setMinimumHeight(35)
        edit_option_btn.clicked.connect(self.edit_option)
        self.edit_option_btn = edit_option_btn
        self.edit_option_btn.setEnabled(False)
        option_buttons_layout.addWidget(edit_option_btn)

        delete_option_btn = QPushButton(TOPPINGS['delete_option'])
        delete_option_btn.setFont(font)
        delete_option_btn.setMinimumHeight(35)
        delete_option_btn.clicked.connect(self.delete_option)
        self.delete_option_btn = delete_option_btn
        self.delete_option_btn.setEnabled(False)
        option_buttons_layout.addWidget(delete_option_btn)

        right_layout.addLayout(option_buttons_layout)

        content_layout.addWidget(right_group, stretch=2)

        layout.addLayout(content_layout)

    def load_groups(self):
        """Load all topping groups"""
        self.groups = ToppingGroup.get_all(active_only=False)
        self.refresh_groups_table()

    def refresh_groups_table(self):
        """Refresh the groups table"""
        self.groups_table.setRowCount(len(self.groups))

        for row, group in enumerate(self.groups):
            self.groups_table.setItem(row, 0, QTableWidgetItem(str(group.id)))
            self.groups_table.setItem(row, 1, QTableWidgetItem(group.name))

    def on_group_selected(self):
        """When a group is selected, load its options"""
        selected_rows = self.groups_table.selectionModel().selectedRows()
        if not selected_rows:
            self.current_group = None
            self.options_table.setRowCount(0)
            self.right_group_box.setTitle(TOPPINGS['options'] + " (" + TOPPINGS['select_group'] + ")")
            self.add_option_btn.setEnabled(False)
            self.edit_option_btn.setEnabled(False)
            self.delete_option_btn.setEnabled(False)
            return

        row = selected_rows[0].row()
        self.current_group = self.groups[row]
        self.right_group_box.setTitle(f"{TOPPINGS['options']} - '{self.current_group.name}'")
        self.add_option_btn.setEnabled(True)
        self.edit_option_btn.setEnabled(True)
        self.delete_option_btn.setEnabled(True)
        self.load_options()

    def load_options(self):
        """Load options for current group"""
        if not self.current_group:
            return

        options = self.current_group.get_options(active_only=False)
        self.options_table.setRowCount(len(options))

        for row, option in enumerate(options):
            self.options_table.setItem(row, 0, QTableWidgetItem(str(option.id)))
            self.options_table.setItem(row, 1, QTableWidgetItem(option.name))
            price_item = QTableWidgetItem(f"{option.price:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.options_table.setItem(row, 2, price_item)

    def add_group(self):
        """Add new topping group"""
        dialog = ToppingGroupDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_groups()

    def edit_group(self):
        """Edit selected group"""
        selected_rows = self.groups_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, TOPPINGS['no_selection'], TOPPINGS['select_to_edit'])
            return

        row = selected_rows[0].row()
        group = self.groups[row]

        dialog = ToppingGroupDialog(group=group, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_groups()

    def delete_group(self):
        """Delete selected group"""
        selected_rows = self.groups_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, TOPPINGS['no_selection'], TOPPINGS['select_to_delete'])
            return

        row = selected_rows[0].row()
        group = self.groups[row]

        reply = QMessageBox.question(
            self,
            COMMON['confirm'],
            f"{TOPPINGS['confirm_delete_group']} '{group.name}' {TOPPINGS['and_options']}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            group.delete()
            self.load_groups()
            self.current_group = None
            self.options_table.setRowCount(0)

    def add_option(self):
        """Add new option to current group"""
        if not self.current_group:
            return

        dialog = ToppingOptionDialog(group=self.current_group, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_options()

    def edit_option(self):
        """Edit selected option"""
        if not self.current_group:
            return

        selected_rows = self.options_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, TOPPINGS['no_selection'], TOPPINGS['select_option_to_edit'])
            return

        row = selected_rows[0].row()
        option_id = int(self.options_table.item(row, 0).text())
        option = ToppingOption.get_by_id(option_id)

        if option:
            dialog = ToppingOptionDialog(group=self.current_group, option=option, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_options()

    def delete_option(self):
        """Delete selected option"""
        if not self.current_group:
            return

        selected_rows = self.options_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, TOPPINGS['no_selection'], TOPPINGS['select_option_to_delete'])
            return

        row = selected_rows[0].row()
        option_id = int(self.options_table.item(row, 0).text())
        option = ToppingOption.get_by_id(option_id)

        if option:
            reply = QMessageBox.question(
                self,
                COMMON['confirm'],
                f"{TOPPINGS['confirm_delete_option']} '{option.name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                option.delete()
                self.load_options()
