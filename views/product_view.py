"""
Product selection view
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QCursor
import config
import os


class ProductView(QWidget):
    """Grid view for selecting products"""

    product_selected = pyqtSignal(object)  # Emits Product object

    def __init__(self, parent=None):
        super().__init__(parent)
        self.products = []
        self.current_category = ""
        self.current_page = 1
        self.total_pages = 1

        self.setup_ui()

    def setup_ui(self):
        """Setup the product grid layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header with pagination
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.category_label = QLabel("")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.category_label.setFont(font)
        header_layout.addWidget(self.category_label)

        header_layout.addStretch()

        # Pagination controls
        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setMaximumWidth(120)
        header_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("Page: 1/1")
        font.setPointSize(12)
        self.page_label.setFont(font)
        header_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setMaximumWidth(120)
        header_layout.addWidget(self.next_btn)

        layout.addWidget(header_widget)

        # Product grid container
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.grid_widget)

    def set_products(self, products, category_name=""):
        """Set and display products"""
        self.products = products
        self.current_category = category_name
        self.current_page = 1
        self.category_label.setText(category_name)

        # Calculate total pages
        active_products = [p for p in products if p.is_active]
        self.total_pages = max(1, (len(active_products) - 1) // config.PRODUCTS_PER_PAGE + 1)

        self.refresh_display()

    def refresh_display(self):
        """Refresh the product grid display"""
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Update pagination
        self.page_label.setText(f"Page: {self.current_page}/{self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

        # Show products for current page
        active_products = [p for p in self.products if p.is_active]
        start_idx = (self.current_page - 1) * config.PRODUCTS_PER_PAGE
        end_idx = start_idx + config.PRODUCTS_PER_PAGE
        page_products = active_products[start_idx:end_idx]

        cols = config.PRODUCT_GRID_COLUMNS
        rows = config.PRODUCT_GRID_ROWS

        row = 0
        col = 0

        for product in page_products:
            product_widget = self.create_product_widget(product)
            self.grid_layout.addWidget(product_widget, row, col)

            col += 1
            if col >= cols:
                col = 0
                row += 1

        # Set column and row stretching
        for i in range(cols):
            self.grid_layout.setColumnStretch(i, 1)
        for i in range(rows):
            self.grid_layout.setRowStretch(i, 1)

    def create_product_widget(self, product):
        """Create a widget for a single product"""
        widget = QLabel()
        widget.setProperty("class", "product-item")
        widget.setCursor(QCursor(Qt.PointingHandCursor))
        widget.setAlignment(Qt.AlignCenter)
        widget.setMaximumSize(250, 100)
        widget.setMinimumSize(150, 100)

        # Try to load product image
        if product.image_path and os.path.exists(product.image_path):
            pixmap = QPixmap(product.image_path)
            scaled_pixmap = pixmap.scaled(
                widget.width(),
                int(widget.height() * 0.75),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            widget.setPixmap(scaled_pixmap)
        else:
            # Placeholder if no image - show product name centered
            widget.setText(product.name)
            font = QFont()
            font.setPointSize(14)
            font.setBold(True)
            widget.setFont(font)

        # Price label at the bottom (replaces the name banner)
        price_label = QLabel(f"{product.price}dt", widget)
        price_label.setProperty("class", "product-price")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setGeometry(
            0,
            widget.height() - 22,
            widget.width(),
            22
        )

        # Click event
        widget.mousePressEvent = lambda event, p=product: self.on_product_clicked(p)

        return widget

    def on_product_clicked(self, product):
        """Handle product click"""
        self.product_selected.emit(product)

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh_display()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_display()
