"""
Topping models for product customization
"""
from .database import get_db


class ToppingGroup:
    """Represents a topping group (e.g., Meat, Sauces, Pasta Type)"""

    def __init__(self, id=None, name='', display_order=0, is_active=True):
        self.id = id
        self.name = name
        self.display_order = display_order
        self.is_active = is_active

    @staticmethod
    def get_all(active_only=True):
        """Get all topping groups"""
        db = get_db()
        if active_only:
            cursor = db.execute(
                "SELECT * FROM topping_groups WHERE is_active = 1 ORDER BY display_order, name"
            )
        else:
            cursor = db.execute("SELECT * FROM topping_groups ORDER BY display_order, name")

        groups = []
        for row in cursor.fetchall():
            groups.append(ToppingGroup(
                id=row['id'],
                name=row['name'],
                display_order=row['display_order'],
                is_active=bool(row['is_active'])
            ))
        return groups

    @staticmethod
    def get_by_id(group_id):
        """Get topping group by ID"""
        db = get_db()
        cursor = db.execute("SELECT * FROM topping_groups WHERE id = ?", (group_id,))
        row = cursor.fetchone()
        if row:
            return ToppingGroup(
                id=row['id'],
                name=row['name'],
                display_order=row['display_order'],
                is_active=bool(row['is_active'])
            )
        return None

    def save(self):
        """Save topping group to database"""
        db = get_db()
        if self.id is None:
            # Insert new group
            cursor = db.execute(
                """INSERT INTO topping_groups (name, display_order, is_active)
                   VALUES (?, ?, ?)""",
                (self.name, self.display_order, int(self.is_active))
            )
            self.id = cursor.lastrowid
        else:
            # Update existing group
            db.execute(
                """UPDATE topping_groups SET name = ?, display_order = ?, is_active = ?
                   WHERE id = ?""",
                (self.name, self.display_order, int(self.is_active), self.id)
            )
        db.commit()
        return self

    def delete(self):
        """Delete topping group from database"""
        if self.id:
            db = get_db()
            # Delete related options first
            db.execute("DELETE FROM topping_options WHERE group_id = ?", (self.id,))
            # Delete category relations
            db.execute("DELETE FROM category_topping_groups WHERE topping_group_id = ?", (self.id,))
            # Delete product relations
            db.execute("DELETE FROM product_topping_groups WHERE topping_group_id = ?", (self.id,))
            # Delete group
            db.execute("DELETE FROM topping_groups WHERE id = ?", (self.id,))
            db.commit()

    def get_options(self, active_only=True):
        """Get all options for this group"""
        if not self.id:
            return []

        db = get_db()
        if active_only:
            cursor = db.execute(
                "SELECT * FROM topping_options WHERE group_id = ? AND is_active = 1 ORDER BY display_order, name",
                (self.id,)
            )
        else:
            cursor = db.execute(
                "SELECT * FROM topping_options WHERE group_id = ? ORDER BY display_order, name",
                (self.id,)
            )

        options = []
        for row in cursor.fetchall():
            options.append(ToppingOption(
                id=row['id'],
                group_id=row['group_id'],
                name=row['name'],
                price=row['price'],
                display_order=row['display_order'],
                is_active=bool(row['is_active'])
            ))
        return options


class ToppingOption:
    """Represents a topping option within a group"""

    def __init__(self, id=None, group_id=None, name='', price=0.0, display_order=0, is_active=True):
        self.id = id
        self.group_id = group_id
        self.name = name
        self.price = price
        self.display_order = display_order
        self.is_active = is_active

    @staticmethod
    def get_by_group(group_id, active_only=True):
        """Get all options for a group"""
        db = get_db()
        if active_only:
            cursor = db.execute(
                "SELECT * FROM topping_options WHERE group_id = ? AND is_active = 1 ORDER BY display_order, name",
                (group_id,)
            )
        else:
            cursor = db.execute(
                "SELECT * FROM topping_options WHERE group_id = ? ORDER BY display_order, name",
                (group_id,)
            )

        options = []
        for row in cursor.fetchall():
            options.append(ToppingOption(
                id=row['id'],
                group_id=row['group_id'],
                name=row['name'],
                price=row['price'],
                display_order=row['display_order'],
                is_active=bool(row['is_active'])
            ))
        return options

    @staticmethod
    def get_by_id(option_id):
        """Get topping option by ID"""
        db = get_db()
        cursor = db.execute("SELECT * FROM topping_options WHERE id = ?", (option_id,))
        row = cursor.fetchone()
        if row:
            return ToppingOption(
                id=row['id'],
                group_id=row['group_id'],
                name=row['name'],
                price=row['price'],
                display_order=row['display_order'],
                is_active=bool(row['is_active'])
            )
        return None

    def save(self):
        """Save topping option to database"""
        db = get_db()
        if self.id is None:
            # Insert new option
            cursor = db.execute(
                """INSERT INTO topping_options (group_id, name, price, display_order, is_active)
                   VALUES (?, ?, ?, ?, ?)""",
                (self.group_id, self.name, self.price, self.display_order, int(self.is_active))
            )
            self.id = cursor.lastrowid
        else:
            # Update existing option
            db.execute(
                """UPDATE topping_options SET group_id = ?, name = ?, price = ?,
                   display_order = ?, is_active = ? WHERE id = ?""",
                (self.group_id, self.name, self.price, self.display_order, int(self.is_active), self.id)
            )
        db.commit()
        return self

    def delete(self):
        """Delete topping option from database"""
        if self.id:
            db = get_db()
            db.execute("DELETE FROM topping_options WHERE id = ?", (self.id,))
            db.commit()
