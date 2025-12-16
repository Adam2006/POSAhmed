"""
Shopping cart view
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton,
    QHBoxLayout, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import config
from models import Client
from translations import CART, COMMON


class CartView(QWidget):
    """Shopping cart display and checkout"""

    checkout_clicked = pyqtSignal(bool, dict)  # is_delivery, delivery_data

    def __init__(self, order_controller, parent=None):
        super().__init__(parent)
        self.order_controller = order_controller
        self.delivery_data = {"place": "", "num": "", "price": 0}

        self.setup_ui()

    def setup_ui(self):
        """Setup cart UI"""
        self.setMinimumWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Order number header
        self.order_label = QLabel(f"Commande N°: {self.order_controller.get_current_order_number()}")
        self.order_label.setProperty("class", "header-label")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.order_label.setFont(font)
        self.order_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.order_label)

        # Scroll area for cart items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(5)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll, stretch=1)

        # Total label
        self.total_label = QLabel(f"{CART['total']}: 0.00dt")
        self.total_label.setProperty("class", "total-label")
        font.setPointSize(18)
        self.total_label.setFont(font)
        self.total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_label)

        # Client selection
        client_layout = QHBoxLayout()
        client_label = QLabel(f"{CART['client']}:")
        client_font = QFont()
        client_font.setPointSize(12)
        client_label.setFont(client_font)
        client_layout.addWidget(client_label)

        self.client_combo = QComboBox()
        self.client_combo.setFont(client_font)
        self.client_combo.addItem(CART['no_client'], None)
        self.load_clients()
        client_layout.addWidget(self.client_combo, stretch=1)
        layout.addLayout(client_layout)

        # Delivery checkbox
        self.delivery_checkbox = QCheckBox(f"  {CART['delivery']}?")
        self.delivery_checkbox.setFont(font)
        self.delivery_checkbox.stateChanged.connect(self.on_delivery_changed)
        layout.addWidget(self.delivery_checkbox)

        # Checkout button
        self.checkout_btn = QPushButton(CART['checkout'])
        self.checkout_btn.setProperty("class", "primary-button")
        font.setPointSize(18)
        font.setBold(True)
        self.checkout_btn.setFont(font)
        self.checkout_btn.setMinimumHeight(60)
        self.checkout_btn.clicked.connect(self.on_checkout_clicked)
        layout.addWidget(self.checkout_btn)

    def refresh(self):
        """Refresh cart display"""
        # Clear current items
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Get cart items
        cart_items = self.order_controller.get_cart_items()

        # Add cart item widgets
        for idx, item in enumerate(cart_items):
            item_widget = self.create_cart_item_widget(item, idx)
            self.scroll_layout.addWidget(item_widget)

        # Update total
        total = self.order_controller.get_total()
        self.total_label.setText(f"{CART['total']}: {total:.2f}dt")

        # Update order number
        self.order_label.setText(f"Commande N°: {self.order_controller.get_current_order_number()}")

    def create_cart_item_widget(self, item, index):
        """Create widget for a cart item"""
        widget = QPushButton()
        widget.setProperty("class", "cart-item")
        widget.setMinimumHeight(70)
        widget.setMaximumHeight(70)

        # Create layout
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(2)

        # Top row: category+name, quantity, price, delete
        top_layout = QHBoxLayout()
        top_layout.setSpacing(5)

        # Name with category
        category_name = item.get('category_name', '')
        full_name = f"{category_name} {item['name']}" if category_name else item['name']
        name_label = QLabel(full_name)
        name_label.setProperty("class", "cart-item-name")
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        name_label.setFont(font)
        name_label.setWordWrap(True)
        top_layout.addWidget(name_label, stretch=1)

        # Quantity
        qty_label = QLabel(f"×{item['quantity']}")
        qty_label.setProperty("class", "cart-item-quantity")
        font.setPointSize(13)
        qty_label.setFont(font)
        top_layout.addWidget(qty_label)

        # Price
        price_label = QLabel(f"{item['final_price']:.2f}dt")
        price_label.setProperty("class", "cart-item-price")
        font.setPointSize(11)
        price_label.setFont(font)
        price_label.setAlignment(Qt.AlignRight)
        price_label.setMinimumWidth(70)
        top_layout.addWidget(price_label)

        # Delete button
        delete_btn = QPushButton("×")
        delete_btn.setProperty("class", "delete-button")
        font.setPointSize(20)
        font.setBold(True)
        delete_btn.setFont(font)
        delete_btn.setMaximumWidth(30)
        delete_btn.clicked.connect(lambda: self.remove_item(index))
        top_layout.addWidget(delete_btn)

        main_layout.addLayout(top_layout)

        # Notes row (if any)
        if item.get('notes'):
            notes_label = QLabel(f"{COMMON['notes']}: {item['notes']}")
            notes_font = QFont()
            notes_font.setPointSize(8)
            notes_font.setItalic(True)
            notes_label.setFont(notes_font)
            notes_label.setStyleSheet("color: #aaaaaa;")
            main_layout.addWidget(notes_label)

        # Click to edit
        widget.clicked.connect(lambda: self.edit_item(index))

        return widget

    def remove_item(self, index):
        """Remove item from cart"""
        self.order_controller.remove_item(index)
        self.refresh()

    def edit_item(self, index):
        """Edit item quantity, price, and notes"""
        from views.edit_item_dialog import EditItemDialog

        cart_items = self.order_controller.get_cart_items()
        if 0 <= index < len(cart_items):
            item = cart_items[index]
            dialog = EditItemDialog(item, self)

            if dialog.exec_():
                # Update item with new values
                updated_data = dialog.get_data()
                self.order_controller.update_quantity(index, updated_data['quantity'])

                # Update price and discount
                cart_items[index]['unit_price'] = updated_data['unit_price']
                cart_items[index]['discount'] = updated_data['discount']
                cart_items[index]['notes'] = updated_data['notes']
                cart_items[index]['final_price'] = (
                    (updated_data['unit_price'] - updated_data['discount']) * updated_data['quantity']
                )

                self.refresh()

    def load_clients(self):
        """Load clients from database"""
        try:
            clients = Client.get_all(active_only=True)
            for client in clients:
                self.client_combo.addItem(client.name, client.id)
        except Exception as e:
            print(f"Error loading clients: {e}")

    def refresh_clients(self):
        """Refresh the client dropdown list"""
        # Save current selection
        current_client_id = self.client_combo.currentData()

        # Clear and reload
        self.client_combo.clear()
        self.client_combo.addItem(CART['no_client'], None)
        self.load_clients()

        # Restore selection if client still exists
        if current_client_id is not None:
            for i in range(self.client_combo.count()):
                if self.client_combo.itemData(i) == current_client_id:
                    self.client_combo.setCurrentIndex(i)
                    break

    def get_selected_client_id(self):
        """Get the selected client ID"""
        return self.client_combo.currentData()

    def on_delivery_changed(self, state):
        """Handle delivery checkbox change"""
        if state == Qt.Checked:
            # TODO: Open delivery dialog
            from views.delivery_dialog import DeliveryDialog
            dialog = DeliveryDialog(self)
            if dialog.exec_():
                self.delivery_data = dialog.get_data()
            else:
                self.delivery_checkbox.setChecked(False)
                self.delivery_data = {"place": "", "num": "", "price": 0}
        else:
            self.delivery_data = {"place": "", "num": "", "price": 0}

    def on_checkout_clicked(self):
        """Handle checkout button click"""
        is_delivery = self.delivery_checkbox.isChecked()
        self.checkout_clicked.emit(is_delivery, self.delivery_data)

        # Reset after checkout
        self.delivery_checkbox.setChecked(False)
        self.delivery_data = {"place": "", "num": "", "price": 0}
        self.client_combo.setCurrentIndex(0)  # Reset to "Cash Sale"
