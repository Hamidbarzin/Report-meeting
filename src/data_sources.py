"""
Data sources for fetching business information from Yelp and OpenStreetMap.
"""

import requests
import overpy
from typing import List, Dict, Optional
import os
import time
from abc import ABC, abstractmethod
from cachetools import TTLCache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseDataSource(ABC):
    """Abstract base class for data sources."""
    
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour cache
    
    @abstractmethod
    def search_businesses(self, search_term: str, categories: List[str], max_results: int) -> List[Dict]:
        """Search for businesses based on criteria."""
        pass

class YelpDataSource(BaseDataSource):
    """Yelp Fusion API data source."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("YELP_API_KEY")
        self.base_url = "https://api.yelp.com/v3/businesses/search"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Toronto coordinates
        self.toronto_lat = float(os.getenv("TORONTO_LAT", "43.6532"))
        self.toronto_lon = float(os.getenv("TORONTO_LON", "-79.3832"))
        self.radius = int(os.getenv("TORONTO_RADIUS", "50000"))  # 50km radius
    
    def search_businesses(self, search_term: str, categories: List[str], max_results: int) -> List[Dict]:
        """Search businesses using Yelp Fusion API."""
        
        if not self.api_key:
            raise ValueError("Yelp API key not found")
        
        # Create cache key
        cache_key = f"yelp_{search_term}_{'_'.join(categories)}_{max_results}"
        
        if cache_key in self.cache:
            logger.info("Returning cached results")
            return self.cache[cache_key]
        
        businesses = []
        offset = 0
        limit = min(50, max_results)  # Yelp max is 50 per request
        
        while len(businesses) < max_results and offset < 1000:  # Yelp max offset is 1000
            try:
                # Prepare search parameters
                params = {
                    "latitude": self.toronto_lat,
                    "longitude": self.toronto_lon,
                    "radius": self.radius,
                    "limit": limit,
                    "offset": offset,
                    "sort_by": "rating"
                }
                
                if search_term:
                    params["term"] = search_term
                
                # Add categories if specified
                if categories and "Logistics & Freight" not in categories:
                    # Map our categories to Yelp categories
                    yelp_categories = self._map_categories_to_yelp(categories)
                    if yelp_categories:
                        params["categories"] = ",".join(yelp_categories)
                
                # Make API request
                response = requests.get(self.base_url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                business_list = data.get("businesses", [])
                
                if not business_list:
                    break
                
                # Process businesses
                for business in business_list:
                    processed_business = self._process_yelp_business(business)
                    if processed_business:
                        businesses.append(processed_business)
                
                offset += limit
                
                # Rate limiting
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Yelp API error: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break
        
        # Cache results
        self.cache[cache_key] = businesses[:max_results]
        
        return businesses[:max_results]
    
    def _map_categories_to_yelp(self, categories: List[str]) -> List[str]:
        """Map our categories to Yelp API categories."""
        category_mapping = {
            "Restaurant": "restaurants",
            "Grocery": "grocery",
            "Pharmacy": "pharmacy",
            "Florist": "flowers",
            "Bakery": "bakeries",
            "Electronics": "electronics",
            "Clothing": "shopping",
            "Logistics & Freight": "shipping_centers"
        }
        
        return [category_mapping.get(cat, "") for cat in categories if cat in category_mapping]
    
    def _process_yelp_business(self, business: Dict) -> Optional[Dict]:
        """Process a Yelp business object into our standard format."""
        try:
            return {
                "name": business.get("name", ""),
                "category": ", ".join([cat.get("title", "") for cat in business.get("categories", [])]),
                "phone": business.get("display_phone", ""),
                "address": self._format_address(business.get("location", {})),
                "url": business.get("url", ""),
                "rating": business.get("rating", 0),
                "review_count": business.get("review_count", 0),
                "latitude": business.get("coordinates", {}).get("latitude"),
                "longitude": business.get("coordinates", {}).get("longitude"),
                "price": business.get("price", ""),
                "is_closed": business.get("is_closed", False)
            }
        except Exception as e:
            logger.error(f"Error processing business: {e}")
            return None
    
    def _format_address(self, location: Dict) -> str:
        """Format address from Yelp location object."""
        address_parts = []
        
        if location.get("address1"):
            address_parts.append(location["address1"])
        if location.get("address2"):
            address_parts.append(location["address2"])
        if location.get("city"):
            address_parts.append(location["city"])
        if location.get("state"):
            address_parts.append(location["state"])
        if location.get("zip_code"):
            address_parts.append(location["zip_code"])
        
        return ", ".join(address_parts)

class OSMDataSource(BaseDataSource):
    """OpenStreetMap/Overpass API data source."""
    
    def __init__(self):
        super().__init__()
        self.api = overpy.Overpass()
        
        # Toronto bounding box
        self.toronto_bbox = "43.5810,-79.6392,43.8555,-79.1156"  # lat_min,lon_min,lat_max,lon_max
    
    def search_businesses(self, search_term: str, categories: List[str], max_results: int) -> List[Dict]:
        """Search businesses using OpenStreetMap/Overpass API."""
        
        # Create cache key
        cache_key = f"osm_{search_term}_{'_'.join(categories)}_{max_results}"
        
        if cache_key in self.cache:
            logger.info("Returning cached results")
            return self.cache[cache_key]
        
        businesses = []
        
        try:
            # Build Overpass QL query
            query = self._build_overpass_query(search_term, categories, max_results)
            
            # Execute query
            result = self.api.query(query)
            
            # Process results
            for node in result.nodes:
                business = self._process_osm_node(node)
                if business:
                    businesses.append(business)
            
            for way in result.ways:
                business = self._process_osm_way(way)
                if business:
                    businesses.append(business)
            
            for relation in result.relations:
                business = self._process_osm_relation(relation)
                if business:
                    businesses.append(business)
        
        except Exception as e:
            logger.error(f"OSM API error: {e}")
        
        # Cache results
        self.cache[cache_key] = businesses[:max_results]
        
        return businesses[:max_results]
    
    def _build_overpass_query(self, search_term: str, categories: List[str], max_results: int) -> str:
        """Build Overpass QL query for business search."""
        
        # Map categories to OSM tags
        osm_tags = self._map_categories_to_osm(categories)
        
        # Build tag filter
        tag_filter = " or ".join([f"['{tag}']" for tag in osm_tags])
        
        # Add search term filter if provided
        name_filter = ""
        if search_term:
            name_filter = f"['name'~'{search_term}',i]"
        
        query = f"""
        [out:json][timeout:25];
        (
          node[{tag_filter}]{name_filter}({self.toronto_bbox});
          way[{tag_filter}]{name_filter}({self.toronto_bbox});
          relation[{tag_filter}]{name_filter}({self.toronto_bbox});
        );
        out center meta;
        """
        
        return query
    
    def _map_categories_to_osm(self, categories: List[str]) -> List[str]:
        """Map our categories to OSM tags."""
        category_mapping = {
            "Restaurant": "amenity=restaurant",
            "Grocery": "shop=supermarket",
            "Pharmacy": "amenity=pharmacy",
            "Florist": "shop=florist",
            "Bakery": "shop=bakery",
            "Electronics": "shop=electronics",
            "Clothing": "shop=clothes",
            "Logistics & Freight": "amenity=post_office"
        }
        
        return [category_mapping.get(cat, "") for cat in categories if cat in category_mapping]
    
    def _process_osm_node(self, node) -> Optional[Dict]:
        """Process an OSM node into our standard format."""
        try:
            tags = node.tags
            
            return {
                "name": tags.get("name", ""),
                "category": self._get_osm_category(tags),
                "phone": tags.get("phone", ""),
                "address": self._format_osm_address(tags),
                "url": tags.get("website", ""),
                "rating": 0,  # OSM doesn't have ratings
                "review_count": 0,  # OSM doesn't have review counts
                "latitude": node.lat,
                "longitude": node.lon,
                "osm_id": node.id,
                "osm_type": "node"
            }
        except Exception as e:
            logger.error(f"Error processing OSM node: {e}")
            return None
    
    def _process_osm_way(self, way) -> Optional[Dict]:
        """Process an OSM way into our standard format."""
        try:
            tags = way.tags
            
            # Get center coordinates
            center_lat = way.center_lat
            center_lon = way.center_lon
            
            return {
                "name": tags.get("name", ""),
                "category": self._get_osm_category(tags),
                "phone": tags.get("phone", ""),
                "address": self._format_osm_address(tags),
                "url": tags.get("website", ""),
                "rating": 0,
                "review_count": 0,
                "latitude": center_lat,
                "longitude": center_lon,
                "osm_id": way.id,
                "osm_type": "way"
            }
        except Exception as e:
            logger.error(f"Error processing OSM way: {e}")
            return None
    
    def _process_osm_relation(self, relation) -> Optional[Dict]:
        """Process an OSM relation into our standard format."""
        try:
            tags = relation.tags
            
            return {
                "name": tags.get("name", ""),
                "category": self._get_osm_category(tags),
                "phone": tags.get("phone", ""),
                "address": self._format_osm_address(tags),
                "url": tags.get("website", ""),
                "rating": 0,
                "review_count": 0,
                "latitude": None,  # Relations don't have direct coordinates
                "longitude": None,
                "osm_id": relation.id,
                "osm_type": "relation"
            }
        except Exception as e:
            logger.error(f"Error processing OSM relation: {e}")
            return None
    
    def _get_osm_category(self, tags: Dict) -> str:
        """Extract category from OSM tags."""
        if "amenity" in tags:
            return tags["amenity"].replace("_", " ").title()
        elif "shop" in tags:
            return tags["shop"].replace("_", " ").title()
        elif "tourism" in tags:
            return tags["tourism"].replace("_", " ").title()
        else:
            return "Unknown"
    
    def _format_osm_address(self, tags: Dict) -> str:
        """Format address from OSM tags."""
        address_parts = []
        
        if tags.get("addr:housenumber"):
            address_parts.append(tags["addr:housenumber"])
        if tags.get("addr:street"):
            address_parts.append(tags["addr:street"])
        if tags.get("addr:city"):
            address_parts.append(tags["addr:city"])
        if tags.get("addr:state"):
            address_parts.append(tags["addr:state"])
        if tags.get("addr:postcode"):
            address_parts.append(tags["addr:postcode"])
        
        return ", ".join(address_parts)
