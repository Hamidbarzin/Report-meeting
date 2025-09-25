"""
Business categorization and delivery/shipping detection logic.
"""

import re
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

class BusinessCategorizer:
    """Categorizes businesses and detects delivery/shipping potential."""
    
    def __init__(self):
        # Keywords that indicate delivery potential
        self.delivery_keywords = {
            'delivery', 'deliver', 'takeout', 'take-out', 'pickup', 'pick-up',
            'catering', 'cater', 'food truck', 'foodtruck', 'online ordering',
            'order online', 'curbside', 'curb-side', 'drive-thru', 'drive through',
            'home delivery', 'express delivery', 'same day', 'next day'
        }
        
        # Keywords that indicate international shipping potential
        self.shipping_keywords = {
            'shipping', 'ship', 'international', 'worldwide', 'global',
            'export', 'import', 'freight', 'logistics', 'courier',
            'express shipping', 'overnight', 'air freight', 'sea freight',
            'customs', 'duty', 'cross border', 'borderless'
        }
        
        # Keywords that indicate logistics/freight services
        self.logistics_keywords = {
            'logistics', 'freight', 'shipping', 'courier', 'express',
            'transport', 'transportation', 'warehouse', 'distribution',
            'fulfillment', 'supply chain', 'cargo', 'parcel',
            'package', 'mail', 'postal', 'delivery service'
        }
        
        # Business categories that typically need delivery
        self.delivery_categories = {
            'restaurant', 'food', 'grocery', 'pharmacy', 'florist',
            'bakery', 'electronics', 'clothing', 'retail', 'shop'
        }
        
        # Business categories that typically need international shipping
        self.shipping_categories = {
            'electronics', 'clothing', 'fashion', 'jewelry', 'books',
            'toys', 'sports', 'outdoor', 'beauty', 'cosmetics',
            'health', 'supplements', 'art', 'crafts', 'handmade'
        }
    
    def categorize_business(self, business: Dict) -> Dict:
        """
        Categorize a business and detect delivery/shipping potential.
        
        Args:
            business: Business data dictionary
            
        Returns:
            Enhanced business dictionary with categorization flags
        """
        try:
            # Extract text for analysis
            text_to_analyze = self._extract_analyzeable_text(business)
            
            # Detect delivery potential
            likely_delivery = self._detect_delivery_potential(business, text_to_analyze)
            
            # Detect international shipping potential
            potential_worldwide_shipping = self._detect_shipping_potential(business, text_to_analyze)
            
            # Detect if it's a logistics/freight business
            is_logistics = self._detect_logistics_business(business, text_to_analyze)
            
            # Add flags to business data
            business.update({
                'likely_delivery': likely_delivery,
                'potential_worldwide_shipping': potential_worldwide_shipping,
                'is_logistics': is_logistics
            })
            
            return business
            
        except Exception as e:
            logger.error(f"Error categorizing business {business.get('name', 'Unknown')}: {e}")
            # Return business with default flags
            business.update({
                'likely_delivery': False,
                'potential_worldwide_shipping': False,
                'is_logistics': False
            })
            return business
    
    def _extract_analyzeable_text(self, business: Dict) -> str:
        """Extract and combine all text fields for analysis."""
        text_fields = [
            business.get('name', ''),
            business.get('category', ''),
            business.get('address', ''),
            business.get('url', '')
        ]
        
        # Join all text fields and convert to lowercase
        combined_text = ' '.join(filter(None, text_fields)).lower()
        
        return combined_text
    
    def _detect_delivery_potential(self, business: Dict, text: str) -> bool:
        """Detect if business likely needs delivery services."""
        
        # Check category-based rules
        category = business.get('category', '').lower()
        if any(cat in category for cat in self.delivery_categories):
            return True
        
        # Check for delivery keywords in text
        if any(keyword in text for keyword in self.delivery_keywords):
            return True
        
        # Check for specific business types that typically need delivery
        business_name = business.get('name', '').lower()
        if any(keyword in business_name for keyword in ['restaurant', 'cafe', 'pizza', 'sushi', 'pharmacy', 'drug']):
            return True
        
        return False
    
    def _detect_shipping_potential(self, business: Dict, text: str) -> bool:
        """Detect if business likely needs international shipping services."""
        
        # Check category-based rules
        category = business.get('category', '').lower()
        if any(cat in category for cat in self.shipping_categories):
            return True
        
        # Check for shipping keywords in text
        if any(keyword in text for keyword in self.shipping_keywords):
            return True
        
        # Check for e-commerce indicators
        url = business.get('url', '').lower()
        if any(domain in url for domain in ['.com', '.ca', 'shop', 'store', 'online']):
            return True
        
        # Check for business name indicators
        business_name = business.get('name', '').lower()
        if any(keyword in business_name for keyword in ['shop', 'store', 'boutique', 'market', 'mart']):
            return True
        
        return False
    
    def _detect_logistics_business(self, business: Dict, text: str) -> bool:
        """Detect if business is a logistics/freight service provider."""
        
        # Check for logistics keywords in text
        if any(keyword in text for keyword in self.logistics_keywords):
            return True
        
        # Check category for logistics indicators
        category = business.get('category', '').lower()
        if any(keyword in category for keyword in ['logistics', 'freight', 'shipping', 'courier', 'transport']):
            return True
        
        # Check business name for logistics indicators
        business_name = business.get('name', '').lower()
        if any(keyword in business_name for keyword in ['logistics', 'freight', 'shipping', 'courier', 'express', 'transport']):
            return True
        
        return False
    
    def get_category_suggestions(self, business_name: str) -> List[str]:
        """Get suggested categories for a business based on its name."""
        suggestions = []
        name_lower = business_name.lower()
        
        # Simple keyword-based category suggestions
        category_keywords = {
            'restaurant': ['restaurant', 'cafe', 'bistro', 'diner', 'pizza', 'sushi', 'burger', 'food'],
            'grocery': ['grocery', 'market', 'supermarket', 'food', 'fresh', 'organic'],
            'pharmacy': ['pharmacy', 'drug', 'medical', 'health', 'clinic'],
            'florist': ['florist', 'flower', 'floral', 'garden', 'plant'],
            'bakery': ['bakery', 'bread', 'cake', 'pastry', 'sweet', 'dessert'],
            'electronics': ['electronics', 'computer', 'phone', 'tech', 'digital', 'gadget'],
            'clothing': ['clothing', 'fashion', 'apparel', 'boutique', 'store', 'shop'],
            'logistics': ['logistics', 'freight', 'shipping', 'courier', 'transport', 'express']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                suggestions.append(category.title())
        
        return suggestions if suggestions else ['Other']
    
    def analyze_business_description(self, description: str) -> Dict[str, bool]:
        """Analyze a business description for delivery/shipping indicators."""
        if not description:
            return {
                'likely_delivery': False,
                'potential_worldwide_shipping': False,
                'is_logistics': False
            }
        
        text = description.lower()
        
        return {
            'likely_delivery': any(keyword in text for keyword in self.delivery_keywords),
            'potential_worldwide_shipping': any(keyword in text for keyword in self.shipping_keywords),
            'is_logistics': any(keyword in text for keyword in self.logistics_keywords)
        }
