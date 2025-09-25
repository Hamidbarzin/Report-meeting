import streamlit as st
import pandas as pd
import requests
import os
from typing import List, Dict, Optional

st.set_page_config(
    page_title="Toronto B2B Lead Generator",
    page_icon="🚚",
    layout="wide"
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyC-xCp_QpinGywzYj8TcC_DPPwOfvxXlxE"

def fetch_places_data(query: str, max_results: int = 20) -> List[Dict]:
    """Fetch business data from Google Places API"""
    businesses = []
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': GOOGLE_API_KEY,
            'location': '43.6532,-79.3832',  # Toronto coordinates
            'radius': '50000'  # 50km radius
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != 'OK':
            st.error(f"Google Places API error: {data.get('error_message', 'Unknown error')}")
            return businesses
        
        for place in data.get('results', [])[:max_results]:
            business = {
                'name': place.get('name', ''),
                'category': ', '.join(place.get('types', [])),
                'phone': place.get('formatted_phone_number', ''),
                'address': place.get('formatted_address', ''),
                'website': place.get('website', ''),
                'url': f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id', '')}",
                'rating': place.get('rating', 0.0),
                'review_count': place.get('user_ratings_total', 0),
                'likely_delivery': False,
                'potential_worldwide_shipping': False,
                'is_logistics': False
            }
            
            # Simple flag logic
            name_lower = business['name'].lower()
            types_lower = business['category'].lower()
            
            if any(word in (name_lower + ' ' + types_lower) for word in ['store', 'retail', 'shop']):
                business['likely_delivery'] = True
                
            if any(word in (name_lower + ' ' + types_lower) for word in ['import', 'export', 'wholesale', 'distributor']):
                business['potential_worldwide_shipping'] = True
                
            if any(word in (name_lower + ' ' + types_lower) for word in ['logistics', 'freight', 'shipping', '3pl']):
                business['is_logistics'] = True
            
            businesses.append(business)
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
    
    return businesses

def main():
    st.title("🏭 Toronto B2B Lead Generator")
    st.markdown("Find **importers, distributors, wholesalers, suppliers, fulfillment/3PL, logistics, and e-commerce** companies in Toronto.")
    
    with st.sidebar:
        st.header("🔍 Search Filters")
        
        search_term = st.text_input(
            "Keywords (optional)",
            placeholder="e.g., electronics, auto parts, beauty, medical devices"
        )
        
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
            default=["Distributors / Wholesalers", "Suppliers / Manufacturers", "Logistics & Freight"]
        )
        
        location = st.text_input("Location", value="Toronto, ON")
        max_results = st.slider("Max Results", 10, 100, 20, step=10)
        
        search_button = st.button("🔎 Search Businesses", type="primary")
    
    if search_button:
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
            st.error("GOOGLE_API_KEY is missing. Please set it in environment or replace placeholder in code.")
            return
        
        if not business_focus:
            st.warning("Please select at least one business focus.")
            return
        
        with st.spinner("Searching Google Places..."):
            try:
                # Build search queries
                queries = []
                focus_keywords = {
                    "Importers": ["importer", "import"],
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
                
                for query in queries:
                    businesses = fetch_places_data(query, max_results)
                    for business in businesses:
                        place_id = business.get('url', '').split('place_id:')[-1]
                        if place_id not in seen_places:
                            seen_places.add(place_id)
                            all_businesses.append(business)
                
                if not all_businesses:
                    st.info("No companies found. Try different keywords or business focus.")
                    return
                
                # Display results
                st.header(f"📊 Found {len(all_businesses)} Businesses")
                
                df = pd.DataFrame(all_businesses)
                
                # Reorder columns
                column_order = [
                    'name', 'category', 'phone', 'address', 'website', 'url', 
                    'rating', 'review_count', 'likely_delivery', 
                    'potential_worldwide_shipping', 'is_logistics'
                ]
                
                available_columns = [col for col in column_order if col in df.columns]
                df_display = df[available_columns]
                
                st.dataframe(df_display, use_container_width=True, height=400)
                
                # Export functionality
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv_data = df_display.to_csv(index=False)
                    st.download_button(
                        "📥 Export to CSV",
                        data=csv_data,
                        file_name="toronto_b2b_leads.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    st.metric("Total Businesses", len(all_businesses))
                
                with col3:
                    if 'likely_delivery' in df.columns:
                        delivery_count = df['likely_delivery'].sum()
                        st.metric("Likely Delivery", delivery_count)
                
                st.info("""
                🌍 **Google Places API**: This app fetches real business data from Google Places API.
                Results include contact information and business categorization flags.
                """)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()
