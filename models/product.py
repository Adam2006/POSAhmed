"""
Product model for managing menu items
"""
from .database import get_db


class Product:
    """Represents a product/menu item"""

    def __init__(self, id=None, category_id=None, name='', price=0.0,
                 image_path='', is_active=True, display_order=0):
        self.id = id
        self.category_id = category_id
        self.name = name
        self.price = price
        self.image_path = image_path
        self.is_active = is_active
        self.display_order = display_order

    @staticmethod
    def get_all(active_only=True):
        """Get all products"""
        db = get_db()
        if active_only:
            cursor = db.execute(
                "SELECT * FROM products WHERE is_active = 1 ORDER BY display_order, name"
            )
        else:
            cursor = db.execute("SELECT * FROM products ORDER BY display_order, name")

        products = []
        for row in cursor.fetchall():
            products.append(Product(
                id=row['id'],
                category_id=row['category_id'],
                name=row['name'],
                price=row['price'],
                image_path=row['image_path'],
                is_active=bool(row['is_active']),
                display_order=row['display_order']
            ))
        return products

    @staticmethod
    def get_by_category(category_id, active_only=True):
        """Get all products in a category"""
        db = get_db()
        if active_only:
            cursor = db.execute(
                "SELECT * FROM products WHERE category_id = ? AND is_active = 1 ORDER BY display_order, name",
                (category_id,)
            )
        else:
            cursor = db.execute(
                "SELECT * FROM products WHERE category_id = ? ORDER BY display_order, name",
                (category_id,)
            )

        products = []
        for row in cursor.fetchall():
            products.append(Product(
                id=row['id'],
                category_id=row['category_id'],
                name=row['name'],
                price=row['price'],
                image_path=row['image_path'],
                is_active=bool(row['is_active']),
                display_order=row['display_order']
            ))
        return products

    @staticmethod
    def get_by_id(product_id):
        """Get product by ID"""
        db = get_db()
        cursor = db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if row:
            return Product(
                id=row['id'],
                category_id=row['category_id'],
                name=row['name'],
                price=row['price'],
                image_path=row['image_path'],
                is_active=bool(row['is_active']),
                display_order=row['display_order']
            )
        return None

    def save(self):
        """Save product to database"""
        db = get_db()
        if self.id is None:
            # Insert new product
            cursor = db.execute(
                """INSERT INTO products (category_id, name, price, image_path, is_active, display_order)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (self.category_id, self.name, self.price, self.image_path,
                 int(self.is_active), self.display_order)
            )
            self.id = cursor.lastrowid
        else:
            # Update existing product
            db.execute(
                """UPDATE products SET category_id = ?, name = ?, price = ?,
                   image_path = ?, is_active = ?, display_order = ? WHERE id = ?""",
                (self.category_id, self.name, self.price, self.image_path,
                 int(self.is_active), self.display_order, self.id)
            )
        db.commit()
        return self

    def delete(self):
        """Delete product from database"""
        if self.id:
            db = get_db()
            db.execute("DELETE FROM products WHERE id = ?", (self.id,))
            db.commit()
