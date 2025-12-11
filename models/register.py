"""
Register model for managing shift sessions
"""
from datetime import datetime
from .database import get_db


class Register:
    """Represents a register/shift session"""

    def __init__(self, id=None, shift_type='', employee_name='', opening_amount=0.0,
                 closing_amount=0.0, opened_at='', closed_at='', is_open=True, notes='',
                 last_order_number=0):
        self.id = id
        self.shift_type = shift_type  # 'morning' or 'evening'
        self.employee_name = employee_name
        self.opening_amount = opening_amount
        self.closing_amount = closing_amount
        self.opened_at = opened_at
        self.closed_at = closed_at
        self.is_open = is_open
        self.notes = notes
        self.last_order_number = last_order_number

    @staticmethod
    def get_current_register():
        """Get the currently open register"""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM registers WHERE is_open = 1 ORDER BY opened_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            return Register(
                id=row['id'],
                shift_type=row['shift_type'],
                employee_name=row['employee_name'],
                opening_amount=row['opening_amount'],
                closing_amount=row['closing_amount'],
                opened_at=row['opened_at'],
                closed_at=row['closed_at'],
                is_open=bool(row['is_open']),
                notes=row['notes'],
                last_order_number=row['last_order_number'] if 'last_order_number' in row.keys() else 0
            )
        return None

    @staticmethod
    def get_all(limit=None):
        """Get all registers"""
        db = get_db()
        query = "SELECT * FROM registers ORDER BY opened_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor = db.execute(query)
        registers = []
        for row in cursor.fetchall():
            registers.append(Register(
                id=row['id'],
                shift_type=row['shift_type'],
                employee_name=row['employee_name'],
                opening_amount=row['opening_amount'],
                closing_amount=row['closing_amount'],
                opened_at=row['opened_at'],
                closed_at=row['closed_at'],
                is_open=bool(row['is_open']),
                notes=row['notes'],
                last_order_number=row['last_order_number'] if 'last_order_number' in row.keys() else 0
            ))
        return registers

    @staticmethod
    def get_by_id(register_id):
        """Get register by ID"""
        db = get_db()
        cursor = db.execute("SELECT * FROM registers WHERE id = ?", (register_id,))
        row = cursor.fetchone()
        if row:
            return Register(
                id=row['id'],
                shift_type=row['shift_type'],
                employee_name=row['employee_name'],
                opening_amount=row['opening_amount'],
                closing_amount=row['closing_amount'],
                opened_at=row['opened_at'],
                closed_at=row['closed_at'],
                is_open=bool(row['is_open']),
                notes=row['notes'],
                last_order_number=row['last_order_number'] if 'last_order_number' in row.keys() else 0
            )
        return None

    def save(self):
        """Save register to database"""
        db = get_db()

        if self.id is None:
            # Insert new register
            if not self.opened_at:
                self.opened_at = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            cursor = db.execute(
                """INSERT INTO registers (shift_type, employee_name, opening_amount,
                   closing_amount, opened_at, closed_at, is_open, notes, last_order_number)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.shift_type, self.employee_name, self.opening_amount,
                 self.closing_amount, self.opened_at, self.closed_at,
                 int(self.is_open), self.notes, self.last_order_number)
            )
            self.id = cursor.lastrowid
        else:
            # Update existing register
            db.execute(
                """UPDATE registers SET shift_type = ?, employee_name = ?,
                   opening_amount = ?, closing_amount = ?, opened_at = ?,
                   closed_at = ?, is_open = ?, notes = ?, last_order_number = ? WHERE id = ?""",
                (self.shift_type, self.employee_name, self.opening_amount,
                 self.closing_amount, self.opened_at, self.closed_at,
                 int(self.is_open), self.notes, self.last_order_number, self.id)
            )

        db.commit()
        return self

    def close_register(self, closing_amount, notes=''):
        """Close the register"""
        self.closing_amount = closing_amount
        self.closed_at = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.is_open = False
        self.notes = notes
        self.save()

    def get_total_sales(self):
        """Get total sales for this register"""
        if not self.id:
            return 0.0

        db = get_db()
        cursor = db.execute(
            "SELECT SUM(total_amount) as total FROM orders WHERE register_id = ?",
            (self.id,)
        )
        result = cursor.fetchone()
        return result['total'] if result['total'] else 0.0

    def get_orders_count(self):
        """Get number of orders for this register"""
        if not self.id:
            return 0

        db = get_db()
        cursor = db.execute(
            "SELECT COUNT(*) as count FROM orders WHERE register_id = ?",
            (self.id,)
        )
        result = cursor.fetchone()
        return result['count'] if result else 0

    def get_expected_amount(self):
        """Get expected cash amount (opening + sales)"""
        return self.opening_amount + self.get_total_sales()

    def get_difference(self):
        """Get difference between expected and actual closing amount"""
        if not self.is_open:
            return self.closing_amount - self.get_expected_amount()
        return 0.0

    def get_next_order_number(self):
        """Get next order number for this register"""
        self.last_order_number += 1
        self.save()
        return self.last_order_number
