"""
Employee management view for admin - track employees, salaries, and expenses
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QDoubleSpinBox, QTextEdit, QDateEdit, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from models import Employee, EmployeeExpense, EmployeeDayOff
from datetime import datetime


class AddEmployeeDialog(QDialog):
    """Dialog for adding/editing employee"""

    def __init__(self, employee=None, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.setWindowTitle("Add Employee" if not employee else "Edit Employee")
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
        title_label = QLabel("Add Employee" if not self.employee else "Edit Employee")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Employee name
        self.name_input = QLineEdit()
        self.name_input.setFont(font)
        self.name_input.setPlaceholderText("Enter employee name")
        if self.employee:
            self.name_input.setText(self.employee.name)
        form_layout.addRow("Name:", self.name_input)

        # Daily salary
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setFont(font)
        self.salary_input.setDecimals(2)
        self.salary_input.setMinimum(0)
        self.salary_input.setMaximum(9999.99)
        self.salary_input.setSuffix(" dt/day")
        if self.employee:
            self.salary_input.setValue(self.employee.daily_salary)
        else:
            self.salary_input.setValue(0.0)
        form_layout.addRow("Daily Salary:", self.salary_input)

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
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def get_data(self):
        """Get employee data"""
        return {
            'name': self.name_input.text().strip(),
            'daily_salary': self.salary_input.value()
        }


class AddExpenseDialog(QDialog):
    """Dialog for adding expense to an employee"""

    def __init__(self, employees, parent=None):
        super().__init__(parent)
        self.employees = employees
        self.setWindowTitle("Add Expense")
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
        title_label = QLabel("Add Expense")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Employee selection
        self.employee_combo = QComboBox()
        self.employee_combo.setFont(font)
        for employee in self.employees:
            self.employee_combo.addItem(employee.name, employee.id)
        form_layout.addRow("Employee:", self.employee_combo)

        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setFont(font)
        self.amount_input.setDecimals(2)
        self.amount_input.setMinimum(0.01)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setSuffix(" dt")
        self.amount_input.setValue(0.0)
        form_layout.addRow("Amount:", self.amount_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setFont(font)
        self.description_input.setPlaceholderText("Enter description (optional)")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

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

        save_btn = QPushButton("Add Expense")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFont(font)
        save_btn.setMinimumWidth(150)
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def get_data(self):
        """Get expense data"""
        return {
            'employee_id': self.employee_combo.currentData(),
            'amount': self.amount_input.value(),
            'description': self.description_input.toPlainText().strip()
        }


class AddDayOffDialog(QDialog):
    """Dialog for adding day off for an employee (date range)"""

    def __init__(self, employees, parent=None):
        super().__init__(parent)
        self.employees = employees
        self.setWindowTitle("Add Days Off")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(550)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Title
        title_label = QLabel("Add Days Off (Date Range)")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Employee selection
        self.employee_combo = QComboBox()
        self.employee_combo.setFont(font)
        for employee in self.employees:
            self.employee_combo.addItem(employee.name, employee.id)
        form_layout.addRow("Employee:", self.employee_combo)

        # Start Date
        self.start_date_input = QDateEdit()
        self.start_date_input.setFont(font)
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setDisplayFormat("yyyy/MM/dd")
        self.start_date_input.dateChanged.connect(self.on_start_date_changed)
        form_layout.addRow("From Date:", self.start_date_input)

        # End Date
        self.end_date_input = QDateEdit()
        self.end_date_input.setFont(font)
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDisplayFormat("yyyy/MM/dd")
        self.end_date_input.setMinimumDate(QDate.currentDate())
        form_layout.addRow("To Date:", self.end_date_input)

        # Days count label
        self.days_label = QLabel("Total Days: 1")
        self.days_label.setFont(font)
        self.days_label.setStyleSheet("color: #2d5016; font-weight: bold;")
        form_layout.addRow("", self.days_label)

        # Connect signals to update days count
        self.start_date_input.dateChanged.connect(self.update_days_count)
        self.end_date_input.dateChanged.connect(self.update_days_count)

        # Reason
        self.reason_input = QTextEdit()
        self.reason_input.setFont(font)
        self.reason_input.setPlaceholderText("Enter reason (e.g., Vacation, Sick Leave, Personal)")
        self.reason_input.setMaximumHeight(80)
        form_layout.addRow("Reason:", self.reason_input)

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

        save_btn = QPushButton("Add Days Off")
        save_btn.setProperty("class", "primary-button")
        save_btn.setFont(font)
        save_btn.setMinimumWidth(150)
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def on_start_date_changed(self, date):
        """Update minimum end date when start date changes"""
        self.end_date_input.setMinimumDate(date)
        if self.end_date_input.date() < date:
            self.end_date_input.setDate(date)

    def update_days_count(self):
        """Update the total days label"""
        start = self.start_date_input.date()
        end = self.end_date_input.date()
        days = start.daysTo(end) + 1
        self.days_label.setText(f"Total Days: {days}")

    def get_data(self):
        """Get day off data"""
        return {
            'employee_id': self.employee_combo.currentData(),
            'start_date': self.start_date_input.date().toString("yyyy/MM/dd"),
            'end_date': self.end_date_input.date().toString("yyyy/MM/dd"),
            'reason': self.reason_input.toPlainText().strip()
        }


class EmployeeView(QWidget):
    """View for managing employees and their expenses"""

    employee_view_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.employees = []
        self.all_employees = []  # Store all employees for filtering
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_search_filter)
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        """Setup employee view UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        font = QFont()
        font.setPointSize(11)

        # Header with close button
        header_layout = QHBoxLayout()

        title_label = QLabel("Employee Management (Admin)")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setFont(font)
        close_btn.clicked.connect(self.employee_view_closed.emit)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setFont(font)
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setFont(font)
        self.search_input.setPlaceholderText("Search by employee name...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.setMinimumWidth(300)
        search_layout.addWidget(self.search_input)

        clear_search_btn = QPushButton("Clear")
        clear_search_btn.setFont(font)
        clear_search_btn.setMinimumHeight(35)
        clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_search_btn)

        search_layout.addStretch()
        layout.addLayout(search_layout)

        # Date filter section for balance calculation
        filter_layout = QHBoxLayout()

        filter_label = QLabel("Calculate Balance:")
        filter_label.setFont(font)
        filter_layout.addWidget(filter_label)

        self.start_date = QDateEdit()
        self.start_date.setFont(font)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setDisplayFormat("yyyy/MM/dd")
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("to"))

        self.end_date = QDateEdit()
        self.end_date.setFont(font)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("yyyy/MM/dd")
        filter_layout.addWidget(self.end_date)

        calculate_btn = QPushButton("Calculate")
        calculate_btn.setFont(font)
        calculate_btn.setMinimumHeight(35)
        calculate_btn.clicked.connect(self.refresh_table)
        filter_layout.addWidget(calculate_btn)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Employees table
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(8)
        self.employees_table.setHorizontalHeaderLabels([
            "Name", "Daily Salary", "Days Off", "Working Days", "Total Salary", "Total Expenses", "Balance", "Status"
        ])
        self.employees_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.employees_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.employees_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.employees_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.employees_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.employees_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.employees_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.employees_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.employees_table.verticalHeader().setVisible(False)
        self.employees_table.setFont(font)
        self.employees_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.employees_table)

        # Action buttons
        action_buttons_layout = QHBoxLayout()

        add_employee_btn = QPushButton("➕ Add Employee")
        add_employee_btn.setProperty("class", "primary-button")
        add_employee_btn.setFont(font)
        add_employee_btn.setMinimumHeight(40)
        add_employee_btn.clicked.connect(self.add_employee)
        action_buttons_layout.addWidget(add_employee_btn)

        edit_employee_btn = QPushButton("✏ Edit Employee")
        edit_employee_btn.setFont(font)
        edit_employee_btn.setMinimumHeight(40)
        edit_employee_btn.clicked.connect(self.edit_employee)
        action_buttons_layout.addWidget(edit_employee_btn)

        add_expense_btn = QPushButton("💰 Add Expense")
        add_expense_btn.setFont(font)
        add_expense_btn.setMinimumHeight(40)
        add_expense_btn.clicked.connect(self.add_expense)
        action_buttons_layout.addWidget(add_expense_btn)

        add_dayoff_btn = QPushButton("📅 Add Day Off")
        add_dayoff_btn.setFont(font)
        add_dayoff_btn.setMinimumHeight(40)
        add_dayoff_btn.clicked.connect(self.add_day_off)
        action_buttons_layout.addWidget(add_dayoff_btn)

        view_expenses_btn = QPushButton("📋 View Expenses")
        view_expenses_btn.setFont(font)
        view_expenses_btn.setMinimumHeight(40)
        view_expenses_btn.clicked.connect(self.view_expenses)
        action_buttons_layout.addWidget(view_expenses_btn)

        delete_employee_btn = QPushButton("🗑 Deactivate")
        delete_employee_btn.setStyleSheet("background-color: #8d2020;")
        delete_employee_btn.setFont(font)
        delete_employee_btn.setMinimumHeight(40)
        delete_employee_btn.clicked.connect(self.deactivate_employee)
        action_buttons_layout.addWidget(delete_employee_btn)

        layout.addLayout(action_buttons_layout)

    def load_employees(self):
        """Load employees from database"""
        self.all_employees = Employee.get_all()
        self.employees = self.all_employees.copy()
        self.refresh_table()

    def on_search_text_changed(self):
        """Handle search text change with debouncing"""
        # Stop any existing timer
        self.search_timer.stop()
        # Start new timer (300ms delay)
        self.search_timer.start(300)

    def apply_search_filter(self):
        """Apply search filter to employee list"""
        search_text = self.search_input.text().strip().lower()

        if not search_text:
            # No search text, show all employees
            self.employees = self.all_employees.copy()
        else:
            # Filter employees by name
            self.employees = [
                emp for emp in self.all_employees
                if search_text in emp.name.lower()
            ]

        self.refresh_table()

    def clear_search(self):
        """Clear search input and show all employees"""
        self.search_input.clear()
        self.employees = self.all_employees.copy()
        self.refresh_table()

    def refresh_table(self):
        """Refresh the employees table"""
        start = self.start_date.date().toString("yyyy/MM/dd")
        end = self.end_date.date().toString("yyyy/MM/dd")

        self.employees_table.setRowCount(len(self.employees))

        for row, employee in enumerate(self.employees):
            # Name
            self.employees_table.setItem(row, 0, QTableWidgetItem(employee.name))

            # Daily salary
            salary_item = QTableWidgetItem(f"{employee.daily_salary:.2f} dt")
            salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.employees_table.setItem(row, 1, salary_item)

            # Calculate balance for date range
            balance_data = employee.calculate_balance(start, end)

            # Days off
            days_off_item = QTableWidgetItem(str(balance_data['days_off']))
            days_off_item.setTextAlignment(Qt.AlignCenter)
            self.employees_table.setItem(row, 2, days_off_item)

            # Working days
            working_days_item = QTableWidgetItem(str(balance_data['working_days']))
            working_days_item.setTextAlignment(Qt.AlignCenter)
            self.employees_table.setItem(row, 3, working_days_item)

            # Total salary
            total_salary_item = QTableWidgetItem(f"{balance_data['total_salary']:.2f} dt")
            total_salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.employees_table.setItem(row, 4, total_salary_item)

            # Total expenses
            total_expenses_item = QTableWidgetItem(f"{balance_data['total_expenses']:.2f} dt")
            total_expenses_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.employees_table.setItem(row, 5, total_expenses_item)

            # Balance
            balance_item = QTableWidgetItem(f"{balance_data['balance']:.2f} dt")
            balance_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if balance_data['balance'] < 0:
                balance_item.setForeground(Qt.red)
            else:
                balance_item.setForeground(Qt.green)
            self.employees_table.setItem(row, 6, balance_item)

            # Status
            status = "Active" if employee.is_active else "Inactive"
            status_item = QTableWidgetItem(status)
            if employee.is_active:
                status_item.setForeground(Qt.green)
            else:
                status_item.setForeground(Qt.red)
            self.employees_table.setItem(row, 7, status_item)

    def add_employee(self):
        """Add new employee"""
        dialog = AddEmployeeDialog(parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            if not data['name']:
                QMessageBox.warning(self, "Invalid Input", "Please enter an employee name.")
                return

            # Create new employee
            employee = Employee(
                name=data['name'],
                daily_salary=data['daily_salary']
            )

            try:
                employee.save()
                QMessageBox.information(self, "Success", f"Employee '{data['name']}' has been added.")
                self.load_employees()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add employee:\n{str(e)}")

    def edit_employee(self):
        """Edit selected employee"""
        selected_rows = self.employees_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an employee to edit.")
            return

        row = selected_rows[0].row()
        employee = self.employees[row]

        dialog = AddEmployeeDialog(employee=employee, parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            if not data['name']:
                QMessageBox.warning(self, "Invalid Input", "Please enter an employee name.")
                return

            employee.name = data['name']
            employee.daily_salary = data['daily_salary']

            try:
                employee.save()
                QMessageBox.information(self, "Success", f"Employee '{data['name']}' has been updated.")
                self.load_employees()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update employee:\n{str(e)}")

    def add_expense(self):
        """Add expense for an employee"""
        active_employees = [e for e in self.employees if e.is_active]

        if not active_employees:
            QMessageBox.warning(self, "No Employees", "No active employees found. Please add employees first.")
            return

        dialog = AddExpenseDialog(active_employees, parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            # Create new expense
            expense = EmployeeExpense(
                employee_id=data['employee_id'],
                amount=data['amount'],
                description=data['description'],
                added_by='admin'
            )

            try:
                expense.save()
                QMessageBox.information(self, "Success", f"Expense of {data['amount']:.2f} dt has been added.")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add expense:\n{str(e)}")

    def add_day_off(self):
        """Add day off for an employee"""
        active_employees = [e for e in self.employees if e.is_active]

        if not active_employees:
            QMessageBox.warning(self, "No Employees", "No active employees found. Please add employees first.")
            return

        dialog = AddDayOffDialog(active_employees, parent=self)
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_data()

            # Create new day off
            day_off = EmployeeDayOff(
                employee_id=data['employee_id'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                reason=data['reason'],
                added_by='admin'
            )

            try:
                day_off.save()
                # Get employee name
                employee = next((e for e in active_employees if e.id == data['employee_id']), None)
                employee_name = employee.name if employee else "Employee"

                # Calculate days
                from PyQt5.QtCore import QDate
                start = QDate.fromString(data['start_date'], "yyyy/MM/dd")
                end = QDate.fromString(data['end_date'], "yyyy/MM/dd")
                days = start.daysTo(end) + 1

                if days == 1:
                    msg = f"Day off for {employee_name} on {data['start_date']} has been added."
                else:
                    msg = f"{days} days off for {employee_name} ({data['start_date']} to {data['end_date']}) have been added."

                QMessageBox.information(self, "Success", msg)
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add days off:\n{str(e)}")

    def view_expenses(self):
        """View expenses for selected employee"""
        selected_rows = self.employees_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an employee to view expenses.")
            return

        row = selected_rows[0].row()
        employee = self.employees[row]

        # Show expenses dialog
        dialog = EmployeeExpensesDialog(employee, parent=self)
        dialog.exec_()
        # Refresh after closing in case expenses were deleted
        self.refresh_table()

    def deactivate_employee(self):
        """Deactivate selected employee"""
        selected_rows = self.employees_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an employee to deactivate.")
            return

        row = selected_rows[0].row()
        employee = self.employees[row]

        if not employee.is_active:
            QMessageBox.information(self, "Already Inactive", f"Employee '{employee.name}' is already inactive.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deactivation",
            f"Are you sure you want to deactivate '{employee.name}'?\n\nThis will not delete the employee or their expense records.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            employee.delete()
            QMessageBox.information(self, "Success", f"Employee '{employee.name}' has been deactivated.")
            self.load_employees()


class EmployeeExpensesDialog(QDialog):
    """Dialog to show employee expenses"""

    def __init__(self, employee, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.expenses = []
        self.setWindowTitle(f"Expenses - {employee.name}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setup_ui()
        self.load_expenses()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Header
        header_label = QLabel(f"Expenses for {self.employee.name}")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Expenses table
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setHorizontalHeaderLabels([
            "Date", "Time", "Amount", "Description"
        ])
        self.expenses_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.expenses_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.expenses_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.expenses_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.expenses_table.verticalHeader().setVisible(False)
        self.expenses_table.setFont(font)
        self.expenses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.expenses_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.expenses_table)

        # Buttons
        button_layout = QHBoxLayout()

        delete_btn = QPushButton("Delete Expense")
        delete_btn.setStyleSheet("background-color: #8d2020;")
        delete_btn.setFont(font)
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(self.delete_expense)
        button_layout.addWidget(delete_btn)

        view_daysoff_btn = QPushButton("View Days Off")
        view_daysoff_btn.setFont(font)
        view_daysoff_btn.setMinimumHeight(40)
        view_daysoff_btn.clicked.connect(self.view_days_off)
        button_layout.addWidget(view_daysoff_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFont(font)
        close_btn.setMinimumHeight(40)
        close_btn.setMinimumWidth(120)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_expenses(self):
        """Load expenses for employee"""
        self.expenses = self.employee.get_expenses()
        self.refresh_table()

    def refresh_table(self):
        """Refresh expenses table"""
        self.expenses_table.setRowCount(len(self.expenses))

        for row, expense in enumerate(self.expenses):
            # Date
            self.expenses_table.setItem(row, 0, QTableWidgetItem(expense.expense_date))

            # Time
            self.expenses_table.setItem(row, 1, QTableWidgetItem(expense.expense_time))

            # Amount
            amount_item = QTableWidgetItem(f"{expense.amount:.2f} dt")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.expenses_table.setItem(row, 2, amount_item)

            # Description
            self.expenses_table.setItem(row, 3, QTableWidgetItem(expense.description or "-"))

    def delete_expense(self):
        """Delete selected expense"""
        selected_rows = self.expenses_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an expense to delete.")
            return

        row = selected_rows[0].row()
        expense = self.expenses[row]

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete this expense?\n\nAmount: {expense.amount:.2f} dt\nDate: {expense.expense_date}\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                expense.delete()
                QMessageBox.information(self, "Success", "Expense has been deleted.")
                self.load_expenses()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete expense:\n{str(e)}")

    def view_days_off(self):
        """View days off for employee"""
        dialog = EmployeeDaysOffDialog(self.employee, parent=self)
        dialog.exec_()


class EmployeeDaysOffDialog(QDialog):
    """Dialog to show employee days off"""

    def __init__(self, employee, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.days_off = []
        self.setWindowTitle(f"Days Off - {employee.name}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(750)
        self.setMinimumHeight(450)
        self.setup_ui()
        self.load_days_off()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        font = QFont()
        font.setPointSize(12)

        # Header
        header_label = QLabel(f"Days Off for {self.employee.name}")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Days off table
        self.daysoff_table = QTableWidget()
        self.daysoff_table.setColumnCount(4)
        self.daysoff_table.setHorizontalHeaderLabels([
            "From Date", "To Date", "Days", "Reason"
        ])
        self.daysoff_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.daysoff_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.daysoff_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.daysoff_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.daysoff_table.verticalHeader().setVisible(False)
        self.daysoff_table.setFont(font)
        self.daysoff_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.daysoff_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.daysoff_table)

        # Buttons
        button_layout = QHBoxLayout()

        delete_btn = QPushButton("Delete Days Off")
        delete_btn.setStyleSheet("background-color: #8d2020;")
        delete_btn.setFont(font)
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(self.delete_day_off)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFont(font)
        close_btn.setMinimumHeight(40)
        close_btn.setMinimumWidth(120)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_days_off(self):
        """Load days off for employee"""
        self.days_off = self.employee.get_days_off()
        self.refresh_table()

    def refresh_table(self):
        """Refresh days off table"""
        self.daysoff_table.setRowCount(len(self.days_off))

        for row, day_off in enumerate(self.days_off):
            # From Date
            self.daysoff_table.setItem(row, 0, QTableWidgetItem(day_off.start_date))

            # To Date
            self.daysoff_table.setItem(row, 1, QTableWidgetItem(day_off.end_date))

            # Days count
            days = day_off.get_total_days()
            days_item = QTableWidgetItem(str(days))
            days_item.setTextAlignment(Qt.AlignCenter)
            self.daysoff_table.setItem(row, 2, days_item)

            # Reason
            self.daysoff_table.setItem(row, 3, QTableWidgetItem(day_off.reason or "-"))

    def delete_day_off(self):
        """Delete selected day off"""
        selected_rows = self.daysoff_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select days off to delete.")
            return

        row = selected_rows[0].row()
        day_off = self.days_off[row]

        days = day_off.get_total_days()
        date_range = f"{day_off.start_date}"
        if day_off.start_date != day_off.end_date:
            date_range = f"{day_off.start_date} to {day_off.end_date} ({days} days)"

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete this days off period?\n\nDates: {date_range}\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                day_off.delete()
                QMessageBox.information(self, "Success", "Days off have been deleted.")
                self.load_days_off()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete days off:\n{str(e)}")
