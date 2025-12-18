"""
Generate mock order data from menu.json for testing
"""
import json
import random
from datetime import datetime, timedelta
from models import Order, OrderItem, Register, get_db
from models.category import Category
from models.product import Product


def load_menu_data():
    """Load products from menu.json"""
    with open('menu.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)
    return menu_data


def get_or_create_categories_products(menu_data):
    """Create categories and products from menu.json if they don't exist"""
    db = get_db()

    category_map = {}
    product_list = []

    for cat_data in menu_data['categories']:
        if cat_data['status'] != 'Active' or not cat_data['products']:
            continue

        # Get or create category
        category_name = cat_data['name']
        cursor = db.execute("SELECT * FROM categories WHERE name = ?", (category_name,))
        cat_row = cursor.fetchone()

        if cat_row:
            category = Category(
                id=cat_row['id'],
                name=cat_row['name'],
                is_active=bool(cat_row['is_active']),
                display_order=cat_row['display_order']
            )
        else:
            category = Category(name=category_name, is_active=True)
            category.save()
            print(f"Created category: {category_name}")

        category_map[category_name] = category

        # Get or create products
        for prod_data in cat_data['products']:
            if prod_data['status'] != 'Active':
                continue

            product_name = prod_data['name']
            cursor = db.execute(
                "SELECT * FROM products WHERE name = ? AND category_id = ?",
                (product_name, category.id)
            )
            prod_row = cursor.fetchone()

            if prod_row:
                product = Product(
                    id=prod_row['id'],
                    category_id=prod_row['category_id'],
                    name=prod_row['name'],
                    price=prod_row['price'],
                    image_path=prod_row['image_path'],
                    is_active=bool(prod_row['is_active']),
                    display_order=prod_row['display_order']
                )
            else:
                product = Product(
                    category_id=category.id,
                    name=product_name,
                    price=prod_data['price'],
                    is_active=True
                )
                product.save()
                print(f"Created product: {category_name} - {product_name}")

            product_list.append({
                'product': product,
                'category': category
            })

    return product_list


def generate_random_order_items(product_list, min_items=1, max_items=5):
    """Generate random order items"""
    num_items = random.randint(min_items, max_items)
    selected_products = random.sample(product_list, min(num_items, len(product_list)))

    items = []
    for prod_data in selected_products:
        product = prod_data['product']
        category = prod_data['category']
        quantity = random.randint(1, 3)

        # Random discount (20% chance of discount)
        discount = 0.0
        if random.random() < 0.2:
            discount = random.choice([0.5, 1.0, 1.5, 2.0])

        # Build product name with category prefix for database storage
        product_name_for_db = f"{category.name} {product.name}"

        item = OrderItem(
            product_name=product_name_for_db,
            quantity=quantity,
            unit_price=product.price,
            discount=discount,
            notes=''
        )
        item.category_name = category.name
        item.base_name = product.name  # Store base name for receipts
        item.calculate_final_price()
        items.append(item)

    return items


def generate_mock_orders(num_orders=50, start_date=None, end_date=None):
    """Generate mock orders"""

    # Load menu data
    print("Loading menu data...")
    menu_data = load_menu_data()

    # Get or create categories and products
    print("Setting up products...")
    product_list = get_or_create_categories_products(menu_data)

    if not product_list:
        print("Error: No active products found in menu.json")
        return

    print(f"Found {len(product_list)} active products")

    # Get or create a register
    registers = Register.get_all()
    if not registers:
        print("Error: No registers found. Please open a register first.")
        return

    # Use the first register (or create orders for closed registers)
    register = registers[0]
    print(f"Using register #{register.id} ({register.employee_name})")

    # Date range
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    # Generate orders
    print(f"\nGenerating {num_orders} mock orders...")

    delivery_addresses = [
        "123 Main Street",
        "456 Oak Avenue",
        "789 Pine Road",
        "321 Elm Street",
        "654 Maple Drive"
    ]

    delivery_phones = [
        "20123456",
        "25987654",
        "22345678",
        "28765432",
        "29876543"
    ]

    for i in range(num_orders):
        # Random date/time within range
        order_datetime = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        order_date = order_datetime.strftime("%Y/%m/%d")
        order_time = order_datetime.strftime("%H:%M:%S")

        # Create order
        order = Order(
            order_date=order_date,
            order_time=order_time,
            register_id=register.id
        )

        # Random delivery (30% chance)
        if random.random() < 0.3:
            order.is_delivery = True
            order.delivery_address = random.choice(delivery_addresses)
            order.delivery_phone = random.choice(delivery_phones)
            order.delivery_price = random.choice([3.0, 5.0, 7.0])

        # Random payment status (95% paid, 5% unpaid/credit)
        order.is_paid = random.random() < 0.95

        # Add random items
        items = generate_random_order_items(product_list, min_items=1, max_items=5)
        for item in items:
            order.add_item(item)

        # Calculate total
        order.calculate_total()

        # Check if prices were modified (has discounts)
        order.price_modified = any(item.discount > 0 for item in order.items)

        # Save order
        order.save()

        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{num_orders} orders...")

    print(f"\n✅ Successfully generated {num_orders} mock orders!")
    print(f"   Date range: {start_date.strftime('%Y/%m/%d')} to {end_date.strftime('%Y/%m/%d')}")
    print(f"   Register: #{register.id} - {register.employee_name}")


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    num_orders = 50
    days_back = 30

    if len(sys.argv) > 1:
        try:
            num_orders = int(sys.argv[1])
        except ValueError:
            print("Usage: python generate_mock_data.py [num_orders] [days_back]")
            print("Example: python generate_mock_data.py 100 60")
            sys.exit(1)

    if len(sys.argv) > 2:
        try:
            days_back = int(sys.argv[2])
        except ValueError:
            print("Usage: python generate_mock_data.py [num_orders] [days_back]")
            sys.exit(1)

    start_date = datetime.now() - timedelta(days=days_back)
    end_date = datetime.now()

    print("=" * 60)
    print("MOCK DATA GENERATOR")
    print("=" * 60)
    print(f"Number of orders: {num_orders}")
    print(f"Date range: {start_date.strftime('%Y/%m/%d')} to {end_date.strftime('%Y/%m/%d')}")
    print("=" * 60)
    print()

    generate_mock_orders(num_orders=num_orders, start_date=start_date, end_date=end_date)
