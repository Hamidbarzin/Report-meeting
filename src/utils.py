"""
Utility functions for the Toronto Business Lead Generator.
"""

import pandas as pd
import io
from typing import List, Dict
import streamlit as st
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)

def setup_caching():
    """Set up caching for the Streamlit app."""
    if 'cache' not in st.session_state:
        st.session_state.cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour cache

def export_to_csv(businesses: List[Dict]) -> str:
    """
    Export businesses data to CSV format.
    
    Args:
        businesses: List of business dictionaries
        
    Returns:
        CSV data as string
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(businesses)
        
        # Reorder columns for better readability
        column_order = [
            'name', 'category', 'phone', 'address', 'url', 
            'rating', 'review_count', 'likely_delivery', 
            'potential_worldwide_shipping', 'is_logistics',
            'ai_likely_delivery', 'ai_potential_worldwide_shipping', 
            'ai_is_logistics', 'ai_confidence', 'ai_reasoning'
        ]
        
        # Only include columns that exist
        available_columns = [col for col in column_order if col in df.columns]
        df_export = df[available_columns]
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_data = csv_buffer.getvalue()
        
        return csv_data
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return "Error generating CSV data"

def format_phone_number(phone: str) -> str:
    """
    Format phone number for display.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Formatted phone number
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format based on length
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't format

def validate_business_data(business: Dict) -> bool:
    """
    Validate business data for completeness.
    
    Args:
        business: Business data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['name']
    
    for field in required_fields:
        if not business.get(field):
            return False
    
    return True

def clean_business_data(business: Dict) -> Dict:
    """
    Clean and standardize business data.
    
    Args:
        business: Raw business data dictionary
        
    Returns:
        Cleaned business data dictionary
    """
    cleaned = business.copy()
    
    # Clean name
    if 'name' in cleaned:
        cleaned['name'] = cleaned['name'].strip()
    
    # Clean phone
    if 'phone' in cleaned:
        cleaned['phone'] = format_phone_number(cleaned['phone'])
    
    # Clean address
    if 'address' in cleaned:
        cleaned['address'] = cleaned['address'].strip()
    
    # Clean URL
    if 'url' in cleaned and cleaned['url']:
        if not cleaned['url'].startswith(('http://', 'https://')):
            cleaned['url'] = 'https://' + cleaned['url']
    
    # Ensure numeric fields are properly typed
    numeric_fields = ['rating', 'review_count', 'latitude', 'longitude']
    for field in numeric_fields:
        if field in cleaned and cleaned[field] is not None:
            try:
                cleaned[field] = float(cleaned[field])
            except (ValueError, TypeError):
                cleaned[field] = 0.0
    
    # Ensure boolean fields are properly typed
    boolean_fields = [
        'likely_delivery', 'potential_worldwide_shipping', 'is_logistics',
        'ai_likely_delivery', 'ai_potential_worldwide_shipping', 'ai_is_logistics'
    ]
    for field in boolean_fields:
        if field in cleaned:
            cleaned[field] = bool(cleaned[field])
    
    return cleaned

def get_business_summary(businesses: List[Dict]) -> Dict:
    """
    Get summary statistics for a list of businesses.
    
    Args:
        businesses: List of business dictionaries
        
    Returns:
        Summary statistics dictionary
    """
    if not businesses:
        return {
            'total_businesses': 0,
            'delivery_count': 0,
            'shipping_count': 0,
            'logistics_count': 0,
            'avg_rating': 0.0,
            'total_reviews': 0
        }
    
    total = len(businesses)
    delivery_count = sum(1 for b in businesses if b.get('likely_delivery', False))
    shipping_count = sum(1 for b in businesses if b.get('potential_worldwide_shipping', False))
    logistics_count = sum(1 for b in businesses if b.get('is_logistics', False))
    
    # Calculate average rating
    ratings = [b.get('rating', 0) for b in businesses if b.get('rating', 0) > 0]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    
    # Calculate total reviews
    total_reviews = sum(b.get('review_count', 0) for b in businesses)
    
    return {
        'total_businesses': total,
        'delivery_count': delivery_count,
        'shipping_count': shipping_count,
        'logistics_count': logistics_count,
        'avg_rating': round(avg_rating, 2),
        'total_reviews': total_reviews
    }

def filter_businesses_by_criteria(businesses: List[Dict], criteria: Dict) -> List[Dict]:
    """
    Filter businesses based on specified criteria.
    
    Args:
        businesses: List of business dictionaries
        criteria: Filter criteria dictionary
        
    Returns:
        Filtered list of businesses
    """
    filtered = businesses.copy()
    
    # Filter by delivery potential
    if criteria.get('delivery_only', False):
        filtered = [b for b in filtered if b.get('likely_delivery', False)]
    
    # Filter by shipping potential
    if criteria.get('shipping_only', False):
        filtered = [b for b in filtered if b.get('potential_worldwide_shipping', False)]
    
    # Filter by logistics only
    if criteria.get('logistics_only', False):
        filtered = [b for b in filtered if b.get('is_logistics', False)]
    
    # Filter by minimum rating
    min_rating = criteria.get('min_rating', 0)
    if min_rating > 0:
        filtered = [b for b in filtered if b.get('rating', 0) >= min_rating]
    
    # Filter by minimum review count
    min_reviews = criteria.get('min_reviews', 0)
    if min_reviews > 0:
        filtered = [b for b in filtered if b.get('review_count', 0) >= min_reviews]
    
    return filtered

def create_business_report(businesses: List[Dict]) -> str:
    """
    Create a text report for the businesses.
    
    Args:
        businesses: List of business dictionaries
        
    Returns:
        Formatted report string
    """
    if not businesses:
        return "No businesses found."
    
    summary = get_business_summary(businesses)
    
    report = f"""
# Toronto Business Lead Generation Report

## Summary
- Total Businesses: {summary['total_businesses']}
- Likely Need Delivery: {summary['delivery_count']}
- Potential Worldwide Shipping: {summary['shipping_count']}
- Logistics/Freight Services: {summary['logistics_count']}
- Average Rating: {summary['avg_rating']}/5
- Total Reviews: {summary['total_reviews']}

## Top Businesses by Rating
"""
    
    # Sort by rating and get top 5
    top_businesses = sorted(
        [b for b in businesses if b.get('rating', 0) > 0],
        key=lambda x: x.get('rating', 0),
        reverse=True
    )[:5]
    
    for i, business in enumerate(top_businesses, 1):
        report += f"\n{i}. {business.get('name', 'Unknown')} - {business.get('rating', 0)}/5 ({business.get('review_count', 0)} reviews)"
    
    return report
