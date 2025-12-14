"""
Client model for managing customers with credit/monthly payment accounts
"""
from datetime import datetime
from .database import get_db
from utils.cache import cached_query, invalidate_cache


class Client:
    """Represents a client with credit account"""

    def __init__(self, id=None, name='', phone='', address='', credit_limit=0.0,
                 current_balance=0.0, notes='', is_active=True, created_at=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address
        self.credit_limit = credit_limit
        self.current_balance = current_balance
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at or datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    @staticmethod
    @cached_query()
    def get_all(active_only=True):
        """Get all clients"""
        db = get_db()
        if active_only:
            cursor = db.execute("SELECT * FROM clients WHERE is_active = 1 ORDER BY name")
        else:
            cursor = db.execute("SELECT * FROM clients ORDER BY name")

        clients = []
        for row in cursor.fetchall():
            client = Client(
                id=row['id'],
                name=row['name'],
                phone=row['phone'],
                address=row['address'],
                credit_limit=row['credit_limit'],
                current_balance=row['current_balance'],
                notes=row['notes'],
                is_active=bool(row['is_active']),
                created_at=row['created_at']
            )
            clients.append(client)
        return clients

    @staticmethod
    @cached_query()
    def get_by_id(client_id):
        """Get client by ID"""
        db = get_db()
        cursor = db.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        if row:
            return Client(
                id=row['id'],
                name=row['name'],
                phone=row['phone'],
                address=row['address'],
                credit_limit=row['credit_limit'],
                current_balance=row['current_balance'],
                notes=row['notes'],
                is_active=bool(row['is_active']),
                created_at=row['created_at']
            )
        return None

    def save(self):
        """Save client to database"""
        db = get_db()

        if self.id is None:
            # Insert new client
            cursor = db.execute(
                """INSERT INTO clients (name, phone, address, credit_limit, current_balance, notes, is_active, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.name, self.phone, self.address, self.credit_limit, self.current_balance,
                 self.notes, int(self.is_active), self.created_at)
            )
            self.id = cursor.lastrowid
        else:
            # Update existing client
            db.execute(
                """UPDATE clients SET name = ?, phone = ?, address = ?, credit_limit = ?,
                   current_balance = ?, notes = ?, is_active = ? WHERE id = ?""",
                (self.name, self.phone, self.address, self.credit_limit, self.current_balance,
                 self.notes, int(self.is_active), self.id)
            )

        db.commit()
        invalidate_cache('Client')
        return self

    def add_to_balance(self, amount):
        """Add amount to client's current balance (for unpaid orders)"""
        self.current_balance += amount
        self.save()

    def subtract_from_balance(self, amount):
        """Subtract amount from client's balance (for payments)"""
        self.current_balance -= amount
        self.save()

    def get_available_credit(self):
        """Get remaining credit available"""
        return self.credit_limit - self.current_balance

    def can_purchase(self, amount):
        """Check if client can purchase given amount on credit"""
        return self.get_available_credit() >= amount

    def delete(self):
        """Deactivate client (soft delete)"""
        self.is_active = False
        self.save()
