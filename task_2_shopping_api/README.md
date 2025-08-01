# Task 2: Mini Shopping API with Cart

### Goal
Create a product and shopping cart API to handle Browse, adding items, and checkout.

### Features
- **Product & Cart Models:** Pydantic models for `Product` and `CartItem`.
- **Endpoints:**
  - `GET /products/`: Get a list of all available products.
  - `POST /cart/add?product_id={id}&qty={qty}`: Add a product to the cart using query parameters.
  - `GET /cart/checkout`: Calculate the total cost of the cart and clear it.
- **Modular Design:** All cart logic is encapsulated in the `cart.py` module.
- **Data Persistence:** Products are loaded from `products.json`, and the cart is managed via `cart.json`.
- **Rounding:** The `math` module is used for accurate rounding during checkout.
- **Console Logging:** Uses `colorama` for clear, color-coded messages in the terminal.

### How to Run
1. Navigate to the `task_2_shopping_api/` directory.
2. Install dependencies: `pip install fastapi "uvicorn[standard]" colorama`
3. Run the application: `uvicorn main:app --reload`
4. Access the interactive documentation at `http://127.0.0.1:8000/docs` to test the endpoints.