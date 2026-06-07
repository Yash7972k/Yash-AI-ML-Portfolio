"""
E-Waste Management System - Streamlit Frontend (FIXED VERSION)
Complete rewrite with API-first architecture, proper error handling, and token validation
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import re
import time
from datetime import datetime
from enum import Enum

# ── API Configuration ─────────────────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000/api/v1"
API_TIMEOUT = 5

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Waste Management System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    
    .main-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #16a34a, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #16a34a;
        margin: 8px 0;
    }
    
    .high-priority { background: #fef2f2; border-left: 4px solid #ef4444; padding: 12px; border-radius: 8px; }
    .medium-priority { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 8px; }
    .low-priority { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 12px; border-radius: 8px; }
    
    .stButton>button {
        background: linear-gradient(135deg, #16a34a, #06b6d4) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        width: 100% !important;
    }
    
    .error-box { background: #fee2e2; border-left: 4px solid #ef4444; padding: 12px; border-radius: 8px; }
    .success-box { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 12px; border-radius: 8px; }
    .warning-box { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 8px; }
    .info-box { background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# UNIFIED API CLIENT - Single source of truth for all API calls
# ════════════════════════════════════════════════════════════════════════════════

class StreamlitAPIClient:
    """Centralized API client with error handling and token management"""
    
    def __init__(self, token=None):
        self.token = token
        self.base_url = API_URL
    
    def _get_headers(self):
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _handle_error(self, response, context=""):
        """Unified error handling"""
        try:
            error_data = response.json()
            detail = error_data.get("detail", "Unknown error")
        except:
            detail = response.text or "Unknown error"
        
        # Handle 401 - expired token
        if response.status_code == 401:
            st.session_state.authenticated = False
            st.session_state.token = None
            st.error("❌ Session expired. Please login again.")
            st.rerun()
        
        # Handle 403 - forbidden
        elif response.status_code == 403:
            return False, "Access denied. Admin privileges required."
        
        # Handle 404 - not found
        elif response.status_code == 404:
            return False, f"Resource not found: {detail}"
        
        # Handle 429 - rate limited
        elif response.status_code == 429:
            return False, "Too many requests. Please wait a moment."
        
        # Handle 422 - validation error
        elif response.status_code == 422:
            try:
                error_data = response.json()
                if "detail" in error_data and isinstance(error_data["detail"], list):
                    # Extract field validation errors
                    field_errors = []
                    for error in error_data["detail"]:
                        if "loc" in error and "msg" in error:
                            field = error["loc"][-1] if error["loc"] else "field"
                            msg = error["msg"]
                            field_errors.append(f"{field}: {msg}")
                    if field_errors:
                        return False, " | ".join(field_errors)
            except:
                pass
            return False, f"Validation error: {detail}"
        
        # Handle 500+ - server error
        elif response.status_code >= 500:
            return False, f"Server error: {detail}"
        
        # Generic error
        return False, f"{context}: {detail}"
    
    def register(self, name, email, phone, address, city, password):
        """Register new user"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json={
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "city": city,
                    "password": password
                },
                timeout=API_TIMEOUT
            )
            if response.status_code == 200 or response.status_code == 201:
                return True, "Registration successful! Please login."
            else:
                return self._handle_error(response, "Registration failed")
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to API server. Is it running on port 8000?"
        except requests.exceptions.Timeout:
            return False, "API request timed out. Please try again."
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def login(self, email, password):
        """Login user and get token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Login failed")
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to API server. Is it running on port 8000?"
        except requests.exceptions.Timeout:
            return False, "API request timed out. Please try again."
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def verify_token(self):
        """Verify current token is valid"""
        try:
            response = requests.get(
                f"{self.base_url}/auth/me",
                params={"token": self.token},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Token verification failed")
        except:
            return False, "Token verification error"
    
    def create_submission(self, data):
        """Create e-waste submission"""
        try:
            response = requests.post(
                f"{self.base_url}/submissions/",
                json=data,
                params={"token": self.token},  # Token as query parameter
                headers={"Content-Type": "application/json"},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200 or response.status_code == 201:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to create submission")
        except requests.exceptions.ConnectionError:
            return False, "Cannot reach API server"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_user_submissions(self, limit=100, offset=0):
        """Get current user's submissions"""
        try:
            response = requests.get(
                f"{self.base_url}/submissions/",
                params={"token": self.token, "limit": limit, "offset": offset},
                headers={"Content-Type": "application/json"},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to fetch submissions")
        except:
            return False, "Error fetching submissions"
    
    def get_all_submissions(self, limit=100, offset=0, status=None, priority=None):
        """Get all submissions (admin only)"""
        try:
            params = {"limit": limit, "offset": offset, "token": self.token}
            if status:
                params["status"] = status
            if priority:
                params["priority"] = priority
            
            response = requests.get(
                f"{self.base_url}/admin/submissions",
                params=params,
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to fetch submissions")
        except:
            return False, []
    
    def get_dashboard_analytics(self):
        """Get analytics dashboard data"""
        try:
            response = requests.get(
                f"{self.base_url}/analytics/dashboard",
                params={"token": self.token},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to fetch analytics")
        except:
            return False, {}
    
    def get_admin_stats(self):
        """Get admin system statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/admin/stats",
                params={"token": self.token},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to fetch stats")
        except:
            return False, {}
    
    def get_all_users(self, limit=100, offset=0):
        """Get all users (admin only)"""
        try:
            response = requests.get(
                f"{self.base_url}/admin/users",
                params={"token": self.token, "limit": limit, "offset": offset},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to fetch users")
        except:
            return False, []
    
    def update_user(self, user_id, is_active=None, is_admin=None):
        """Update user status/role (admin only)"""
        try:
            updates = {}
            if is_active is not None:
                updates["is_active"] = is_active
            if is_admin is not None:
                updates["is_admin"] = is_admin
            
            response = requests.patch(
                f"{self.base_url}/admin/users/{user_id}",
                json=updates,
                params={"token": self.token},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to update user")
        except:
            return False, {}
    
    def update_submission_status(self, submission_id, status, priority=None):
        """Update submission status (admin only)"""
        try:
            updates = {"status": status}
            if priority:
                updates["priority"] = priority
            
            response = requests.patch(
                f"{self.base_url}/admin/submissions/{submission_id}",
                json=updates,
                params={"token": self.token},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to update submission")
        except:
            return False, {}
    
    def get_collection_points(self):
        """Get all collection points"""
        try:
            response = requests.get(
                f"{self.base_url}/collection-points",
                params={"token": self.token},
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                return True, response.json()
            else:
                return self._handle_error(response, "Failed to fetch collection points")
        except:
            return False, []

# ════════════════════════════════════════════════════════════════════════════════
# SESSION STATE & VALIDATION
# ════════════════════════════════════════════════════════════════════════════════

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.token = None
    st.session_state.is_admin = False
    st.session_state.last_submit_time = 0

def validate_session():
    """Validate current session and token"""
    if not st.session_state.authenticated:
        return False
    
    # Optional: Verify token is still valid (on each page load)
    # Uncomment to add stricter validation
    # client = StreamlitAPIClient(st.session_state.token)
    # success, data = client.verify_token()
    # if not success:
    #     st.session_state.authenticated = False
    #     st.error("Session expired. Please login again.")
    #     st.stop()
    
    return True

def prevent_double_submit():
    """Prevent accidental double submissions"""
    current_time = time.time()
    if current_time - st.session_state.last_submit_time < 1:
        st.warning("Please wait a moment before submitting again")
        return False
    st.session_state.last_submit_time = current_time
    return True

# ════════════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    """Validate phone number format - more flexible"""
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Accept formats:
    # +919876543210 (India with country code)
    # 919876543210 (India without +)
    # 9876543210 (10 digits only)
    # 91-9876543210 (with dash)
    
    # Must have at least 10 digits
    digits_only = re.sub(r'\D', '', cleaned)
    
    if len(digits_only) == 10:
        return True  # Valid 10-digit number
    elif len(digits_only) == 12 and digits_only.startswith('91'):
        return True  # Valid 91 + 10 digits
    elif len(digits_only) == 13 and cleaned.startswith('+91'):
        return True  # Valid +91 + 10 digits
    
    return False

def is_valid_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, "Password is strong"

# ════════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION PAGE (NOT LOGGED IN)
# ════════════════════════════════════════════════════════════════════════════════

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-title">♻️ E-Waste Management</div>', unsafe_allow_html=True)
        st.markdown("**Smart e-waste collection & environmental impact tracking**")
        st.markdown("---")
        
        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])
        
        # ── LOGIN TAB ─────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("### Welcome Back!")
            st.markdown("Login to access your e-waste submissions")
            
            login_email = st.text_input(
                "📧 Email",
                placeholder="your@email.com",
                key="login_email"
            )
            login_password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", use_container_width=True, key="login_btn"):
                    if not login_email or not login_email.strip():
                        st.error("❌ Please enter your email")
                    elif not login_password or not login_password.strip():
                        st.error("❌ Please enter your password")
                    elif not is_valid_email(login_email):
                        st.error("❌ Invalid email format")
                    else:
                        with st.spinner("Logging in..."):
                            client = StreamlitAPIClient()
                            success, result = client.login(login_email, login_password)
                            
                            if success:
                                st.session_state.authenticated = True
                                st.session_state.user_email = login_email
                                st.session_state.user_name = result.get("user_name", login_email)
                                st.session_state.token = result.get("access_token")
                                st.session_state.is_admin = result.get("is_admin", False)
                                st.success(f"✅ Welcome, {st.session_state.user_name}!")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {result}")
        
        # ── REGISTER TAB ──────────────────────────────────────────────────────
        with tab_register:
            st.markdown("### Create Account")
            st.markdown("Join our community to manage e-waste responsibly")
            
            reg_name = st.text_input(
                "👤 Full Name",
                placeholder="John Doe",
                key="reg_name"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                reg_email = st.text_input(
                    "📧 Email",
                    placeholder="your@email.com",
                    key="reg_email"
                )
            with col2:
                reg_phone = st.text_input(
                    "📱 Phone",
                    placeholder="+91-9876543210",
                    key="reg_phone",
                    help="Format: +91XXXXXXXXXX or 10 digits"
                )
            
            reg_address = st.text_input(
                "📍 Address",
                placeholder="Your street address",
                key="reg_address",
                help="Minimum 5 characters"
            )
            
            reg_city = st.text_input(
                "🏙️ City",
                value="Pune",
                placeholder="Pune",
                key="reg_city"
            )
            
            reg_password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Min 8 chars, 1 uppercase, 1 digit",
                key="reg_password"
            )
            reg_confirm = st.text_input(
                "🔒 Confirm Password",
                type="password",
                placeholder="Re-enter password",
                key="reg_confirm"
            )
            
            if st.button("Create Account", use_container_width=True, key="register_btn"):
                errors = []
                
                # Check each field individually
                if not reg_name or not reg_name.strip():
                    errors.append("❌ Full Name is required")
                if not reg_email or not reg_email.strip():
                    errors.append("❌ Email is required")
                if not reg_phone or not reg_phone.strip():
                    errors.append("❌ Phone is required")
                if not reg_address or not reg_address.strip():
                    errors.append("❌ Address is required (minimum 5 characters)")
                if not reg_city or not reg_city.strip():
                    errors.append("❌ City is required")
                if not reg_password or not reg_password.strip():
                    errors.append("❌ Password is required")
                if not reg_confirm or not reg_confirm.strip():
                    errors.append("❌ Confirm Password is required")
                
                # Only validate format if fields are filled
                if not errors:
                    if not is_valid_email(reg_email):
                        errors.append("❌ Invalid email format (example: user@example.com)")
                    if not is_valid_phone(reg_phone):
                        errors.append("❌ Invalid phone format (10 digits or +91XXXXXXXXXX)")
                    if len(reg_address) < 5:
                        errors.append("❌ Address must be at least 5 characters")
                    if reg_password and len(reg_password) < 8:
                        errors.append("❌ Password must be at least 8 characters")
                    if reg_password != reg_confirm:
                        errors.append("❌ Passwords don't match")
                
                if errors:
                    st.error("⚠️ Please fix the following:")
                    for error in errors:
                        st.write(error)
                else:
                    valid, msg = is_valid_password(reg_password)
                    if not valid:
                        st.warning(f"⚠️ {msg}")
                    
                    with st.spinner("Creating account..."):
                        client = StreamlitAPIClient()
                        success, msg = client.register(
                            name=reg_name,
                            email=reg_email,
                            phone=reg_phone,
                            address=reg_address,
                            city=reg_city,
                            password=reg_password
                        )
                        
                        if success:
                            st.success("✅ Account created! Please login.")
                            st.info("💡 Use your new credentials to login")
                        else:
                            st.error(f"❌ {msg}")
    
    st.stop()

# ════════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION (LOGGED IN USERS ONLY)
# ════════════════════════════════════════════════════════════════════════════════

# Validate session on each load
if not validate_session():
    st.error("❌ Please login first")
    st.stop()

# Initialize API client for authenticated user
api_client = StreamlitAPIClient(st.session_state.token)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Account")
    st.markdown(f"**Name:** {st.session_state.user_name}")
    st.markdown(f"**Email:** {st.session_state.user_email}")
    
    if st.session_state.is_admin:
        st.markdown("🔑 **Admin Access**", help="You have administrator privileges")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.token = None
        st.session_state.is_admin = False
        st.success("✅ Logged out successfully!")
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    st.markdown("**About**")
    st.markdown("""
    E-Waste Management System
    - Version 1.0.0
    - API: FastAPI
    - UI: Streamlit
    """)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">♻️ E-Waste Management System</div>', unsafe_allow_html=True)
st.markdown("**Smart e-waste collection, classification & environmental impact tracking | Pune**")

# ── Dynamic Tabs Based on Role ────────────────────────────────────────────────
if st.session_state.is_admin:
    tabs = st.tabs([
        "📝 Submit E-Waste",
        "📊 Dashboard",
        "📍 Collection Points",
        "📋 My Submissions",
        "👑 Admin Panel"
    ])
    tab1, tab2, tab3, tab4, admin_tab = tabs
else:
    tabs = st.tabs([
        "📝 Submit E-Waste",
        "📊 Dashboard",
        "📍 Collection Points",
        "📋 My Submissions"
    ])
    tab1, tab2, tab3, tab4 = tabs
    admin_tab = None

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1: SUBMIT E-WASTE
# ════════════════════════════════════════════════════════════════════════════════

with tab1:
    st.markdown("### 📝 Submit E-Waste for Collection")
    st.markdown("Fill in the details below to submit your e-waste")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Personal Information**")
        name = st.text_input("Your Name", placeholder="John Doe", key="submit_name")
        phone = st.text_input("Phone Number", placeholder="+91-9876543210", key="submit_phone")
        email = st.text_input("Email", placeholder="your@email.com", key="submit_email")
    
    with col2:
        st.markdown("**E-Waste Details**")
        item_type = st.selectbox(
            "E-Waste Type",
            ["Mobile Phone", "Laptop", "Desktop Computer", "Television",
             "Refrigerator", "Washing Machine", "Air Conditioner", "Printer", "Battery", "Other"],
            key="submit_item"
        )
        quantity = st.number_input("Quantity", min_value=1, max_value=100, value=1, key="submit_qty")
        condition = st.selectbox(
            "Condition",
            ["Working", "Partially Working", "Broken/Non-functional"],
            key="submit_condition"
        )
    
    st.markdown("---")
    address = st.text_area("Pickup Address", placeholder="123, Street Name, City, Postal Code", key="submit_address")
    
    # Load collection points
    success_cp, collection_points = api_client.get_collection_points()
    if success_cp and collection_points:
        cp_names = [cp["name"] for cp in collection_points]
        collection_point = st.selectbox("Preferred Collection Point", cp_names, key="submit_cp")
    else:
        collection_point = st.text_input("Collection Point", placeholder="Enter collection point", key="submit_cp")
    
    notes = st.text_area("Additional Notes (Optional)", placeholder="Any special handling instructions?", key="submit_notes", height=80)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("✅ Submit E-Waste Request", use_container_width=True, key="submit_btn"):
            # Validation
            errors = []
            if not all([name, phone, email, address, collection_point]):
                errors.append("Please fill all required fields")
            if email and not is_valid_email(email):
                errors.append("Invalid email format")
            if phone and not is_valid_phone(phone):
                errors.append("Invalid phone format")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            elif not prevent_double_submit():
                st.warning("⚠️ Please wait before submitting again")
            else:
                with st.spinner("Processing submission..."):
                    submission_data = {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "item_type": item_type,
                        "quantity": quantity,
                        "condition": condition,
                        "collection_point": collection_point,
                        "notes": notes if notes else None
                    }
                    
                    success, result = api_client.create_submission(submission_data)
                    
                    if success:
                        st.success(f"✅ Submission successful!")
                        st.markdown(f"**Your Request ID:** `{result.get('id', 'N/A')}`")
                        st.markdown(f"**Status:** {result.get('status', 'Pending')}")
                        st.balloons()
                        
                        # Show impact metrics
                        st.markdown("---")
                        st.markdown("### 🌍 Environmental Impact")
                        metric_cols = st.columns(4)
                        with metric_cols[0]:
                            st.metric("CO₂ Saved", f"{result.get('co2_saved', 0)} kg")
                        with metric_cols[1]:
                            st.metric("Weight", f"{result.get('weight_kg', 0)} kg")
                        with metric_cols[2]:
                            st.metric("Value", f"${result.get('recycle_value', 0)}")
                        with metric_cols[3]:
                            st.metric("Trees Saved", result.get('tree_equivalents', 0))
                    else:
                        st.error(f"❌ {result}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════

with tab2:
    st.markdown("### 📊 Dashboard & Analytics")
    
    if st.button("🔄 Refresh", key="refresh_dashboard"):
        st.rerun()
    
    with st.spinner("Loading analytics..."):
        success, analytics = api_client.get_dashboard_analytics()
        
        if success:
            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("📦 Total Submissions", analytics.get("total_submissions", 0))
            with col2:
                st.metric("🌱 CO₂ Saved (kg)", f"{analytics.get('total_co2_saved', 0):.1f}")
            with col3:
                st.metric("⚖️ Weight (kg)", f"{analytics.get('total_weight_kg', 0):.1f}")
            with col4:
                st.metric("💰 Value ($)", f"{analytics.get('total_recycle_value', 0):.0f}")
            with col5:
                st.metric("✅ Recycled", analytics.get("recycled_count", 0))
            
            st.markdown("---")
            st.info("📊 Real-time analytics data from API server")
        else:
            st.error(f"❌ {analytics}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3: COLLECTION POINTS
# ════════════════════════════════════════════════════════════════════════════════

with tab3:
    st.markdown("### 📍 E-Waste Collection Points")
    
    if st.button("🔄 Refresh", key="refresh_points"):
        st.rerun()
    
    with st.spinner("Loading collection points..."):
        success, points = api_client.get_collection_points()
        
        if success and points:
            # Display as table
            points_df = pd.DataFrame(points)
            st.markdown("**Active Collection Centers:**")
            st.dataframe(
                points_df[["name", "address", "city", "capacity", "status"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("ℹ️ No collection points available")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4: MY SUBMISSIONS
# ════════════════════════════════════════════════════════════════════════════════

with tab4:
    st.markdown("### 📋 Your E-Waste Submissions")
    st.markdown(f"Viewing submissions for: **{st.session_state.user_email}**")
    
    if st.button("🔄 Refresh", key="refresh_submissions"):
        st.rerun()
    
    with st.spinner("Loading submissions..."):
        success, submissions = api_client.get_user_submissions(limit=100)
        
        if success and submissions:
            st.markdown(f"**Total Submissions:** {len(submissions)}")
            st.markdown("---")
            
            for submission in submissions:
                with st.expander(f"📦 {submission.get('item_type')} - {submission.get('status')} ({submission.get('id')})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Status:** {submission.get('status')}")
                        st.markdown(f"**Priority:** {submission.get('priority')}")
                        st.markdown(f"**Quantity:** {submission.get('quantity')}")
                    
                    with col2:
                        st.markdown(f"**CO₂ Saved:** {submission.get('co2_saved', 0)} kg")
                        st.markdown(f"**Weight:** {submission.get('weight_kg', 0)} kg")
                        st.markdown(f"**Value:** ${submission.get('recycle_value', 0)}")
                    
                    with col3:
                        created = submission.get('created_at', 'N/A')
                        if created:
                            created_date = created.split('T')[0] if 'T' in created else created
                        else:
                            created_date = 'N/A'
                        st.markdown(f"**Created:** {created_date}")
                        st.markdown(f"**ID:** `{submission.get('id')}`")
        else:
            st.info("ℹ️ No submissions yet. Go to 'Submit E-Waste' tab to create one.")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5: ADMIN PANEL (ADMIN ONLY)
# ════════════════════════════════════════════════════════════════════════════════

if st.session_state.is_admin and admin_tab is not None:
    with admin_tab:
        st.markdown("### 👑 Admin Control Panel")
        st.markdown("**Manage users, submissions, and system statistics**")
        st.markdown("---")
        
        admin_subtabs = st.tabs(["📊 Statistics", "👥 Users", "📦 Submissions"])
        
        # ── ADMIN TAB 1: STATISTICS ──────────────────────────────────────────
        with admin_subtabs[0]:
            st.markdown("#### System Statistics")
            
            if st.button("🔄 Refresh Stats", key="refresh_stats"):
                st.rerun()
            
            with st.spinner("Loading system statistics..."):
                success, stats = api_client.get_admin_stats()
                
                if success:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("👥 Total Users", stats.get("total_users", 0))
                    col2.metric("📦 Submissions", stats.get("total_submissions", 0))
                    col3.metric("📍 Centers", stats.get("total_collection_points", 0))
                    col4.metric("🌱 CO₂ (kg)", f"{stats.get('total_co2_saved', 0):.0f}")
                    col5.metric("💰 Value ($)", f"{stats.get('total_recycle_value', 0):.0f}")
                    
                    st.markdown("---")
                    st.markdown("**Status Breakdown**")
                    status_data = stats.get("status_breakdown", {})
                    col1, col2, col3 = st.columns(3)
                    col1.metric("⏳ Pending", status_data.get("Pending", 0))
                    col2.metric("📦 Collected", status_data.get("Collected", 0))
                    col3.metric("✅ Recycled", status_data.get("Recycled", 0))
                else:
                    st.error(f"❌ {stats}")
        
        # ── ADMIN TAB 2: USER MANAGEMENT ─────────────────────────────────────
        with admin_subtabs[1]:
            st.markdown("#### User Management")
            
            if st.button("🔄 Refresh Users", key="refresh_users"):
                st.rerun()
            
            with st.spinner("Loading users..."):
                success, users = api_client.get_all_users()
                
                if success and users:
                    st.markdown(f"**Total Users:** {len(users)}")
                    
                    for idx, user in enumerate(users):
                        with st.expander(f"👤 {user.get('name')} ({user.get('email')})"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"**Email:** {user.get('email')}")
                                st.markdown(f"**Phone:** {user.get('phone')}")
                            
                            with col2:
                                is_admin = user.get('is_admin', False)
                                is_active = user.get('is_active', False)
                                st.markdown(f"**Admin:** {'🔑 Yes' if is_admin else '❌ No'}")
                                st.markdown(f"**Active:** {'✅ Yes' if is_active else '🚫 No'}")
                            
                            with col3:
                                new_admin = st.checkbox("Make Admin", value=is_admin, key=f"admin_{user.get('id')}")
                                new_active = st.checkbox("Active", value=is_active, key=f"active_{user.get('id')}")
                                
                                if st.button("Update", key=f"upd_user_{user.get('id')}"):
                                    success, msg = api_client.update_user(
                                        str(user.get('id')),
                                        is_active=new_active,
                                        is_admin=new_admin
                                    )
                                    if success:
                                        st.success("✅ User updated!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                else:
                    st.info("ℹ️ No users found")
        
        # ── ADMIN TAB 3: SUBMISSION MANAGEMENT ────────────────────────────────
        with admin_subtabs[2]:
            st.markdown("#### Submission Management")
            
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox("Status", ["All", "Pending", "Collected", "Recycled"], key="adm_status")
            with col2:
                priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"], key="adm_priority")
            
            if st.button("🔄 Refresh", key="refresh_subs"):
                st.rerun()
            
            with st.spinner("Loading submissions..."):
                stat_param = None if status_filter == "All" else status_filter
                pri_param = None if priority_filter == "All" else priority_filter
                
                success, subs = api_client.get_all_submissions(status=stat_param, priority=pri_param)
                
                if success and subs:
                    st.markdown(f"**Total Submissions:** {len(subs)}")
                    
                    for sub in subs:
                        with st.expander(f"📦 {sub.get('item_type')} - {sub.get('status')} ({sub.get('id')})"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"**Item:** {sub.get('item_type')}")
                                st.markdown(f"**Qty:** {sub.get('quantity')}")
                                st.markdown(f"**Priority:** {sub.get('priority')}")
                            
                            with col2:
                                st.markdown(f"**Status:** {sub.get('status')}")
                                st.markdown(f"**Hazard:** {sub.get('hazard_level')}")
                                st.markdown(f"**CO₂:** {sub.get('co2_saved')} kg")
                            
                            with col3:
                                new_status = st.selectbox(
                                    "Change Status",
                                    ["Pending", "Collected", "Recycled"],
                                    index=["Pending", "Collected", "Recycled"].index(sub.get('status', 'Pending')),
                                    key=f"new_stat_{sub.get('id')}"
                                )
                                
                                if st.button("Update Status", key=f"upd_sub_{sub.get('id')}"):
                                    success, msg = api_client.update_submission_status(
                                        sub.get('id'),
                                        new_status
                                    )
                                    if success:
                                        st.success("✅ Updated!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                else:
                    st.info("ℹ️ No submissions found")
