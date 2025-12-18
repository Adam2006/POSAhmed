"""
Custom Report Dialog for filtering register reports
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QLineEdit, QGroupBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models import Category
from translations import STATISTICS, COMMON


class CustomReportDialog(QDialog):
    """Dialog for customizing register reports with filters"""

    def __init__(self, register=None, registers=None, parent=None):
        super().__init__(parent)
        self.register = register
        self.registers = registers
        self.category_checkboxes = {}

        title = STATISTICS['custom_report']
        if register:
            title += f" - Register #{register.id}"
        elif registers:
            title += f" - {len(registers)} Registers"

        self.setWindowTitle(title)
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

        # Header
        header_label = QLabel(STATISTICS['filter_options'])
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Category Filter Section
        category_group = QGroupBox(STATISTICS['filter_by_category'])
        category_group.setFont(font)
        category_layout = QVBoxLayout(category_group)

        # "All Categories" checkbox
        self.all_categories_checkbox = QCheckBox(STATISTICS['all_categories'])
        self.all_categories_checkbox.setFont(font)
        self.all_categories_checkbox.setChecked(True)
        self.all_categories_checkbox.stateChanged.connect(self.on_all_categories_toggled)
        category_layout.addWidget(self.all_categories_checkbox)

        # Scroll area for category checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Get all categories
        categories = Category.get_all(active_only=False)
        for category in categories:
            checkbox = QCheckBox(category.name)
            checkbox.setFont(font)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_category_checkbox_changed)
            self.category_checkboxes[category.id] = {
                'checkbox': checkbox,
                'name': category.name
            }
            scroll_layout.addWidget(checkbox)

        scroll.setWidget(scroll_widget)
        category_layout.addWidget(scroll)
        layout.addWidget(category_group)

        # Keyword Filter Section
        keyword_group = QGroupBox(STATISTICS['filter_by_keyword'])
        keyword_group.setFont(font)
        keyword_layout = QVBoxLayout(keyword_group)

        keyword_label = QLabel(STATISTICS['enter_keywords'] + ":")
        keyword_label.setFont(font)
        keyword_layout.addWidget(keyword_label)

        self.keyword_input = QLineEdit()
        self.keyword_input.setFont(font)
        self.keyword_input.setPlaceholderText(STATISTICS['keywords_help'])
        keyword_layout.addWidget(self.keyword_input)

        layout.addWidget(keyword_group)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton(COMMON['cancel'])
        cancel_btn.setFont(font)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        generate_btn = QPushButton(STATISTICS['generate_report'])
        generate_btn.setFont(font)
        generate_btn.setMinimumHeight(40)
        generate_btn.setMinimumWidth(150)
        generate_btn.setProperty("class", "primary-button")
        generate_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(generate_btn)

        layout.addLayout(buttons_layout)

    def on_all_categories_toggled(self, state):
        """When 'All Categories' is toggled, update all category checkboxes"""
        is_checked = (state == Qt.Checked)
        for category_data in self.category_checkboxes.values():
            category_data['checkbox'].blockSignals(True)
            category_data['checkbox'].setChecked(is_checked)
            category_data['checkbox'].blockSignals(False)

    def on_category_checkbox_changed(self):
        """When any category checkbox changes, update 'All Categories' checkbox"""
        all_checked = all(
            category_data['checkbox'].isChecked()
            for category_data in self.category_checkboxes.values()
        )
        self.all_categories_checkbox.blockSignals(True)
        self.all_categories_checkbox.setChecked(all_checked)
        self.all_categories_checkbox.blockSignals(False)

    def get_selected_categories(self):
        """Get list of selected category names"""
        selected = []
        for category_data in self.category_checkboxes.values():
            if category_data['checkbox'].isChecked():
                selected.append(category_data['name'])
        return selected

    def get_keywords(self):
        """Get list of keywords from input"""
        keywords_text = self.keyword_input.text().strip()
        if not keywords_text:
            return []
        # Split by comma and clean up
        keywords = [kw.strip().lower() for kw in keywords_text.split(',') if kw.strip()]
        return keywords

    def get_filter_config(self):
        """Get complete filter configuration"""
        return {
            'categories': self.get_selected_categories(),
            'keywords': self.get_keywords(),
            'all_categories': self.all_categories_checkbox.isChecked()
        }
