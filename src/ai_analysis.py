"""
AI-powered analysis for business delivery and shipping potential.
"""

import openai
import os
from typing import Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI-powered business analysis using OpenAI API."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("OpenAI API key not found. AI analysis will be disabled.")
    
    def analyze_business(self, business: Dict) -> Dict[str, bool]:
        """
        Analyze a business using AI to determine delivery/shipping potential.
        
        Args:
            business: Business data dictionary
            
        Returns:
            Dictionary with AI analysis results
        """
        if not self.api_key:
            return {
                'ai_likely_delivery': False,
                'ai_potential_worldwide_shipping': False,
                'ai_is_logistics': False,
                'ai_confidence': 0.0
            }
        
        try:
            # Prepare business information for analysis
            business_info = self._prepare_business_info(business)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(business_info)
            
            # Call OpenAI API
            response = self._call_openai_api(prompt)
            
            # Parse response
            analysis_result = self._parse_ai_response(response)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                'ai_likely_delivery': False,
                'ai_potential_worldwide_shipping': False,
                'ai_is_logistics': False,
                'ai_confidence': 0.0
            }
    
    def _prepare_business_info(self, business: Dict) -> str:
        """Prepare business information for AI analysis."""
        info_parts = []
        
        if business.get('name'):
            info_parts.append(f"Business Name: {business['name']}")
        
        if business.get('category'):
            info_parts.append(f"Category: {business['category']}")
        
        if business.get('address'):
            info_parts.append(f"Address: {business['address']}")
        
        if business.get('url'):
            info_parts.append(f"Website: {business['url']}")
        
        if business.get('rating'):
            info_parts.append(f"Rating: {business['rating']}/5")
        
        if business.get('review_count'):
            info_parts.append(f"Review Count: {business['review_count']}")
        
        return "\n".join(info_parts)
    
    def _create_analysis_prompt(self, business_info: str) -> str:
        """Create a prompt for AI analysis."""
        return f"""
        Analyze the following Toronto business to determine its potential for delivery services and international shipping needs.
        
        Business Information:
        {business_info}
        
        Please analyze this business and determine:
        1. Does this business likely need delivery services? (Consider if it's a restaurant, retail store, pharmacy, etc.)
        2. Does this business have potential for international shipping? (Consider if it sells products that could be shipped globally)
        3. Is this business a logistics/freight service provider? (Consider if it provides shipping, courier, or logistics services)
        
        Respond with a JSON object in this exact format:
        {{
            "likely_delivery": true/false,
            "potential_worldwide_shipping": true/false,
            "is_logistics": true/false,
            "confidence": 0.0-1.0,
            "reasoning": "Brief explanation of your analysis"
        }}
        
        Consider:
        - Business type and category
        - Location (Toronto businesses)
        - Website presence
        - Rating and review count (indicates online presence)
        - Business name keywords
        
        Be conservative in your analysis - only mark as true if there's strong evidence.
        """
    
    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with the analysis prompt."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst specializing in e-commerce and logistics. Analyze businesses for their delivery and shipping potential."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _parse_ai_response(self, response: str) -> Dict[str, bool]:
        """Parse AI response and extract analysis results."""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                
                return {
                    'ai_likely_delivery': analysis.get('likely_delivery', False),
                    'ai_potential_worldwide_shipping': analysis.get('potential_worldwide_shipping', False),
                    'ai_is_logistics': analysis.get('is_logistics', False),
                    'ai_confidence': analysis.get('confidence', 0.0),
                    'ai_reasoning': analysis.get('reasoning', '')
                }
            else:
                # Fallback: try to extract boolean values from text
                return self._extract_booleans_from_text(response)
                
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return self._extract_booleans_from_text(response)
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                'ai_likely_delivery': False,
                'ai_potential_worldwide_shipping': False,
                'ai_is_logistics': False,
                'ai_confidence': 0.0,
                'ai_reasoning': 'Error parsing response'
            }
    
    def _extract_booleans_from_text(self, text: str) -> Dict[str, bool]:
        """Extract boolean values from text response as fallback."""
        text_lower = text.lower()
        
        return {
            'ai_likely_delivery': 'likely_delivery' in text_lower and 'true' in text_lower,
            'ai_potential_worldwide_shipping': 'potential_worldwide_shipping' in text_lower and 'true' in text_lower,
            'ai_is_logistics': 'is_logistics' in text_lower and 'true' in text_lower,
            'ai_confidence': 0.5,  # Default confidence
            'ai_reasoning': text[:200] + '...' if len(text) > 200 else text
        }
    
    def batch_analyze_businesses(self, businesses: list) -> list:
        """Analyze multiple businesses in batch for efficiency."""
        if not self.api_key:
            return businesses
        
        # For now, analyze one by one
        # In the future, this could be optimized for batch processing
        analyzed_businesses = []
        
        for business in businesses:
            try:
                analysis_result = self.analyze_business(business)
                business.update(analysis_result)
                analyzed_businesses.append(business)
            except Exception as e:
                logger.error(f"Error analyzing business {business.get('name', 'Unknown')}: {e}")
                analyzed_businesses.append(business)
        
        return analyzed_businesses
    
    def is_available(self) -> bool:
        """Check if AI analysis is available."""
        return self.api_key is not None
