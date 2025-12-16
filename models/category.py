"""
Category model for managing product categories
"""
from .database import get_db


class Category:
    """Represents a product category"""

    def __init__(self, id=None, name='', is_active=True, display_order=0):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.display_order = display_order

    @staticmethod
    def get_all(active_only=True):
        """Get all categories"""
        db = get_db()
        if active_only:
            cursor = db.execute(
                "SELECT * FROM categories WHERE is_active = 1 ORDER BY display_order, name"
            )
        else:
            cursor = db.execute("SELECT * FROM categories ORDER BY display_order, name")

        categories = []
        for row in cursor.fetchall():
            categories.append(Category(
                id=row['id'],
                name=row['name'],
                is_active=bool(row['is_active']),
                display_order=row['display_order']
            ))
        return categories

    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        db = get_db()
        cursor = db.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        if row:
            return Category(
                id=row['id'],
                name=row['name'],
                is_active=bool(row['is_active']),
                display_order=row['display_order']
            )
        return None

    @staticmethod
    def get_by_name(name):
        """Get category by name"""
        db = get_db()
        cursor = db.execute("SELECT * FROM categories WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return Category(
                id=row['id'],
                name=row['name'],
                is_active=bool(row['is_active']),
                display_order=row['display_order']
            )
        return None

    def save(self):
        """Save category to database"""
        db = get_db()
        if self.id is None:
            # Insert new category
            cursor = db.execute(
                "INSERT INTO categories (name, is_active, display_order) VALUES (?, ?, ?)",
                (self.name, int(self.is_active), self.display_order)
            )
            self.id = cursor.lastrowid
        else:
            # Update existing category
            db.execute(
                "UPDATE categories SET name = ?, is_active = ?, display_order = ? WHERE id = ?",
                (self.name, int(self.is_active), self.display_order, self.id)
            )
        db.commit()
        return self

    def delete(self, delete_products=False):
        """Delete category from database

        Args:
            delete_products: If True, also delete all products in this category
        """
        if self.id:
            db = get_db()

            if delete_products:
                # Delete all products in this category first
                db.execute("DELETE FROM products WHERE category_id = ?", (self.id,))

            # Delete topping group associations
            db.execute("DELETE FROM category_topping_groups WHERE category_id = ?", (self.id,))

            # Delete the category
            db.execute("DELETE FROM categories WHERE id = ?", (self.id,))
            db.commit()

    def get_topping_groups(self):
        """Get all topping groups associated with this category"""
        if not self.id:
            return []

        from .topping import ToppingGroup
        db = get_db()
        cursor = db.execute("""
            SELECT tg.*
            FROM topping_groups tg
            INNER JOIN category_topping_groups ctg ON tg.id = ctg.topping_group_id
            WHERE ctg.category_id = ?
            ORDER BY tg.display_order, tg.name
        """, (self.id,))

        groups = []
        for row in cursor.fetchall():
            groups.append(ToppingGroup(
                id=row['id'],
                name=row['name'],
                display_order=row['display_order'],
                is_active=bool(row['is_active'])
            ))
        return groups

    def set_topping_groups(self, topping_group_ids):
        """Set which topping groups are available for this category

        Args:
            topping_group_ids: List of topping group IDs
        """
        if not self.id:
            return

        db = get_db()

        # Remove all existing associations
        db.execute("DELETE FROM category_topping_groups WHERE category_id = ?", (self.id,))

        # Add new associations
        for group_id in topping_group_ids:
            db.execute(
                "INSERT INTO category_topping_groups (category_id, topping_group_id) VALUES (?, ?)",
                (self.id, group_id)
            )

        db.commit()
