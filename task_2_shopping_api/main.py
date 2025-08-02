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
    get_cart
)

# Initialize colorama
init(autoreset=True)

# --- Constants & Data Stores ---
PRODUCTS_FILE = "products.json"
products_db: Dict[int, dict] = {}

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

# This model is no longer used for the POST endpoint, but we can keep it
# for documentation or other potential endpoints if needed.
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
def load_products_data():
    """Load and validate products database"""
    global products_db
    try:
        if not os.path.exists(PRODUCTS_FILE):
            raise FileNotFoundError(f"Missing products file: {PRODUCTS_FILE}")
            
        with open(PRODUCTS_FILE) as f:
            raw_data = json.load(f)
            
        # Validate basic structure
        if not isinstance(raw_data, list):
            raise ValueError("Products data must be a list")
            
        # Process and validate each product
        products_db = {}
        for idx, item in enumerate(raw_data):
            try:
                product = Product(**item)
                products_db[product.id] = product.model_dump()
            except Exception as e:
                print(f"{Fore.YELLOW}WARNING: Invalid product at index {idx}: {e}{Style.RESET_ALL}")
                
        if not products_db:
            raise ValueError("No valid products found in file")
            
        print(f"{Fore.GREEN}Loaded {len(products_db)} valid products{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}ERROR: Product load failed: {e}{Style.RESET_ALL}")
        products_db = {}  # Ensures app has empty state rather than crashing
        raise  # Re-raise if you want startup to fail on product load


# --- FastAPI App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown with robust error handling"""
    startup_success = False
    print(f"{Fore.MAGENTA}=== API Startup: Loading Data ==={Style.RESET_ALL}")
    
    try:
        # Phase 1: Load critical data
        load_products_data()
        
        # Phase 2: Load secondary data (cart can start empty)
        try:
            load_cart_data()
        except Exception as e:
            print(f"{Fore.YELLOW}WARNING: Cart load failed - starting with empty cart: {e}{Style.RESET_ALL}")
        
        startup_success = True
        yield
        
    except FileNotFoundError as e:
        print(f"{Fore.RED}FATAL: Missing required file: {e}{Style.RESET_ALL}")
        raise RuntimeError(f"Critical startup failure: {e}")
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}FATAL: Corrupted data file: {e}{Style.RESET_ALL}")
        raise RuntimeError("Invalid data format in storage files")
    except Exception as e:
        print(f"{Fore.RED}FATAL: Unexpected startup error: {e}{Style.RESET_ALL}")
        raise RuntimeError("Application failed to initialize")
    
    finally:
        shutdown_msg = "Graceful shutdown" if startup_success else "Abnormal shutdown"
        color = Fore.GREEN if startup_success else Fore.RED
        print(f"{color}=== API Shutdown: {shutdown_msg} ==={Style.RESET_ALL}")

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
    summary="Add a product to the cart (using query parameters)",
    description="Adds a specified quantity of a product to the shopping cart via query parameters.",
    response_model=CartOperationResponse 
)
async def add_to_cart_endpoint(
    product_id: int = Query(..., description="ID of the product to add", gt=0),
    quantity: int = Query(1, description="Quantity to add", gt=0)
):
    try:
        cart_data = add_to_cart(product_id, quantity, products_db)
        action = "updated" if cart_data['quantity'] > quantity else "added"
        print(f"{Fore.GREEN}INFO: {action.capitalize()} {quantity} of product ID {product_id} to cart. "
              f"Now has {cart_data['quantity']} items. Current cart has {len(cart_db)} products.{Style.RESET_ALL}")

        return CartOperationResponse(
            message=f"Product {product_id} {action} to cart",
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
    cart = get_cart()
    print(f"{Fore.BLUE}INFO: Cart contents retrieved. Current items: {len(cart)}{Style.RESET_ALL}")
    return cart

@app.get(
    "/cart/items/",
    summary="View current cart items as a list",
    description="Retrieves the current list of items in the cart.",
    response_model=List[Dict[str, Any]]
)
async def view_cart_as_list():
    cart = get_cart()
    print(f"{Fore.BLUE}INFO: Cart contents retrieved as a list. Current items: {len(cart)}{Style.RESET_ALL}")
    return list(cart.values())

@app.get(
    "/cart/checkout",
    response_model=CheckoutResponse,
    summary="Checkout the cart",
    description="Calculates the total cost of all items in the cart and then clears the cart."
)
async def checkout():
    cart = get_cart()
    if not cart:
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