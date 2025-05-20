import sqlite3
from datetime import datetime

DB_PATH = "cartcreations.db"

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            email TEXT,
            address TEXT,
            product_summary TEXT,
            total_amount REAL,
            currency TEXT,
            payment_method TEXT,
            transaction_ref TEXT,
            transaction_time TEXT,
            transaction_status TEXT,
            is_paid INTEGER,
            cnic TEXT,
            mobile TEXT
        )
    ''')

    # Create products table
        # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT,
            category TEXT
        )
    ''')


    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def log_event(event_type, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (event_type, message, created_at)
        VALUES (?, ?, ?)
    ''', (event_type, message, datetime.now()))
    conn.commit()
    conn.close()

def save_order(order_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (
            customer_name, email, address, product_summary, total_amount,
            currency, payment_method, transaction_ref, transaction_time,
            transaction_status, is_paid, cnic, mobile
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_data['customer_name'],
        order_data['email'],
        order_data['address'],
        order_data['product_summary'],
        order_data['total_amount'],
        order_data['currency'],
        order_data['payment_method'],
        order_data['transaction_ref'],
        order_data['transaction_time'],
        order_data['transaction_status'],
        order_data['is_paid'],
        order_data['cnic'],
        order_data['mobile']
    ))
    conn.commit()
    conn.close()

#initialize_database()
