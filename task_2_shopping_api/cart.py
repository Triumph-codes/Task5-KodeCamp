# task_2_shopping_api/cart.py

import json
import os
from datetime import datetime
from typing import List, Dict, Any

# --- Constants ---
CART_FILE = "cart.json"

# --- Data Store ---
cart_db: Dict[str, Dict[str, Any]] = {}

def load_cart_data() -> None:
    """Loads cart data from a JSON file."""
    global cart_db
    if os.path.exists(CART_FILE):
        try:
            with open(CART_FILE, "r") as f:
                # IMPORTANT: Initialize with empty dictionary if file is empty
                data = json.load(f)
                cart_db = data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {CART_FILE}: {e}")
            cart_db = {}
    else:
        cart_db = {}

def save_cart_data() -> None:
    """Saves cart data to a JSON file."""
    try:
        with open(CART_FILE, "w") as f:
            json.dump(cart_db, f, indent=4)
    except IOError as e:
        print(f"Error saving data to {CART_FILE}: {e}")

def add_to_cart(product_id: int, quantity: int, products_db: Dict) -> Dict[str, Any]:
    """Adds a product to the cart or updates its quantity."""
    product_id_str = str(product_id)
    
    if product_id not in products_db:
        raise ValueError(f"Product {product_id} not found in catalog.")
    
    # Get current quantity or 0 if not in cart
    current_qty = cart_db.get(product_id_str, {}).get('quantity', 0)
    
    # Update cart
    cart_db[product_id_str] = {
        'product_id': product_id,
        'quantity': current_qty + quantity,
        'name': products_db[product_id]['name'],
        'price': products_db[product_id]['price'],
        'last_updated': datetime.now().isoformat()
    }

    save_cart_data()
    return cart_db[product_id_str]

def checkout_cart(products_db: Dict[int, Any]) -> tuple[float, List[Dict[str, Any]]]:
    """Calculates total cost and returns detailed cart items."""
    total = 0.0
    detailed_items = []
    
    for product_id_str, item in cart_db.items():
        product_id = int(product_id_str)
        if product_id in products_db:
            subtotal = item['price'] * item['quantity']
            total += subtotal
            detailed_items.append({
                'product_id': product_id,
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'subtotal': round(subtotal, 2)
            })
    
    return round(total, 2), detailed_items

def clear_cart() -> None:
    """Clears all items from the cart."""
    global cart_db
    cart_db = {}
    save_cart_data()