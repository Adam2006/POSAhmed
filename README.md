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
- **Admin Password** - Default: "ab65"

## 💾 Database

The SQLite database ([data/restaurant.db](data/restaurant.db)) contains:
- Categories and Products
- Orders and Order Items
- Settings (order counter, etc.)

**Backup**: Simply copy the `restaurant.db` file!

## 📊 Data Migration

### From Old JSON Format
If you have a `menu.json` file from the old system:
```bash
python utils/migrate_data.py menu.json
```

### Create Sample Data
```bash
python utils/migrate_data.py --sample
```

## 🖨️ Printing

The system supports ESC/POS thermal printers.

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
- Number pad for editing quantities/discounts
- Sales history and reporting
- Product/category management UI
- Table management (for dine-in)
- Split payments
- Inventory tracking
- User authentication
- Analytics dashboard

## 📝 License

Private use for Woods Restaurant.

---

Built with ❤️ using PyQt5
