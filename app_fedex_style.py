import streamlit as st
import pandas as pd
import requests
import os
import re
import time
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Toronto B2B Lead Generator",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyC-xCp_QpinGywzYj8TcC_DPPwOfvxXlxE"
HUNTER_API_KEY = "a1023549c94df1b7ed093d7ae2f007d115930954"

# FedEx-style CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    background: #f8fafc;
    color: #1e293b;
    line-height: 1.6;
}

/* Main app styling */
.stApp {
    background: #f8fafc;
}

.stApp > div {
    background: transparent;
}

/* Sidebar styling - FedEx style */
.css-1d391kg {
    background: white !important;
    border-right: 1px solid #e2e8f0;
    box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    width: 280px !important;
    min-width: 280px !important;
}

/* Sidebar header */
.sidebar-header {
    background: linear-gradient(135deg, #4D148C 0%, #7B2CBF 100%);
    color: white;
    padding: 1.5rem;
    margin: -1rem -1rem 2rem -1rem;
    border-radius: 0 0 12px 12px;
    text-align: center;
}

.sidebar-header h2 {
    color: white !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    background: none !important;
    -webkit-background-clip: unset !important;
    -webkit-text-fill-color: unset !important;
}

/* Form sections */
.form-section {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.form-section h3 {
    color: #4D148C;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Form elements */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stTextArea > div > div > textarea {
    border: 2px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    background: white !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #4D148C !important;
    box-shadow: 0 0 0 3px rgba(77, 20, 140, 0.1) !important;
    outline: none !important;
}

/* Labels */
label {
    font-weight: 600 !important;
    color: #374151 !important;
    font-size: 0.9rem !important;
    margin-bottom: 0.5rem !important;
    font-family: 'Inter', sans-serif !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4D148C 0%, #7B2CBF 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(77, 20, 140, 0.2) !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(77, 20, 140, 0.3) !important;
}

/* Secondary button */
.secondary-btn {
    background: #f1f5f9 !important;
    color: #4D148C !important;
    border: 2px solid #e2e8f0 !important;
}

.secondary-btn:hover {
    background: #e2e8f0 !important;
    transform: translateY(-1px) !important;
}

/* Main content area */
.main-content {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
    margin: 1rem;
}

/* Header */
.main-header {
    text-align: center;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid #f1f5f9;
}

.main-header h1 {
    color: #4D148C !important;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    margin-bottom: 0.5rem !important;
    background: none !important;
    -webkit-background-clip: unset !important;
    -webkit-text-fill-color: unset !important;
    font-family: 'Inter', sans-serif !important;
}

.main-header p {
    color: #64748b !important;
    font-size: 1.1rem !important;
    font-weight: 400 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Stats cards */
.stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.stat-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    color: #4D148C;
    margin-bottom: 0.5rem;
    font-family: 'Inter', sans-serif;
}

.stat-label {
    color: #64748b;
    font-weight: 500;
    font-size: 0.9rem;
    font-family: 'Inter', sans-serif;
}

/* Data table */
.dataframe {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
    margin: 1.5rem 0;
    font-family: 'Inter', sans-serif;
}

.dataframe th {
    background: #4D148C !important;
    color: white !important;
    padding: 1rem !important;
    text-align: left !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
}

.dataframe td {
    padding: 1rem !important;
    border-bottom: 1px solid #f1f5f9 !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
}

.dataframe tr:hover {
    background: #f8fafc !important;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
}

.badge-success {
    background: #dcfce7;
    color: #166534;
}

.badge-warning {
    background: #fef3c7;
    color: #92400e;
}

.badge-info {
    background: #dbeafe;
    color: #1e40af;
}

/* Business cards */
.business-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
}

.business-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.business-name {
    font-size: 1.2rem;
    font-weight: 700;
    color: #4D148C;
    margin-bottom: 0.5rem;
    font-family: 'Inter', sans-serif;
}

.business-category {
    color: #64748b;
    font-size: 0.9rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
    font-family: 'Inter', sans-serif;
}

.business-details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: #64748b;
    font-family: 'Inter', sans-serif;
}

/* Export button */
.export-btn {
    background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(255, 102, 0, 0.2) !important;
    margin: 1rem auto !important;
    display: block !important;
}

.export-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(255, 102, 0, 0.3) !important;
}

/* Info box */
.info-box {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 1px solid #0ea5e9;
    border-radius: 12px;
    padding: 1.25rem;
    margin: 1.5rem 0;
    font-family: 'Inter', sans-serif;
}

.info-box strong {
    color: #0ea5e9;
    font-weight: 600;
}

/* Checkbox styling */
.stCheckbox > label {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Slider styling */
.stSlider > div > div > div > div {
    background: #4D148C !important;
}

/* Toggle buttons */
.toggle-container {
    display: flex;
    background: #f1f5f9;
    border-radius: 8px;
    padding: 0.25rem;
    margin: 1rem 0;
}

.toggle-btn {
    flex: 1;
    padding: 0.5rem 1rem;
    border: none;
    background: transparent;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: 'Inter', sans-serif;
}

.toggle-btn.active {
    background: #4D148C;
    color: white;
}

.toggle-btn:hover:not(.active) {
    background: #e2e8f0;
}

/* Responsive design */
@media (max-width: 768px) {
    .stats-container {
        grid-template-columns: 1fr;
    }
    
    .main-header h1 {
        font-size: 2rem !important;
    }
    
    .business-details {
        grid-template-columns: 1fr;
    }
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Database functions
def init_database():
    conn = sqlite3.connect('toronto_leads.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            phone TEXT,
            email TEXT,
            email_source TEXT,
            website TEXT,
            domain TEXT,
            address TEXT,
            url TEXT,
            rating REAL,
            review_count INTEGER,
            likely_delivery BOOLEAN DEFAULT 0,
            potential_worldwide_shipping BOOLEAN DEFAULT 0,
            is_logistics BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_business_to_db(business):
    conn = sqlite3.connect('toronto_leads.db')
    cursor = conn.cursor()
    
    # Extract domain from website
    domain = None
    if business.get('website'):
        domain = business['website'].replace('http://', '').replace('https://', '').replace('www.', '')
        domain = domain.split('/')[0].split('?')[0]
    
    cursor.execute('''
        INSERT OR REPLACE INTO businesses 
        (name, category, phone, email, email_source, website, domain, address, url, 
         rating, review_count, likely_delivery, potential_worldwide_shipping, is_logistics, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        business.get('name'),
        business.get('category'),
        business.get('phone'),
        business.get('email'),
        business.get('email_source'),
        business.get('website'),
        domain,
        business.get('address'),
        business.get('url'),
        business.get('rating'),
        business.get('review_count', 0),
        business.get('likely_delivery', False),
        business.get('potential_worldwide_shipping', False),
        business.get('is_logistics', False),
        datetime.now()
    ))
    conn.commit()
    conn.close()

def load_businesses_from_db():
    conn = sqlite3.connect('toronto_leads.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM businesses ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    columns = ['id', 'name', 'category', 'phone', 'email', 'email_source', 'website', 'domain', 
               'address', 'url', 'rating', 'review_count', 'likely_delivery', 
               'potential_worldwide_shipping', 'is_logistics', 'created_at', 'updated_at']
    
    return [dict(zip(columns, row)) for row in rows]

def get_database_stats():
    conn = sqlite3.connect('toronto_leads.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM businesses')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE email IS NOT NULL')
    with_emails = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE likely_delivery = 1')
    with_delivery = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE potential_worldwide_shipping = 1')
    with_shipping = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total': total,
        'with_emails': with_emails,
        'with_delivery': with_delivery,
        'with_shipping': with_shipping
    }

# Google Places API functions
def geocode_location(location: str) -> Optional[Dict[str, float]]:
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        r = requests.get(url, params={"address": location, "key": GOOGLE_API_KEY}, timeout=12)
        data = r.json()
        if data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"]}
    except Exception:
        pass
    return None

def fetch_places_textsearch(query: str, loc_bias: Optional[Dict[str, float]] = None, max_results: int = 20):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_API_KEY}
    if loc_bias:
        params.update({"location": f'{loc_bias["lat"]},{loc_bias["lng"]}', "radius": 30000})
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])[:max_results]

def fetch_place_details(place_id: str) -> Dict[str, Optional[str]]:
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    fields = "formatted_phone_number,international_phone_number,website,types"
    r = requests.get(url, params={"place_id": place_id, "fields": fields, "key": GOOGLE_API_KEY}, timeout=15)
    data = r.json().get("result", {}) if r.ok else {}
    return {
        "phone": data.get("formatted_phone_number") or data.get("international_phone_number"),
        "website": data.get("website"),
        "types": data.get("types", [])
    }

def classify_flags(name: str, types: List[str], category_hint: str = "") -> Dict[str, bool]:
    n = (name or "").lower()
    t = " ".join(types or []).lower()
    h = (category_hint or "").lower()

    likely_delivery = any(k in (t + " " + n + " " + h)
                          for k in ["restaurant", "food", "grocery", "bakery", "pharmacy", "florist", "electronics", "clothing", "furniture"])

    potential_worldwide = any(k in (t + " " + n + " " + h)
                              for k in ["import", "export", "wholesale", "global", "international", "distributor", "shipping", "couriers", "mailbox", "post office", "logistics"])

    is_logistics = any(k in (t + " " + n + " " + h)
                       for k in ["logistics", "freight", "courier", "3pl", "forwarder", "shipping"])

    return {
        "likely_delivery": bool(likely_delivery),
        "potential_worldwide_shipping": bool(potential_worldwide),
        "is_logistics": bool(is_logistics)
    }

def maps_url(place_id: str) -> str:
    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"

# Email extraction
EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

def extract_email_from_website(website: str) -> Optional[str]:
    if not website:
        return None
    
    candidates = [website.rstrip("/")]
    for tail in ["/contact", "/contact-us", "/about", "/support"]:
        candidates.append(website.rstrip("/") + tail)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for url in candidates:
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            if not resp.ok:
                continue
            match = re.search(EMAIL_REGEX, resp.text, re.IGNORECASE)
            if match:
                return match.group(0)
        except Exception:
            continue
    return None

def enrich_with_hunter_io(website: str) -> Dict[str, Optional[str]]:
    if not website:
        return {"email": None, "contact_role": None}
    
    try:
        domain = website.replace('http://', '').replace('https://', '').replace('www.', '')
        domain = domain.split('/')[0].split('?')[0]
        
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            emails = data.get('data', {}).get('emails', [])
            if emails:
                email = emails[0].get('value')
                position = emails[0].get('position', '')
                return {"email": email, "contact_role": position}
        elif response.status_code == 429:
            st.warning("Hunter.io API quota exceeded. Using website scraping instead.")
        else:
            st.warning(f"Hunter.io API error: {response.status_code}")
    except Exception as e:
        st.warning(f"Hunter.io API error: {str(e)}")
    
    return {"email": None, "contact_role": None}

def display_business_cards(businesses: List[Dict]):
    """Display businesses as cards"""
    for i, business in enumerate(businesses):
        with st.container():
            st.markdown(f"""
            <div class="business-card">
                <div class="business-name">{business.get('name', 'N/A')}</div>
                <div class="business-category">{business.get('category', 'N/A')}</div>
                <div class="business-details">
                    <div><strong>📞 Phone:</strong> {business.get('phone', 'N/A')}</div>
                    <div><strong>📧 Email:</strong> {business.get('email', 'N/A')}</div>
                    <div><strong>🌐 Website:</strong> {business.get('website', 'N/A')}</div>
                    <div><strong>📍 Address:</strong> {business.get('address', 'N/A')}</div>
                    <div><strong>⭐ Rating:</strong> {business.get('rating', 'N/A')} ({business.get('review_count', 0)} reviews)</div>
                    <div><strong>🚚 Delivery:</strong> {'Yes' if business.get('likely_delivery') else 'No'}</div>
                    <div><strong>🌍 Shipping:</strong> {'Yes' if business.get('potential_worldwide_shipping') else 'No'}</div>
                    <div><strong>📦 Logistics:</strong> {'Yes' if business.get('is_logistics') else 'No'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def main():
    # Initialize database
    init_database()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🚚 Toronto B2B Lead Generator</h1>
        <p>Find and connect with Toronto businesses that need delivery or international shipping services</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with collapsible sections
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>🔍 Search Filters</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Search Section
        with st.expander("🔍 Search Options", expanded=True):
            search_term = st.text_input(
                "Search Term",
                placeholder="e.g., 'restaurant', 'pharmacy'",
                help="Enter keywords to search for specific business types"
            )
            
            location = st.text_input(
                "Location",
                value="Toronto, ON",
                help="City or area to search in"
            )
            
            max_results = st.slider(
                "Number of Results",
                min_value=10,
                max_value=100,
                value=20,
                step=10,
                help="Maximum number of results to return"
            )
        
        # Business Focus Section
        with st.expander("📦 Business Focus", expanded=True):
            business_categories = st.multiselect(
                "Business Categories",
                options=[
                    "Restaurant", "Grocery", "Pharmacy", "Florist", 
                    "Bakery", "Electronics", "Clothing", "Furniture",
                    "Logistics", "Shipping", "Courier", "3PL", "Wholesale",
                    "Distributor", "Import/Export", "E-commerce"
                ],
                default=["Restaurant", "Grocery", "Pharmacy"],
                help="Select business types to search for"
            )
        
        # Advanced Options Section
        with st.expander("⚙️ Advanced Options", expanded=False):
            data_source = st.selectbox(
                "Data Source",
                options=["Google Places API", "Demo Data"],
                index=0,
                help="Choose data source for business information"
            )
            
            enrich_emails = st.checkbox(
                "Enrich with Hunter.io (emails)",
                value=False,
                help="Get verified emails from Hunter.io API (may have rate limits)"
            )
            
            use_place_details = st.checkbox(
                "Use Place Details API",
                value=True,
                help="Get additional details like phone and website"
            )
        
        # Search button
        search_button = st.button("🔍 Search Businesses", type="primary")
    
    # Main content area
    if search_button:
        if data_source == "Demo Data":
            # Demo data
            demo_businesses = [
                {
                    "name": "Pizza Palace",
                    "category": "Restaurant",
                    "phone": "(416) 555-0123",
                    "email": "info@pizzapalace.com",
                    "website": "https://pizzapalace.com",
                    "address": "123 Main St, Toronto, ON",
                    "url": "https://maps.google.com/place1",
                    "rating": 4.2,
                    "review_count": 156,
                    "likely_delivery": True,
                    "potential_worldwide_shipping": False,
                    "is_logistics": False
                },
                {
                    "name": "Fresh Market Grocery",
                    "category": "Grocery",
                    "phone": "(416) 555-0456",
                    "email": "contact@freshmarket.com",
                    "website": "https://freshmarket.com",
                    "address": "456 Queen St, Toronto, ON",
                    "url": "https://maps.google.com/place2",
                    "rating": 4.0,
                    "review_count": 89,
                    "likely_delivery": True,
                    "potential_worldwide_shipping": False,
                    "is_logistics": False
                },
                {
                    "name": "TechWorld Electronics",
                    "category": "Electronics",
                    "phone": "(416) 555-0789",
                    "email": "sales@techworld.com",
                    "website": "https://techworld.com",
                    "address": "789 King St, Toronto, ON",
                    "url": "https://maps.google.com/place3",
                    "rating": 4.5,
                    "review_count": 234,
                    "likely_delivery": True,
                    "potential_worldwide_shipping": True,
                    "is_logistics": False
                },
                {
                    "name": "Global Logistics Inc",
                    "category": "Logistics",
                    "phone": "(416) 555-0321",
                    "email": "info@globallogistics.com",
                    "website": "https://globallogistics.com",
                    "address": "321 Bay St, Toronto, ON",
                    "url": "https://maps.google.com/place4",
                    "rating": 4.3,
                    "review_count": 78,
                    "likely_delivery": False,
                    "potential_worldwide_shipping": True,
                    "is_logistics": True
                }
            ]
            
            businesses = demo_businesses
            
        else:
            # Google Places API
            if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
                st.error("GOOGLE_API_KEY is missing. Set it in environment or replace placeholder in code.")
                return
            
            with st.spinner("Searching Google Places..."):
                try:
                    bias = geocode_location(location)
                    
                    raw = {}
                    for category in business_categories:
                        query = f"{category} in {location}"
                        if search_term:
                            query = f"{search_term} {category} in {location}"
                        
                        results = fetch_places_textsearch(query, bias, max_results)
                        
                        for place in results:
                            place_id = place.get("place_id")
                            if not place_id or place_id in raw:
                                continue
                            
                            base_types = place.get("types", [])
                            flags = classify_flags(place.get("name", ""), base_types, category)
                            
                            business = {
                                "name": place.get("name"),
                                "category": category,
                                "phone": None,
                                "email": None,
                                "website": None,
                                "address": place.get("formatted_address"),
                                "url": maps_url(place_id),
                                "rating": place.get("rating"),
                                "review_count": place.get("user_ratings_total", 0),
                                "place_id": place_id,
                                **flags
                            }
                            
                            # Get details if enabled
                            if use_place_details:
                                details = fetch_place_details(place_id)
                                business["phone"] = details.get("phone")
                                business["website"] = details.get("website")
                                
                                # Re-evaluate flags with more types
                                all_types = details.get("types", []) + base_types
                                flags = classify_flags(business["name"], all_types, category)
                                business.update(flags)
                            
                            # Email enrichment
                            if enrich_emails and business.get("website"):
                                hunter_result = enrich_with_hunter_io(business["website"])
                                business["email"] = hunter_result["email"]
                                business["contact_role"] = hunter_result["contact_role"]
                                business["email_source"] = "hunter"
                            elif business.get("website"):
                                # Fallback to website scraping
                                business["email"] = extract_email_from_website(business["website"])
                                business["email_source"] = "scraping"
                            
                            raw[place_id] = business
                    
                    businesses = list(raw.values())
                    
                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")
                    return
        
        if not businesses:
            st.info("No businesses found. Try different search terms or categories.")
            return
        
        # Display results
        st.markdown(f"### 📊 Found {len(businesses)} Businesses")
        
        # Stats cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(businesses)}</div>
                <div class="stat-label">Total Businesses</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            delivery_count = sum(1 for b in businesses if b.get("likely_delivery"))
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{delivery_count}</div>
                <div class="stat-label">Likely Delivery</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            shipping_count = sum(1 for b in businesses if b.get("potential_worldwide_shipping"))
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{shipping_count}</div>
                <div class="stat-label">Potential Shipping</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            email_count = sum(1 for b in businesses if b.get("email"))
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{email_count}</div>
                <div class="stat-label">With Emails</div>
            </div>
            """, unsafe_allow_html=True)
        
        # View toggle
        col1, col2 = st.columns([1, 4])
        with col1:
            view_mode = st.radio("View Mode", ["Cards", "Table"], horizontal=True)
        
        # Display results based on view mode
        if view_mode == "Cards":
            display_business_cards(businesses)
        else:
            # Table view
            df = pd.DataFrame(businesses)
            
            if not df.empty:
                # Format the dataframe for display
                display_columns = ["name", "category", "phone", "email", "website", "address", "rating", "review_count"]
                available_columns = [col for col in display_columns if col in df.columns]
                
                df_display = df[available_columns].copy()
                
                # Format rating column
                if "rating" in df_display.columns and "review_count" in df_display.columns:
                    df_display["rating"] = df_display.apply(
                        lambda row: f"⭐ {row['rating']:.1f} ({row['review_count']} reviews)" 
                        if pd.notna(row['rating']) else "No rating", axis=1
                    )
                    df_display = df_display.drop("review_count", axis=1)
                
                # Format flags
                if "likely_delivery" in df.columns:
                    df_display["Delivery"] = df["likely_delivery"].apply(
                        lambda x: '✓ Yes' if x else '✗ No'
                    )
                
                if "potential_worldwide_shipping" in df.columns:
                    df_display["Shipping"] = df["potential_worldwide_shipping"].apply(
                        lambda x: '✓ Yes' if x else '✗ No'
                    )
                
                # Display table
                st.dataframe(df_display, use_container_width=True, height=400)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save All to Database"):
                for business in businesses:
                    save_business_to_db(business)
                st.success(f"✅ Saved {len(businesses)} businesses to database!")
        
        with col2:
            if st.button("👁️ View Saved Records"):
                saved_businesses = load_businesses_from_db()
                if saved_businesses:
                    st.dataframe(pd.DataFrame(saved_businesses), use_container_width=True)
                else:
                    st.info("No saved records found.")
        
        with col3:
            # Export CSV
            csv_data = pd.DataFrame(businesses).to_csv(index=False)
            st.download_button(
                "📥 Export CSV",
                data=csv_data,
                file_name="toronto_business_leads.csv",
                mime="text/csv",
                key="export_csv"
            )
        
        # Info box
        if data_source == "Demo Data":
            st.markdown("""
            <div class="info-box">
                <strong>🚀 Demo Mode</strong><br>
                This is a demonstration version with sample data. 
                Switch to "Google Places API" to fetch real business data.
            </div>
            """, unsafe_allow_html=True)
    
    # Database stats
    stats = get_database_stats()
    if stats['total'] > 0:
        st.markdown("---")
        st.markdown("### 📊 Database Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Saved", stats['total'])
        
        with col2:
            st.metric("With Emails", stats['with_emails'])
        
        with col3:
            st.metric("Likely Delivery", stats['with_delivery'])
        
        with col4:
            st.metric("Potential Shipping", stats['with_shipping'])

if __name__ == "__main__":
    main()
