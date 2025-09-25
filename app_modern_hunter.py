import streamlit as st
import pandas as pd
import requests
import os
import re
from typing import List, Dict, Optional
import time

st.set_page_config(
    page_title="Modern Toronto Business Lead Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyC-xCp_QpinGywzYj8TcC_DPPwOfvxXlxE"
HUNTER_API_KEY = "a1023549c94df1b7ed093d7ae2f007d115930954"

# Custom CSS for modern digital website styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: #64748b;
        font-size: 1.2rem;
        font-weight: 400;
        margin: 0;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Cards and containers */
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.5);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Data table styling */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Progress and loading */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
    }
    
    /* Sidebar header */
    .sidebar .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Stats cards */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        flex: 1;
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.5);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #64748b;
        font-weight: 500;
        font-size: 1rem;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(145deg, #f0f9ff, #e0f2fe);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid #0ea5e9;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.1);
    }
    
    /* Hunter.io status box */
    .hunter-status {
        background: linear-gradient(145deg, #f0fdf4, #dcfce7);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid #22c55e;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.1);
    }
    
    /* Business cards for card view */
    .business-card {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .business-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    }
    
    .business-name {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .business-info {
        color: #64748b;
        margin: 0.3rem 0;
        font-size: 0.95rem;
    }
    
    .business-info strong {
        color: #374151;
        font-weight: 600;
    }
    
    .contact-info {
        background: linear-gradient(145deg, #f8fafc, #f1f5f9);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 3px solid #667eea;
    }
    
    .email-info {
        background: linear-gradient(145deg, #f0fdf4, #dcfce7);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #22c55e;
    }
    
    .flag-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .flag-delivery {
        background: linear-gradient(145deg, #dcfce7, #bbf7d0);
        color: #166534;
        border: 1px solid #22c55e;
    }
    
    .flag-worldwide {
        background: linear-gradient(145deg, #dbeafe, #bfdbfe);
        color: #1e40af;
        border: 1px solid #3b82f6;
    }
    
    .flag-logistics {
        background: linear-gradient(145deg, #fef3c7, #fde68a);
        color: #92400e;
        border: 1px solid #f59e0b;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        .stats-container {
            flex-direction: column;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from website URL - simplified version"""
    if not url:
        return None
    
    # Simple domain extraction - just remove protocol and www
    domain = url.lower()
    
    # Remove protocol
    if domain.startswith('http://'):
        domain = domain[7:]
    elif domain.startswith('https://'):
        domain = domain[8:]
    
    # Remove www prefix
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Remove path and query parameters
    domain = domain.split('/')[0].split('?')[0]
    
    return domain if domain else None

def fetch_hunter_emails(domain: str) -> Dict[str, Optional[str]]:
    """Fetch verified emails from Hunter.io API with rate limiting"""
    try:
        # Add delay to avoid rate limiting
        time.sleep(2)  # 2 second delay between requests
        
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            'domain': domain,
            'api_key': HUNTER_API_KEY,
            'limit': 3  # Get up to 3 emails
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # Check for rate limiting
        if response.status_code == 429:
            st.warning(f"Rate limit reached for Hunter.io. Skipping {domain}")
            return {'email': None, 'contact_role': None}
        
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data', {}).get('emails'):
            emails = data['data']['emails']
            
            # Extract email addresses and roles
            email_list = []
            roles = []
            
            for email_data in emails[:3]:  # Max 3 emails
                email_value = email_data.get('value')
                if email_value:
                    email_list.append(email_value)
                    
                    # Extract position/role
                    position = email_data.get('position')
                    if position:
                        roles.append(position)
            
            # Combine emails and roles
            combined_emails = ', '.join(email_list) if email_list else None
            combined_roles = ', '.join(roles) if roles else None
            
            return {
                'email': combined_emails,
                'contact_role': combined_roles
            }
        else:
            return {'email': None, 'contact_role': None}
            
    except requests.exceptions.RequestException as e:
        if "429" in str(e):
            st.warning(f"Rate limit reached for {domain}. Skipping...")
        else:
            st.warning(f"Hunter.io API error for {domain}: {str(e)}")
        return {'email': None, 'contact_role': None}
    except Exception as e:
        st.warning(f"Error fetching Hunter.io data for {domain}: {str(e)}")
        return {'email': None, 'contact_role': None}

def geocode_location(location: str) -> Optional[Dict[str, float]]:
    """Get coordinates for location"""
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": location, "key": GOOGLE_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"]}
    except Exception:
        pass
    return None

def fetch_place_details(place_id: str) -> Dict[str, Optional[str]]:
    """Fetch detailed information from Google Places Details API"""
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        fields = "formatted_phone_number,international_phone_number,website,types,formatted_address,email"
        params = {
            "place_id": place_id,
            "fields": fields,
            "key": GOOGLE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json().get("result", {}) if response.ok else {}
        
        return {
            "phone": data.get("formatted_phone_number") or data.get("international_phone_number"),
            "website": data.get("website"),
            "email": data.get("email"),
            "types": data.get("types", []),
            "address": data.get("formatted_address")
        }
    except Exception:
        return {"phone": None, "website": None, "email": None, "types": [], "address": None}

def classify_business_flags(name: str, types: List[str], category: str = "") -> Dict[str, bool]:
    """Classify business based on name, types, and category"""
    text = f"{name} {' '.join(types)} {category}".lower()
    
    likely_delivery = any(keyword in text for keyword in [
        'store', 'retail', 'shop', 'ecommerce', 'online', 'supermarket', 'market'
    ])
    
    potential_worldwide = any(keyword in text for keyword in [
        'import', 'export', 'wholesale', 'distributor', 'global', 'international', 'worldwide'
    ])
    
    is_logistics = any(keyword in text for keyword in [
        'logistics', 'freight', 'shipping', 'courier', '3pl', 'forwarder', 'transport'
    ])
    
    return {
        "likely_delivery": likely_delivery,
        "potential_worldwide_shipping": potential_worldwide,
        "is_logistics": is_logistics
    }

def fetch_places_data(query: str, location: str, max_results: int = 20) -> List[Dict]:
    """Fetch business data from Google Places API with enhanced details"""
    businesses = []
    
    try:
        # Get location coordinates
        coords = geocode_location(location)
        
        # Text search
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': GOOGLE_API_KEY,
            'location': f"{coords['lat']},{coords['lng']}" if coords else "43.6532,-79.3832",
            'radius': '50000'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'OK':
            st.error(f"Google Places API error: {data.get('error_message', 'Unknown error')}")
            return businesses
        
        # Process each place
        for place in data.get('results', [])[:max_results]:
            place_id = place.get('place_id')
            if not place_id:
                continue
            
            # Get detailed information
            details = fetch_place_details(place_id)
            
            # Classify business
            flags = classify_business_flags(
                place.get('name', ''),
                details.get('types', []),
                ', '.join(place.get('types', []))
            )
            
            business = {
                'name': place.get('name', ''),
                'category': ', '.join(place.get('types', [])),
                'phone': details.get('phone', ''),
                'email': details.get('email'),  # From Google Places Details
                'contact_role': None,  # Will be filled by Hunter.io if needed
                'address': details.get('address') or place.get('formatted_address', ''),
                'website': details.get('website', ''),
                'url': f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                'rating': place.get('rating', 0.0),
                'review_count': place.get('user_ratings_total', 0),
                **flags
            }
            
            businesses.append(business)
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
    
    return businesses

def enrich_with_hunter_emails(businesses: List[Dict]) -> List[Dict]:
    """Enrich businesses with Hunter.io verified emails"""
    enriched_businesses = []
    hunter_stats = {'processed': 0, 'emails_found': 0, 'errors': 0}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, business in enumerate(businesses):
        status_text.text(f"Enriching with Hunter.io: {business['name']}")
        
        # Only use Hunter.io if we don't already have an email from Google Places
        if not business.get('email') and business.get('website'):
            domain = extract_domain_from_url(business['website'])
            if domain:
                hunter_stats['processed'] += 1
                hunter_data = fetch_hunter_emails(domain)
                
                if hunter_data['email']:
                    business['email'] = hunter_data['email']
                    business['contact_role'] = hunter_data['contact_role']
                    hunter_stats['emails_found'] += 1
                else:
                    hunter_stats['errors'] += 1
        
        enriched_businesses.append(business)
        progress_bar.progress((i + 1) / len(businesses))
    
    progress_bar.empty()
    status_text.empty()
    
    # Display Hunter.io stats
    st.markdown(f"""
    <div class="hunter-status">
        <h4>📧 Hunter.io Enrichment Results</h4>
        <p><strong>Domains Processed:</strong> {hunter_stats['processed']}</p>
        <p><strong>Emails Found:</strong> {hunter_stats['emails_found']}</p>
        <p><strong>Success Rate:</strong> {(hunter_stats['emails_found']/max(hunter_stats['processed'], 1)*100):.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    return enriched_businesses

def display_business_cards(businesses: List[Dict]):
    """Display businesses as modern cards"""
    for i, business in enumerate(businesses):
        # Flags
        flags_html = ""
        if business.get('likely_delivery'):
            flags_html += '<span class="flag-badge flag-delivery">📦 Delivery</span>'
        if business.get('potential_worldwide_shipping'):
            flags_html += '<span class="flag-badge flag-worldwide">🌍 Worldwide</span>'
        if business.get('is_logistics'):
            flags_html += '<span class="flag-badge flag-logistics">🚚 Logistics</span>'
        
        # Contact info
        contact_html = ""
        if business.get('phone'):
            contact_html += f'<p class="business-info"><strong>📞 Phone:</strong> {business["phone"]}</p>'
        if business.get('website'):
            contact_html += f'<p class="business-info"><strong>🌐 Website:</strong> <a href="{business["website"]}" target="_blank">{business["website"]}</a></p>'
        
        # Email info (highlighted if available)
        email_html = ""
        if business.get('email'):
            role_text = f" ({business['contact_role']})" if business.get('contact_role') else ""
            email_html = f"""
            <div class="email-info">
                <p class="business-info"><strong>✉️ Verified Email:</strong> {business['email']}{role_text}</p>
            </div>
            """
        
        st.markdown(f"""
        <div class="business-card">
            <div class="business-name">{business['name']}</div>
            <p class="business-info"><strong>📦 Category:</strong> {business.get('category', 'N/A')}</p>
            <p class="business-info"><strong>📍 Address:</strong> {business.get('address', 'N/A')}</p>
            <div class="contact-info">
                {contact_html}
            </div>
            {email_html}
            <p class="business-info"><strong>⭐ Rating:</strong> {business.get('rating', 'N/A')} ({business.get('review_count', 0)} reviews)</p>
            <div style="margin-top: 1rem;">
                {flags_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Load custom CSS
    load_custom_css()
    
    # Header with modern styling
    st.markdown("""
    <div class="main-container">
        <div class="main-header">
            <h1>🚀 Modern Toronto Business Lead Generator</h1>
            <p>Enhanced with contemporary digital website styling and Hunter.io email enrichment</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for filters
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🔍 Search Filters</div>', unsafe_allow_html=True)
        
        # Search term
        search_term = st.text_input(
            "Search Term",
            placeholder="e.g., 'electronics', 'auto parts', 'beauty'",
            help="Enter keywords to search for specific business types"
        )
        
        # Business focus selection
        business_focus = st.multiselect(
            "Business Focus",
            options=[
                "Importers",
                "Distributors / Wholesalers", 
                "Suppliers / Manufacturers",
                "Fulfillment / 3PL",
                "Logistics & Freight",
                "E-commerce / Online Retail",
            ],
            default=["Distributors / Wholesalers", "Suppliers / Manufacturers", "Logistics & Freight"],
            help="Select the types of businesses you want to find"
        )
        
        # Location
        location = st.text_input("Location", value="Toronto, ON")
        
        # Number of results
        max_results = st.slider(
            "Number of Results",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
            help="Maximum number of businesses to return"
        )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            enrich_emails = st.checkbox("Enrich with Hunter.io (emails)", value=False, help="Get verified emails from Hunter.io API. Note: May hit rate limits with free tier.")
            show_ratings = st.checkbox("Show ratings & reviews", value=True)
        
        # Search button
        search_button = st.button("🔍 Search Businesses", type="primary")
    
    # Main content area
    if search_button:
        if not business_focus:
            st.error("Please select at least one business focus.")
            return
        
        # Show loading spinner with custom message
        with st.spinner("🔍 Searching for businesses..."):
            try:
                # Build search queries
                queries = []
                focus_keywords = {
                    "Importers": ["importer", "import company"],
                    "Distributors / Wholesalers": ["distributor", "wholesale", "wholesaler"],
                    "Suppliers / Manufacturers": ["supplier", "manufacturer", "factory"],
                    "Fulfillment / 3PL": ["fulfillment center", "3pl", "order fulfillment"],
                    "Logistics & Freight": ["logistics", "freight", "shipping company", "forwarder"],
                    "E-commerce / Online Retail": ["ecommerce", "online store", "online retailer"]
                }
                
                for focus in business_focus:
                    keywords = focus_keywords.get(focus, [])
                    for keyword in keywords:
                        if search_term:
                            queries.append(f"{keyword} {search_term} in {location}")
                        else:
                            queries.append(f"{keyword} in {location}")
                
                # Remove duplicates
                queries = list(set(queries))
                
                all_businesses = []
                seen_places = set()
                
                # Progress bar for Google Places search
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, query in enumerate(queries):
                    status_text.text(f"Searching Google Places: {query}")
                    businesses = fetch_places_data(query, location, max_results)
                    
                    for business in businesses:
                        place_id = business.get('url', '').split('place_id:')[-1]
                        if place_id not in seen_places:
                            seen_places.add(place_id)
                            all_businesses.append(business)
                    
                    progress_bar.progress((i + 1) / len(queries))
                
                progress_bar.empty()
                status_text.empty()
                
                if not all_businesses:
                    st.info("No companies found. Try different keywords or business focus.")
                    return
                
                # Enrich with Hunter.io if enabled
                if enrich_emails:
                    st.info("📧 Enriching with Hunter.io verified emails...")
                    all_businesses = enrich_with_hunter_emails(all_businesses)
                
                # Results Header
                st.markdown(f"""
                <div class="main-container">
                    <h2 style="text-align: center; margin-bottom: 2rem; 
                               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                               font-size: 2.5rem; font-weight: 700;">
                        📊 Found {len(all_businesses)} Businesses
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Statistics cards
                delivery_count = sum(1 for b in all_businesses if b.get('likely_delivery'))
                worldwide_count = sum(1 for b in all_businesses if b.get('potential_worldwide_shipping'))
                logistics_count = sum(1 for b in all_businesses if b.get('is_logistics'))
                email_count = sum(1 for b in all_businesses if b.get('email'))
                
                st.markdown(f"""
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-number">{len(all_businesses)}</div>
                        <div class="stat-label">Total Businesses</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{delivery_count}</div>
                        <div class="stat-label">Delivery Ready</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{worldwide_count}</div>
                        <div class="stat-label">Worldwide Shipping</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{email_count}</div>
                        <div class="stat-label">With Emails</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display Options
                display_mode = st.radio(
                    "📋 Display Mode",
                    ["Cards View", "Table View"],
                    horizontal=True
                )
                
                if display_mode == "Cards View":
                    display_business_cards(all_businesses)
                else:
                    # Table View
                    df = pd.DataFrame(all_businesses)
                    
                    # Reorder columns
                    column_order = [
                        'name', 'category', 'phone', 'email', 'contact_role', 'address', 'website', 
                        'rating', 'review_count', 'likely_delivery', 
                        'potential_worldwide_shipping', 'is_logistics'
                    ]
                    
                    available_columns = [col for col in column_order if col in df.columns]
                    df_display = df[available_columns]
                    
                    st.dataframe(df_display, use_container_width=True, height=500)
                
                # Export functionality
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv_data = df_display.to_csv(index=False)
                    st.download_button(
                        "📥 Export to CSV",
                        data=csv_data,
                        file_name=f"toronto_businesses_modern_{int(time.time())}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Export companies with emails only
                    if st.button("📧 Export with Emails Only", use_container_width=True):
                        email_businesses = [b for b in all_businesses if b.get('email')]
                        if email_businesses:
                            df_emails = pd.DataFrame(email_businesses)
                            csv_emails = df_emails.to_csv(index=False)
                            st.download_button(
                                "📥 Download Emails CSV",
                                data=csv_emails,
                                file_name=f"toronto_businesses_with_emails_{int(time.time())}.csv",
                                mime="text/csv"
                            )
                
                with col3:
                    if st.button("🌍 Export Worldwide + Emails", use_container_width=True):
                        worldwide_businesses = [b for b in all_businesses if b.get('potential_worldwide_shipping') and b.get('email')]
                        if worldwide_businesses:
                            df_worldwide = pd.DataFrame(worldwide_businesses)
                            csv_worldwide = df_worldwide.to_csv(index=False)
                            st.download_button(
                                "📥 Download Worldwide CSV",
                                data=csv_worldwide,
                                file_name=f"toronto_worldwide_with_emails_{int(time.time())}.csv",
                                mime="text/csv"
                            )
                
                # Information box with modern styling
                st.markdown("""
                <div class="info-box">
                    <strong>🌍 Google Places API + Hunter.io</strong><br>
                    This app fetches real business data from Google Places API and enriches it with verified emails from Hunter.io. 
                    All contact information is verified and ready for B2B outreach.
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()
