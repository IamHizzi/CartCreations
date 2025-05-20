import itertools
import random
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import hmac, hashlib
from datetime import datetime, timedelta
## database
from db_utils import DB_PATH, log_event, save_order

app = Flask(__name__)
app.secret_key = 'you_cant_guess_this'  

JAZZCASH_MERCHANT_ID = "MC151070"
JAZZCASH_PASSWORD = "x1u0z38h01"
JAZZCASH_INTEGRITY_SALT = "8s257vww96"

# PREFIX = 'aBcDeFgHIJk'
# NUMBER = '12345678901234567890'

# # Generate all prefix+suffix combinations to keep total length 20
# prefixes = [PREFIX[:i] for i in range(1, len(PREFIX) + 1)]
# txn_refs = [(p + NUMBER[:20 - len(p)]) for p in prefixes]

# # Cycle through them in memory only
# prefix_cycle = itertools.cycle(txn_refs)

@app.route('/pay-now', methods=['POST'])
def pay_now():
    cart_items = session.get('cart', [])
    cart_total = sum(item['price'] * item['quantity'] for item in cart_items)
    payment_method = request.form.get("payment_method")

    # customer details
    customer_name = request.form.get('billing_name')
    email = request.form.get('billing_email')
    address = request.form.get('billing_address')
    product_summary = ", ".join([f"{item['name']} x {item['quantity']}" for item in cart_items])
    currency = "PKR"

    # Common order details
    now = datetime.now()
    txn_ref = "T" + now.strftime("%Y%m%d%H%M%S")
    #txn_ref = next(prefix_cycle)
    #txn_ref= "J00050n7j2rskqvh5m78"
    txn_time = now.strftime("%Y%m%d%H%M%S")
    expiry_time = (now + timedelta(hours=1)).strftime("%Y%m%d%H%M%S")
    amount_pkr = int(cart_total * 264)  # Convert to PKR

    if payment_method == "CashOnDelivery":
        session.pop('cart', None)
        transaction_data = {
            "pp_ResponseCode": "COD",
            "pp_ResponseMessage": "Order placed with Cash on Delivery.",
            "pp_TxnRefNo": txn_ref,
            "pp_Amount": amount_pkr,
            "pp_TxnDateTime": txn_time
        }

        save_order({
            "customer_name": customer_name,
            "email": email,
            "address": address,
            "product_summary": product_summary,
            "total_amount": amount_pkr,
            "currency": currency,
            "payment_method": payment_method,
            "transaction_ref": txn_ref,
            "transaction_time": txn_time,
            "transaction_status": "Success",
            "is_paid": "No",
            "cnic": None,
            "mobile": None
        })

        log_event("order_cod", f"COD order placed: {txn_ref}")
        return render_template("order_complete.html",
                               transaction_data=transaction_data,
                               cart_items=cart_items,
                               cart_total=cart_total)

                               
    elif payment_method in ["JazzCash", "EasyPaisa"]:
        # JazzCash and EasyPaisa share similar API structure
        cnic = request.form.get('cnic')
        mobile = request.form.get('msisdn')

        data = {
        "pp_Amount": str(amount_pkr),
        "pp_BillReference": "CartCreations",
        "pp_CNIC": cnic,
        "pp_Description": "Order from Cart Creations",
        "pp_Language": "EN",
        "pp_MerchantID": JAZZCASH_MERCHANT_ID,
        "pp_MobileNumber": mobile,
        "pp_Password": JAZZCASH_PASSWORD,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": txn_time,
        "pp_TxnExpiryDateTime": expiry_time,
        "pp_TxnRefNo": txn_ref,
        "ppmpf_1": "",
        "ppmpf_2": "",
        "ppmpf_3": "",
        "ppmpf_4": "",
        "ppmpf_5": ""
    }

    # Generate hash string (sorted by key)
    keys_to_include = [k for k in data if k.startswith("pp_")]
    sorted_items = sorted((k, data[k]) for k in keys_to_include)
    hash_string = '&'.join([v for k, v in sorted_items if v])
    hash_input = f"{JAZZCASH_INTEGRITY_SALT}&{hash_string}"
    secure_hash = hmac.new(
        JAZZCASH_INTEGRITY_SALT.encode(),
        hash_input.encode(),
        hashlib.sha256
    ).hexdigest()

    data['pp_SecureHash'] = secure_hash

    # Send request to JazzCash
    response = requests.post(
        "https://sandbox.jazzcash.com.pk/ApplicationAPI/API/2.0/Purchase/DoMWalletTransaction",
        json=data
    )

    response_json = response.json()
  
    if response_json.get("pp_ResponseCode") == "000":
        # Clear cart after success
        session.pop('cart', None)
        save_order({
                "customer_name": customer_name,
                "email": email,
                "address": address,
                "product_summary": product_summary,
                "total_amount": amount_pkr,
                "currency": currency,
                "payment_method": payment_method,
                "transaction_ref": txn_ref,
                "transaction_time": txn_time,
                "transaction_status": "Success",
                "is_paid": "Yes",
                "cnic": cnic,
                "mobile": mobile
            })
        log_event("payment_success", f"{payment_method} - {txn_ref}")
        return render_template("order_complete.html", 
                               transaction_data=response_json,
                               cart_items=cart_items,
                               cart_total=cart_total)
    else:
        log_event("payment_failure", f"{payment_method} - {txn_ref} - {response_json.get('pp_ResponseMessage')}")
        flash("Payment failed: " + response_json.get("pp_ResponseMessage", "Unknown error"))
        return redirect(url_for('checkout'))


CATEGORIES = ["furniture", "lighting", "textiles", "decor"]
def get_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

    

@app.route('/')
def home():
    PRODUCTS = get_products()
    featured_products = PRODUCTS[:3]  # First 3 products as featured
    return render_template('index.html', featured_products=featured_products, categories=CATEGORIES)

@app.route('/products')
def products():
    PRODUCTS = get_products()
    category = request.args.get('category')
    if category:
        filtered_products = [p for p in PRODUCTS if p[5] == category]
        return render_template('products.html', products=filtered_products, categories=CATEGORIES, current_category=category)
    return render_template('products.html', products=PRODUCTS, categories=CATEGORIES)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    PRODUCTS = get_products()
    product = next((p for p in PRODUCTS if p[0] == product_id), None)
    if product:
        related_products = [p for p in PRODUCTS if p[5] == product[5] and p[0] != product_id]
        return render_template('product_detail.html', product=product, categories=CATEGORIES, related_products=related_products)
    return redirect(url_for('products'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    PRODUCTS = get_products()
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))
    
    product = next((p for p in PRODUCTS if p[0] == product_id), None)  # p[0] is likely the ID
    
    if product:
        if 'cart' not in session:
            session['cart'] = []

        cart_item = next((item for item in session['cart'] if item['id'] == product_id), None)

        if cart_item:
            cart_item['quantity'] += quantity
        else:
            cart_item = {
                'id': product[0],        # ID
                'name': product[1],      # Name
                'price': product[2],     # Price
                'image': product[4],     # Image URL
                'quantity': quantity
            }
            session['cart'].append(cart_item)

        session.modified = True
        flash(f"{product[1]} added to your cart!")
        
    return redirect(request.referrer or url_for('products'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    cart_total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total, categories=CATEGORIES)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    
    if 'cart' in session:
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] = quantity
                break
        
        # Remove items with quantity 0
        session['cart'] = [item for item in session['cart'] if item['quantity'] > 0]
        session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    # Simulate cart
    cart_items = session.get('cart', [])
    cart_total = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template("checkout.html", cart_items=cart_items, cart_total=cart_total)

@app.route('/about')
def about():
    return render_template('about.html', categories=CATEGORIES)

@app.route('/contact')
def contact():
    return render_template('contact.html', categories=CATEGORIES)


if __name__ == '__main__':
    app.run(port=8000)

