"""
Order controller for managing cart and checkout
"""
from models import Order, OrderItem, Register
from datetime import datetime


class OrderController:
    """Manages current order and cart operations"""

    def __init__(self):
        self.cart_items = []
        self.current_order_number = None

    def get_current_order_number(self):
        """Get the next order number from the current register"""
        # Get current register
        current_register = Register.get_current_register()
        if not current_register:
            return 0  # No register open

        # Return the next order number (current last_order_number + 1)
        return current_register.last_order_number + 1

    def add_item(self, product, quantity=1, notes='', category_name='', toppings=None, custom_price=None):
        """Add a product to the cart (always creates new item, never combines)"""
        # Use custom price if provided (includes toppings), otherwise use product price
        unit_price = custom_price if custom_price is not None else product.price

        # Build display name for cart (with toppings inline)
        display_name = product.name
        if toppings:
            topping_names = []
            for group_options in toppings.values():
                for option in group_options:
                    topping_names.append(option['name'])
            if topping_names:
                display_name += f" ({', '.join(topping_names)})"

        # Always add new item - each click creates a separate cart item
        cart_item = {
            'product_id': product.id,
            'name': display_name,  # Display name for cart (includes toppings)
            'base_name': product.name,  # Original product name without toppings
            'category_name': category_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'original_price': product.price,  # Store original price for comparison
            'discount': 0.0,
            'final_price': unit_price * quantity,
            'notes': notes,
            'toppings': toppings  # Store toppings data
        }
        self.cart_items.append(cart_item)

    def remove_item(self, index):
        """Remove item from cart by index"""
        if 0 <= index < len(self.cart_items):
            self.cart_items.pop(index)

    def update_quantity(self, index, quantity):
        """Update item quantity"""
        if 0 <= index < len(self.cart_items) and quantity > 0:
            self.cart_items[index]['quantity'] = quantity
            self.cart_items[index]['final_price'] = (
                (self.cart_items[index]['unit_price'] - self.cart_items[index]['discount'])
                * quantity
            )

    def update_discount(self, index, discount):
        """Update item discount"""
        if 0 <= index < len(self.cart_items):
            self.cart_items[index]['discount'] = discount
            self.cart_items[index]['final_price'] = (
                (self.cart_items[index]['unit_price'] - discount)
                * self.cart_items[index]['quantity']
            )

    def get_cart_items(self):
        """Get all cart items"""
        return self.cart_items

    def get_total(self):
        """Calculate cart total"""
        return sum(item['final_price'] for item in self.cart_items)

    def clear_cart(self):
        """Clear all items from cart"""
        self.cart_items = []
        self.current_order_number = None

    def checkout(self, is_delivery=False, delivery_data=None, client_id=None):
        """Process checkout and create order"""
        if not self.cart_items:
            return False

        # Get current register
        current_register = Register.get_current_register()
        if not current_register:
            raise Exception("No register is currently open. Please open a register before making sales.")

        # Create order
        order = Order()
        order.order_number = Order.get_next_order_number()  # This will get and increment from register
        order.order_date = datetime.now().strftime("%Y/%m/%d")
        order.order_time = datetime.now().strftime("%H:%M:%S")
        order.register_id = current_register.id

        # Set client and payment status
        order.client_id = client_id
        if client_id is not None:
            order.is_paid = False  # Credit sale
        else:
            order.is_paid = True   # Cash sale

        # Set delivery info
        if is_delivery and delivery_data:
            order.is_delivery = True
            order.delivery_address = delivery_data.get('place', '')
            order.delivery_phone = delivery_data.get('num', '')
            order.delivery_price = float(delivery_data.get('price', 0))

        # Check if any prices were modified
        price_modified = False
        for cart_item in self.cart_items:
            original_price = cart_item.get('original_price', cart_item['unit_price'])
            if cart_item['unit_price'] != original_price or cart_item['discount'] > 0:
                price_modified = True
                break

        order.price_modified = price_modified

        # Add items to order
        for cart_item in self.cart_items:
            # Build product name with category prefix for database storage
            base_name = cart_item.get('base_name', cart_item['name'])
            category_name = cart_item.get('category_name', '')

            # Store as "CategoryName ProductName" in database for proper reporting
            if category_name:
                product_name_for_db = f"{category_name} {base_name}"
            else:
                product_name_for_db = base_name

            order_item = OrderItem(
                product_name=product_name_for_db,
                quantity=cart_item['quantity'],
                unit_price=cart_item['unit_price'],
                discount=cart_item['discount'],
                notes=cart_item['notes']
            )
            # Add category name and toppings as attributes for printing
            order_item.category_name = category_name
            order_item.base_name = base_name  # Store base name for receipts
            order_item.toppings = cart_item.get('toppings')  # Store toppings for kitchen receipt
            order_item.calculate_final_price()
            order.add_item(order_item)

        # Save order to database
        order.save()

        # Update client balance if credit sale
        if client_id is not None and not order.is_paid:
            from models import Client
            client = Client.get_by_id(client_id)
            if client:
                client.add_to_balance(order.total_amount)

        # Print receipt
        self.print_receipt(order)

        # Clear cart
        self.clear_cart()

        return True

    def print_receipt(self, order):
        """Print receipt for the order"""
        from utils.printer import print_customer_receipt, print_kitchen_receipt

        try:
            print_customer_receipt(order)
            print_kitchen_receipt(order)
        except Exception as e:
            print(f"Printing error: {e}")
            # Continue even if printing fails
