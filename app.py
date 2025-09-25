"""
Toronto Business Lead Generation Bot
A web app for finding Toronto businesses that need delivery or international shipping services.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Tuple
import os
from dotenv import load_dotenv

from src.data_sources import YelpDataSource, OSMDataSource
from src.categorization import BusinessCategorizer
from src.ai_analysis import AIAnalyzer
from src.utils import setup_caching, export_to_csv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Toronto Business Lead Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize caching
setup_caching()

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
            options=["Yelp", "OpenStreetMap"],
            index=0,
            help="Choose data source (Yelp requires API key)"
        )
        
        # AI Analysis toggle
        use_ai_analysis = st.checkbox(
            "Enable AI Analysis",
            value=False,
            help="Use AI to analyze delivery/shipping potential (requires OpenAI API key)"
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
                # Initialize data source
                if data_source == "Yelp":
                    if not os.getenv("YELP_API_KEY"):
                        st.error("Yelp API key not found. Please set YELP_API_KEY in your environment or use OpenStreetMap.")
                        return
                    data_source_obj = YelpDataSource()
                else:
                    data_source_obj = OSMDataSource()
                
                # Search for businesses
                businesses = data_source_obj.search_businesses(
                    search_term=search_term,
                    categories=categories,
                    max_results=max_results
                )
                
                if not businesses:
                    st.warning("No businesses found matching your criteria.")
                    return
                
                # Categorize businesses
                categorizer = BusinessCategorizer()
                categorized_businesses = []
                
                for business in businesses:
                    categorized_business = categorizer.categorize_business(business)
                    categorized_businesses.append(categorized_business)
                
                # AI Analysis (if enabled)
                if use_ai_analysis and os.getenv("OPENAI_API_KEY"):
                    ai_analyzer = AIAnalyzer()
                    with st.spinner("Running AI analysis..."):
                        for business in categorized_businesses:
                            ai_analysis = ai_analyzer.analyze_business(business)
                            business.update(ai_analysis)
                
                # Display results
                display_results(categorized_businesses)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

def display_results(businesses: List[Dict]) -> None:
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
            csv_data = export_to_csv(businesses)
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

if __name__ == "__main__":
    main()
