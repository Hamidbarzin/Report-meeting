import streamlit as st
import pandas as pd
import requests
import os
import re
import time
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Toronto B2B Lead Generator with Database",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyC-xCp_QpinGywzYj8TcC_DPPwOfvxXlxE"
HUNTER_API_KEY = "a1023549c94df1b7ed093d7ae2f007d115930954"  # This key has reached quota limit

# Database setup
DB_NAME = "toronto_leads.db"

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            domain TEXT,
            address TEXT,
            rating REAL,
            review_count INTEGER,
            likely_delivery BOOLEAN DEFAULT 0,
            potential_worldwide_shipping BOOLEAN DEFAULT 0,
            is_logistics BOOLEAN DEFAULT 0,
            email_source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON businesses(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain ON businesses(domain)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON businesses(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON businesses(created_at)')
    
    conn.commit()
    conn.close()

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
                
                # Extract domain from website
                domain = extract_domain_from_url(details.get('website', ''))
                
                business = {
                    'name': place.get('name', ''),
                    'category': ', '.join(place.get('types', [])),
                    'phone': details.get('phone', ''),
                    'email': None,  # Will be filled by enrichment
                    'website': details.get('website', ''),
                    'domain': domain,
                    'address': details.get('address') or place.get('formatted_address', ''),
                    'url': f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                    'rating': place.get('rating', 0.0),
                    'review_count': place.get('user_ratings_total', 0),
                    'email_source': None,
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
            domain = business.get('domain')
            if domain:
                hunter_data = fetch_hunter_emails(domain)
                if hunter_data['email']:
                    business['email'] = hunter_data['email']
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
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <h4>📧 Email Enrichment Results</h4>
            <p><strong>Processed:</strong> {email_stats['processed']} websites</p>
            <p><strong>Emails Found:</strong> {email_stats['emails_found']}</p>
            <p><strong>Success Rate:</strong> {(email_stats['emails_found']/email_stats['processed']*100):.1f}%</p>
            <p><strong>Hunter.io Errors:</strong> {email_stats['hunter_errors']}</p>
            <p><strong>Scraping Errors:</strong> {email_stats['scraping_errors']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    return enriched_businesses

def save_to_database(businesses: List[Dict]):
    """Save businesses to SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    saved_count = 0
    updated_count = 0
    
    for business in businesses:
        # Check if business already exists (by name and address)
        cursor.execute('''
            SELECT id FROM businesses 
            WHERE name = ? AND address = ?
        ''', (business['name'], business['address']))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            cursor.execute('''
                UPDATE businesses SET
                    category = ?, phone = ?, email = ?, website = ?, domain = ?,
                    rating = ?, review_count = ?, likely_delivery = ?,
                    potential_worldwide_shipping = ?, is_logistics = ?,
                    email_source = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                business['category'], business['phone'], business['email'],
                business['website'], business['domain'], business['rating'],
                business['review_count'], business['likely_delivery'],
                business['potential_worldwide_shipping'], business['is_logistics'],
                business['email_source'], existing[0]
            ))
            updated_count += 1
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO businesses (
                    name, category, phone, email, website, domain, address,
                    rating, review_count, likely_delivery, potential_worldwide_shipping,
                    is_logistics, email_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                business['name'], business['category'], business['phone'],
                business['email'], business['website'], business['domain'],
                business['address'], business['rating'], business['review_count'],
                business['likely_delivery'], business['potential_worldwide_shipping'],
                business['is_logistics'], business['email_source']
            ))
            saved_count += 1
    
    conn.commit()
    conn.close()
    
    return saved_count, updated_count

def get_database_stats():
    """Get statistics from database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Total businesses
    cursor.execute('SELECT COUNT(*) FROM businesses')
    total = cursor.fetchone()[0]
    
    # With emails
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE email IS NOT NULL AND email != ""')
    with_emails = cursor.fetchone()[0]
    
    # With domains
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE domain IS NOT NULL AND domain != ""')
    with_domains = cursor.fetchone()[0]
    
    # Recent additions (last 24 hours)
    cursor.execute('SELECT COUNT(*) FROM businesses WHERE created_at > datetime("now", "-1 day")')
    recent = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total': total,
        'with_emails': with_emails,
        'with_domains': with_domains,
        'recent': recent
    }

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
                    st.markdown(f"**🔗 Domain:** `{business['domain'] or 'N/A'}`")
                else:
                    st.markdown("**🌐 Website:** N/A")
            
            with info_col2:
                # Email display with better formatting
                email = business.get('email')
                if email:
                    st.markdown(f"**📧 Email:** [📧 {email}](mailto:{email})")
                    if business.get('email_source'):
                        st.markdown(f"**Source:** {business['email_source']}")
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
    # Initialize database
    init_database()
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4D148C 0%, #7B2CBF 100%); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
        <h1 style="margin: 0; font-size: 2.5rem;">🏭 Toronto B2B Lead Generator with Database</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Find and store B2B companies with domain extraction and email enrichment</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Database stats
    stats = get_database_stats()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total in DB", stats['total'])
    with col2:
        st.metric("With Emails", stats['with_emails'])
    with col3:
        st.metric("With Domains", stats['with_domains'])
    with col4:
        st.metric("Recent (24h)", stats['recent'])
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Search Filters")
        
        search_term = st.text_input(
            "Keywords (optional)",
            placeholder="e.g., electronics, auto parts, beauty, medical devices",
            help="Enter specific keywords to narrow your search"
        )
        
        business_focus = st.multiselect(
            "Business Focus",
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
        
        st.markdown("### ⚙️ Advanced Options")
        
        enrich_emails = st.checkbox("Enrich with emails", value=True, 
                                  help="Get emails from Hunter.io and website scraping")
        save_to_db = st.checkbox("Save to database", value=True,
                               help="Save results to SQLite database")
        view_mode = st.radio("View Mode", ["Cards", "Table"], index=0)
        
        # Search button
        search_button = st.button("🔍 Search & Save", type="primary")
    
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
        
        # Save to database if enabled
        if save_to_db and businesses:
            st.info("💾 Saving to database...")
            saved_count, updated_count = save_to_database(businesses)
            st.success(f"✅ Saved {saved_count} new records, updated {updated_count} existing records")
        
        # Display results
        if view_mode == "Cards":
            display_business_cards(businesses)
        else:
            # Table view
            df = pd.DataFrame(businesses)
            
            # Reorder columns for better display
            column_order = [
                'name', 'category', 'phone', 'email', 'website', 'domain', 'address',
                'rating', 'review_count', 'likely_delivery', 'potential_worldwide_shipping', 'is_logistics', 'email_source'
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
                'domain': 'Domain',
                'address': 'Address',
                'rating': 'Rating',
                'review_count': 'Reviews',
                'likely_delivery': 'Delivery',
                'potential_worldwide_shipping': 'Worldwide',
                'is_logistics': 'Logistics',
                'email_source': 'Email Source'
            })
            
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
            st.metric("Total Results", len(businesses))
        
        with col3:
            with_emails = sum(1 for b in businesses if b.get('email'))
            st.metric("With Emails", with_emails)
    
    # Database management section
    st.markdown("---")
    st.markdown("### 💾 Database Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Stats"):
            st.rerun()
    
    with col2:
        if st.button("📊 View All Records"):
            conn = sqlite3.connect(DB_NAME)
            df_all = pd.read_sql_query("SELECT * FROM businesses ORDER BY created_at DESC LIMIT 100", conn)
            conn.close()
            st.dataframe(df_all, use_container_width=True)
    
    with col3:
        if st.button("🗑️ Clear Database"):
            if st.session_state.get('confirm_clear', False):
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM businesses')
                conn.commit()
                conn.close()
                st.success("Database cleared!")
                st.session_state.confirm_clear = False
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm database clear")

if __name__ == "__main__":
    main()
