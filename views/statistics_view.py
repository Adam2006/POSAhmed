"""
Statistics view for admin to view comprehensive sales reports and register history
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from models import Order, Register, get_db
from views.custom_report_dialog import CustomReportDialog
from translations import STATISTICS


class RegisterDetailDialog(QDialog):
    """Dialog to show register details"""

    def __init__(self, register, parent=None):
        super().__init__(parent)
        self.register = register
        self.setWindowTitle(f"Register Details - {register.shift_type.title()} Shift")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Register header info
        header_label = QLabel(f"Register #{self.register.id} - {self.register.shift_type.title()} Shift")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Employee and dates
        info_label = QLabel(
            f"Employee: {self.register.employee_name}\n"
            f"Opened: {self.register.opened_at}\n"
            f"Closed: {self.register.closed_at if not self.register.is_open else 'Still Open'}"
        )
        info_label.setFont(font)
        info_label.setStyleSheet("padding: 10px; background-color: #3a3a3a; border-radius: 5px;")
        layout.addWidget(info_label)

        # Financial summary
        total_sales = self.register.get_total_sales()
        orders_count = self.register.get_orders_count()
        expected_amount = self.register.get_expected_amount()

        financial_text = (
            f"Opening Amount: {self.register.opening_amount:.2f} dt\n"
            f"Total Orders: {orders_count}\n"
            f"Total Sales: {total_sales:.2f} dt\n"
            f"Expected Cash: {expected_amount:.2f} dt"
        )

        if not self.register.is_open:
            difference = self.register.get_difference()
            color = "#2d5016" if difference >= 0 else "#8d2020"
            sign = "+" if difference > 0 else ""
            financial_text += f"\nClosing Amount: {self.register.closing_amount:.2f} dt"
            financial_text += f"\nDifference: {sign}{difference:.2f} dt"
            style = f"color: white; padding: 15px; background-color: #3a3a3a; border-radius: 5px; border-left: 5px solid {color};"
        else:
            style = "color: white; padding: 15px; background-color: #3a3a3a; border-radius: 5px;"

        financial_label = QLabel(financial_text)
        financial_font = QFont()
        financial_font.setPointSize(12)
        financial_font.setBold(True)
        financial_label.setFont(financial_font)
        financial_label.setStyleSheet(style)
        layout.addWidget(financial_label)

        # Notes if any
        if self.register.notes:
            notes_label = QLabel("Notes:")
            notes_label.setFont(font)
            notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(notes_label)

            notes_text = QLabel(self.register.notes)
            notes_text.setFont(font)
            notes_text.setWordWrap(True)
            notes_text.setStyleSheet("padding: 10px; background-color: #3a3a3a; border-radius: 5px;")
            layout.addWidget(notes_text)

        layout.addStretch()

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


class StatisticsView(QWidget):
    """Admin view for comprehensive statistics and reports"""

    statistics_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.orders = []
        self.registers = []
        self.all_registers = []  # Store all registers for pagination
        self.current_page = 1
        self.items_per_page = 7  # Reduced for low-memory systems
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup statistics view UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        font = QFont()
        font.setPointSize(11)

        # Header with close button
        header_layout = QHBoxLayout()

        title_label = QLabel("Statistics & Reports (Admin)")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setFont(font)
        close_btn.clicked.connect(self.statistics_closed.emit)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Setup registers view directly
        self.setup_registers_view(layout, font)

    def setup_registers_view(self, layout, font):
        """Setup the registers view"""
        # Search section
        search_layout = QHBoxLayout()

        search_label = QLabel("Search:")
        search_label.setFont(font)
        search_layout.addWidget(search_label)

        from PyQt5.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setFont(font)
        self.search_input.setPlaceholderText("Search by employee name, shift type, or date...")
        self.search_input.textChanged.connect(self.apply_search)
        search_layout.addWidget(self.search_input, stretch=1)

        clear_search_btn = QPushButton("Clear")
        clear_search_btn.setFont(font)
        clear_search_btn.setMinimumHeight(35)
        clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_search_btn)

        search_layout.addStretch()

        layout.addLayout(search_layout)

        # Summary section
        self.summary_label = QLabel()
        self.summary_label.setFont(font)
        self.summary_label.setStyleSheet("background-color: #2d5016; color: white; padding: 15px; border-radius: 5px;")
        layout.addWidget(self.summary_label)

        # Registers table
        registers_label = QLabel("Register History:")
        registers_label.setFont(font)
        registers_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(registers_label)

        self.registers_table = QTableWidget()
        self.registers_table.setColumnCount(7)
        self.registers_table.setHorizontalHeaderLabels([
            "ID", "Shift", "Employee", "Opened", "Closed", "Sales", "Status"
        ])
        self.registers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.registers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.registers_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.registers_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.registers_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.registers_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.registers_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.registers_table.verticalHeader().setVisible(False)
        self.registers_table.setFont(font)
        self.registers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.registers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.registers_table.doubleClicked.connect(self.show_register_details)
        layout.addWidget(self.registers_table)

        # Pagination controls
        pagination_layout = QHBoxLayout()

        self.page_info_label = QLabel()
        self.page_info_label.setFont(font)
        pagination_layout.addWidget(self.page_info_label)

        pagination_layout.addStretch()

        self.first_page_btn = QPushButton("⏮ First")
        self.first_page_btn.setFont(font)
        self.first_page_btn.setMinimumHeight(35)
        self.first_page_btn.clicked.connect(self.go_to_first_page)
        pagination_layout.addWidget(self.first_page_btn)

        self.prev_page_btn = QPushButton("◀ Previous")
        self.prev_page_btn.setFont(font)
        self.prev_page_btn.setMinimumHeight(35)
        self.prev_page_btn.clicked.connect(self.go_to_previous_page)
        pagination_layout.addWidget(self.prev_page_btn)

        self.page_label = QLabel()
        self.page_label.setFont(font)
        self.page_label.setStyleSheet("font-weight: bold; padding: 0 20px;")
        pagination_layout.addWidget(self.page_label)

        self.next_page_btn = QPushButton("Next ▶")
        self.next_page_btn.setFont(font)
        self.next_page_btn.setMinimumHeight(35)
        self.next_page_btn.clicked.connect(self.go_to_next_page)
        pagination_layout.addWidget(self.next_page_btn)

        self.last_page_btn = QPushButton("Last ⏭")
        self.last_page_btn.setFont(font)
        self.last_page_btn.setMinimumHeight(35)
        self.last_page_btn.clicked.connect(self.go_to_last_page)
        pagination_layout.addWidget(self.last_page_btn)

        layout.addLayout(pagination_layout)

        # Action buttons layout
        action_buttons_layout = QHBoxLayout()

        view_details_btn = QPushButton("View Register Details")
        view_details_btn.setProperty("class", "primary-button")
        view_details_btn.setFont(font)
        view_details_btn.setMinimumHeight(40)
        view_details_btn.clicked.connect(self.view_selected_register)
        action_buttons_layout.addWidget(view_details_btn)

        print_register_btn = QPushButton("Print Register Report")
        print_register_btn.setFont(font)
        print_register_btn.setMinimumHeight(40)
        print_register_btn.clicked.connect(self.print_selected_register)
        action_buttons_layout.addWidget(print_register_btn)

        print_all_btn = QPushButton("Print All Shown Registers")
        print_all_btn.setFont(font)
        print_all_btn.setMinimumHeight(40)
        print_all_btn.clicked.connect(self.print_all_shown_registers)
        action_buttons_layout.addWidget(print_all_btn)

        print_custom_btn = QPushButton(STATISTICS['custom_report'])
        print_custom_btn.setFont(font)
        print_custom_btn.setMinimumHeight(40)
        print_custom_btn.clicked.connect(self.print_custom_report)
        action_buttons_layout.addWidget(print_custom_btn)

        layout.addLayout(action_buttons_layout)

    def load_data(self):
        """Load orders and registers from database"""
        # Load all orders (without items to save memory)
        self.orders = Order.get_all(load_items=False)

        # Load all registers
        self.original_registers = Register.get_all()
        self.all_registers = self.original_registers.copy()

        # Reset to first page when loading new data
        self.current_page = 1
        self.apply_pagination()
        self.update_summary()

    def refresh_registers_table(self):
        """Refresh the registers table"""
        self.registers_table.setRowCount(len(self.registers))

        for row, register in enumerate(self.registers):
            # ID
            self.registers_table.setItem(row, 0, QTableWidgetItem(str(register.id)))

            # Shift type
            self.registers_table.setItem(row, 1, QTableWidgetItem(register.shift_type.title()))

            # Employee
            self.registers_table.setItem(row, 2, QTableWidgetItem(register.employee_name))

            # Opened
            self.registers_table.setItem(row, 3, QTableWidgetItem(register.opened_at))

            # Closed
            closed_text = register.closed_at if not register.is_open else "-"
            self.registers_table.setItem(row, 4, QTableWidgetItem(closed_text))

            # Total sales
            total_sales = register.get_total_sales()
            sales_item = QTableWidgetItem(f"{total_sales:.2f} dt")
            sales_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.registers_table.setItem(row, 5, sales_item)

            # Status
            status = "Open" if register.is_open else "Closed"
            status_item = QTableWidgetItem(status)
            if register.is_open:
                status_item.setForeground(Qt.green)
            self.registers_table.setItem(row, 6, status_item)

    def apply_pagination(self):
        """Apply pagination to registers list"""
        total_registers = len(self.all_registers)
        total_pages = (total_registers + self.items_per_page - 1) // self.items_per_page

        if total_pages == 0:
            total_pages = 1

        # Ensure current page is within bounds
        self.current_page = max(1, min(self.current_page, total_pages))

        # Calculate start and end indices
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_registers)

        # Get registers for current page
        self.registers = self.all_registers[start_idx:end_idx]

        # Update table and pagination controls
        self.refresh_registers_table()
        self.update_pagination_controls(total_pages)

    def update_pagination_controls(self, total_pages):
        """Update pagination button states and labels"""
        total_registers = len(self.all_registers)
        start_idx = (self.current_page - 1) * self.items_per_page + 1
        end_idx = min(self.current_page * self.items_per_page, total_registers)

        # Update page label
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")

        # Update info label
        self.page_info_label.setText(f"Showing {start_idx}-{end_idx} of {total_registers} registers")

        # Enable/disable buttons based on current page
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)
        self.last_page_btn.setEnabled(self.current_page < total_pages)

    def go_to_first_page(self):
        """Go to first page"""
        self.current_page = 1
        self.apply_pagination()

    def go_to_previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.apply_pagination()

    def go_to_next_page(self):
        """Go to next page"""
        total_pages = (len(self.all_registers) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.apply_pagination()

    def go_to_last_page(self):
        """Go to last page"""
        total_pages = (len(self.all_registers) + self.items_per_page - 1) // self.items_per_page
        self.current_page = max(1, total_pages)
        self.apply_pagination()

    def update_summary(self):
        """Update summary statistics"""
        if not self.orders and not self.all_registers:
            self.summary_label.setText("No data found")
            return

        total_orders = len(self.orders)
        total_sales = sum(order.total_amount for order in self.orders)

        # Calculate total items efficiently using SQL instead of loading all items
        db = get_db()
        cursor = db.execute("SELECT SUM(quantity) as total FROM order_items")
        result = cursor.fetchone()
        total_items = result['total'] if result['total'] else 0

        delivery_orders = sum(1 for order in self.orders if order.is_delivery)
        total_registers = len(self.all_registers)
        open_registers = sum(1 for reg in self.all_registers if reg.is_open)

        summary_text = (
            f"Total Registers: {total_registers} ({open_registers} Open)  |  "
            f"Total Orders: {total_orders}  |  "
            f"Total Sales: {total_sales:.2f} dt  |  "
            f"Total Items Sold: {total_items}  |  "
            f"Delivery Orders: {delivery_orders}"
        )
        self.summary_label.setText(summary_text)

    def apply_search(self):
        """Apply search filter"""
        search_text = self.search_input.text().strip().lower()

        if not search_text:
            # No search, show all
            self.all_registers = self.original_registers.copy()
        else:
            # Filter registers based on search text
            self.all_registers = [
                reg for reg in self.original_registers
                if (search_text in reg.employee_name.lower() or
                    search_text in reg.shift_type.lower() or
                    search_text in reg.opened_at.lower() or
                    (reg.closed_at and search_text in reg.closed_at.lower()))
            ]

        # Reset to first page and update display
        self.current_page = 1
        self.apply_pagination()
        self.update_summary()

    def clear_search(self):
        """Clear search filter"""
        self.search_input.clear()
        self.all_registers = self.original_registers.copy()
        self.current_page = 1
        self.apply_pagination()
        self.update_summary()

    def view_selected_register(self):
        """View details of selected register"""
        from PyQt5.QtWidgets import QMessageBox

        selected_rows = self.registers_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a register to view details.")
            return

        row = selected_rows[0].row()
        register = self.registers[row]
        self.show_register_details_dialog(register)

    def show_register_details(self, index):
        """Show register details when double-clicked"""
        row = index.row()
        register = self.registers[row]
        self.show_register_details_dialog(register)

    def show_register_details_dialog(self, register):
        """Show register details in a dialog"""
        dialog = RegisterDetailDialog(register, self)
        dialog.exec_()

    def get_register_product_summary(self, register):
        """Get product summary for a register grouped by product type"""
        db = get_db()

        # Get all order items for orders in this register with category names
        cursor = db.execute("""
            SELECT oi.product_name,
                   c.name as category_name,
                   SUM(oi.quantity) as total_quantity
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            LEFT JOIN products p ON oi.product_name = p.name
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE o.register_id = ?
            GROUP BY oi.product_name, c.name
            ORDER BY c.name, oi.product_name
        """, (register.id,))

        products = {}
        for row in cursor.fetchall():
            category_name = row['category_name'] if row['category_name'] else ''
            product_name = row['product_name']
            total_quantity = row['total_quantity']

            product_display = f"{category_name} {product_name}" if category_name else product_name
            products[product_display] = total_quantity

        return products

    def print_selected_register(self):
        """Print report for selected register"""
        from PyQt5.QtWidgets import QMessageBox

        selected_rows = self.registers_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a register to print.")
            return

        row = selected_rows[0].row()
        register = self.registers[row]

        # Get product summary
        products = self.get_register_product_summary(register)

        if not products:
            QMessageBox.information(self, "No Data", "No products sold in this register.")
            return

        # Print the register report
        self.print_register_report(register, products)

        QMessageBox.information(self, "Success", "Register report sent to printer.")

    def print_all_shown_registers(self):
        """Print combined report for all currently displayed registers (respects search filter)"""
        from PyQt5.QtWidgets import QMessageBox

        if not self.all_registers:
            QMessageBox.warning(self, "No Data", "No registers to print.")
            return

        # Confirm before printing
        reply = QMessageBox.question(
            self,
            "Confirm Print",
            f"Print combined report for all {len(self.all_registers)} shown registers?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Combine products from all registers
            combined_products = {}
            total_sales = 0
            total_orders = 0

            for register in self.all_registers:
                products = self.get_register_product_summary(register)
                # Sum up products
                for product_name, quantity in products.items():
                    combined_products[product_name] = combined_products.get(product_name, 0) + quantity

                # Sum up sales and orders
                total_sales += register.get_total_sales()
                total_orders += register.get_orders_count()

            if not combined_products:
                QMessageBox.information(self, "No Data", "No products sold in the selected registers.")
                return

            # Print combined report
            self.print_combined_registers_report(self.all_registers, combined_products, total_sales, total_orders)
            QMessageBox.information(self, "Success", f"Combined report for {len(self.all_registers)} registers sent to printer.")

    def print_register_report(self, register, products):
        """Print a register report with product summary"""
        import config

        # Check if printing is available
        try:
            import win32print
            if not config.ENABLE_PRINTING:
                print("Printing disabled in config")
                return
        except ImportError:
            print("win32print not available")
            return

        # ESC/POS commands
        set_size_command = "\x1B\x4D\x00"
        set_font_command = "\x1B\x21\x00"
        bold_command = "\x1B\x45\x01"
        title_command = "\x1B\x21\x30" + "\x1B\x45\x01"

        # Build report
        lines = [
            title_command + f"    REGISTER REPORT #{register.id}",
            "",
            set_font_command + bold_command,
            f"Shift:         {register.shift_type.title()}",
            f"Employee:      {register.employee_name}",
            f"Opened:        {register.opened_at}",
            f"Closed:        {register.closed_at if not register.is_open else 'Still Open'}",
            "",
            "_____________________________________________",
        ]

        # Financial summary
        total_sales = register.get_total_sales()
        orders_count = register.get_orders_count()
        expected_amount = register.get_expected_amount()

        lines.extend([
            f"Opening Amount:              {register.opening_amount:.2f}dt",
            f"Total Orders:                {orders_count}",
            f"Total Sales:                 {total_sales:.2f}dt",
            f"Expected Cash:               {expected_amount:.2f}dt",
        ])

        if not register.is_open:
            difference = register.get_difference()
            sign = "+" if difference > 0 else ""
            lines.extend([
                f"Closing Amount:              {register.closing_amount:.2f}dt",
                f"Difference:                  {sign}{difference:.2f}dt",
            ])

        lines.extend([
            "_____________________________________________",
            "",
            bold_command + "PRODUCTS SOLD:",
            "_____________________________________________",
            "Product                         Quantity",
            "_____________________________________________",
        ])

        # Add products sorted by quantity (descending)
        total_items = 0
        sorted_products = sorted(products.items(), key=lambda x: x[1], reverse=True)
        for product_name, quantity in sorted_products:
            total_items += quantity
            # Truncate product name to 30 chars
            product_display = product_name[:30].ljust(30)
            quantity_display = str(quantity).rjust(8)
            lines.append(f"{product_display}{quantity_display}")

        lines.extend([
            "_____________________________________________",
            bold_command + f"Total Items Sold:               {total_items}",
            "_____________________________________________",
        ])

        # Add notes if any
        if register.notes:
            lines.extend([
                "",
                "Notes:",
                register.notes,
            ])

        report_text = "\n".join(lines)
        report_data = set_size_command + report_text

        # Add paper cut command at the end
        cut_command = "\x1D\x56\x01"
        cut_data = "\n\n\n\n\n" + cut_command

        try:
            hPrinter = win32print.OpenPrinter(config.PRINTER_NAME)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Register Report", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, report_data.encode("utf-8"))
                    win32print.WritePrinter(hPrinter, cut_data.encode("utf-8"))
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            print(f"Error printing register report: {e}")

    def print_combined_registers_report(self, registers, combined_products, total_sales, total_orders):
        """Print a combined report for multiple registers with product summary"""
        import config

        # Check if printing is available
        try:
            import win32print
            if not config.ENABLE_PRINTING:
                print("Printing disabled in config")
                return
        except ImportError:
            print("win32print not available")
            return

        # ESC/POS commands
        set_size_command = "\x1B\x4D\x00"
        set_font_command = "\x1B\x21\x00"
        bold_command = "\x1B\x45\x01"
        title_command = "\x1B\x21\x30" + "\x1B\x45\x01"

        # Build report
        lines = [
            title_command + f"REGISTERS REPORT",
            "",
            set_font_command + bold_command,
            f"Number of Registers: {len(registers)}",
            "",
            "_____________________________________________",
        ]

        # (Removed register details section as requested)

        lines.extend([
            "_____________________________________________",
            "",
            f"Total Orders:                {total_orders}",
            f"Total Sales:                 {total_sales:.2f}dt",
            "",
            "_____________________________________________",
            "",
            bold_command + "PRODUCTS SOLD (COMBINED):",
            "_____________________________________________",
            "Product                         Quantity",
            "_____________________________________________",
        ])

        # Add combined products sorted by quantity (descending)
        total_items = 0
        sorted_products = sorted(combined_products.items(), key=lambda x: x[1], reverse=True)
        for product_name, quantity in sorted_products:
            total_items += quantity
            # Truncate product name to 30 chars
            product_display = product_name[:30].ljust(30)
            quantity_display = str(quantity).rjust(8)
            lines.append(f"{product_display}{quantity_display}")

        lines.extend([
            "_____________________________________________",
            bold_command + f"Total Items Sold:               {total_items}",
            "_____________________________________________",
        ])

        report_text = "\n".join(lines)
        report_data = set_size_command + report_text

        # Add paper cut command at the end
        cut_command = "\x1D\x56\x01"
        cut_data = "\n\n\n\n\n" + cut_command

        try:
            hPrinter = win32print.OpenPrinter(config.PRINTER_NAME)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Combined Registers Report", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, report_data.encode("utf-8"))
                    win32print.WritePrinter(hPrinter, cut_data.encode("utf-8"))
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            print(f"Error printing combined registers report: {e}")

    def print_custom_report(self):
        """Print custom filtered register report"""
        from PyQt5.QtWidgets import QMessageBox

        # Determine which registers to use
        selected_rows = self.registers_table.selectionModel().selectedRows()

        if selected_rows:
            # Single register selected
            row = selected_rows[0].row()
            register = self.registers[row]

            # Show dialog for single register
            dialog = CustomReportDialog(register=register, parent=self)
            if dialog.exec_() != QDialog.Accepted:
                return

            # Get filter configuration
            filter_config = dialog.get_filter_config()

            # Get products for this register
            products = self.get_register_product_summary(register)

            # Apply filters
            filtered_products = self.apply_product_filters(products, filter_config)

            if not filtered_products:
                QMessageBox.information(self, "No Data", "No products match the selected filters.")
                return

            # Print filtered register report
            self.print_register_report(register, filtered_products)
            QMessageBox.information(self, "Success", "Custom register report sent to printer.")

        else:
            # No selection - use all shown registers
            if not self.all_registers:
                QMessageBox.warning(self, "No Data", "No registers to print.")
                return

            # Show dialog for all registers
            dialog = CustomReportDialog(registers=self.all_registers, parent=self)
            if dialog.exec_() != QDialog.Accepted:
                return

            # Get filter configuration
            filter_config = dialog.get_filter_config()

            # Combine products from all registers - FILTER FIRST, THEN COMBINE
            combined_products = {}
            total_sales = 0
            total_orders = 0

            for register in self.all_registers:
                # Get products for this register
                products = self.get_register_product_summary(register)
                print(f"\n>>> Register {register.id} RAW products from DB:")
                for p, q in sorted(products.items()):
                    if 'jambon' in p.lower():
                        print(f"  {p}: {q}")

                # Apply filters WITHOUT adding total lines yet (pass skip_totals flag)
                filter_config_no_totals = filter_config.copy()
                filter_config_no_totals['skip_totals'] = True
                filtered_products_for_register = self.apply_product_filters(products, filter_config_no_totals)

                print(f">>> Register {register.id} AFTER filtering:")
                for p, q in sorted(filtered_products_for_register.items()):
                    print(f"  {p}: {q}")

                # Sum up only the filtered products
                print(f">>> Combining into combined_products:")
                for product_name, quantity in filtered_products_for_register.items():
                    old_val = combined_products.get(product_name, 0)
                    new_val = old_val + quantity
                    combined_products[product_name] = new_val
                    print(f"  {product_name}: {old_val} + {quantity} = {new_val}")

                # Sum up sales and orders (still sum all, as we want total register stats)
                total_sales += register.get_total_sales()
                total_orders += register.get_orders_count()

            if not combined_products:
                QMessageBox.information(self, "No Data", "No products match the selected filters.")
                return

            # Now add the TOTAL lines for keywords AFTER combining
            if filter_config.get('keywords'):
                keywords = filter_config['keywords']
                keyword_totals = {kw: 0 for kw in keywords}

                # Calculate totals from combined products
                for product_name, quantity in combined_products.items():
                    for kw in keywords:
                        if kw.lower() in product_name.lower():
                            keyword_totals[kw] += quantity

                # DEBUG: Print what we're about to send to printer
                print("\n=== FINAL COMBINED PRODUCTS ===")
                for product_name, quantity in sorted(combined_products.items()):
                    print(f"{product_name}: {quantity}")
                print(f"\nKeyword totals: {keyword_totals}")
                print("================================\n")

                # Add total lines
                for keyword, total in keyword_totals.items():
                    if total > 0:
                        combined_products[f"═══ TOTAL {keyword.upper()}: ═══"] = total

            # Print filtered combined report
            self.print_combined_registers_report(self.all_registers, combined_products, total_sales, total_orders)
            QMessageBox.information(self, "Success", f"Custom combined report for {len(self.all_registers)} registers sent to printer.")

    def apply_product_filters(self, products, filter_config):
        """Apply category and keyword filters to products dict

        If keywords are provided, shows both individual products AND totals by keyword
        to track ingredient/stock usage across all product types.
        """
        selected_categories = filter_config['categories']
        keywords = filter_config['keywords']
        all_categories = filter_config['all_categories']
        skip_totals = filter_config.get('skip_totals', False)  # Flag to skip adding total lines

        filtered_products = {}

        # If keywords are provided, show individual products + totals by keyword
        if keywords:
            # Track totals for each keyword
            keyword_totals = {kw: 0 for kw in keywords}

            # First pass: add individual products that match keywords
            for product_display, quantity in products.items():
                # Check if product matches any keyword
                matches_keyword = any(kw.lower() in product_display.lower() for kw in keywords)

                if matches_keyword:
                    # Check category filter
                    parts = product_display.split(' ', 1)
                    if len(parts) == 2:
                        category_name = parts[0]
                    else:
                        category_name = ''

                    category_match = all_categories or (category_name in selected_categories) or (not category_name and len(selected_categories) > 0)

                    if category_match:
                        # Add individual product
                        filtered_products[product_display] = quantity

                        # Add to keyword totals
                        for kw in keywords:
                            if kw.lower() in product_display.lower():
                                keyword_totals[kw] += quantity

            # Second pass: add total lines for each keyword (if there were matches)
            # Only add totals if skip_totals is False (for single register or final combined report)
            if not skip_totals:
                for keyword, total in keyword_totals.items():
                    if total > 0:
                        # Add a summary line with the keyword total
                        filtered_products[f"═══ TOTAL {keyword.upper()}: ═══"] = total

        else:
            # No keywords - use normal category filtering (show all products in category)
            for product_display, quantity in products.items():
                parts = product_display.split(' ', 1)

                if len(parts) == 2:
                    category_name = parts[0]
                else:
                    category_name = ''

                # Check category filter
                category_match = all_categories or (category_name in selected_categories) or (not category_name and len(selected_categories) > 0)

                if category_match:
                    filtered_products[product_display] = quantity

        return filtered_products
