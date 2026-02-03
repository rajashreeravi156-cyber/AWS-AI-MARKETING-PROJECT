import os
import boto3
import json
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key')

# Simple "Database" for Campaigns
CAMPAIGNS = [
    {"name": "Winter Clearance", "budget": "2000", "audience": "Bargain Hunters", "description": "End of season sale.", "status": "Completed", "date": "2023-12-01"},
    {"name": "Product Launch V2", "budget": "5000", "audience": "Tech Enthusiasts", "description": "New features announcement.", "status": "Active", "date": "2024-02-15"}
]

# Gemini Setup
try:
    import google.generativeai as genai
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini not available")

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return jsonify({'message': 'Account created (Mock)!'})
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        session['user'] = data.get('email')
        return jsonify({'message': 'Login successful'})
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if session.get('is_admin'):
        return render_template('dashboard.html')
    if 'user' in session:
        return redirect(url_for('about'))
    return redirect(url_for('login'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json()
        if data.get('username') == 'ADMIN_AWS' and data.get('password') == 'AWS@Admin123':
            session['is_admin'] = True
            return jsonify({'message': 'Admin Access Granted'})
        return jsonify({'error': 'Invalid Credentials'}), 401
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return redirect(url_for('dashboard'))

# --- CAMPAIGN FEATURES ---

@app.route('/new_campaign')
def new_campaign():
    if not session.get('is_admin'): return redirect(url_for('login'))
    return render_template('new_campaign.html')

@app.route('/campaign_history')
def campaign_history():
    if not session.get('is_admin'): return redirect(url_for('login'))
    return render_template('campaign_history.html', campaigns=CAMPAIGNS)

@app.route('/api/save_campaign', methods=['POST'])
def save_campaign():
    data = request.json
    # Add metadata
    data['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    data['status'] = "Active"
    CAMPAIGNS.insert(0, data) # Add to top of list
    return jsonify({'message': 'Campaign Saved'})

@app.route('/api/generate_campaign_idea', methods=['POST'])
def generate_campaign_idea():
    name = request.json.get('name')
    print(f"🤖 Generating strategy for: {name}")

    mock_data = {
        "description": f"Launch a high-impact digital campaign for '{name}' focusing on user engagement and conversion optimization.",
        "audience": "Tech Enthusiasts, Early Adopters, Professionals (25-45)",
        "budget": "5000"
    }

    if GEMINI_AVAILABLE:
        try:
            prompt = f"Act as a marketing expert. For the product/campaign '{name}', provide a JSON with fields: description (short strategy summary), audience (target demographics), budget (just a number suggestion). No markdown."
            response = model.generate_content(prompt)
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return jsonify(json.loads(clean_text))
        except Exception as e:
            print(f"⚠️ AI Failed: {e}")
            return jsonify(mock_data)
    
    return jsonify(mock_data)

# --- PRODUCT FEATURES ---

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/api/generate_product_data', methods=['POST'])
def generate_product_data():
    name = request.json.get('product_name')
    mock_data = {
        "price": 199.99,
        "description": f"Premium quality {name} for professionals.",
        "category": "Electronics",
        "tags": "new, premium, best-seller"
    }
    # (Simplified for brevity - assumes same logic as before)
    return jsonify(mock_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
