"""
Receipt PDF export utilities with 80mm thermal paper size
"""
from PyQt5.QtCore import QSizeF
from PyQt5.QtGui import QTextDocument, QTextCursor, QFont, QPageSize
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import config
import os


def export_receipt_to_pdf(order, receipt_type='customer', parent=None):
    """
    Export receipt to PDF with 80mm thermal paper size

    Args:
        order: Order object to generate receipt for
        receipt_type: 'customer' or 'kitchen'
        parent: Parent widget for dialogs
    """
    # Get default filename
    default_filename = f"Receipt_{order.order_number}_{receipt_type}.pdf"

    # Ask user where to save
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        "Save Receipt as PDF",
        default_filename,
        "PDF Files (*.pdf)"
    )

    if not file_path:
        return  # User cancelled

    try:
        # Create QPrinter for PDF
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)

        # Set 80mm thermal paper size
        # 80mm = 226.77 points (1mm = 2.83465 points)
        # Height is variable based on content, using a reasonable default
        width_mm = 80
        height_mm = 297  # Will auto-adjust based on content

        # Convert mm to points (1 mm = 2.83465 points)
        width_points = width_mm * 2.83465
        height_points = height_mm * 2.83465

        # Set custom page size
        page_size = QPageSize(QSizeF(width_points, height_points), QPageSize.Point)
        printer.setPageSize(page_size)

        # Set margins (5mm on all sides)
        margin_mm = 5
        margin_points = margin_mm * 2.83465
        printer.setPageMargins(margin_points, margin_points, margin_points, margin_points, QPrinter.Point)

        # Generate receipt content
        if receipt_type == 'customer':
            content = generate_customer_receipt_html(order)
        else:
            content = generate_kitchen_receipt_html(order)

        # Create text document
        document = QTextDocument()
        document.setHtml(content)

        # Print to PDF
        document.print_(printer)

        # Show success message
        if parent:
            QMessageBox.information(
                parent,
                "Success",
                f"Receipt saved to:\n{file_path}"
            )

        return file_path

    except Exception as e:
        if parent:
            QMessageBox.critical(
                parent,
                "Export Error",
                f"Failed to export receipt to PDF:\n{str(e)}"
            )
        return None


def generate_customer_receipt_html(order):
    """Generate HTML content for customer receipt"""
    html = """
    <html>
    <head>
        <style>
            body {
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                margin: 0;
                padding: 10px;
            }
            .header {
                text-align: center;
                font-weight: bold;
                font-size: 12pt;
                margin-bottom: 10px;
            }
            .section {
                margin: 5px 0;
            }
            .separator {
                border-top: 1px solid #000;
                margin: 5px 0;
            }
            .total {
                font-size: 14pt;
                font-weight: bold;
                text-align: center;
                margin-top: 10px;
            }
            .footer {
                text-align: center;
                margin-top: 10px;
                font-size: 9pt;
            }
            .item-row {
                margin: 3px 0;
            }
            .note {
                margin-left: 10px;
                font-size: 9pt;
                font-style: italic;
            }
        </style>
    </head>
    <body>
    """

    # Add header
    html += f'<div class="header">{config.RESTAURANT_NAME}</div>'
    html += '<div class="separator"></div>'

    # Phone
    html += f'<div class="section" style="text-align: center;">{config.RESTAURANT_PHONE}</div>'

    # Order info
    html += f'<div class="section">Order#: {order.order_number}</div>'
    html += f'<div class="section">Date: {order.order_date}</div>'
    html += f'<div class="section">Time: {order.order_time}</div>'

    # Delivery info
    if order.is_delivery:
        html += '<div class="separator"></div>'
        html += '<div class="section"><strong>Delivery Order</strong></div>'
        html += f'<div class="section">Address: {order.delivery_address}</div>'
        html += f'<div class="section">Phone: {order.delivery_phone}</div>'
        html += f'<div class="section">Delivery Fee: {order.delivery_price}dt</div>'

    # Items
    html += '<div class="separator"></div>'
    html += '<div class="section"><strong>Items:</strong></div>'

    for item in order.items:
        quantity = int(item.quantity)
        final_price = float(item.final_price)
        unit_price = final_price / quantity
        html += f'<div class="item-row">{item.product_name} x{quantity} - {unit_price:.2f}dt</div>'
        if item.notes:
            html += f'<div class="note">Note: {item.notes}</div>'

    # Total
    total = float(order.total_amount)
    html += '<div class="separator"></div>'
    html += f'<div class="total">Total: {total:.2f} dt</div>'

    # Add footer
    html += '<div class="separator"></div>'
    html += '<div class="footer">Thank you for your order!</div>'

    html += """
    </body>
    </html>
    """

    return html


def generate_kitchen_receipt_html(order):
    """Generate HTML content for kitchen receipt"""
    html = """
    <html>
    <head>
        <style>
            body {
                font-family: 'Courier New', monospace;
                font-size: 12pt;
                font-weight: bold;
                margin: 0;
                padding: 10px;
            }
            .header {
                text-align: center;
                font-size: 14pt;
                margin-bottom: 10px;
            }
            .section {
                margin: 5px 0;
            }
            .separator {
                border-top: 2px solid #000;
                margin: 10px 0;
            }
            .item {
                font-size: 13pt;
                margin: 8px 0;
            }
            .note {
                margin-left: 15px;
                font-size: 11pt;
                font-style: italic;
            }
        </style>
    </head>
    <body>
    """

    # Add header
    html += '<div class="header">KITCHEN ORDER</div>'
    html += '<div class="separator"></div>'

    # Order info
    html += f'<div class="section">Order#: {order.order_number}</div>'
    html += f'<div class="section">Date: {order.order_date}</div>'
    html += f'<div class="section">Time: {order.order_time}</div>'

    # Items
    html += '<div class="separator"></div>'
    for item in order.items:
        html += f'<div class="item">{item.quantity} x {item.product_name}</div>'
        if item.notes:
            html += f'<div class="note">{item.notes}</div>'

    html += '<div class="separator"></div>'

    html += """
    </body>
    </html>
    """

    return html
