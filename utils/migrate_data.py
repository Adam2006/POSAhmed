"""
Utility to migrate data from old JSON format to new database
"""
import json
import os
from models import Category, Product, get_db


def migrate_from_json(json_path="menu.json"):
    """Migrate menu data from JSON file to database"""
    if not os.path.exists(json_path):
        print(f"JSON file not found: {json_path}")
        return False

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return False

    # Initialize database
    db = get_db()

    print("Starting migration...")

    # Check if data has "categories" key (new format)
    categories_list = data.get("categories", [])

    if not categories_list:
        print("No categories found in JSON file")
        return False

    # Iterate through categories
    for category_data in categories_list:
        category_name = category_data.get("name", "")
        if not category_name:
            continue

        is_active = category_data.get("status", "Active") == "Active"

        # Create or get category
        category = Category.get_by_name(category_name)
        if not category:
            category = Category(name=category_name, is_active=is_active)
            category.save()
            print(f"Created category: {category_name}")
        else:
            print(f"Category already exists: {category_name}")

        # Get products list
        products_list = category_data.get("products", [])

        # Iterate through products
        for product_data in products_list:
            product_name = product_data.get("name", "")
            if not product_name:
                continue

            try:
                is_product_active = product_data.get("status", "Active") == "Active"
                price = float(product_data.get("price", 0.0))
                image_path = product_data.get("image", "")

                # Create product
                product = Product(
                    category_id=category.id,
                    name=product_name,
                    price=price,
                    image_path=image_path,
                    is_active=is_product_active
                )
                product.save()
                print(f"  Created product: {product_name} ({price}dt)")

            except Exception as e:
                print(f"  Error creating product {product_name}: {e}")
                continue

    print("Migration completed!")
    return True


def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")

    # Create categories
    categories_data = [
        ("Sandwiches", True),
        ("Pizza", True),
        ("Pasta", True),
        ("Drinks", True),
        ("Desserts", True),
    ]

    for cat_name, is_active in categories_data:
        category = Category.get_by_name(cat_name)
        if not category:
            category = Category(name=cat_name, is_active=is_active)
            category.save()
            print(f"Created category: {cat_name}")

    # Create sample products
    sandwiches = Category.get_by_name("Sandwiches")
    if sandwiches:
        products_data = [
            ("Chicken Sandwich", 8.5),
            ("Beef Burger", 10.0),
            ("Tuna Sandwich", 7.5),
            ("Veggie Burger", 7.0),
        ]
        for prod_name, price in products_data:
            product = Product(
                category_id=sandwiches.id,
                name=prod_name,
                price=price,
                is_active=True
            )
            product.save()
            print(f"  Created product: {prod_name}")

    pizza = Category.get_by_name("Pizza")
    if pizza:
        products_data = [
            ("Margherita", 12.0),
            ("Pepperoni", 15.0),
            ("4 Cheese", 16.0),
            ("Vegetarian", 14.0),
        ]
        for prod_name, price in products_data:
            product = Product(
                category_id=pizza.id,
                name=prod_name,
                price=price,
                is_active=True
            )
            product.save()
            print(f"  Created product: {prod_name}")

    drinks = Category.get_by_name("Drinks")
    if drinks:
        products_data = [
            ("Coca Cola", 2.0),
            ("Fanta", 2.0),
            ("Water", 1.0),
            ("Coffee", 3.0),
        ]
        for prod_name, price in products_data:
            product = Product(
                category_id=drinks.id,
                name=prod_name,
                price=price,
                is_active=True
            )
            product.save()
            print(f"  Created product: {prod_name}")

    print("Sample data created!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        create_sample_data()
    elif len(sys.argv) > 1:
        migrate_from_json(sys.argv[1])
    else:
        # Try default path
        if os.path.exists("menu.json"):
            migrate_from_json("menu.json")
        else:
            print("No menu.json found. Creating sample data instead...")
            create_sample_data()
