from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import os
import sys
import io
import qrcode

# Ensure backend folder is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.google_services import GoogleServices
from backend.data_models import FabricSpec

app = Flask(__name__)
app.secret_key = 'fabric-library-secret-key-2024'  # Change in production

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple user store (can be replaced with database)
USERS = {
    'user': {'password': 'user123', 'role': 'user'},
    'customer': {'password': 'scan123', 'role': 'customer'}
}

class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.role = role

@login_manager.user_loader
def load_user(username):
    if username in USERS:
        return User(username, USERS[username]['role'])
    return None

def user_required(f):
    """Decorator to require 'user' role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'user':
            flash('Access denied. User role required.')
            return redirect(url_for('mobile'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize Google Services
google_services = GoogleServices()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return redirect(url_for('index'))
        return redirect(url_for('mobile'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if username in USERS and USERS[username]['password'] == password:
            user = User(username, USERS[username]['role'])
            login_user(user)
            if user.role == 'user':
                return redirect(url_for('index'))
            return redirect(url_for('mobile'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
@user_required
def index():
    return render_template('dashboard.html')

@app.route('/mobile')
@login_required
def mobile():
    return render_template('mobile_scan.html')

@app.route('/api/fabrics')
def get_fabrics():
    # TODO: Implement caching or efficient fetching
    # For now, just fetching all data from the sheet "Fabric_List" (assuming that's the name)
    # You might need to adjust the sheet name
    try:
        # Open by Key using the ID found in legacy code
        SHEET_ID = "1QBHM2ybTvgZFRjduFdxZnOu4dR4p_xBKdR6LE5fNJT4"
        sheet_data = google_services.sheet_client.open_by_key(SHEET_ID)
        records = sheet_data.sheet1.get_all_records()
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add_fabric', methods=['POST'])
def add_fabric():
    data = request.json
    # Convert dict to FabricSpec object
    # This needs careful mapping depending on what the frontend sends
    try:
        new_fabric = FabricSpec(
            fabric_code=data.get('fabric_code'),
            supplier=data.get('supplier', ''),
            category=data.get('category', ''),
            composition=data.get('composition', ''),
            # Defaults for others
            moq=data.get('moq', ''),
            shade=data.get('shade', ''),
            weight=data.get('weight', ''),
            finish=data.get('finish', ''),
            width=data.get('width', ''),
            warp_shrink=data.get('warp_shrink', ''),
            weft_shrink=data.get('weft_shrink', ''),
            weave=data.get('weave', ''),
            stretch=data.get('stretch', ''),
            growth=data.get('growth', '')
        )
        
        # Open by Key using the SHEET_ID (reusing the one defined in get_fabrics scope ideally, but redefining for safety here)
        SHEET_ID = "1QBHM2ybTvgZFRjduFdxZnOu4dR4p_xBKdR6LE5fNJT4"
        
        # Ideally move this to a helper in google_services, but direct call works for now
        # We need to append the row. existing 'append_fabric_row' in google_services takes sheet_name, but we want ID.
        # Let's fix this inline for now.
        
        sheet = google_services.sheet_client.open_by_key(SHEET_ID).sheet1
        sheet.append_row(new_fabric.to_sheet_row())
        
        return jsonify({"message": "Fabric added successfully"}), 200
    except Exception as e:
        print(f"Error adding fabric: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/qr/<fabric_code>')
def generate_qr(fabric_code):
    """Generate a QR code image for a given fabric code."""
    try:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(fabric_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes buffer
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        return send_file(
            buf,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'{fabric_code}_QR.png'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible from other devices on the network
    app.run(debug=True, host='0.0.0.0', port=5000)
