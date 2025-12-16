"""
Order model for managing sales transactions
"""
from datetime import datetime
from .database import get_db
from utils.cache import cached_query, invalidate_cache


class OrderItem:
    """Represents an item in an order"""

    def __init__(self, id=None, order_id=None, product_name='', quantity=1,
                 unit_price=0.0, discount=0.0, final_price=0.0, notes=''):
        self.id = id
        self.order_id = order_id
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount = discount
        self.final_price = final_price
        self.notes = notes

    def calculate_final_price(self):
        """Calculate final price after discount"""
        self.final_price = (self.unit_price - self.discount) * self.quantity
        return self.final_price


class Order:
    """Represents a customer order"""

    def __init__(self, id=None, order_number=None, order_date='', order_time='',
                 total_amount=0.0, is_delivery=False, delivery_address='',
                 delivery_phone='', delivery_price=0.0, register_id=None,
                 client_id=None, is_paid=True, price_modified=False, reprint_count=0):
        self.id = id
        self.order_number = order_number
        self.order_date = order_date
        self.order_time = order_time
        self.total_amount = total_amount
        self.is_delivery = is_delivery
        self.delivery_address = delivery_address
        self.delivery_phone = delivery_phone
        self.delivery_price = delivery_price
        self.register_id = register_id
        self.client_id = client_id
        self.is_paid = is_paid
        self.price_modified = price_modified
        self.reprint_count = reprint_count
        self.items = []

    @staticmethod
    def get_next_order_number():
        """Get the next order number from the current register"""
        from .register import Register

        current_register = Register.get_current_register()
        if not current_register:
            raise Exception("No register is currently open. Please open a register before creating orders.")

        return current_register.get_next_order_number()

    @staticmethod
    @cached_query()
    def get_all(start_date=None, end_date=None, load_items=False):
        """Get all orders, optionally filtered by date range"""
        db = get_db()
        if start_date and end_date:
            cursor = db.execute(
                "SELECT * FROM orders WHERE order_date BETWEEN ? AND ? ORDER BY order_date DESC, order_time DESC",
                (start_date, end_date)
            )
        else:
            cursor = db.execute("SELECT * FROM orders ORDER BY order_date DESC, order_time DESC")

        orders = []
        for row in cursor.fetchall():
            order = Order(
                id=row['id'],
                order_number=row['order_number'],
                order_date=row['order_date'],
                order_time=row['order_time'],
                total_amount=row['total_amount'],
                is_delivery=bool(row['is_delivery']),
                delivery_address=row['delivery_address'],
                delivery_phone=row['delivery_phone'],
                delivery_price=row['delivery_price'],
                register_id=row['register_id'] if 'register_id' in row.keys() else None,
                client_id=row['client_id'] if 'client_id' in row.keys() else None,
                is_paid=bool(row['is_paid']) if 'is_paid' in row.keys() else True,
                price_modified=bool(row['price_modified']) if 'price_modified' in row.keys() else False,
                reprint_count=row['reprint_count'] if 'reprint_count' in row.keys() else 0
            )
            # Only load items if explicitly requested (saves memory)
            if load_items:
                order.load_items()
            orders.append(order)
        return orders

    @staticmethod
    @cached_query()
    def get_by_register(register_id, load_items=True):
        """Get all orders for a specific register"""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM orders WHERE register_id = ? ORDER BY order_date DESC, order_time DESC",
            (register_id,)
        )

        orders = []
        for row in cursor.fetchall():
            order = Order(
                id=row['id'],
                order_number=row['order_number'],
                order_date=row['order_date'],
                order_time=row['order_time'],
                total_amount=row['total_amount'],
                is_delivery=bool(row['is_delivery']),
                delivery_address=row['delivery_address'],
                delivery_phone=row['delivery_phone'],
                delivery_price=row['delivery_price'],
                register_id=row['register_id'],
                client_id=row['client_id'] if 'client_id' in row.keys() else None,
                is_paid=bool(row['is_paid']) if 'is_paid' in row.keys() else True,
                price_modified=bool(row['price_modified']) if 'price_modified' in row.keys() else False,
                reprint_count=row['reprint_count'] if 'reprint_count' in row.keys() else 0
            )
            # Load order items only if requested
            if load_items:
                order.load_items()
            orders.append(order)
        return orders

    @staticmethod
    @cached_query()
    def get_by_id(order_id):
        """Get order by ID"""
        db = get_db()
        cursor = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        if row:
            order = Order(
                id=row['id'],
                order_number=row['order_number'],
                order_date=row['order_date'],
                order_time=row['order_time'],
                total_amount=row['total_amount'],
                is_delivery=bool(row['is_delivery']),
                delivery_address=row['delivery_address'],
                delivery_phone=row['delivery_phone'],
                delivery_price=row['delivery_price'],
                register_id=row['register_id'] if 'register_id' in row.keys() else None,
                client_id=row['client_id'] if 'client_id' in row.keys() else None,
                is_paid=bool(row['is_paid']) if 'is_paid' in row.keys() else True,
                price_modified=bool(row['price_modified']) if 'price_modified' in row.keys() else False,
                reprint_count=row['reprint_count'] if 'reprint_count' in row.keys() else 0
            )
            order.load_items()
            return order
        return None

    def add_item(self, item):
        """Add an item to the order"""
        self.items.append(item)

    def calculate_total(self):
        """Calculate total order amount"""
        self.total_amount = sum(item.final_price for item in self.items)
        if self.is_delivery:
            self.total_amount += self.delivery_price
        return self.total_amount

    def save(self):
        """Save order and its items to database"""
        db = get_db()

        # Calculate total
        self.calculate_total()

        if self.id is None:
            # Get next order number if not set
            if self.order_number is None:
                self.order_number = Order.get_next_order_number()

            # Set date and time if not set
            if not self.order_date:
                self.order_date = datetime.now().strftime("%Y/%m/%d")
            if not self.order_time:
                self.order_time = datetime.now().strftime("%H:%M:%S")

            # Insert new order
            cursor = db.execute(
                """INSERT INTO orders (order_number, order_date, order_time, total_amount,
                   is_delivery, delivery_address, delivery_phone, delivery_price, register_id,
                   client_id, is_paid, price_modified, reprint_count)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.order_number, self.order_date, self.order_time, self.total_amount,
                 int(self.is_delivery), self.delivery_address, self.delivery_phone, self.delivery_price, self.register_id,
                 self.client_id, int(self.is_paid), int(self.price_modified), self.reprint_count)
            )
            self.id = cursor.lastrowid

            # Insert order items
            for item in self.items:
                item.order_id = self.id
                db.execute(
                    """INSERT INTO order_items (order_id, product_name, quantity, unit_price,
                       discount, final_price, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (item.order_id, item.product_name, item.quantity, item.unit_price,
                     item.discount, item.final_price, item.notes)
                )
        else:
            # Update existing order
            db.execute(
                """UPDATE orders SET order_number = ?, order_date = ?, order_time = ?,
                   total_amount = ?, is_delivery = ?, delivery_address = ?,
                   delivery_phone = ?, delivery_price = ?, register_id = ?,
                   client_id = ?, is_paid = ?, price_modified = ?, reprint_count = ? WHERE id = ?""",
                (self.order_number, self.order_date, self.order_time, self.total_amount,
                 int(self.is_delivery), self.delivery_address, self.delivery_phone,
                 self.delivery_price, self.register_id,
                 self.client_id, int(self.is_paid), int(self.price_modified), self.reprint_count, self.id)
            )

        db.commit()

        # Invalidate order cache
        invalidate_cache('Order')

        return self

    def load_items(self):
        """Load order items from database"""
        if self.id:
            db = get_db()
            cursor = db.execute("""
                SELECT oi.*,
                       c.name as category_name
                FROM order_items oi
                LEFT JOIN products p ON oi.product_name = p.name
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE oi.order_id = ?
            """, (self.id,))
            self.items = []
            for row in cursor.fetchall():
                item = OrderItem(
                    id=row['id'],
                    order_id=row['order_id'],
                    product_name=row['product_name'],
                    quantity=row['quantity'],
                    unit_price=row['unit_price'],
                    discount=row['discount'],
                    final_price=row['final_price'],
                    notes=row['notes']
                )
                # Add category name as attribute for printing
                item.category_name = row['category_name'] if row['category_name'] else ''
                self.items.append(item)

    def delete(self):
        """Delete order and its items from database"""
        if self.id:
            db = get_db()
            # Delete order items first
            db.execute("DELETE FROM order_items WHERE order_id = ?", (self.id,))
            # Delete order
            db.execute("DELETE FROM orders WHERE id = ?", (self.id,))
            db.commit()

            # Invalidate order cache
            invalidate_cache('Order')
