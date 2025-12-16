# Mock Data Generator

This script generates realistic mock order data from your `menu.json` file for testing purposes.

## Features

- ✅ Reads products from `menu.json`
- ✅ Creates categories and products in the database if they don't exist
- ✅ Generates random orders with 1-5 items each
- ✅ Includes category names in order items (for proper receipt printing)
- ✅ Random delivery orders (30% of orders)
- ✅ Random discounts (20% chance per item)
- ✅ Random payment status (95% paid, 5% credit)
- ✅ Distributes orders across a date range
- ✅ Uses existing registers

## Usage

### Basic Usage (50 orders, last 30 days)
```bash
python generate_mock_data.py
```

### Custom Number of Orders
```bash
python generate_mock_data.py 100
```

### Custom Date Range (100 orders over last 60 days)
```bash
python generate_mock_data.py 100 60
```

## Parameters

1. **num_orders** (default: 50) - Number of orders to generate
2. **days_back** (default: 30) - How many days back to spread the orders

## Requirements

- At least one register must exist in the database
- Active products in `menu.json`

## What It Does

1. **Loads Menu Data**: Reads all active categories and products from `menu.json`

2. **Creates Database Entries**:
   - Creates categories if they don't exist
   - Creates products if they don't exist
   - Links products to categories

3. **Generates Orders**:
   - Random date/time within specified range
   - 1-5 random items per order
   - 30% chance of delivery (with random address and phone)
   - 20% chance of discount on each item
   - 5% chance of unpaid/credit order
   - Proper category names attached to items

4. **Saves to Database**: All orders are saved with proper relationships

## Example Output

```
============================================================
MOCK DATA GENERATOR
============================================================
Number of orders: 50
Date range: 2024/12/16 to 2025/01/15
============================================================

Loading menu data...
Setting up products...
Found 67 active products
Using register #1 (Ahmed)

Generating 50 mock orders...
  Generated 10/50 orders...
  Generated 20/50 orders...
  Generated 30/50 orders...
  Generated 40/50 orders...
  Generated 50/50 orders...

✅ Successfully generated 50 mock orders!
   Date range: 2024/12/16 to 2025/01/15
   Register: #1 - Ahmed
```

## Testing

After generating mock data, you can test:

- 📊 Statistics view with search and filtering
- 📄 Register reports with product summaries
- 🖨️ Receipt printing with category names
- 📜 Order history and reprints
- 🔍 Date range filtering

## Notes

- Orders are randomly distributed across the date range
- Each order gets a unique order number from the register
- Price modifications are tracked (when discounts are applied)
- Delivery prices are random: 3.0dt, 5.0dt, or 7.0dt
- Only products marked as "Active" in menu.json are used
- Only categories marked as "Active" are used

## Cleanup

To remove mock data, you can manually delete orders from the database or use SQL:

```sql
DELETE FROM order_items;
DELETE FROM orders;
```

⚠️ **Warning**: This will delete ALL orders, not just mock data!
