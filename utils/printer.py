"""
Receipt printing utilities
"""
import config

try:
    import win32print
    PRINTING_AVAILABLE = True
except ImportError:
    PRINTING_AVAILABLE = False
    print("Warning: win32print not available. Printing disabled.")


def print_customer_receipt(order):
    """Print customer receipt"""
    if not config.ENABLE_PRINTING or not PRINTING_AVAILABLE:
        print("Printing disabled or unavailable")
        return

    # ESC/POS commands
    set_size_command = "\x1B\x4D\x00"
    set_font_command = "\x1B\x21\x00"
    bold_command = "\x1B\x45\x01"
    title_command = "\x1B\x21\x30" + "\x1B\x45\x01"

    # Build receipt
    lines = [
        config.RESTAURANT_PHONE,
        f"Order#:                    {order.order_number}",
        f"Order Date:                {order.order_date}",
        f"Order Time:                {order.order_time}",
    ]

    # Add delivery info if applicable
    if order.is_delivery:
        lines.extend([
            f"Customer house:",
            f"{order.delivery_address}",
            f"Customer phone:                {order.delivery_phone}",
            f"Delivery price:                {order.delivery_price}dt",
        ])

    lines.extend([
        "_____________________________________________",
        "Product                     Quantity     Price",
        "_____________________________________________",
        "",
    ])

    # Add order items
    for item in order.items:
        # For customer receipt, show full product name with category for clear instructions
        product_text = item.product_name
        quantity = int(item.quantity)
        final_price = float(item.final_price)
        unit_price = final_price / quantity
        line = f"{product_text.ljust(33)}x{quantity}  {unit_price:.2f}dt".rjust(8)
        lines.append(line)

        # Add notes if any
        if item.notes:
            lines.append(f"  Note: {item.notes}")

    # Add total
    total = float(order.total_amount)
    lines.extend([
        "",
        "_______________________________________________",
        "",
        title_command + f"     Total: {total:.2f}dt",
    ])

    ticket_text = "\n".join(lines)
    ticket_data = set_size_command + set_font_command + bold_command + ticket_text
    title_data = title_command + f"\t  {config.RESTAURANT_NAME} \n\n"

    # Add paper cut command at the end
    cut_command = "\x1D\x56\x01"
    cut_data = "\n\n\n\n\n" + cut_command

    try:
        hPrinter = win32print.OpenPrinter(config.PRINTER_NAME)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                # Write everything in one job: title + receipt + cut
                win32print.WritePrinter(hPrinter, title_data.encode("utf-8"))
                win32print.WritePrinter(hPrinter, ticket_data.encode("utf-8"))
                win32print.WritePrinter(hPrinter, cut_data.encode("utf-8"))
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

    except Exception as e:
        print(f"Error printing customer receipt: {e}")


def print_kitchen_receipt(order):
    """Print kitchen receipt"""
    if not config.ENABLE_PRINTING or not PRINTING_AVAILABLE:
        return

    # Build kitchen ticket
    lines = [
        f"Order#: {order.order_number}",
        f"Date: {order.order_date}",
        f"Time: {order.order_time}",
        "",
    ]

    for item in order.items:
        # For kitchen receipt, use base_name (without category prefix in product_name)
        base_name = getattr(item, 'base_name', None)
        if not base_name:
            # Legacy: extract base name from "Category ProductName" format
            parts = item.product_name.split(' ', 1)
            base_name = parts[1] if len(parts) == 2 else item.product_name

        category = getattr(item, 'category_name', '')
        product_line = f"{item.quantity} {((category + ' ') if category else '')}{base_name}"
        lines.append(product_line)

        # Add toppings on separate lines under the product
        toppings = getattr(item, 'toppings', None)
        if toppings:
            for group_options in toppings.values():
                for option in group_options:
                    lines.append(f"   + {option['name']}")

        if item.notes:
            lines.append(f"   Note: {item.notes}")

        lines.append("")

    kitchen_text = "\n".join(lines)
    kitchen_data = "\x1D\x21\x01" + "\x1D\x21\x10" + kitchen_text

    # Add paper cut command at the end
    cut_command = "\x1D\x56\x01"
    cut_data = "\n\n\n\n\n" + cut_command

    try:
        hPrinter = win32print.OpenPrinter(config.KITCHEN_PRINTER_NAME)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Kitchen", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                # Write everything in one job: receipt + cut
                win32print.WritePrinter(hPrinter, kitchen_data.encode("utf-8"))
                win32print.WritePrinter(hPrinter, cut_data.encode("utf-8"))
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

    except Exception as e:
        print(f"Error printing kitchen receipt: {e}")
