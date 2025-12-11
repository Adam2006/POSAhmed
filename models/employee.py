"""
Employee model for managing employees and their expenses
"""
from datetime import datetime
from .database import get_db
from utils.cache import cached_query, invalidate_cache


class Employee:
    """Represents an employee"""

    def __init__(self, id=None, name='', daily_salary=0.0, is_active=True):
        self.id = id
        self.name = name
        self.daily_salary = daily_salary
        self.is_active = is_active

    @staticmethod
    @cached_query()
    def get_all(active_only=False):
        """Get all employees"""
        db = get_db()
        if active_only:
            cursor = db.execute("SELECT * FROM employees WHERE is_active = 1 ORDER BY name")
        else:
            cursor = db.execute("SELECT * FROM employees ORDER BY name")

        employees = []
        for row in cursor.fetchall():
            employees.append(Employee(
                id=row['id'],
                name=row['name'],
                daily_salary=row['daily_salary'],
                is_active=bool(row['is_active'])
            ))
        return employees

    @staticmethod
    @cached_query()
    def get_by_id(employee_id):
        """Get employee by ID"""
        db = get_db()
        cursor = db.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        row = cursor.fetchone()
        if row:
            return Employee(
                id=row['id'],
                name=row['name'],
                daily_salary=row['daily_salary'],
                is_active=bool(row['is_active'])
            )
        return None

    @staticmethod
    def get_by_name(name):
        """Get employee by name"""
        db = get_db()
        cursor = db.execute("SELECT * FROM employees WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return Employee(
                id=row['id'],
                name=row['name'],
                daily_salary=row['daily_salary'],
                is_active=bool(row['is_active'])
            )
        return None

    def save(self):
        """Save employee to database"""
        db = get_db()

        if self.id is None:
            # Insert new employee
            cursor = db.execute(
                "INSERT INTO employees (name, daily_salary, is_active) VALUES (?, ?, ?)",
                (self.name, self.daily_salary, int(self.is_active))
            )
            self.id = cursor.lastrowid
        else:
            # Update existing employee
            db.execute(
                "UPDATE employees SET name = ?, daily_salary = ?, is_active = ? WHERE id = ?",
                (self.name, self.daily_salary, int(self.is_active), self.id)
            )

        db.commit()

        # Invalidate employee cache
        invalidate_cache('get_all')
        invalidate_cache('get_by_id')

        return self

    def delete(self):
        """Soft delete employee (set is_active to False)"""
        self.is_active = False
        self.save()

    def get_total_expenses(self, start_date=None, end_date=None):
        """Get total expenses for this employee"""
        if not self.id:
            return 0.0

        db = get_db()
        if start_date and end_date:
            cursor = db.execute(
                "SELECT SUM(amount) as total FROM employee_expenses WHERE employee_id = ? AND expense_date BETWEEN ? AND ?",
                (self.id, start_date, end_date)
            )
        else:
            cursor = db.execute(
                "SELECT SUM(amount) as total FROM employee_expenses WHERE employee_id = ?",
                (self.id,)
            )

        result = cursor.fetchone()
        return result['total'] if result['total'] else 0.0

    def get_expenses(self, start_date=None, end_date=None):
        """Get all expenses for this employee"""
        if not self.id:
            return []

        db = get_db()
        if start_date and end_date:
            cursor = db.execute(
                "SELECT * FROM employee_expenses WHERE employee_id = ? AND expense_date BETWEEN ? AND ? ORDER BY expense_date DESC, expense_time DESC",
                (self.id, start_date, end_date)
            )
        else:
            cursor = db.execute(
                "SELECT * FROM employee_expenses WHERE employee_id = ? ORDER BY expense_date DESC, expense_time DESC",
                (self.id,)
            )

        expenses = []
        for row in cursor.fetchall():
            expenses.append(EmployeeExpense(
                id=row['id'],
                employee_id=row['employee_id'],
                amount=row['amount'],
                description=row['description'],
                expense_date=row['expense_date'],
                expense_time=row['expense_time'],
                added_by=row['added_by']
            ))
        return expenses

    def get_days_off(self, start_date=None, end_date=None):
        """Get all days off for this employee"""
        if not self.id:
            return []

        db = get_db()
        if start_date and end_date:
            # Get periods that overlap with the requested range
            cursor = db.execute(
                """SELECT * FROM employee_days_off
                   WHERE employee_id = ?
                   AND ((start_date <= ? AND end_date >= ?)
                   OR (start_date >= ? AND start_date <= ?))
                   ORDER BY start_date DESC""",
                (self.id, end_date, start_date, start_date, end_date)
            )
        else:
            cursor = db.execute(
                "SELECT * FROM employee_days_off WHERE employee_id = ? ORDER BY start_date DESC",
                (self.id,)
            )

        days_off = []
        for row in cursor.fetchall():
            days_off.append(EmployeeDayOff(
                id=row['id'],
                employee_id=row['employee_id'],
                start_date=row['start_date'],
                end_date=row['end_date'],
                reason=row['reason'],
                added_by=row['added_by']
            ))
        return days_off

    def get_days_off_count(self, start_date=None, end_date=None):
        """Get count of days off for this employee within a date range"""
        from datetime import datetime, timedelta

        if not self.id:
            return 0

        # Get all days off periods for this employee
        days_off_periods = self.get_days_off(start_date, end_date)

        if not start_date or not end_date:
            # If no date range specified, sum all the periods
            total = 0
            for period in days_off_periods:
                total += period.get_total_days()
            return total

        # Calculate total days off within the specified range
        period_start = datetime.strptime(start_date, "%Y/%m/%d")
        period_end = datetime.strptime(end_date, "%Y/%m/%d")

        total_days_off = 0

        for day_off in days_off_periods:
            off_start = datetime.strptime(day_off.start_date, "%Y/%m/%d")
            off_end = datetime.strptime(day_off.end_date, "%Y/%m/%d")

            # Calculate the overlap between the period and this day off range
            overlap_start = max(period_start, off_start)
            overlap_end = min(period_end, off_end)

            # If there's an overlap, count the days
            if overlap_start <= overlap_end:
                days = (overlap_end - overlap_start).days + 1
                total_days_off += days

        return total_days_off

    def calculate_balance(self, start_date, end_date):
        """Calculate employee balance (salary - expenses) for a date range, accounting for days off"""
        from datetime import datetime

        # Calculate number of days in the period
        start = datetime.strptime(start_date, "%Y/%m/%d")
        end = datetime.strptime(end_date, "%Y/%m/%d")
        total_days = (end - start).days + 1

        # Get number of days off
        days_off = self.get_days_off_count(start_date, end_date)

        # Calculate working days (total days minus days off)
        working_days = total_days - days_off

        # Calculate total salary based on working days
        total_salary = self.daily_salary * working_days

        # Get total expenses
        total_expenses = self.get_total_expenses(start_date, end_date)

        # Calculate balance
        balance = total_salary - total_expenses

        return {
            'total_days': total_days,
            'days_off': days_off,
            'working_days': working_days,
            'total_salary': total_salary,
            'total_expenses': total_expenses,
            'balance': balance
        }


class EmployeeExpense:
    """Represents an employee expense/spending entry"""

    def __init__(self, id=None, employee_id=None, amount=0.0, description='',
                 expense_date='', expense_time='', added_by=''):
        self.id = id
        self.employee_id = employee_id
        self.amount = amount
        self.description = description
        self.expense_date = expense_date
        self.expense_time = expense_time
        self.added_by = added_by

    @staticmethod
    @cached_query()
    def get_all(start_date=None, end_date=None):
        """Get all expenses"""
        db = get_db()
        if start_date and end_date:
            cursor = db.execute(
                "SELECT * FROM employee_expenses WHERE expense_date BETWEEN ? AND ? ORDER BY expense_date DESC, expense_time DESC",
                (start_date, end_date)
            )
        else:
            cursor = db.execute("SELECT * FROM employee_expenses ORDER BY expense_date DESC, expense_time DESC")

        expenses = []
        for row in cursor.fetchall():
            expenses.append(EmployeeExpense(
                id=row['id'],
                employee_id=row['employee_id'],
                amount=row['amount'],
                description=row['description'],
                expense_date=row['expense_date'],
                expense_time=row['expense_time'],
                added_by=row['added_by']
            ))
        return expenses

    def save(self):
        """Save expense to database"""
        db = get_db()

        if self.id is None:
            # Set date and time if not set
            if not self.expense_date:
                self.expense_date = datetime.now().strftime("%Y/%m/%d")
            if not self.expense_time:
                self.expense_time = datetime.now().strftime("%H:%M:%S")

            # Insert new expense
            cursor = db.execute(
                """INSERT INTO employee_expenses (employee_id, amount, description, expense_date, expense_time, added_by)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (self.employee_id, self.amount, self.description, self.expense_date, self.expense_time, self.added_by)
            )
            self.id = cursor.lastrowid
        else:
            # Update existing expense
            db.execute(
                """UPDATE employee_expenses SET employee_id = ?, amount = ?, description = ?,
                   expense_date = ?, expense_time = ?, added_by = ? WHERE id = ?""",
                (self.employee_id, self.amount, self.description, self.expense_date, self.expense_time, self.added_by, self.id)
            )

        db.commit()

        # Invalidate expense cache
        invalidate_cache('EmployeeExpense')

        return self

    def delete(self):
        """Delete expense from database"""
        if self.id:
            db = get_db()
            db.execute("DELETE FROM employee_expenses WHERE id = ?", (self.id,))
            db.commit()

            # Invalidate expense cache
            invalidate_cache('EmployeeExpense')


class EmployeeDayOff:
    """Represents an employee day off entry (date range)"""

    def __init__(self, id=None, employee_id=None, start_date='', end_date='', reason='', added_by=''):
        self.id = id
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.added_by = added_by

    def get_total_days(self):
        """Calculate total number of days in this period"""
        from datetime import datetime
        start = datetime.strptime(self.start_date, "%Y/%m/%d")
        end = datetime.strptime(self.end_date, "%Y/%m/%d")
        return (end - start).days + 1

    @staticmethod
    def get_all(start_date=None, end_date=None):
        """Get all days off"""
        db = get_db()
        if start_date and end_date:
            # Get periods that overlap with the requested range
            cursor = db.execute(
                """SELECT * FROM employee_days_off
                   WHERE (start_date <= ? AND end_date >= ?)
                   OR (start_date >= ? AND start_date <= ?)
                   ORDER BY start_date DESC""",
                (end_date, start_date, start_date, end_date)
            )
        else:
            cursor = db.execute("SELECT * FROM employee_days_off ORDER BY start_date DESC")

        days_off = []
        for row in cursor.fetchall():
            days_off.append(EmployeeDayOff(
                id=row['id'],
                employee_id=row['employee_id'],
                start_date=row['start_date'],
                end_date=row['end_date'],
                reason=row['reason'],
                added_by=row['added_by']
            ))
        return days_off

    def save(self):
        """Save day off to database"""
        db = get_db()

        if self.id is None:
            # Insert new day off
            cursor = db.execute(
                """INSERT INTO employee_days_off (employee_id, start_date, end_date, reason, added_by)
                   VALUES (?, ?, ?, ?, ?)""",
                (self.employee_id, self.start_date, self.end_date, self.reason, self.added_by)
            )
            self.id = cursor.lastrowid
        else:
            # Update existing day off
            db.execute(
                """UPDATE employee_days_off SET employee_id = ?, start_date = ?, end_date = ?, reason = ?, added_by = ? WHERE id = ?""",
                (self.employee_id, self.start_date, self.end_date, self.reason, self.added_by, self.id)
            )

        db.commit()
        return self

    def delete(self):
        """Delete day off from database"""
        if self.id:
            db = get_db()
            db.execute("DELETE FROM employee_days_off WHERE id = ?", (self.id,))
            db.commit()
