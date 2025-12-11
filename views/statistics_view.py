"""
Statistics view for admin to view comprehensive sales reports and register history
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QDialog
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from models import Order, Register, get_db


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
        # Date filter section
        filter_layout = QHBoxLayout()

        filter_label = QLabel("Filter by Date:")
        filter_label.setFont(font)
        filter_layout.addWidget(filter_label)

        self.start_date = QDateEdit()
        self.start_date.setFont(font)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setDisplayFormat("yyyy/MM/dd")
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("to"))

        self.end_date = QDateEdit()
        self.end_date.setFont(font)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("yyyy/MM/dd")
        filter_layout.addWidget(self.end_date)

        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.setFont(font)
        apply_filter_btn.setMinimumHeight(35)
        apply_filter_btn.clicked.connect(self.apply_filter)
        filter_layout.addWidget(apply_filter_btn)

        show_all_btn = QPushButton("Show All")
        show_all_btn.setFont(font)
        show_all_btn.setMinimumHeight(35)
        show_all_btn.clicked.connect(self.show_all_data)
        filter_layout.addWidget(show_all_btn)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

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

        # View details button
        view_details_btn = QPushButton("View Register Details")
        view_details_btn.setProperty("class", "primary-button")
        view_details_btn.setFont(font)
        view_details_btn.setMinimumHeight(40)
        view_details_btn.clicked.connect(self.view_selected_register)
        layout.addWidget(view_details_btn)

    def load_data(self, start_date=None, end_date=None):
        """Load orders and registers from database"""
        # Load orders (without items to save memory)
        if start_date and end_date:
            self.orders = Order.get_all(start_date, end_date, load_items=False)
        else:
            self.orders = Order.get_all(load_items=False)

        # Load registers (with optional date filtering)
        self.all_registers = Register.get_all()

        # Filter registers by date if needed
        if start_date and end_date:
            self.all_registers = [
                reg for reg in self.all_registers
                if start_date <= reg.opened_at.split()[0] <= end_date
            ]

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

    def apply_filter(self):
        """Apply date filter"""
        start = self.start_date.date().toString("yyyy/MM/dd")
        end = self.end_date.date().toString("yyyy/MM/dd")
        self.load_data(start, end)

    def show_all_data(self):
        """Show all data without filter"""
        self.load_data()

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
