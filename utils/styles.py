"""
QSS Stylesheets for the application
"""
import config


def get_main_stylesheet():
    """Get the main application stylesheet"""
    return f"""
    QMainWindow {{
        background-color: {config.THEME_COLOR};
    }}

    QWidget {{
        background-color: {config.THEME_COLOR};
        color: {config.TEXT_COLOR};
        font-family: Arial, sans-serif;
    }}

    QPushButton {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 7px;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
    }}

    QPushButton:hover {{
        background-color: {config.HIGHLIGHT_COLOR};
        border: 2px solid {config.TEXT_COLOR};
    }}

    QPushButton:pressed {{
        background-color: #1a1a1a;
        border-top: 2px solid black;
        border-left: 2px solid black;
    }}

    QPushButton:disabled {{
        background-color: #2a2a2a;
        color: #666666;
        border: 2px solid #333333;
    }}

    /* Category Buttons */
    .category-button {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 7px;
        padding: 5px;
        font-size: 16px;
        font-weight: bold;
        min-height: 25px;
    }}

    .category-button:hover {{
        background-color: {config.HIGHLIGHT_COLOR};
    }}

    .category-button:pressed {{
        background-color: {config.ACCENT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
    }}

    .category-button-selected {{
        background-color: {config.THEME_COLOR};
        border: 2px solid {config.TEXT_COLOR};
        
    }}

    .category-button-selected:pressed {{
        background-color: {config.THEME_COLOR};
        border: 2px solid {config.TEXT_COLOR};
    }}

    /* Product Items */
    .product-item {{
        background-color: {config.THEME_COLOR};
        border: 2px solid {config.ACCENT_COLOR};
        border-radius: 5px;
    }}

    .product-name {{
        background-color: rgba(0, 0, 0, 0.9);
        color: {config.TEXT_COLOR};
        padding: 5px;
        font-size: 12px;
        font-weight: bold;
    }}

    .product-price {{
        background-color: rgba(0, 0, 0, 0.9);
        color: {config.TEXT_COLOR};
        padding: 5px;
        font-size: 13px;
        font-weight: bold;
    }}

    /* Cart Items */
    .cart-item {{
        background-color: {config.THEME_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        min-height: 70px;
        margin: 3px;
        padding: 5px;
    }}

    .cart-item:hover {{
        background-color: {config.ACCENT_COLOR};
        border: 1px solid {config.TEXT_COLOR};
    }}

    .cart-item-name {{
        font-size: 11px;
        font-weight: bold;
        color: {config.TEXT_COLOR};
    }}

    .cart-item-price {{
        font-size: 12px;
        font-weight: bold;
        color: {config.TEXT_COLOR};
    }}

    .cart-item-quantity {{
        font-size: 14px;
        font-weight: bold;
        color: {config.TEXT_COLOR};
    }}

    .delete-button {{
        color: red;
        border: 0;
        background: transparent;
        font-size: 20px;
        font-weight: bold;
    }}

    .delete-button:hover {{
        color: #ff3333;
        background: transparent;
    }}

    /* Labels */
    QLabel {{
        color: {config.TEXT_COLOR};
        background-color: transparent;
    }}

    .header-label {{
        font-size: 18px;
        font-weight: bold;
        color: {config.TEXT_COLOR};
        background-color: {config.THEME_COLOR};
        padding: 10px;
        border-radius: 10px;
    }}

    .total-label {{
        font-size: 18px;
        font-weight: bold;
        color: {config.TEXT_COLOR};
        background-color: {config.THEME_COLOR};
        padding: 15px;
        border-radius: 20px;
    }}

    /* Scroll Areas */
    QScrollArea {{
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        background-color: {config.THEME_COLOR};
    }}

    QScrollBar:vertical {{
        border: none;
        background: {config.THEME_COLOR};
        width: 10px;
        margin: 0px;
    }}

    QScrollBar::handle:vertical {{
        background: {config.ACCENT_COLOR};
        min-height: 20px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {config.HIGHLIGHT_COLOR};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Number Pad */
    .numpad-button {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        font-size: 20px;
        font-weight: bold;
        min-height: 50px;
        min-width: 70px;
    }}

    .numpad-button:hover {{
        background-color: {config.HIGHLIGHT_COLOR};
    }}

    .numpad-button:pressed {{
        background-color: #1a1a1a;
    }}

    /* Primary Action Buttons */
    .primary-button {{
        background-color: #2d5016;
        color: {config.TEXT_COLOR};
        border: 2px solid #3d6020;
        border-radius: 10px;
        padding: 15px;
        font-size: 16px;
        font-weight: bold;
        min-height: 50px;
    }}

    .primary-button:hover {{
        background-color: #3d6020;
        border: 2px solid #4d7030;
    }}

    .primary-button:pressed {{
        background-color: #1d4010;
    }}

    /* Danger Buttons */
    .danger-button {{
        background-color: #6d1616;
        color: {config.TEXT_COLOR};
        border: 2px solid #8d2020;
        border-radius: 10px;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
    }}

    .danger-button:hover {{
        background-color: #8d2020;
    }}

    /* Dialogs */
    QDialog {{
        background-color: {config.THEME_COLOR};
    }}

    QLineEdit {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        padding: 8px;
        font-size: 14px;
    }}

    QLineEdit:focus {{
        border: 2px solid {config.TEXT_COLOR};
    }}

    QCheckBox {{
        color: {config.TEXT_COLOR};
        font-size: 18px;
        spacing: 10px;
    }}

    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 3px;
        background-color: {config.ACCENT_COLOR};
    }}

    QCheckBox::indicator:checked {{
        background-color: #2d5016;
        border: 2px solid #3d6020;
    }}

    QCheckBox::indicator:hover {{
        border: 2px solid {config.TEXT_COLOR};
    }}

    /* Radio Buttons */
    QRadioButton {{
        color: {config.TEXT_COLOR};
        font-size: 14px;
        spacing: 10px;
    }}

    QRadioButton::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 11px;
        background-color: {config.ACCENT_COLOR};
    }}

    QRadioButton::indicator:hover {{
        border: 2px solid {config.TEXT_COLOR};
        background-color: {config.HIGHLIGHT_COLOR};
    }}

    QRadioButton::indicator:checked {{
        background-color: #2d5016;
        border: 2px solid #3d6020;
    }}

    QRadioButton::indicator:checked:hover {{
        background-color: #3d6020;
    }}

    QDoubleSpinBox, QSpinBox, QDateEdit {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        padding: 8px;
        font-size: 14px;
        font-weight: bold;
    }}

    QDoubleSpinBox:hover, QSpinBox:hover, QDateEdit:hover {{
        border: 2px solid {config.TEXT_COLOR};
        background-color: {config.HIGHLIGHT_COLOR};
    }}

    QDoubleSpinBox:focus, QSpinBox:focus, QDateEdit:focus {{
        border: 2px solid {config.TEXT_COLOR};
    }}

    QDateEdit::drop-down {{
        border: none;
        width: 30px;
        background: transparent;
    }}

    QDateEdit::drop-down:hover {{
        background: rgba(255, 255, 255, 0.1);
        border-top-right-radius: 5px;
        border-bottom-right-radius: 5px;
    }}

    QDateEdit::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 8px solid {config.TEXT_COLOR};
        width: 0;
        height: 0;
        margin-right: 8px;
    }}

    QCalendarWidget {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
    }}

    QCalendarWidget QToolButton {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        padding: 5px;
        font-size: 13px;
    }}

    QCalendarWidget QToolButton:hover {{
        background-color: {config.HIGHLIGHT_COLOR};
        border: 2px solid {config.TEXT_COLOR};
    }}

    QCalendarWidget QMenu {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
    }}

    QCalendarWidget QSpinBox {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        selection-background-color: {config.HIGHLIGHT_COLOR};
    }}

    QCalendarWidget QTableView {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        selection-background-color: #2d5016;
        selection-color: {config.TEXT_COLOR};
    }}

    QCalendarWidget QAbstractItemView:enabled {{
        color: {config.TEXT_COLOR};
        background-color: {config.ACCENT_COLOR};
        selection-background-color: #2d5016;
        selection-color: {config.TEXT_COLOR};
    }}

    /* Tab Widget */
    QTabWidget::pane {{
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        background-color: {config.THEME_COLOR};
    }}

    QTabBar::tab {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-bottom: none;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        padding: 10px 20px;
        margin-right: 2px;
        font-size: 13px;
        font-weight: bold;
    }}

    QTabBar::tab:selected {{
        background-color: {config.THEME_COLOR};
        border: 2px solid {config.TEXT_COLOR};
        border-bottom: none;
    }}

    QTabBar::tab:hover {{
        background-color: {config.HIGHLIGHT_COLOR};
    }}

    /* Table Widget */
    QTableWidget {{
        background-color: {config.THEME_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        gridline-color: {config.HIGHLIGHT_COLOR};
        selection-background-color: {config.HIGHLIGHT_COLOR};
    }}

    QTableWidget::item {{
        padding: 8px;
        border: none;
    }}

    QTableWidget::item:selected {{
        background-color: {config.HIGHLIGHT_COLOR};
        color: {config.TEXT_COLOR};
    }}

    QHeaderView::section {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 1px solid {config.HIGHLIGHT_COLOR};
        padding: 8px;
        font-weight: bold;
        font-size: 12px;
    }}

    /* ComboBox */
    QComboBox {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 7px;
        padding: 10px 15px;
        padding-right: 40px;
        font-size: 14px;
        font-weight: bold;
        min-height: 30px;
    }}

    QComboBox:hover {{
        border: 2px solid {config.TEXT_COLOR};
        background-color: {config.HIGHLIGHT_COLOR};
    }}

    QComboBox:focus {{
        border: 2px solid {config.TEXT_COLOR};
    }}

    QComboBox:disabled {{
        background-color: #2a2a2a;
        color: #666666;
        border: 2px solid #333333;
    }}

    QComboBox::drop-down {{
        border: none;
        width: 35px;
        background: transparent;
    }}

    QComboBox::drop-down:hover {{
        background: rgba(255, 255, 255, 0.1);
        border-top-right-radius: 7px;
        border-bottom-right-radius: 7px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 9px solid {config.TEXT_COLOR};
        width: 0;
        height: 0;
        margin-right: 10px;
    }}

    QComboBox::down-arrow:hover {{
        border-top-color: #ffffff;
    }}

    QComboBox QAbstractItemView {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        selection-background-color: {config.HIGHLIGHT_COLOR};
        selection-color: {config.TEXT_COLOR};
        padding: 5px;
        outline: none;
    }}

    QComboBox QAbstractItemView::item {{
        padding: 10px 15px;
        border-radius: 3px;
        min-height: 30px;
    }}

    QComboBox QAbstractItemView::item:hover {{
        background-color: {config.HIGHLIGHT_COLOR};
        color: {config.TEXT_COLOR};
    }}

    QComboBox QAbstractItemView::item:selected {{
        background-color: #2d5016;
        color: {config.TEXT_COLOR};
        border: 1px solid #3d6020;
    }}

    /* TextEdit */
    QTextEdit {{
        background-color: {config.ACCENT_COLOR};
        color: {config.TEXT_COLOR};
        border: 2px solid {config.HIGHLIGHT_COLOR};
        border-radius: 5px;
        padding: 8px;
        font-size: 14px;
    }}

    QTextEdit:focus {{
        border: 2px solid {config.TEXT_COLOR};
    }}
    """
