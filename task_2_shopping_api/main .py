# task_2_shopping_api/main.py

from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import json
import os
import math
from datetime import datetime
from colorama import Fore, Style, init

from cart import (
    load_cart_data, 
    save_cart_data, 
    add_to_cart, 
    checkout_cart, 
    clear_cart,
    cart_db
)

# Initialize colorama
init(autoreset=True)

# --- Constants & Data Stores ---
PRODUCTS_FILE = "products.json"
products_db: Dict[int, dict] = {} # Key: product_id, Value: product dict

# --- Pydantic Models ---
class Product(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

    @model_validator(mode='after')
    def validate_price(self):
        if math.isnan(self.price) or math.isinf(self.price):
            raise ValueError("Price must be a finite number")
        return self

class CartItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class CartOperationResponse(BaseModel):
    message: str
    action: str
    current_quantity: int
    product_id: int
    product_name: Optional[str] = None

class CheckoutResponse(BaseModel):
    total_cost: float
    items: List[Dict[str, Any]]

# --- Utility Functions ---
def load_products_data() -> None:
    """Loads product data from a JSON file."""
    global products_db
    if not os.path.exists(PRODUCTS_FILE):
        print(f"{Fore.RED}ERROR: Products file '{PRODUCTS_FILE}' not found. {Style.RESET_ALL}")
        raise FileNotFoundError("Products file is missing.")
    try:
        with open(PRODUCTS_FILE, "r") as f:
            product_list = json.load(f)
            products_db = {p['id']: Product(**p).model_dump() for p in product_list}
        print(f"{Fore.GREEN}INFO: Successfully loaded {len(products_db)} products from {PRODUCTS_FILE}{Style.RESET_ALL}")
    except (json.JSONDecodeError, IOError) as e:
        print(f"{Fore.RED}ERROR: Could not load products from {PRODUCTS_FILE}: {e}{Style.RESET_ALL}")
        products_db = {}
    except Exception as e:
        print(f"{Fore.RED}ERROR: Failed to load products: {e}{Style.RESET_ALL}")
        raise


# --- FastAPI App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"{Fore.MAGENTA}--- API Startup: Loading data ---{Style.RESET_ALL}")
    try:
        load_products_data()
        load_cart_data()
        yield
    except FileNotFoundError as e:
        print(f"{Fore.RED}FATAL: Startup failed due to missing file: {e}{Style.RESET_ALL}")
        raise RuntimeError("Application cannot start without products file.")
    finally:
        # Shutdown
        print(f"{Fore.MAGENTA}--- API Shutdown ---{Style.RESET_ALL}")

app = FastAPI(
    title="Mini Shopping API",
    description="An API for managing products and a shopping cart.",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints ---

@app.get(
    "/products/",
    response_model=List[Product],
    summary="Get all products",
    description="Retrieves a list of all available products."
)
async def get_products():
    print(f"{Fore.BLUE}INFO: Retrieved all products.{Style.RESET_ALL}")
    return list(products_db.values())

@app.post(
    "/cart/add",
    status_code=status.HTTP_200_OK,
    summary="Add or update a product in the cart",
    description="Adds a specified quantity of a product to the shopping cart.",
    response_model=CartOperationResponse 
)
async def add_to_cart_endpoint(item: CartItem):
    try:
        cart_data = add_to_cart(item.product_id, item.quantity, products_db)
        action = "updated" if cart_data['quantity'] > item.quantity else "added"
        print(f"{Fore.GREEN}INFO: {action.capitalize()} {item.quantity} of product ID {item.product_id} to cart. "
              f"Now has {cart_data['quantity']} items. Current cart has {len(cart_db)} products.{Style.RESET_ALL}")

        return CartOperationResponse(
            message=f"Product {item.product_id} {action} to cart",
            action=action,
            current_quantity=cart_data['quantity'],
            product_id=cart_data['product_id'],
            product_name=cart_data['name']
        )
    except ValueError as e:
        print(f"{Fore.YELLOW}WARNING: {e}{Style.RESET_ALL}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        print(f"{Fore.RED}ERROR: An unexpected error occurred: {e}{Style.RESET_ALL}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@app.get(
    "/cart/",
    summary="View current cart items",
    description="Retrieves the current list of items in the cart.",
    response_model=Dict[str, Any]
)
async def view_cart():
    print(f"{Fore.BLUE}INFO: Cart contents retrieved. Current items: {len(cart_db)}{Style.RESET_ALL}")
    return cart_db

@app.get(
    "/cart/items/",
    summary="View current cart items as a list",
    description="Retrieves the current list of items in the cart.",
    response_model=List[Dict[str, Any]]
)
async def view_cart_as_list():
    print(f"{Fore.BLUE}INFO: Cart contents retrieved as a list. Current items: {len(cart_db)}{Style.RESET_ALL}")
    return list(cart_db.values())

@app.get(
    "/cart/checkout",
    response_model=CheckoutResponse,
    summary="Checkout the cart",
    description="Calculates the total cost of all items in the cart and then clears the cart."
)
async def checkout():
    if not cart_db:
        print(f"{Fore.YELLOW}WARNING: Checkout attempted on an empty cart.{Style.RESET_ALL}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot checkout an empty cart."
        )
    
    total_cost, detailed_items = checkout_cart(products_db)
    clear_cart()
    
    print(f"{Fore.CYAN}INFO: Cart checked out. Total cost: ${total_cost:.2f}. Cart has been cleared.{Style.RESET_ALL}")
    return CheckoutResponse(total_cost=total_cost, items=detailed_items)


@app.delete(
    "/cart/", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Empty the cart",
    description="Removes all items from the cart."
)
async def empty_cart():
    clear_cart()
    print(f"{Fore.GREEN}INFO: Cart has been emptied.{Style.RESET_ALL}")
    return None