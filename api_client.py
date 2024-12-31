import requests
import json
from datetime import datetime
from typing import Dict, Any

class FoxholeAPI:
    """Client for the Foxhole War API with caching support"""
    
    BASE_URL = "https://war-service-live.foxholeservices.com/api/worldconquest"
    
    def __init__(self):
        self.session = requests.Session()
        self.etags = {}  # Store ETags for each endpoint
        self.cache = {}  # Store cached responses
        
    def _make_request(self, endpoint, params=None):
        """Make an API request with ETag support"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {}
        
        # Add If-None-Match header if we have a cached ETag
        if endpoint in self.etags:
            headers['If-None-Match'] = self.etags[endpoint]
        
        response = self.session.get(url, headers=headers, params=params)
        
        # Handle 304 Not Modified
        if response.status_code == 304:
            print(f"Cache hit for {endpoint}")
            return self.cache[endpoint]
        
        # Handle successful response
        if response.status_code == 200:
            # Store the new ETag if provided
            if 'ETag' in response.headers:
                self.etags[endpoint] = response.headers['ETag']
                self.cache[endpoint] = response.json()
            return response.json()
        
        # Handle errors
        response.raise_for_status()
        return None

    def get_map_data(self, map_name: str) -> Dict[str, Any]:
        """
        Fetch dynamic map data for a specific map
        
        Args:
            map_name: Name of the map to fetch data for
            
        Returns:
            Dictionary containing map data
        """
        return self._make_request(f"maps/{map_name}/dynamic/public")

    def get_static_map_data(self, map_name: str) -> Dict[str, Any]:
        """Get static map data (text labels, etc) for a specific map"""
        return self._make_request(f"maps/{map_name}/static")

    def get_war_data(self) -> Dict[str, Any]:
        """
        Fetch current war data
        
        Returns:
            Dictionary containing war status data
        """
        return self._make_request("war")

    def get_war_report(self, map_name: str) -> Dict[str, Any]:
        """
        Get war report data for a specific map
        
        Args:
            map_name: Name of the map to fetch war report data for
            
        Returns:
            Dictionary containing war report data
        """
        return self._make_request(f"warReport/{map_name}")
