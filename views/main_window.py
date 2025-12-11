"""
Main window for the POS application
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QScrollArea, QGridLayout, QStackedWidget, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
import config
from models import Category, Product, Register
from views.category_view import CategoryView
from views.product_view import ProductView
from views.cart_view import CartView
from views.settings_view import SettingsView
from views.history_view import HistoryView
from views.statistics_view import StatisticsView
from views.employee_view import EmployeeView
from views.register_dialog import OpenRegisterDialog, CloseRegisterDialog
from views.admin_auth_dialog import AdminAuthDialog
from controllers.order_controller import OrderController
from utils.memory_optimizer import get_optimizer


class MainWindow(QMainWindow):
    """Main POS application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)

        # Set window icon if exists
        try:
            icon = QIcon("ico.png")
            self.setWindowIcon(icon)
        except:
            pass

        # Initialize memory optimizer
        self.memory_optimizer = get_optimizer()
        self.memory_optimizer.optimize_for_low_memory()

        # Initialize order controller
        self.order_controller = OrderController()

        # Current register
        self.current_register = None

        # Setup UI
        self.setup_ui()

        # Check for open register on startup
        self.check_register()

        # Setup periodic memory cleanup (every 5 minutes)
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.periodic_memory_cleanup)
        self.cleanup_timer.start(300000)  # 5 minutes in milliseconds

    def setup_ui(self):
        """Setup the main user interface"""
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Stacked widget to switch between main view and settings
        self.stacked_widget = QStackedWidget()
        main_container_layout = QVBoxLayout(central_widget)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.addWidget(self.stacked_widget)

        # Main POS view
        main_view = QWidget()
        main_layout = QHBoxLayout(main_view)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left side - Categories and Products
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Header with settings button
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_label = QLabel(config.RESTAURANT_NAME)
        header_label.setProperty("class", "header-label")
        header_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        header_label.setFont(font)
        header_layout.addWidget(header_label)

        # Register status label
        self.register_status_label = QLabel()
        self.register_status_label.setStyleSheet("color: #ff9900; font-weight: bold;")
        register_font = QFont()
        register_font.setPointSize(10)
        self.register_status_label.setFont(register_font)
        header_layout.addWidget(self.register_status_label)

        # Register button
        self.register_btn = QPushButton("Open Register")
        self.register_btn.setMaximumWidth(140)
        self.register_btn.setMinimumHeight(40)
        btn_font = QFont()
        btn_font.setPointSize(11)
        self.register_btn.setFont(btn_font)
        self.register_btn.clicked.connect(self.toggle_register)
        header_layout.addWidget(self.register_btn)

        # History button
        history_btn = QPushButton("📊 History")
        history_btn.setMaximumWidth(120)
        history_btn.setMinimumHeight(40)
        history_btn.setFont(btn_font)
        history_btn.clicked.connect(self.open_history)
        header_layout.addWidget(history_btn)

        # Statistics button (admin only)
        statistics_btn = QPushButton("📈 Statistics")
        statistics_btn.setMaximumWidth(140)
        statistics_btn.setMinimumHeight(40)
        statistics_btn.setFont(btn_font)
        statistics_btn.clicked.connect(self.open_statistics)
        header_layout.addWidget(statistics_btn)

        # Employees button (admin only)
        employees_btn = QPushButton("👥 Employees")
        employees_btn.setMaximumWidth(140)
        employees_btn.setMinimumHeight(40)
        employees_btn.setFont(btn_font)
        employees_btn.clicked.connect(self.open_employees)
        header_layout.addWidget(employees_btn)

        # Settings button (top right)
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.setMaximumWidth(120)
        settings_btn.setMinimumHeight(40)
        settings_btn.setFont(btn_font)
        settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(settings_btn)

        left_layout.addWidget(header_widget)

        # Category view
        self.category_view = CategoryView()
        self.category_view.category_selected.connect(self.on_category_selected)
        left_layout.addWidget(self.category_view)

        # Product view
        self.product_view = ProductView()
        self.product_view.product_selected.connect(self.on_product_selected)
        left_layout.addWidget(self.product_view, stretch=1)

        main_layout.addWidget(left_widget, stretch=5)

        # Right side - Cart (wider)
        self.cart_view = CartView(self.order_controller)
        self.cart_view.checkout_clicked.connect(self.on_checkout)
        main_layout.addWidget(self.cart_view, stretch=3)

        # Add main view to stacked widget
        self.stacked_widget.addWidget(main_view)

        # Settings view
        self.settings_view = SettingsView()
        self.settings_view.settings_closed.connect(self.close_settings)
        self.stacked_widget.addWidget(self.settings_view)

        # History view
        self.history_view = HistoryView()
        self.history_view.history_closed.connect(self.close_history)
        self.stacked_widget.addWidget(self.history_view)

        # Statistics view
        self.statistics_view = StatisticsView()
        self.statistics_view.statistics_closed.connect(self.close_statistics)
        self.stacked_widget.addWidget(self.statistics_view)

        # Employee view
        self.employee_view = EmployeeView()
        self.employee_view.employee_view_closed.connect(self.close_employees)
        self.stacked_widget.addWidget(self.employee_view)

        # Show main view by default
        self.stacked_widget.setCurrentIndex(0)

        # Load initial data
        self.load_categories()

    def load_categories(self):
        """Load categories from database"""
        categories = Category.get_all(active_only=True)
        self.category_view.set_categories(categories)

        # Auto-select first category
        if categories:
            self.category_view.select_category(categories[0])
            self.on_category_selected(categories[0])

    def on_category_selected(self, category):
        """Handle category selection"""
        self.current_category = category
        products = Product.get_by_category(category.id, active_only=True)
        self.product_view.set_products(products, category.name)

    def on_product_selected(self, product):
        """Handle product selection"""
        category_name = self.current_category.name if hasattr(self, 'current_category') else ''
        self.order_controller.add_item(product, category_name=category_name)
        self.cart_view.refresh()

    def on_checkout(self, is_delivery, delivery_data):
        """Handle checkout"""
        try:
            success = self.order_controller.checkout(is_delivery, delivery_data)
            if success:
                self.cart_view.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Checkout Error", str(e))
            # If no register is open, prompt to open one
            if "No register" in str(e):
                self.toggle_register()

    def open_settings(self):
        """Open settings page with admin authentication"""
        auth_dialog = AdminAuthDialog(self)
        if auth_dialog.exec_() == auth_dialog.Accepted:
            # Switch to settings view
            self.stacked_widget.setCurrentIndex(1)

    def close_settings(self):
        """Close settings and return to main view"""
        self.stacked_widget.setCurrentIndex(0)
        # Reload categories in case settings changed
        self.load_categories()
        # Refresh current products view if category is selected
        if hasattr(self, 'current_category'):
            products = Product.get_by_category(self.current_category.id, active_only=True)
            self.product_view.set_products(products, self.current_category.name)

    def open_history(self):
        """Open history page (no auth required for employees)"""
        # Refresh history data before showing
        self.history_view.load_orders()
        # Switch to history view
        self.stacked_widget.setCurrentIndex(2)

    def close_history(self):
        """Close history and return to main view"""
        self.stacked_widget.setCurrentIndex(0)

    def open_statistics(self):
        """Open statistics page (admin only)"""
        auth_dialog = AdminAuthDialog(self)
        if auth_dialog.exec_() == auth_dialog.Accepted:
            # Refresh statistics data before showing
            self.statistics_view.load_data()
            # Switch to statistics view
            self.stacked_widget.setCurrentIndex(3)

    def close_statistics(self):
        """Close statistics and return to main view"""
        self.stacked_widget.setCurrentIndex(0)

    def open_employees(self):
        """Open employee management page (admin only)"""
        auth_dialog = AdminAuthDialog(self)
        if auth_dialog.exec_() == auth_dialog.Accepted:
            # Refresh employee data before showing
            self.employee_view.load_employees()
            # Switch to employee view
            self.stacked_widget.setCurrentIndex(4)

    def close_employees(self):
        """Close employees and return to main view"""
        self.stacked_widget.setCurrentIndex(0)

    def check_register(self):
        """Check if a register is open and update UI accordingly"""
        self.current_register = Register.get_current_register()
        self.update_register_ui()

    def update_register_ui(self):
        """Update register-related UI elements"""
        if self.current_register:
            # Register is open
            self.register_btn.setText("Close Register")
            self.register_status_label.setText(
                f"Register Open: {self.current_register.shift_type.title()} - {self.current_register.employee_name}"
            )
            self.register_status_label.setStyleSheet("color: #2d5016; font-weight: bold;")
        else:
            # No register open
            self.register_btn.setText("Open Register")
            self.register_status_label.setText("⚠ No Register Open - Sales Disabled")
            self.register_status_label.setStyleSheet("color: #8d2020; font-weight: bold;")

    def toggle_register(self):
        """Open or close register"""
        if self.current_register:
            # Close register
            dialog = CloseRegisterDialog(self.current_register, self)
            if dialog.exec_() == dialog.Accepted:
                data = dialog.get_data()
                self.current_register.close_register(data['closing_amount'], data['notes'])
                QMessageBox.information(
                    self,
                    "Register Closed",
                    f"Register closed successfully.\n\nDifference: {self.current_register.get_difference():.2f} dt"
                )
                self.current_register = None
                self.update_register_ui()
        else:
            # Open register
            dialog = OpenRegisterDialog(self)
            if dialog.exec_() == dialog.Accepted:
                data = dialog.get_data()

                # Validate employee name
                if not data['employee_name']:
                    QMessageBox.warning(self, "Invalid Input", "Please enter an employee name.")
                    return

                # Create new register
                register = Register(
                    shift_type=data['shift_type'],
                    employee_name=data['employee_name'],
                    opening_amount=data['opening_amount']
                )
                register.save()
                self.current_register = register
                self.update_register_ui()
                QMessageBox.information(
                    self,
                    "Register Opened",
                    f"Register opened for {data['shift_type']} shift.\nEmployee: {data['employee_name']}"
                )

    def periodic_memory_cleanup(self):
        """Periodically clean up memory"""
        self.memory_optimizer.periodic_cleanup()
