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
    page_title="Toronto B2B Lead Generator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyC-xCp_QpinGywzYj8TcC_DPPwOfvxXlxE")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "a1023549c94df1b7ed093d7ae2f007d115930954")

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

def fetch_places_data(search_term: str, business_focus: List[str], location: str, max_results: int = 20) -> List[Dict]:
    """Fetch real business data from Google Places API"""
    businesses = []
    
    try:
        # Get location coordinates
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": location, "key": GOOGLE_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        coords = None
        if data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            coords = {"lat": loc["lat"], "lng": loc["lng"]}
        
        # Build search queries
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
        for query in queries[:3]:  # Limit to 3 queries
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "key": GOOGLE_API_KEY,
                "fields": "place_id,name,formatted_address,types,rating,user_ratings_total"
            }
            
            if coords:
                params["location"] = f"{coords['lat']},{coords['lng']}"
                params["radius"] = 50000
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            places = data.get("results", [])[:max_results]
            
            for place in places:
                place_id = place.get("place_id")
                if not place_id:
                    continue
                
                # Get detailed information
                url = "https://maps.googleapis.com/maps/api/place/details/json"
                fields = "formatted_phone_number,international_phone_number,website,types,formatted_address"
                params = {
                    "place_id": place_id,
                    "fields": fields,
                    "key": GOOGLE_API_KEY
                }
                
                response = requests.get(url, params=params, timeout=15)
                details = response.json().get("result", {}) if response.ok else {}
                
                # Extract domain from website
                domain = extract_domain_from_url(details.get('website', ''))
                
                # Classify business flags
                text = f"{place.get('name', '')} {' '.join(place.get('types', []))}".lower()
                
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
                
                business = {
                    'name': place.get('name', ''),
                    'category': ', '.join(place.get('types', [])),
                    'phone': details.get('formatted_phone_number') or details.get('international_phone_number'),
                    'email': None,
                    'website': details.get('website', ''),
                    'domain': domain,
                    'address': details.get('formatted_address') or place.get('formatted_address', ''),
                    'url': f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                    'rating': place.get('rating', 0.0),
                    'review_count': place.get('user_ratings_total', 0),
                    'email_source': None,
                    'likely_delivery': likely_delivery,
                    'potential_worldwide_shipping': potential_worldwide,
                    'is_logistics': is_logistics
                }
                
                businesses.append(business)
                
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
    
    return businesses

def save_to_database(businesses: List[Dict]):
    """Save businesses to SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    saved_count = 0
    updated_count = 0
    
    for business in businesses:
        # Check if business already exists
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
    
    conn.close()
    
    return {
        'total': total,
        'with_emails': with_emails,
        'with_domains': with_domains
    }

def main():
    # Initialize database
    init_database()
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4D148C 0%, #7B2CBF 100%); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
        <h1 style="margin: 0; font-size: 2.5rem;">🏭 Toronto B2B Lead Generator</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Find and store B2B companies with domain extraction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Database stats
    stats = get_database_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total in DB", stats['total'])
    with col2:
        st.metric("With Emails", stats['with_emails'])
    with col3:
        st.metric("With Domains", stats['with_domains'])
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Search Filters")
        
        search_term = st.text_input(
            "Keywords (optional)",
            placeholder="e.g., electronics, auto parts"
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
            default=["Distributors / Wholesalers", "Suppliers / Manufacturers", "Logistics & Freight"]
        )
        
        location = st.text_input("Location", value="Toronto, ON")
        max_results = st.slider("Maximum results", 10, 100, 20, step=10)
        
        search_button = st.button("🔍 Search & Save", type="primary")
    
    # Main content
    if search_button:
        if not business_focus:
            st.warning("⚠️ Please select at least one business focus type.")
            return
        
        with st.spinner("🔍 Searching Google Places..."):
            businesses = fetch_places_data(search_term, business_focus, location, max_results)
        
        if not businesses:
            st.info("ℹ️ No businesses found. Try different keywords.")
            return
        
        # Save to database
        st.info("💾 Saving to database...")
        saved_count, updated_count = save_to_database(businesses)
        st.success(f"✅ Saved {saved_count} new records, updated {updated_count} existing records")
        
        # Display results
        df = pd.DataFrame(businesses)
        
        # Show key columns
        display_columns = ['name', 'category', 'phone', 'website', 'domain', 'address', 'rating']
        available_columns = [col for col in display_columns if col in df.columns]
        df_display = df[available_columns]
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Export
        csv_data = df_display.to_csv(index=False)
        st.download_button(
            "📥 Export to CSV",
            data=csv_data,
            file_name="toronto_b2b_leads.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()