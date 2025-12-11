"""
Order history view for viewing past orders and sales reports
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from models import Order, Register


class ReprintDialog(QDialog):
    """Dialog to choose which ticket to reprint"""

    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        self.setWindowTitle(f"Reprint Order #{order.order_number}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        font = QFont()
        font.setPointSize(12)

        # Title
        title_label = QLabel(f"Reprint Order #{self.order.order_number}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Info
        info_label = QLabel("Choose which ticket to print:")
        info_label.setFont(font)
        layout.addWidget(info_label)

        # Buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)

        # Customer receipt button
        customer_btn = QPushButton("🧾 Customer Receipt")
        customer_btn.setProperty("class", "primary-button")
        customer_btn.setFont(font)
        customer_btn.setMinimumHeight(60)
        customer_btn.clicked.connect(self.print_customer)
        buttons_layout.addWidget(customer_btn)

        # Kitchen receipt button
        kitchen_btn = QPushButton("👨‍🍳 Kitchen Receipt")
        kitchen_btn.setFont(font)
        kitchen_btn.setMinimumHeight(60)
        kitchen_btn.clicked.connect(self.print_kitchen)
        buttons_layout.addWidget(kitchen_btn)

        # Both button
        both_btn = QPushButton("📋 Both Receipts")
        both_btn.setFont(font)
        both_btn.setMinimumHeight(60)
        both_btn.clicked.connect(self.print_both)
        buttons_layout.addWidget(both_btn)

        layout.addLayout(buttons_layout)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(font)
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

    def print_customer(self):
        """Print customer receipt only"""
        try:
            from utils.printer import print_customer_receipt
            print_customer_receipt(self.order)
            QMessageBox.information(self, "Success", f"Customer receipt for Order #{self.order.order_number} has been printed.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print customer receipt:\n{str(e)}")

    def print_kitchen(self):
        """Print kitchen receipt only"""
        try:
            from utils.printer import print_kitchen_receipt
            print_kitchen_receipt(self.order)
            QMessageBox.information(self, "Success", f"Kitchen receipt for Order #{self.order.order_number} has been printed.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print kitchen receipt:\n{str(e)}")

    def print_both(self):
        """Print both receipts"""
        try:
            from utils.printer import print_customer_receipt, print_kitchen_receipt
            print_customer_receipt(self.order)
            print_kitchen_receipt(self.order)
            QMessageBox.information(self, "Success", f"Both receipts for Order #{self.order.order_number} have been printed.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print receipts:\n{str(e)}")


class OrderDetailDialog(QDialog):
    """Dialog to show order details"""

    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        self.setWindowTitle(f"Order Details - #{order.order_number}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Order header info
        header_label = QLabel(f"Order #{self.order.order_number}")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Date and time
        datetime_label = QLabel(f"Date: {self.order.order_date}  |  Time: {self.order.order_time}")
        datetime_label.setFont(font)
        layout.addWidget(datetime_label)

        # Delivery info if applicable
        if self.order.is_delivery:
            delivery_label = QLabel(f"Delivery Order\nAddress: {self.order.delivery_address}\nPhone: {self.order.delivery_phone}")
            delivery_label.setFont(font)
            delivery_label.setStyleSheet("color: #ff9900; padding: 10px; border: 1px solid #ff9900; border-radius: 5px;")
            layout.addWidget(delivery_label)

        # Items table
        items_label = QLabel("Order Items:")
        items_label.setFont(font)
        items_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(items_label)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Unit Price", "Discount", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setFont(font)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.setSelectionMode(QTableWidget.NoSelection)

        # Populate items
        self.items_table.setRowCount(len(self.order.items))
        for row, item in enumerate(self.order.items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item.product_name))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{item.unit_price:.2f} dt"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item.discount:.2f} dt"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{item.final_price:.2f} dt"))

        layout.addWidget(self.items_table)

        # Total section
        total_layout = QHBoxLayout()
        total_layout.addStretch()

        total_label = QLabel(f"Total: {self.order.total_amount:.2f} dt")
        total_font = QFont()
        total_font.setPointSize(16)
        total_font.setBold(True)
        total_label.setFont(total_font)
        total_label.setStyleSheet("color: #2d5016; padding: 10px;")
        total_layout.addWidget(total_label)

        layout.addLayout(total_layout)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFont(font)
        close_btn.setMinimumHeight(40)
        close_btn.setMinimumWidth(120)
        close_btn.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)


class HistoryView(QWidget):
    """View for displaying order history for current register"""

    history_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.orders = []
        self.all_orders = []  # Store all orders for filtering
        self.current_register = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_search_filter)
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        """Setup history view UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        font = QFont()
        font.setPointSize(11)

        # Header with close button
        header_layout = QHBoxLayout()

        title_label = QLabel("Order History - Current Register")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setFont(font)
        close_btn.clicked.connect(self.history_closed.emit)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setFont(font)
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setFont(font)
        self.search_input.setPlaceholderText("Search by order number or product name...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.setMinimumWidth(400)
        search_layout.addWidget(self.search_input)

        clear_search_btn = QPushButton("Clear")
        clear_search_btn.setFont(font)
        clear_search_btn.setMinimumHeight(35)
        clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_search_btn)

        search_layout.addStretch()
        layout.addLayout(search_layout)

        # Register info section
        self.register_info_label = QLabel()
        self.register_info_label.setFont(font)
        self.register_info_label.setStyleSheet("background-color: #3a3a3a; padding: 15px; border-radius: 5px;")
        layout.addWidget(self.register_info_label)

        # Summary section (simple order count)
        self.summary_label = QLabel()
        self.summary_label.setFont(font)
        self.summary_label.setStyleSheet("background-color: #2d5016; color: white; padding: 15px; border-radius: 5px;")
        layout.addWidget(self.summary_label)

        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels([
            "Order #", "Date", "Time", "Items", "Total (dt)", "Type"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.orders_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setFont(font)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.doubleClicked.connect(self.show_order_details)
        layout.addWidget(self.orders_table)

        # Action buttons layout
        action_buttons_layout = QHBoxLayout()

        view_details_btn = QPushButton("View Order Details")
        view_details_btn.setProperty("class", "primary-button")
        view_details_btn.setFont(font)
        view_details_btn.setMinimumHeight(40)
        view_details_btn.clicked.connect(self.view_selected_order)
        action_buttons_layout.addWidget(view_details_btn)

        export_pdf_btn = QPushButton("📄 Export to PDF")
        export_pdf_btn.setFont(font)
        export_pdf_btn.setMinimumHeight(40)
        export_pdf_btn.clicked.connect(self.export_to_pdf)
        action_buttons_layout.addWidget(export_pdf_btn)

        reprint_btn = QPushButton("🖨 Reprint Ticket")
        reprint_btn.setFont(font)
        reprint_btn.setMinimumHeight(40)
        reprint_btn.clicked.connect(self.reprint_order)
        action_buttons_layout.addWidget(reprint_btn)

        delete_btn = QPushButton("🗑 Delete Order")
        delete_btn.setStyleSheet("background-color: #8d2020;")
        delete_btn.setFont(font)
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(self.delete_order)
        action_buttons_layout.addWidget(delete_btn)

        layout.addLayout(action_buttons_layout)

    def load_orders(self):
        """Load orders for current register"""
        # Get current register
        self.current_register = Register.get_current_register()

        if self.current_register:
            # Load orders for this register only
            self.all_orders = Order.get_by_register(self.current_register.id)
            self.orders = self.all_orders.copy()
            self.update_register_info()
        else:
            # No register open
            self.all_orders = []
            self.orders = []
            self.register_info_label.setText("No register is currently open")

        self.refresh_table()
        self.update_summary()

    def on_search_text_changed(self):
        """Handle search text change with debouncing"""
        # Stop any existing timer
        self.search_timer.stop()
        # Start new timer (300ms delay)
        self.search_timer.start(300)

    def apply_search_filter(self):
        """Apply search filter to order list"""
        search_text = self.search_input.text().strip().lower()

        if not search_text:
            # No search text, show all orders
            self.orders = self.all_orders.copy()
        else:
            # Filter orders by order number or product name
            self.orders = []
            for order in self.all_orders:
                # Check order number
                if search_text in str(order.order_number).lower():
                    self.orders.append(order)
                    continue

                # Check product names in order items
                for item in order.items:
                    if search_text in item.product_name.lower():
                        self.orders.append(order)
                        break

        self.refresh_table()
        self.update_summary()

    def clear_search(self):
        """Clear search input and show all orders"""
        self.search_input.clear()
        self.orders = self.all_orders.copy()
        self.refresh_table()
        self.update_summary()

    def refresh_table(self):
        """Refresh the orders table"""
        self.orders_table.setRowCount(len(self.orders))

        for row, order in enumerate(self.orders):
            # Order number
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order.order_number)))

            # Date
            self.orders_table.setItem(row, 1, QTableWidgetItem(order.order_date))

            # Time
            self.orders_table.setItem(row, 2, QTableWidgetItem(order.order_time))

            # Number of items
            item_count = sum(item.quantity for item in order.items)
            self.orders_table.setItem(row, 3, QTableWidgetItem(str(item_count)))

            # Total
            total_item = QTableWidgetItem(f"{order.total_amount:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.orders_table.setItem(row, 4, total_item)

            # Type
            order_type = "Delivery" if order.is_delivery else "Dine-in"
            self.orders_table.setItem(row, 5, QTableWidgetItem(order_type))

    def update_register_info(self):
        """Update register information display"""
        if self.current_register:
            info_text = (
                f"Register: {self.current_register.shift_type.title()} Shift  |  "
                f"Employee: {self.current_register.employee_name}  |  "
                f"Opened: {self.current_register.opened_at}"
            )
            self.register_info_label.setText(info_text)

    def update_summary(self):
        """Update summary statistics"""
        if not self.orders:
            self.summary_label.setText("No orders for this register")
            return

        total_orders = len(self.orders)
        total_items = sum(sum(item.quantity for item in order.items) for order in self.orders)
        delivery_orders = sum(1 for order in self.orders if order.is_delivery)

        summary_text = (
            f"Total Orders: {total_orders}  |  "
            f"Total Items Sold: {total_items}  |  "
            f"Delivery Orders: {delivery_orders}"
        )
        self.summary_label.setText(summary_text)

    def view_selected_order(self):
        """View details of selected order"""
        selected_rows = self.orders_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an order to view details.")
            return

        row = selected_rows[0].row()
        order = self.orders[row]
        self.show_order_details_dialog(order)

    def show_order_details(self, index):
        """Show order details when double-clicked"""
        row = index.row()
        order = self.orders[row]
        self.show_order_details_dialog(order)

    def show_order_details_dialog(self, order):
        """Show order details in a dialog"""
        dialog = OrderDetailDialog(order, self)
        dialog.exec_()

    def export_to_pdf(self):
        """Export receipt for selected order to PDF"""
        selected_rows = self.orders_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an order to export.")
            return

        row = selected_rows[0].row()
        order = self.orders[row]

        # Ask which receipt type to export
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Select Receipt Type")
        msg_box.setText("Which receipt would you like to export?")
        customer_btn = msg_box.addButton("Customer Receipt", QMessageBox.YesRole)
        kitchen_btn = msg_box.addButton("Kitchen Receipt", QMessageBox.NoRole)
        both_btn = msg_box.addButton("Both Receipts", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Cancel)

        msg_box.exec_()
        clicked_btn = msg_box.clickedButton()

        from utils.receipt_pdf import export_receipt_to_pdf

        if clicked_btn == customer_btn:
            export_receipt_to_pdf(order, 'customer', self)
        elif clicked_btn == kitchen_btn:
            export_receipt_to_pdf(order, 'kitchen', self)
        elif clicked_btn == both_btn:
            # Export both
            export_receipt_to_pdf(order, 'customer', self)
            export_receipt_to_pdf(order, 'kitchen', self)

    def reprint_order(self):
        """Reprint ticket for selected order"""
        selected_rows = self.orders_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an order to reprint.")
            return

        row = selected_rows[0].row()
        order = self.orders[row]

        # Show reprint dialog to choose which ticket to print
        dialog = ReprintDialog(order, self)
        dialog.exec_()

    def delete_order(self):
        """Delete selected order (requires admin auth)"""
        from views.admin_auth_dialog import AdminAuthDialog

        selected_rows = self.orders_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an order to delete.")
            return

        row = selected_rows[0].row()
        order = self.orders[row]

        # Require admin authentication
        auth_dialog = AdminAuthDialog(self)
        if auth_dialog.exec_() != auth_dialog.Accepted:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete Order #{order.order_number}?\n\n"
            f"Date: {order.order_date} {order.order_time}\n"
            f"Total: {order.total_amount:.2f} dt\n\n"
            "This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                order.delete()
                QMessageBox.information(self, "Success", f"Order #{order.order_number} has been deleted.")
                # Reload orders
                self.load_orders()
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete order:\n{str(e)}")
