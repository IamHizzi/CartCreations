# 🛒 Cart Creations — E-commerce Web App

**Cart Creations** is a sleek and responsive e-commerce web application built with **Flask**, **SQLite**, and **Bootstrap**. It allows users to browse products, add them to a cart, and place orders using **Cash on Delivery**, **JazzCash**, or **EasyPaisa**. An admin panel is available separately for order and product management.

---

## 🚀 Features

- 🛍️ Browse and filter products by category
- 🔎 Product detail pages with related items
- 🛒 Add to cart, update quantities, and checkout
- 💵 Place orders via:
  - Cash on Delivery (COD)
  - JazzCash (sandbox API integration)
  - EasyPaisa (sandbox API integration)
- ✉️ Contact and About pages
- 🔐 Admin dashboard (separate route `/admin`) for managing orders and logs

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, Bootstrap 5, Jinja2
- **Database:** SQLite
- **Payments:** JazzCash & EasyPaisa (sandbox endpoints)

---

## 🧪 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/cart-creations.git
cd cart-creations
```

2. Install dependencies
pip install -r requirements.txt

3. Set up the SQLite database
If not already created, run this SQL:

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    email TEXT,
    address TEXT,
    product_summary TEXT,
    total_amount INTEGER,
    currency TEXT,
    payment_method TEXT,
    transaction_ref TEXT,
    transaction_time TEXT,
    transaction_status TEXT,
    is_paid TEXT,
    cnic TEXT,
    mobile TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    message TEXT,
    timestamp TEXT
);
Or just launch the app and it will auto-create the database if handled in code.

4. Run the Flask App
python app.py

Access the app at: http://localhost:5000
