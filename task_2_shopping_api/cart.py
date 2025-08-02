import json
import os
from datetime import datetime
from typing import Dict, Any, List
from colorama import Fore, Style

# --- Constants ---
CART_FILE = "cart.json"

# --- Data Store ---
cart_db: Dict[str, Dict[str, Any]] = {}

def load_cart_data() -> None:
    """Loads cart data from JSON file into memory with proper error handling"""
    global cart_db
    try:
        if os.path.exists(CART_FILE):
            with open(CART_FILE, "r") as f:
                data = json.load(f)
                # Ensure we always get a dictionary, even if file is empty/corrupt
                cart_db = data if isinstance(data, dict) else {}
                print(f"{Fore.GREEN}Cart loaded with {len(cart_db)} items{Style.RESET_ALL}")
        else:
            cart_db = {}
            print(f"{Fore.YELLOW}No existing cart file, starting fresh{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error loading cart: {e}{Style.RESET_ALL}")
        cart_db = {}  # Reset to empty dict on error

def save_cart_data() -> None:
    """Saves cart data to JSON file with error handling"""
    try:
        with open(CART_FILE, "w") as f:
            json.dump(cart_db, f, indent=4)
        print(f"{Fore.CYAN}Cart saved with {len(cart_db)} items{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error saving cart: {e}{Style.RESET_ALL}")

def add_to_cart(product_id: int, quantity: int, products_db: Dict[int, Any]) -> Dict[str, Any]:
    """Adds or updates product in cart with full synchronization"""
    global cart_db
    
    # First ensure we have fresh data
    load_cart_data()
    
    product_id_str = str(product_id)
    if product_id not in products_db:
        raise ValueError(f"Product {product_id} not in catalog")
    
    # Get current quantity or 0 if not in cart
    current_qty = cart_db.get(product_id_str, {}).get('quantity', 0)
    new_qty = current_qty + quantity
    
    # Update in-memory cart
    cart_db[product_id_str] = {
        'product_id': product_id,
        'quantity': new_qty,
        'name': products_db[product_id]['name'],
        'price': products_db[product_id]['price'],
        'updated_at': datetime.now().isoformat()
    }
    
    # Persist to disk
    save_cart_data()
    return cart_db[product_id_str]

def checkout_cart(products_db: Dict[int, Any]) -> tuple[float, List[Dict[str, Any]]]:
    """Calculates total cost with proper type handling"""
    load_cart_data()  # Ensure we have latest data
    
    total = 0.0
    detailed_items = []
    
    for product_id_str, item in cart_db.items():
        try:
            product_id = int(product_id_str)
            if product_id in products_db:
                subtotal = float(item['price']) * int(item['quantity'])
                total += subtotal
                detailed_items.append({
                    'product_id': product_id,
                    'name': str(item['name']),
                    'price': float(item['price']),
                    'quantity': int(item['quantity']),
                    'subtotal': round(subtotal, 2)
                })
        except (ValueError, KeyError) as e:
            print(f"{Fore.RED}Error processing cart item {product_id_str}: {e}{Style.RESET_ALL}")
    
    return round(total, 2), detailed_items

def get_cart() -> Dict[str, Dict[str, Any]]:
    """Returns the current state of the in-memory cart."""
    global cart_db
    return cart_db

def clear_cart() -> None:
    """Clears cart both in memory and on disk"""
    global cart_db
    cart_db = {}
    save_cart_data()
    print(f"{Fore.GREEN}Cart cleared{Style.RESET_ALL}")