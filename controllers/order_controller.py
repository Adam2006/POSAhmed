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

    def add_item(self, product, quantity=1, notes='', category_name=''):
        """Add a product to the cart (always creates new item, never combines)"""
        # Always add new item - each click creates a separate cart item
        cart_item = {
            'product_id': product.id,
            'name': product.name,
            'category_name': category_name,
            'quantity': quantity,
            'unit_price': product.price,
            'discount': 0.0,
            'final_price': product.price * quantity,
            'notes': notes
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

    def checkout(self, is_delivery=False, delivery_data=None):
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

        # Set delivery info
        if is_delivery and delivery_data:
            order.is_delivery = True
            order.delivery_address = delivery_data.get('place', '')
            order.delivery_phone = delivery_data.get('num', '')
            order.delivery_price = float(delivery_data.get('price', 0))

        # Add items to order
        for cart_item in self.cart_items:
            order_item = OrderItem(
                product_name=cart_item['name'],
                quantity=cart_item['quantity'],
                unit_price=cart_item['unit_price'],
                discount=cart_item['discount'],
                notes=cart_item['notes']
            )
            order_item.calculate_final_price()
            order.add_item(order_item)

        # Save order to database
        order.save()

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
