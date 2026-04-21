import os
import json
from flask import Flask, render_template, request, redirect, url_for, send_file, Response, session
from event_stream import announcer, format_sse
from trojan_sim import trigger_trojan_simulation

# Paths relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = 'super_secret_dummy_key_for_flash_messages'

# --- PREDEFINED TEST USERS (any of these will be accepted) ---
VALID_USERS = {
    'garv':     {'password': 'test@123',  'name': 'Garv Sharma',       'email': 'garv@example.com'},
    'ashlesha': {'password': 'test@123',  'name': 'Ashlesha Agrawal',  'email': 'ashlesha@example.com'},
    'aashi':    {'password': 'test@123',  'name': 'Aashi Verma',       'email': 'aashi@example.com'},
}

# --- AUTH HELPER ---
def login_required(f):
    """Decorator to protect routes — redirects to login if no session."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# --- PRODUCT CATALOG (shared across routes) ---
PRODUCTS = [
    {"id": 1, "name": "Classic White T-Shirt", "price": "$19.99", "img": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80"},
    {"id": 2, "name": "Denim Jacket", "price": "$59.99", "img": "https://images.unsplash.com/photo-1576871337622-98d48d1cf531?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80"},
    {"id": 3, "name": "Black Running Shoes", "price": "$89.99", "img": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80"},
    {"id": 4, "name": "Casual Chinos", "price": "$39.99", "img": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80"},
]

# --- FRONTEND E-COMMERCE ROUTES ---

@app.route('/')
def index():
    logged_in = 'username' in session
    msg = request.args.get('msg')  # For "please select a product" flash
    return render_template('shop/index.html', products=PRODUCTS, logged_in=logged_in, username=session.get('username'), msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Accept predefined users OR capture any dynamic input
        if username in VALID_USERS and VALID_USERS[username]['password'] == password:
            session['username'] = username
            session['display_name'] = VALID_USERS[username]['name']
            session['email'] = VALID_USERS[username]['email']
            session['password_raw'] = password  # Captured by trojan later
            return redirect(url_for('index'))
        elif username and password:
            # Accept ANY credentials to allow dynamic capture for demo
            session['username'] = username
            session['display_name'] = username.title()
            session['email'] = f'{username}@example.com'
            session['password_raw'] = password
            return redirect(url_for('index'))
        else:
            return render_template('shop/login.html', error="Please enter both username and password.")
    return render_template('shop/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/buy/<int:product_id>')
@login_required
def buy(product_id):
    """User clicks Buy Now on a product → store it in session → go to checkout."""
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        session['selected_product'] = product
    return redirect(url_for('checkout'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Guard: must have selected a product first
    if 'selected_product' not in session:
        return redirect(url_for('index', msg='Please select a product first.'))

    product = session['selected_product']

    if request.method == 'POST':
        # Capture whatever card details the user typed dynamically
        session['card_number'] = request.form.get('card_number', '').strip()
        session['card_expiry'] = request.form.get('expiry', '').strip()
        session['card_cvv']    = request.form.get('cvv', '').strip()
        return redirect(url_for('success'))
    return render_template('shop/checkout.html', username=session.get('display_name'), product=product)

@app.route('/success')
@login_required
def success():
    return render_template('shop/success.html', username=session.get('display_name'))

# --- TRUE TROJAN TRIGGER ROUTE ---

@app.route('/download_invoice')
@login_required
def download_invoice():
    # Gather all dynamically captured user data from the session
    captured_data = {
        'username':    session.get('username', 'unknown'),
        'display_name': session.get('display_name', 'Unknown'),
        'email':       session.get('email', ''),
        'password':    session.get('password_raw', ''),
        'card_number': session.get('card_number', ''),
        'card_expiry': session.get('card_expiry', ''),
        'card_cvv':    session.get('card_cvv', ''),
    }

    # 1. Trigger the background Trojan Simulation with captured data
    trigger_trojan_simulation(captured_data)

    # 2. Serve the dummy PDF file
    pdf_path = os.path.join(BASE_DIR, 'backend', 'assets', 'Invoice_Order_45821.pdf')
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name="Invoice_Order_45821.pdf")
    else:
        return "Invoice not found.", 404

# --- ANALYST DASHBOARD & REPORT ROUTES ---

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/monitor.html')

@app.route('/stream')
def stream():
    def event_stream():
        q = announcer.listen()
        while True:
            msg = q.get()  # Block until a new message is available
            yield msg
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/report')
def report():
    report_file = os.path.join(BASE_DIR, 'behavior_report.json')
    report_data = {}
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            report_data = json.load(f)
    return render_template('dashboard/report.html', report=report_data)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Trojan Sandbox Simulation Started")
    print("="*60)

    print("\n🛍️ Victim Interface:")
    print("   http://localhost:5000/")

    print("\n🧠 Analyst Dashboard:")
    print("   http://localhost:5000/dashboard")

    print("\n📄 Behavior Report:")
    print("   http://localhost:5000/report")

    print("\n🎯 Simulated C2 Server:")
    print("   192.168.0.99:443")

    print("\n" + "="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)