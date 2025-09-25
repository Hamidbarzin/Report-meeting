import streamlit as st
import pandas as pd
import requests
import os
import re
import time
from typing import List, Dict, Optional

# Page config
st.set_page_config(
    page_title="Toronto B2B Lead Generator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyC-xCp_QpinGywzYj8TcC_DPPwOfvxXlxE"
HUNTER_API_KEY = "a1023549c94df1b7ed093d7ae2f007d115930954"  # This key has reached quota limit

# Custom CSS for modern FedEx-style design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #4D148C 0%, #7B2CBF 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(77, 20, 140, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
    }
    
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #4D148C;
    }
    
    .sidebar-section h3 {
        color: #4D148C;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Stats Cards */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #4D148C;
        transition: transform 0.2s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #4D148C;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Business Cards - Simplified */
    .business-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 3px solid #4D148C;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4D148C 0%, #7B2CBF 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(77, 20, 140, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(77, 20, 140, 0.4);
    }
    
    /* Tables */
    .dataframe {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
    }
    
    .dataframe th {
        background: #4D148C;
        color: white;
        font-weight: 600;
        padding: 0.75rem;
    }
    
    .dataframe td {
        padding: 0.75rem;
        border-bottom: 1px solid #eee;
    }
    
    .dataframe tr:hover {
        background: #f8f9fa;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #4D148C 0%, #7B2CBF 100%);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        border-radius: 8px;
    }
    
    .stError {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        border-radius: 8px;
    }
    
    .stWarning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        border-radius: 8px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .stats-container {
            grid-template-columns: 1fr;
        }
        .business-info {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from website URL"""
    if not url:
        return None
    
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

def extract_email_from_website(website: str) -> Optional[str]:
    """Extract email from website using simple scraping"""
    try:
        if not website or not website.startswith(('http://', 'https://')):
            return None
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(website, headers=headers, timeout=10)
        if response.status_code == 200:
            # Look for common email patterns
            email_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                r'email["\']?\s*:\s*["\']?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            ]
            
            for pattern in email_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    # Return the first valid email
                    email = matches[0] if isinstance(matches[0], str) else matches[0]
                    if '@' in email and '.' in email.split('@')[1]:
                        return email
    except Exception:
        pass
    return None

def fetch_hunter_emails(domain: str) -> Dict[str, Optional[str]]:
    """Fetch verified emails from Hunter.io API with rate limiting"""
    try:
        # Add delay to avoid rate limiting
        time.sleep(1.5)  # 1.5 second delay between requests
        
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            'domain': domain,
            'api_key': HUNTER_API_KEY,
            'limit': 3
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # Check for rate limiting
        if response.status_code == 429:
            return {'email': None, 'contact_role': None}
        
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data', {}).get('emails'):
            emails = data['data']['emails']
            
            # Extract email addresses and roles
            email_list = []
            roles = []
            
            for email_data in emails[:3]:
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
            
    except Exception as e:
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
        fields = "formatted_phone_number,international_phone_number,website,types,formatted_address"
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
            "email": None,  # Google Places doesn't provide email
            "types": data.get("types", []),
            "address": data.get("formatted_address")
        }
    except Exception:
        return {"phone": None, "website": None, "email": None, "types": [], "address": None}

def classify_business_flags(name: str, types: List[str], category: str = "") -> Dict[str, bool]:
    """Classify business based on name, types, and category"""
    text = f"{name} {' '.join(types)} {category}".lower()
    
    likely_delivery = any(keyword in text for keyword in [
        'store', 'retail', 'shop', 'market', 'supermarket', 'grocery', 'pharmacy',
        'restaurant', 'food', 'bakery', 'cafe', 'ecommerce', 'online'
    ])
    
    potential_worldwide = any(keyword in text for keyword in [
        'import', 'export', 'wholesale', 'distributor', 'global', 'international',
        'shipping', 'logistics', 'freight', 'forwarder'
    ])
    
    is_logistics = any(keyword in text for keyword in [
        'logistics', 'freight', 'courier', 'shipping', 'transport', '3pl',
        'fulfillment', 'warehouse', 'supply chain'
    ])
    
    return {
        'likely_delivery': likely_delivery,
        'potential_worldwide_shipping': potential_worldwide,
        'is_logistics': is_logistics
    }

def fetch_places_data(search_term: str, business_focus: List[str], location: str, max_results: int = 20) -> List[Dict]:
    """Fetch real business data from Google Places API"""
    businesses = []
    
    try:
        # Get location coordinates
        coords = geocode_location(location)
        
        # Build search queries based on business focus
        focus_keywords = {
            "Importers": ["importer", "import"],
            "Distributors / Wholesalers": ["distributor", "wholesale", "wholesaler"],
            "Suppliers / Manufacturers": ["supplier", "manufacturer", "factory"],
            "Fulfillment / 3PL": ["fulfillment", "3pl", "warehouse"],
            "Logistics & Freight": ["logistics", "freight", "shipping"],
            "E-commerce / Online Retail": ["ecommerce", "online store", "retail"]
        }
        
        queries = []
        if search_term:
            queries.append(f"{search_term} in {location}")
        
        for focus in business_focus:
            keywords = focus_keywords.get(focus, [])
            for keyword in keywords:
                if search_term:
                    queries.append(f"{keyword} {search_term} in {location}")
                else:
                    queries.append(f"{keyword} in {location}")
        
        # Remove duplicates
        queries = list(dict.fromkeys(queries))
        
        # Fetch data for each query
        for query in queries[:3]:  # Limit to 3 queries to avoid rate limits
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "key": GOOGLE_API_KEY,
                "fields": "place_id,name,formatted_address,types,rating,user_ratings_total"
            }
            
            if coords:
                params["location"] = f"{coords['lat']},{coords['lng']}"
                params["radius"] = 50000  # 50km radius
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            places = data.get("results", [])[:max_results]
            
            for place in places:
                place_id = place.get("place_id")
                if not place_id:
                    continue
                
                # Get detailed information
                details = fetch_place_details(place_id)
                
                # Classify business flags
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

def enrich_with_emails(businesses: List[Dict]) -> List[Dict]:
    """Enrich businesses with emails from multiple sources"""
    enriched_businesses = []
    email_stats = {'processed': 0, 'emails_found': 0, 'hunter_errors': 0, 'scraping_errors': 0}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, business in enumerate(businesses):
        status_text.text(f"Enriching with emails: {business['name']}")
        
        # Try to get email if we don't have one
        if not business.get('email') and business.get('website'):
            email_stats['processed'] += 1
            
            # First try Hunter.io
            domain = extract_domain_from_url(business['website'])
            if domain:
                hunter_data = fetch_hunter_emails(domain)
                if hunter_data['email']:
                    business['email'] = hunter_data['email']
                    business['contact_role'] = hunter_data['contact_role']
                    business['email_source'] = 'Hunter.io'
                    email_stats['emails_found'] += 1
                else:
                    email_stats['hunter_errors'] += 1
                    
                    # If Hunter.io fails, try website scraping
                    scraped_email = extract_email_from_website(business['website'])
                    if scraped_email:
                        business['email'] = scraped_email
                        business['email_source'] = 'Website Scraping'
                        email_stats['emails_found'] += 1
                    else:
                        email_stats['scraping_errors'] += 1
        
        enriched_businesses.append(business)
        progress_bar.progress((i + 1) / len(businesses))
    
    progress_bar.empty()
    status_text.empty()
    
    # Display email stats
    if email_stats['processed'] > 0:
        st.markdown(f"""
        <div class="sidebar-section">
            <h4>📧 Email Enrichment Results</h4>
            <p><strong>Processed:</strong> {email_stats['processed']} websites</p>
            <p><strong>Emails Found:</strong> {email_stats['emails_found']}</p>
            <p><strong>Success Rate:</strong> {(email_stats['emails_found']/email_stats['processed']*100):.1f}%</p>
            <p><strong>Hunter.io Errors:</strong> {email_stats['hunter_errors']}</p>
            <p><strong>Scraping Errors:</strong> {email_stats['scraping_errors']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    return enriched_businesses

def display_business_cards(businesses: List[Dict]):
    """Display businesses as modern cards using Streamlit components"""
    for business in businesses:
        # Create columns for the card layout
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {business['name']}")
                st.markdown(f"*{business['category']}*")
            
            with col2:
                # Rating display
                if business.get('rating', 0) > 0:
                    st.markdown(f"**⭐ {business['rating']:.1f}** ({business['review_count']} reviews)")
            
            # Business information
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.markdown(f"**📍 Address:** {business['address']}")
                st.markdown(f"**📞 Phone:** {business['phone'] or 'N/A'}")
                if business.get('website'):
                    st.markdown(f"**🌐 Website:** [{business['website']}]({business['website']})")
                else:
                    st.markdown("**🌐 Website:** N/A")
            
            with info_col2:
                # Email display with better formatting
                email = business.get('email')
                if email:
                    st.markdown(f"**📧 Email:** `{email}`")
                    # Make email clickable
                    st.markdown(f"**📧 Email:** [📧 {email}](mailto:{email})")
                else:
                    st.markdown("**📧 Email:** ❌ Not Available")
                
                if business.get('url'):
                    st.markdown(f"**🔗 Maps:** [View on Google Maps]({business['url']})")
                
                # Flags
                flags = []
                if business.get('likely_delivery'):
                    flags.append("📦 Delivery")
                if business.get('potential_worldwide_shipping'):
                    flags.append("🌐 Worldwide")
                if business.get('is_logistics'):
                    flags.append("🚚 Logistics")
                
                if flags:
                    st.markdown(f"**Tags:** {', '.join(flags)}")
            
            # Add separator
            st.markdown("---")

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏭 Toronto B2B Lead Generator</h1>
        <p>Find importers, distributors, wholesalers, suppliers, fulfillment/3PL, logistics, and e-commerce companies in Toronto</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h3>🔍 Search Filters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        search_term = st.text_input(
            "Keywords (optional)",
            placeholder="e.g., electronics, auto parts, beauty, medical devices",
            help="Enter specific keywords to narrow your search"
        )
        
        st.markdown("""
        <div class="sidebar-section">
            <h3>📦 Business Focus</h3>
        </div>
        """, unsafe_allow_html=True)
        
        business_focus = st.multiselect(
            "Select business types",
            options=[
                "Importers",
                "Distributors / Wholesalers", 
                "Suppliers / Manufacturers",
                "Fulfillment / 3PL",
                "Logistics & Freight",
                "E-commerce / Online Retail"
            ],
            default=["Distributors / Wholesalers", "Suppliers / Manufacturers", "Logistics & Freight"],
            help="Choose the types of businesses you want to find"
        )
        
        location = st.text_input("Location", value="Toronto, ON", help="Enter the city or region to search in")
        
        max_results = st.slider(
            "Maximum results",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
            help="Maximum number of businesses to return"
        )
        
        st.markdown("""
        <div class="sidebar-section">
            <h3>⚙️ Advanced Options</h3>
        </div>
        """, unsafe_allow_html=True)
        
        enrich_emails = st.checkbox("Enrich with Hunter.io (emails)", value=True, 
                                  help="Get verified emails from Hunter.io API. Note: May hit rate limits with free tier.")
        show_ratings = st.checkbox("Show ratings & reviews", value=True)
        view_mode = st.radio("View Mode", ["Cards", "Table"], index=0)
        
        # Email priority explanation
        st.info("📧 **Email Sources:** 1) Google Places Details API 2) Hunter.io Domain Search (if enabled)")
        
        # Search button
        search_button = st.button("🔍 Search Businesses", type="primary")
    
    # Main content area
    if search_button:
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
            st.error("❌ GOOGLE_API_KEY is missing. Please set it in environment or replace placeholder in code.")
            return
        
        if not business_focus:
            st.warning("⚠️ Please select at least one business focus type.")
            return
        
        with st.spinner("🔍 Searching Google Places..."):
            businesses = fetch_places_data(search_term, business_focus, location, max_results)
        
        if not businesses:
            st.info("ℹ️ No businesses found. Try different keywords or business focus types.")
            return
        
        # Enrich with emails if enabled
        if enrich_emails and businesses:
            st.info("📧 Enriching with emails from Hunter.io and website scraping...")
            businesses = enrich_with_emails(businesses)
        elif businesses:
            # If email enrichment is disabled, show warning
            st.warning("⚠️ Email enrichment is disabled. Enable it to get email addresses.")
        
        # Display stats
        total_businesses = len(businesses)
        with_emails = sum(1 for b in businesses if b.get('email'))
        with_delivery = sum(1 for b in businesses if b.get('likely_delivery'))
        with_worldwide = sum(1 for b in businesses if b.get('potential_worldwide_shipping'))
        with_logistics = sum(1 for b in businesses if b.get('is_logistics'))
        
        # Email statistics
        email_sources = {'google': 0, 'hunter': 0}
        for b in businesses:
            if b.get('email'):
                # Check if email came from Google Places (has website) or Hunter.io
                if b.get('website') and not b.get('contact_role'):
                    email_sources['google'] += 1
                else:
                    email_sources['hunter'] += 1
        
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">{total_businesses}</div>
                <div class="stat-label">Total Businesses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{with_emails}</div>
                <div class="stat-label">With Emails</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{with_delivery}</div>
                <div class="stat-label">Delivery Ready</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{with_worldwide}</div>
                <div class="stat-label">Worldwide Shipping</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{with_logistics}</div>
                <div class="stat-label">Logistics Companies</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create DataFrame for export
        df = pd.DataFrame(businesses)
        
        # Reorder columns for better display
        column_order = [
            'name', 'category', 'phone', 'email', 'website', 'address',
            'rating', 'review_count', 'likely_delivery', 'potential_worldwide_shipping', 'is_logistics'
        ]
        available_columns = [col for col in column_order if col in df.columns]
        df_display = df[available_columns]
        
        # Rename columns for better readability
        df_display = df_display.rename(columns={
            'name': 'Business Name',
            'category': 'Category',
            'phone': 'Phone',
            'email': 'Email',
            'website': 'Website',
            'address': 'Address',
            'rating': 'Rating',
            'review_count': 'Reviews',
            'likely_delivery': 'Delivery',
            'potential_worldwide_shipping': 'Worldwide',
            'is_logistics': 'Logistics'
        })
        
        # Display results
        if view_mode == "Cards":
            display_business_cards(businesses)
        else:
            # Table view
            st.dataframe(df_display, use_container_width=True, height=600)
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df_display.to_csv(index=False)
            st.download_button(
                "📥 Export to CSV",
                data=csv_data,
                file_name="toronto_b2b_leads.csv",
                mime="text/csv",
                help="Download the results as a CSV file"
            )
        
        with col2:
            st.metric("Total Results", total_businesses)
        
        with col3:
            st.metric("With Emails", with_emails)
        
        # Email breakdown
        if with_emails > 0:
            st.markdown("### 📧 Email Breakdown")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📧 Total Emails", with_emails)
            
            with col2:
                st.metric("🌍 Google Places", email_sources['google'])
            
            with col3:
                st.metric("🔍 Hunter.io", email_sources['hunter'])
            
            # Email success rate
            email_rate = (with_emails / total_businesses) * 100
            st.markdown(f"**📊 Email Success Rate:** {email_rate:.1f}% ({with_emails}/{total_businesses})")
        
        # Footer info
        st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #4D148C;">
            <h4>ℹ️ About This Tool</h4>
            <p><strong>🌍 Google Places API + Hunter.io</strong><br>
            This app fetches real business data from Google Places API and enriches it with verified emails from Hunter.io.</p>
            <p><strong>📊 Data Sources:</strong> Google Places Text Search + Place Details API</p>
            <p><strong>📧 Email Enrichment:</strong> Hunter.io Domain Search API (optional)</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
