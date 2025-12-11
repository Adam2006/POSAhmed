"""
Generate mock order history data for 1 month
"""
import random
from datetime import datetime, timedelta
from models import get_db, Product, Register, Order, OrderItem

# Sample product names and prices
MOCK_PRODUCTS = [
    ("Pizza Margherita", 12.50),
    ("Pizza Pepperoni", 14.00),
    ("Chicken Sandwich", 8.00),
    ("Beef Burger", 9.50),
    ("Pasta Carbonara", 11.00),
    ("Pasta Bolognese", 10.50),
    ("Coca Cola", 2.00),
    ("Fanta", 2.00),
    ("Water", 1.50),
    ("Coffee", 2.50),
    ("French Fries", 3.50),
    ("Onion Rings", 3.00),
    ("Caesar Salad", 7.00),
    ("Chicken Wings", 8.50),
    ("Tiramisu", 5.00),
]

DELIVERY_ADDRESSES = [
    "123 Main Street, Apt 5B",
    "456 Park Avenue, Floor 3",
    "789 Ocean Drive, Villa 12",
    "321 Lake View Road",
    "555 Mountain Street, Apt 2A",
    "777 River Road, House 15",
    "999 Beach Boulevard",
    "147 Garden Lane, Apt 8C",
    "258 Forest Drive",
    "369 Valley Road, House 22",
]

DELIVERY_PHONES = [
    "99777197",
    "98765432",
    "97654321",
    "96543210",
    "95432109",
    "94321098",
    "93210987",
    "92109876",
    "91098765",
    "90987654",
]


def generate_mock_orders():
    """Generate mock orders for the past month"""
    db = get_db()

    # Employee names for registers
    employees = ['Shawky', 'Chokri']

    # Close any existing open registers first
    db.execute("UPDATE registers SET is_open = 0, closed_at = ? WHERE is_open = 1",
               (datetime.now().strftime("%Y/%m/%d %H:%M:%S"),))
    db.commit()

    # Create registers for the mock data period
    # We'll create registers for different shifts over the 30 days
    registers = []

    # Get current order number
    cursor = db.execute("SELECT MAX(order_number) as max_num FROM orders")
    result = cursor.fetchone()
    current_order_num = result['max_num'] if result['max_num'] else 0

    # Generate orders for the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    total_orders = 0
    current_date = start_date

    while current_date <= end_date:
        # Create morning shift register (9 AM - 5 PM) - Alternate between employees
        employee_index = (current_date - start_date).days % 2
        morning_employee = employees[employee_index]

        morning_shift_start = current_date.replace(hour=9, minute=0, second=0)
        cursor = db.execute(
            """INSERT INTO registers (shift_type, employee_name, opening_amount, opened_at, closed_at, is_open)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ('morning', morning_employee, 100.0,
             morning_shift_start.strftime("%Y/%m/%d %H:%M:%S"),
             current_date.replace(hour=17, minute=0, second=0).strftime("%Y/%m/%d %H:%M:%S"),
             0)
        )
        morning_register_id = cursor.lastrowid
        registers.append(('morning', morning_register_id, morning_employee))

        # Create evening shift register (5 PM - 11 PM) - Other employee
        evening_employee = employees[1 - employee_index]
        evening_shift_start = current_date.replace(hour=17, minute=0, second=0)
        cursor = db.execute(
            """INSERT INTO registers (shift_type, employee_name, opening_amount, opened_at, closed_at, is_open)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ('evening', evening_employee, 100.0,
             evening_shift_start.strftime("%Y/%m/%d %H:%M:%S"),
             current_date.replace(hour=23, minute=0, second=0).strftime("%Y/%m/%d %H:%M:%S"),
             0)
        )
        evening_register_id = cursor.lastrowid
        registers.append(('evening', evening_register_id, evening_employee))

        # Generate 5-15 orders per day
        orders_per_day = random.randint(5, 15)

        for _ in range(orders_per_day):
            current_order_num += 1

            # Random time during the day (9 AM to 11 PM)
            hour = random.randint(9, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)

            order_datetime = current_date.replace(hour=hour, minute=minute, second=second)
            order_date = order_datetime.strftime("%Y/%m/%d")
            order_time = order_datetime.strftime("%H:%M:%S")

            # Assign to correct register based on time
            if hour < 17:
                register_id = morning_register_id
            else:
                register_id = evening_register_id

            # 30% chance of delivery order
            is_delivery = random.random() < 0.3
            delivery_address = random.choice(DELIVERY_ADDRESSES) if is_delivery else ""
            delivery_phone = random.choice(DELIVERY_PHONES) if is_delivery else ""
            delivery_price = 3.0 if is_delivery else 0.0

            # Generate 1-5 items per order
            num_items = random.randint(1, 5)
            order_items = random.sample(MOCK_PRODUCTS, min(num_items, len(MOCK_PRODUCTS)))

            # Calculate total
            total_amount = sum(price * random.randint(1, 3) for _, price in order_items)
            if is_delivery:
                total_amount += delivery_price

            # Insert order
            cursor = db.execute(
                """INSERT INTO orders
                   (order_number, order_date, order_time, total_amount, is_delivery,
                    delivery_address, delivery_phone, delivery_price, register_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (current_order_num, order_date, order_time, total_amount,
                 int(is_delivery), delivery_address, delivery_phone, delivery_price, register_id)
            )
            order_id = cursor.lastrowid

            # Insert order items
            for product_name, unit_price in order_items:
                quantity = random.randint(1, 3)
                final_price = unit_price * quantity

                # 20% chance of having notes
                notes = ""
                if random.random() < 0.2:
                    note_options = ["Extra cheese", "No onions", "Well done", "Extra crispy", "Light on sauce"]
                    notes = random.choice(note_options)

                db.execute(
                    """INSERT INTO order_items
                       (order_id, product_name, quantity, unit_price, discount, final_price, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (order_id, product_name, quantity, unit_price, 0.0, final_price, notes)
                )

            total_orders += 1

        # Move to next day
        current_date += timedelta(days=1)

    db.commit()

    # Update last order number in settings
    db.execute("UPDATE settings SET value = ? WHERE key = 'last_order_number'", (str(current_order_num),))
    db.execute("UPDATE settings SET value = ? WHERE key = 'last_order_date'", (end_date.strftime("%Y/%m/%d"),))
    db.commit()

    print(f"\n[OK] Generated {total_orders} mock orders spanning 30 days")
    print(f"[OK] Date range: {start_date.strftime('%Y/%m/%d')} to {end_date.strftime('%Y/%m/%d')}")
    print(f"[OK] Order numbers: 1 to {current_order_num}")
    print(f"[OK] Created {len(registers)} registers (2 shifts per day)")
    print(f"[OK] Employees: {', '.join(employees)}")

    # Show summary statistics
    cursor = db.execute("SELECT COUNT(*) as total, SUM(total_amount) as revenue FROM orders")
    stats = cursor.fetchone()
    print(f"\nStatistics:")
    print(f"   Total Orders: {stats['total']}")
    print(f"   Total Revenue: {stats['revenue']:.2f} dt")

    cursor = db.execute("SELECT COUNT(*) as delivery_count FROM orders WHERE is_delivery = 1")
    delivery_stats = cursor.fetchone()
    print(f"   Delivery Orders: {delivery_stats['delivery_count']}")
    print(f"   Dine-in Orders: {stats['total'] - delivery_stats['delivery_count']}")

    # Show register statistics
    print(f"\nRegister Statistics:")
    for employee in employees:
        cursor = db.execute(
            "SELECT COUNT(*) as reg_count FROM registers WHERE employee_name = ?",
            (employee,)
        )
        reg_stats = cursor.fetchone()
        cursor = db.execute(
            """SELECT COUNT(o.id) as order_count, COALESCE(SUM(o.total_amount), 0) as revenue
               FROM orders o
               JOIN registers r ON o.register_id = r.id
               WHERE r.employee_name = ?""",
            (employee,)
        )
        order_stats = cursor.fetchone()
        print(f"   {employee}: {reg_stats['reg_count']} shifts, {order_stats['order_count']} orders, {order_stats['revenue']:.2f} dt")


if __name__ == "__main__":
    print("Generating mock order history...")
    print("=" * 50)
    generate_mock_orders()
    print("=" * 50)
    print("\n[SUCCESS] Mock data generation complete!")
    print("\nYou can now view the history in the application.")
