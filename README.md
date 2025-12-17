# Woods Restaurant POS System

Modern Point of Sale system for restaurants built with PyQt5 and SQLite.

## 🎯 Prototype Features (v1.0)

### ✅ Completed Features
- **Category-based Product Browsing** - Grid view of categories and products
- **Shopping Cart** - Add/remove items with quantity tracking
- **Order Management** - Auto-incrementing order numbers with daily reset
- **Delivery Orders** - Customer address, phone, and delivery price
- **Receipt Printing** - ESC/POS thermal printer support (customer + kitchen receipts)
- **SQLite Database** - Persistent data storage
- **Modern Dark UI** - Professional styling with QSS
- **Data Migration** - Import from old JSON format or create sample data
- **Number Pad for Editing Quantities/Discounts** - EditItemDialog allows quantity/price/discount changes
- **Sales History and Reporting** - Full order history and statistics views, with register/product summaries
- **Product/Category Management UI** - Add, edit, and delete products and categories from the UI

### 📋 Not Included in Prototype
- Table management (removed for simplicity)
- Number pad dialog for quantity/discount editing
- Sales history viewer
- Product/category management UI
- Admin panel
- Multi-user support

## 🚀 Installation

### Requirements
- Python 3.7+
- Windows OS (for win32print)

### Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## 📁 Project Structure

```
POSAhmed/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
│
├── models/                # Database models
│   ├── database.py       # SQLite connection & schema
│   ├── category.py       # Category model
│   ├── product.py        # Product model
│   └── order.py          # Order & OrderItem models
│
├── views/                 # UI components
│   ├── main_window.py    # Main application window
│   ├── category_view.py  # Category selection grid
│   ├── product_view.py   # Product selection grid
│   ├── cart_view.py      # Shopping cart display
│   └── delivery_dialog.py # Delivery info dialog
│
├── controllers/           # Business logic
│   └── order_controller.py # Order management
│
├── utils/                 # Utilities
│   ├── styles.py         # QSS stylesheets
│   ├── printer.py        # Receipt printing
│   └── migrate_data.py   # Data migration tool
│
└── data/                  # Database & backups
    ├── restaurant.db     # SQLite database
    └── backups/          # Database backups
```

## 🎨 Configuration

Edit [config.py](config.py) to customize:

- **Printer Settings** - Printer names for receipts
- **Restaurant Info** - Name, phone number
- **Order Reset Time** - Daily order counter reset (default: 02:30)
- **UI Theme** - Colors and styling
- **Admin Password** - Default: ""

## 💾 Database

The SQLite database is located at `data/restaurant.db`.
- Contains: Categories, Products, Orders, Order Items, Settings

**Backup**: Simply copy the `restaurant.db` file!

## 📊 Data Migration & Menu Management

### Importing Menu from JSON
If you have a `menu.json` file (see below for the new format):
```bash
python utils/migrate_data.py menu.json
```

### Clearing All Menu Data
To completely remove all products and categories from the database:
```bash
python clear_menu.py
```
This will wipe the menu (products & categories) from `data/restaurant.db`.

### Re-importing Menu
After clearing, you can re-import your menu from `menu.json` as above.

### Create Sample Data
```bash
python utils/migrate_data.py --sample
```

### Example menu.json Format
```json
{
  "categories": [
    {
      "name": "tabouna",
      "status": "Active",
      "products": [
        {"name": "Escalope", "price": 7.5, "status": "Active", "description": "", "image": ""},
        {"name": "Chawarma", "price": 7.5, "status": "Active", "description": "", "image": ""}
      ]
    },
    ...
  ]
}
```
For a full example, see the provided `menu.json` in this repository.

## 🖨️ Printing

The system supports ESC/POS thermal printers (Windows only).

**Configure printers in [config.py](config.py):**
- `PRINTER_NAME` - Customer receipt printer
- `KITCHEN_PRINTER_NAME` - Kitchen order printer

**Disable printing for testing:**
```python
ENABLE_PRINTING = False
```

## 🎮 Usage

1. **Select Category** - Click on a category button
2. **Select Products** - Click products to add to cart
3. **Review Cart** - See items in the right panel
4. **Remove Items** - Click the × button
5. **Delivery Order?** - Check "Delivery?" and enter details
6. **Checkout** - Click "Print Receipt" to complete order

## 🔄 Daily Reset

Order numbers reset daily at the configured time (default 02:30 AM).
- Orders before reset time continue previous day's sequence
- Orders after reset start from 1

## 📦 Deployment

To copy to POS computer:
1. Copy entire `POSAhmed` folder
2. Ensure Python + dependencies installed
3. Run `python main.py`

**OR** package as executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## 🛠️ Next Steps

Future enhancements could include:
- Table management (for dine-in)
- Split payments
- Inventory tracking
- User authentication (beyond admin password)
- Analytics dashboard

## 🐞 Troubleshooting

### QWindowsWindow::setGeometry Warning
If you see a warning like:
```
QWindowsWindow::setGeometry: Unable to set geometry ...
```
This means the requested window size does not fit your screen. The app will still work, but you can adjust your screen resolution or edit the window sizing code in `views/main_window.py` if needed.

## 📝 License

Private use for Woods Restaurant.

---

Built with ❤️ using PyQt5
