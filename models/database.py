"""
Database connection and initialization module
"""
import sqlite3
from pathlib import Path
import config


class Database:
    """Manages database connection and schema creation"""

    def __init__(self, db_path=None):
        self.db_path = db_path or config.DATABASE_PATH
        self.connection = None

    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Access columns by name
        return self.connection

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def execute(self, query, params=None):
        """Execute a query and return cursor"""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()

    def initialize_schema(self):
        """Create all database tables"""
        self.connect()

        # Categories table
        self.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                is_active INTEGER DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Products table
        self.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                image_path TEXT,
                is_active INTEGER DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)

        # Orders table
        self.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                order_time TEXT NOT NULL,
                total_amount REAL NOT NULL,
                is_delivery INTEGER DEFAULT 0,
                delivery_address TEXT,
                delivery_phone TEXT,
                delivery_price REAL DEFAULT 0,
                register_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (register_id) REFERENCES registers(id)
            )
        """)

        # Order items table
        self.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL DEFAULT 0,
                final_price REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)

        # Settings table
        self.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Registers table (for shift management)
        self.execute("""
            CREATE TABLE IF NOT EXISTS registers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shift_type TEXT NOT NULL,
                employee_name TEXT NOT NULL,
                opening_amount REAL DEFAULT 0,
                closing_amount REAL DEFAULT 0,
                opened_at TIMESTAMP NOT NULL,
                closed_at TIMESTAMP,
                is_open INTEGER DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Employees table
        self.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                daily_salary REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Employee expenses/spending table
        self.execute("""
            CREATE TABLE IF NOT EXISTS employee_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                expense_date TEXT NOT NULL,
                expense_time TEXT NOT NULL,
                added_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)

        # Employee days off table
        self.execute("""
            CREATE TABLE IF NOT EXISTS employee_days_off (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                reason TEXT,
                added_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)

        # Create indexes for better performance
        self.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_employee_expenses_employee ON employee_expenses(employee_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_employee_expenses_date ON employee_expenses(expense_date)")

        self.commit()

        # Run migrations (including employee_days_off table migration)
        self._run_migrations()

        # Create indexes for employee_days_off after migration
        self.execute("CREATE INDEX IF NOT EXISTS idx_employee_days_off_employee ON employee_days_off(employee_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_employee_days_off_start_date ON employee_days_off(start_date)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_employee_days_off_end_date ON employee_days_off(end_date)")
        self.commit()

        # Initialize default settings
        self._initialize_default_settings()

    def _run_migrations(self):
        """Run database migrations for schema updates"""
        # Check if register_id column exists in orders table
        try:
            cursor = self.execute("PRAGMA table_info(orders)")
            columns = [row['name'] for row in cursor.fetchall()]
            if 'register_id' not in columns:
                # Add register_id column to orders table
                self.execute("ALTER TABLE orders ADD COLUMN register_id INTEGER")
                self.commit()
                print("Migration: Added register_id column to orders table")
        except Exception as e:
            print(f"Migration error: {e}")

        # Check if last_order_number column exists in registers table
        try:
            cursor = self.execute("PRAGMA table_info(registers)")
            columns = [row['name'] for row in cursor.fetchall()]
            if 'last_order_number' not in columns:
                # Add last_order_number column to registers table
                self.execute("ALTER TABLE registers ADD COLUMN last_order_number INTEGER DEFAULT 0")
                self.commit()
                print("Migration: Added last_order_number column to registers table")
        except Exception as e:
            print(f"Migration error: {e}")

        # Migrate employee_days_off table from single day to date range
        try:
            cursor = self.execute("PRAGMA table_info(employee_days_off)")
            columns = [row['name'] for row in cursor.fetchall()]

            # If we have the old schema (day_off_date), migrate to new schema (start_date, end_date)
            if 'day_off_date' in columns and 'start_date' not in columns:
                print("Migration: Converting employee_days_off from single day to date range...")

                # Get all existing days off
                cursor = self.execute("SELECT * FROM employee_days_off")
                old_data = cursor.fetchall()

                # Drop the old table
                self.execute("DROP TABLE employee_days_off")

                # Recreate with new schema
                self.execute("""
                    CREATE TABLE employee_days_off (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        reason TEXT,
                        added_by TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employees(id)
                    )
                """)

                # Migrate old data (single day becomes start_date = end_date)
                for row in old_data:
                    self.execute(
                        """INSERT INTO employee_days_off (employee_id, start_date, end_date, reason, added_by, created_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (row['employee_id'], row['day_off_date'], row['day_off_date'],
                         row['reason'], row['added_by'], row['created_at'])
                    )

                # Recreate indexes
                self.execute("CREATE INDEX IF NOT EXISTS idx_employee_days_off_employee ON employee_days_off(employee_id)")
                self.execute("CREATE INDEX IF NOT EXISTS idx_employee_days_off_start_date ON employee_days_off(start_date)")
                self.execute("CREATE INDEX IF NOT EXISTS idx_employee_days_off_end_date ON employee_days_off(end_date)")

                self.commit()
                print(f"Migration: Migrated {len(old_data)} days off records to date range format")
        except Exception as e:
            print(f"Migration error for employee_days_off: {e}")

    def _initialize_default_settings(self):
        """Insert default settings if not exists"""
        cursor = self.execute("SELECT COUNT(*) as count FROM settings")
        if cursor.fetchone()['count'] == 0:
            self.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                ('last_order_number', '0')
            )
            self.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                ('last_order_date', '')
            )
            self.commit()


# Singleton instance
_db_instance = None

def get_db():
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.initialize_schema()
    return _db_instance
