import streamlit as st
import pandas as pd
import requests
import os
import re
from typing import List, Dict, Optional
import time
from urllib.parse import urlparse

st.set_page_config(
    page_title="Toronto B2B Lead Generator Pro + Hunter.io",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyC-xCp_QpinGywzYj8TcC_DPPwOfvxXlxE"
HUNTER_API_KEY = "a1023549c94df1b7ed093d7ae2f007d115930954"

# Custom CSS for FedEx-style design
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #2e0f5d 0%, #4b0082 50%, #ff6600 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(46, 15, 93, 0.3);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #ff6600;
        margin: 0.5rem 0;
    }
    
    .business-card {
        background: white;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .business-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(46, 15, 93, 0.15);
    }
    
    .business-name {
        color: #2e0f5d;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .business-info {
        color: #555;
        margin: 0.3rem 0;
        font-size: 0.95rem;
    }
    
    .business-info strong {
        color: #2e0f5d;
        font-weight: 600;
    }
    
    .contact-info {
        background: #f8f9ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #ff6600;
    }
    
    .email-info {
        background: #e8f5e8;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #4caf50;
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
        background: #e8f5e8;
        color: #2d5a2d;
        border: 1px solid #4caf50;
    }
    
    .flag-worldwide {
        background: #e3f2fd;
        color: #1565c0;
        border: 1px solid #2196f3;
    }
    
    .flag-logistics {
        background: #fff3e0;
        color: #e65100;
        border: 1px solid #ff9800;
    }
    
    .search-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .results-header {
        background: linear-gradient(135deg, #2e0f5d, #4b0082);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ff6600, #ff8533);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(255, 102, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 102, 0, 0.4);
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .tab-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .hunter-status {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from website URL"""
    if not url:
        return None
    
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except Exception:
        return None

def fetch_hunter_emails(domain: str) -> Dict[str, Optional[str]]:
    """Fetch verified emails from Hunter.io API"""
    try:
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            'domain': domain,
            'api_key': HUNTER_API_KEY,
            'limit': 3  # Get up to 3 emails
        }
        
        response = requests.get(url, params=params, timeout=10)
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
            
    except Exception as e:
        st.warning(f"Hunter.io API error for {domain}: {str(e)}")
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
            "types": data.get("types", []),
            "address": data.get("formatted_address")
        }
    except Exception:
        return {"phone": None, "website": None, "types": [], "address": None}

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
                'email': None,  # Will be filled by Hunter.io
                'contact_role': None,  # Will be filled by Hunter.io
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
        
        if business.get('website'):
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
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏭 Toronto B2B Lead Generator Pro + Hunter.io</h1>
        <p>Find importers, distributors, wholesalers, suppliers, fulfillment/3PL, logistics, and e-commerce companies in Toronto with verified emails</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search Section
    with st.container():
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input(
                "🔍 Keywords (optional)",
                placeholder="e.g., electronics, auto parts, beauty, medical devices",
                help="Enter specific keywords to narrow down your search"
            )
            
            business_focus = st.multiselect(
                "🎯 Business Focus",
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
        
        with col2:
            location = st.text_input("📍 Location", value="Toronto, ON")
            max_results = st.slider("📊 Max Results", 10, 100, 20, step=10)
            
            # Advanced options
            with st.expander("⚙️ Advanced Options"):
                enrich_emails = st.checkbox("Enrich with Hunter.io (emails)", value=True, help="Get verified emails from Hunter.io API")
                show_ratings = st.checkbox("Show ratings & reviews", value=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Search Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("🔎 Search Businesses", type="primary", use_container_width=True)
    
    if search_button:
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
            st.error("❌ GOOGLE_API_KEY is missing. Please set it in environment or replace placeholder in code.")
            return
        
        if not business_focus:
            st.warning("⚠️ Please select at least one business focus.")
            return
        
        with st.spinner("🔍 Searching Google Places and extracting contact details..."):
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
                    st.info("ℹ️ No companies found. Try different keywords or business focus.")
                    return
                
                # Enrich with Hunter.io if enabled
                if enrich_emails:
                    st.info("📧 Enriching with Hunter.io verified emails...")
                    all_businesses = enrich_with_hunter_emails(all_businesses)
                
                # Results Header
                st.markdown(f"""
                <div class="results-header">
                    <h2>📊 Found {len(all_businesses)} Businesses</h2>
                    <p>Complete with contact information, verified emails, and business classification</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #2e0f5d; margin: 0;">Total Companies</h3>
                        <h2 style="color: #ff6600; margin: 0.5rem 0;">{len(all_businesses)}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    delivery_count = sum(1 for b in all_businesses if b.get('likely_delivery'))
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #2e0f5d; margin: 0;">Delivery Ready</h3>
                        <h2 style="color: #ff6600; margin: 0.5rem 0;">{delivery_count}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    worldwide_count = sum(1 for b in all_businesses if b.get('potential_worldwide_shipping'))
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #2e0f5d; margin: 0;">Worldwide Shipping</h3>
                        <h2 style="color: #ff6600; margin: 0.5rem 0;">{worldwide_count}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    logistics_count = sum(1 for b in all_businesses if b.get('is_logistics'))
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #2e0f5d; margin: 0;">Logistics</h3>
                        <h2 style="color: #ff6600; margin: 0.5rem 0;">{logistics_count}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    email_count = sum(1 for b in all_businesses if b.get('email'))
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #2e0f5d; margin: 0;">With Emails</h3>
                        <h2 style="color: #ff6600; margin: 0.5rem 0;">{email_count}</h2>
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
                
                # Export Section
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv_data = df_display.to_csv(index=False)
                    st.download_button(
                        "📥 Export to CSV",
                        data=csv_data,
                        file_name=f"toronto_b2b_leads_hunter_{int(time.time())}.csv",
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
                                file_name=f"toronto_b2b_with_emails_{int(time.time())}.csv",
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
                
                # Info Section
                st.info("""
                🌍 **Data Source**: Google Places API + Hunter.io verified emails
                📧 **Email Verification**: Hunter.io API provides verified, deliverable email addresses
                📞 **Phone Numbers**: Retrieved from Google Places Details API
                🏷️ **Classification**: Automated flagging based on business name and category
                👥 **Contact Roles**: CEO, Sales, Marketing, etc. from Hunter.io
                """)
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()
