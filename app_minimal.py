"""
Minimal Toronto Business Lead Generator
A simplified version that works without external dependencies.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import os
import json
import time
import requests

# Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyC-xCp_QpinGywzYj8TcC_DPPwOfvxXlxE"

# Page configuration
st.set_page_config(
    page_title="Toronto Business Lead Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function."""
    
    # Header
    st.title("🚀 Toronto Business Lead Generator")
    st.markdown("Find Toronto businesses that need delivery or international shipping services")
    
    # Sidebar for filters
    with st.sidebar:
        st.header("🔍 Search Filters")
        
        # Search term
        search_term = st.text_input(
            "Search Term",
            placeholder="e.g., 'restaurant', 'pharmacy', 'electronics'",
            help="Enter keywords to search for specific business types"
        )
        
        # Category selection
        categories = st.multiselect(
            "Business Categories",
            options=[
                "Restaurant", "Grocery", "Pharmacy", "Florist", 
                "Bakery", "Electronics", "Clothing", "Logistics & Freight"
            ],
            default=["Restaurant", "Grocery", "Pharmacy"],
            help="Select business categories to include"
        )
        
        # Number of results
        max_results = st.slider(
            "Number of Results",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
            help="Maximum number of businesses to return"
        )
        
        # Data source selection
        data_source = st.selectbox(
            "Data Source",
            options=["Google Places API", "Demo Data"],
            index=0,
            help="Choose data source"
        )
        
        # AI Analysis toggle
        use_ai_analysis = st.checkbox(
            "Enable AI Analysis",
            value=False,
            help="Use AI to analyze delivery/shipping potential (Coming Soon)"
        )
        
        # Search button
        search_button = st.button("🔍 Search Businesses", type="primary")
    
    # Main content area
    if search_button:
        if not search_term and not categories:
            st.error("Please enter a search term or select at least one category.")
            return
        
        # Show loading spinner
        with st.spinner("Searching for businesses..."):
            try:
                # Fetch data based on selected source
                if data_source == "Google Places API":
                    if GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
                        st.error("Please set your Google API key in the GOOGLE_API_KEY environment variable or replace 'YOUR_API_KEY_HERE' in the code.")
                        return
                    businesses = fetch_places_data(search_term, categories, max_results)
                else:
                    businesses = generate_demo_data(search_term, categories, max_results)
                
                if not businesses:
                    st.warning("No businesses found matching your criteria.")
                    return
                
                # Display results
                display_results(businesses, data_source)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

def generate_demo_data(search_term: str, categories: List[str], max_results: int) -> List[Dict]:
    """Generate demo business data for testing."""
    
    # Sample business data
    sample_businesses = [
        {
            "name": "Pizza Palace",
            "category": "Restaurant",
            "phone": "(416) 555-0123",
            "address": "123 Queen St W, Toronto, ON M5H 2M9",
            "url": "https://pizzapalace.ca",
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
            "address": "456 King St E, Toronto, ON M5A 1K6",
            "url": "https://freshmarket.ca",
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
            "address": "789 Yonge St, Toronto, ON M4W 2G8",
            "url": "https://techworld.ca",
            "rating": 4.5,
            "review_count": 234,
            "likely_delivery": True,
            "potential_worldwide_shipping": True,
            "is_logistics": False
        },
        {
            "name": "Fashion Forward",
            "category": "Clothing",
            "phone": "(416) 555-0321",
            "address": "321 Bloor St W, Toronto, ON M5S 1W7",
            "url": "https://fashionforward.ca",
            "rating": 4.1,
            "review_count": 67,
            "likely_delivery": True,
            "potential_worldwide_shipping": True,
            "is_logistics": False
        },
        {
            "name": "Express Logistics",
            "category": "Logistics & Freight",
            "phone": "(416) 555-0654",
            "address": "654 Bay St, Toronto, ON M5G 1M5",
            "url": "https://expresslogistics.ca",
            "rating": 4.3,
            "review_count": 145,
            "likely_delivery": False,
            "potential_worldwide_shipping": False,
            "is_logistics": True
        },
        {
            "name": "Green Thumb Florist",
            "category": "Florist",
            "phone": "(416) 555-0987",
            "address": "987 College St, Toronto, ON M6G 1A5",
            "url": "https://greenthumb.ca",
            "rating": 4.4,
            "review_count": 78,
            "likely_delivery": True,
            "potential_worldwide_shipping": False,
            "is_logistics": False
        },
        {
            "name": "Sweet Dreams Bakery",
            "category": "Bakery",
            "phone": "(416) 555-0147",
            "address": "147 Dundas St W, Toronto, ON M5G 1C3",
            "url": "https://sweetdreams.ca",
            "rating": 4.6,
            "review_count": 123,
            "likely_delivery": True,
            "potential_worldwide_shipping": False,
            "is_logistics": False
        },
        {
            "name": "Health Plus Pharmacy",
            "category": "Pharmacy",
            "phone": "(416) 555-0258",
            "address": "258 Spadina Ave, Toronto, ON M5T 2E2",
            "url": "https://healthplus.ca",
            "rating": 4.0,
            "review_count": 91,
            "likely_delivery": True,
            "potential_worldwide_shipping": False,
            "is_logistics": False
        }
    ]
    
    # Filter by search term and categories
    filtered_businesses = []
    
    for business in sample_businesses:
        # Check if business matches search term
        if search_term:
            search_lower = search_term.lower()
            if not (search_lower in business["name"].lower() or 
                   search_lower in business["category"].lower()):
                continue
        
        # Check if business matches selected categories
        if categories and business["category"] not in categories:
            continue
        
        filtered_businesses.append(business)
    
    # Limit results
    return filtered_businesses[:max_results]

def fetch_places_data(search_term: str, categories: List[str], max_results: int) -> List[Dict]:
    """Fetch real business data from Google Places API."""
    
    businesses = []
    
    # Build search queries based on search term and categories
    queries = []
    
    if search_term:
        # Use search term + Toronto
        queries.append(f"{search_term} Toronto")
    else:
        # Use categories + Toronto
        for category in categories:
            queries.append(f"{category} Toronto")
    
    # If no search term or categories, use a default query
    if not queries:
        queries = ["business Toronto"]
    
    # Process each query
    for query in queries:
        try:
            # Google Places Text Search API
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': query,
                'key': GOOGLE_API_KEY,
                'region': 'ca',  # Canada
                'location': '43.6532,-79.3832',  # Toronto coordinates
                'radius': '50000'  # 50km radius
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                st.warning(f"Google Places API error: {data.get('error_message', 'Unknown error')}")
                continue
            
            # Process results
            for place in data.get('results', [])[:max_results]:
                # Extract business information
                business = {
                    'name': place.get('name', ''),
                    'category': ', '.join(place.get('types', [])) if place.get('types') else '',
                    'phone': place.get('formatted_phone_number', ''),
                    'address': place.get('formatted_address', ''),
                    'url': f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id', '')}",
                    'rating': place.get('rating', 0.0),
                    'review_count': place.get('user_ratings_total', 0),
                    'likely_delivery': False,
                    'potential_worldwide_shipping': False,
                    'is_logistics': False
                }
                
                # Determine flags based on business type and name
                business_types = place.get('types', [])
                business_name = business['name'].lower()
                
                # Check for likely delivery
                delivery_keywords = ['restaurant', 'food', 'grocery', 'pharmacy', 'florist', 'bakery']
                if any(keyword in business_types for keyword in delivery_keywords):
                    business['likely_delivery'] = True
                
                # Check for potential worldwide shipping
                shipping_keywords = ['electronics', 'clothing', 'furniture', 'store']
                if any(keyword in business_types for keyword in shipping_keywords):
                    business['potential_worldwide_shipping'] = True
                
                # Check for logistics
                logistics_keywords = ['logistics', 'freight', 'courier', 'shipping']
                if (any(keyword in business_name for keyword in logistics_keywords) or 
                    any(keyword in business_types for keyword in logistics_keywords)):
                    business['is_logistics'] = True
                
                businesses.append(business)
                
                # Stop if we have enough results
                if len(businesses) >= max_results:
                    break
                    
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data from Google Places API: {str(e)}")
            continue
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            continue
    
    return businesses[:max_results]

def display_results(businesses: List[Dict], data_source: str = "Demo Data") -> None:
    """Display search results in a table format."""
    
    st.header(f"📊 Found {len(businesses)} Businesses")
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(businesses)
    
    # Reorder columns for better visibility
    column_order = [
        'name', 'category', 'phone', 'address', 'url', 
        'rating', 'review_count', 'likely_delivery', 
        'potential_worldwide_shipping', 'is_logistics'
    ]
    
    # Only include columns that exist
    available_columns = [col for col in column_order if col in df.columns]
    df_display = df[available_columns]
    
    # Display the table
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400
    )
    
    # Export functionality
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to CSV"):
            csv_data = df_display.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="toronto_businesses.csv",
                mime="text/csv"
            )
    
    with col2:
        # Summary statistics
        st.metric("Total Businesses", len(businesses))
        if 'likely_delivery' in df.columns:
            delivery_count = df['likely_delivery'].sum()
            st.metric("Likely Delivery", delivery_count)
        if 'potential_worldwide_shipping' in df.columns:
            shipping_count = df['potential_worldwide_shipping'].sum()
            st.metric("Potential Worldwide Shipping", shipping_count)
    
    # Show info about data source
    if data_source == "Google Places API":
        st.info("""
        🌍 **Google Places API**: This app is now fetching real business data from Google Places API. 
        Make sure you have a valid Google API key set in the GOOGLE_API_KEY environment variable.
        """)
    else:
        st.info("""
        🚀 **Demo Mode**: This is a demonstration version with sample data. 
        Switch to "Google Places API" to fetch real business data.
        """)

if __name__ == "__main__":
    main()
