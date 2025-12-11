"""
Category selection view
"""
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QCursor
import config


class CategoryView(QWidget):
    """Grid view for selecting product categories"""

    category_selected = pyqtSignal(object)  # Emits Category object

    def __init__(self, parent=None):
        super().__init__(parent)
        self.categories = []
        self.category_buttons = {}
        self.selected_category = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the category grid layout"""
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.setMaximumHeight(150)

    def set_categories(self, categories):
        """Set and display categories"""
        self.categories = categories
        self.clear_layout()

        cols = config.CATEGORY_GRID_COLUMNS
        row = 0
        col = 0

        for category in categories:
            btn = QPushButton(category.name)
            btn.setProperty("class", "category-button")
            btn.setCursor(QCursor(Qt.PointingHandCursor))

            font = QFont()
            font.setPointSize(16)
            font.setBold(True)
            btn.setFont(font)

            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, c=category: self.on_category_clicked(c))

            self.category_buttons[category.id] = btn
            self.layout.addWidget(btn, row, col)

            col += 1
            if col >= cols:
                col = 0
                row += 1

        # Set column stretch
        for i in range(cols):
            self.layout.setColumnStretch(i, 1)

    def on_category_clicked(self, category):
        """Handle category button click"""
        self.select_category(category)
        self.category_selected.emit(category)

    def select_category(self, category):
        """Visually select a category"""
        # Reset all buttons
        for btn in self.category_buttons.values():
            btn.setProperty("class", "category-button")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Highlight selected
        if category and category.id in self.category_buttons:
            btn = self.category_buttons[category.id]
            btn.setProperty("class", "category-button-selected")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            self.selected_category = category

    def clear_layout(self):
        """Clear all widgets from layout"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.category_buttons.clear()
