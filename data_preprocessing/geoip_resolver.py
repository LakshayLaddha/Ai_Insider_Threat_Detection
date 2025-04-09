import pandas as pd
import requests
import time
from typing import Dict, Any, List, Optional
import json
import os

class GeoIPResolver:
    """
    Resolves IP addresses to geographic locations using free IP API services.
    Handles rate limiting and caching for efficiency.
    """
    
    def __init__(self, cache_file: str = '../config/ip_cache.json'):
        """
        Initialize the GeoIP resolver.
        
        Args:
            cache_file: Path to JSON file for caching IP resolutions
        """
        self.cache_file = cache_file
        self.ip_cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load previously cached IP data if available."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.ip_cache = json.load(f)
                print(f"Loaded {len(self.ip_cache)} cached IP records")
            except Exception as e:
                print(f"Error loading IP cache: {e}")
                self.ip_cache = {}
    
    def _save_cache(self):
        """Save the IP cache to disk."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.ip_cache, f)
        except Exception as e:
            print(f"Error saving IP cache: {e}")
    
    def resolve_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Resolve a single IP address to geographic information.
        Uses cache if available, otherwise queries API.
        
        Args:
            ip_address: The IP address to resolve
            
        Returns:
            Dictionary with geolocation data
        """
        # Check cache first
        if ip_address in self.ip_cache:
            return self.ip_cache[ip_address]
        
        # Query the free IP-API service
        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Create a standardized response
                geo_data = {
                    "ip": ip_address,
                    "country": data.get("country", "Unknown"),
                    "country_code": data.get("countryCode", ""),
                    "region": data.get("regionName", ""),
                    "city": data.get("city", "Unknown"),
                    "latitude": data.get("lat", 0),
                    "longitude": data.get("lon", 0),
                    "isp": data.get("isp", "Unknown"),
                    "org": data.get("org", ""),
                    "timezone": data.get("timezone", "")
                }
                
                # Cache the result
                self.ip_cache[ip_address] = geo_data
                
                # Periodically save cache
                if len(self.ip_cache) % 10 == 0:
                    self._save_cache()
                
                # Respect rate limits (1000 requests/day = ~1 request per 86 seconds)
                time.sleep(0.1)
                
                return geo_data
            else:
                print(f"Failed to resolve IP {ip_address}: HTTP {response.status_code}")
                return self._get_default_geo_data(ip_address)
                
        except Exception as e:
            print(f"Error resolving IP {ip_address}: {e}")
            return self._get_default_geo_data(ip_address)
    
    def _get_default_geo_data(self, ip_address: str) -> Dict[str, Any]:
        """Return default geo data for failed resolutions."""
        return {
            "ip": ip_address,
            "country": "Unknown",
            "country_code": "",
            "region": "",
            "city": "Unknown",
            "latitude": 0,
            "longitude": 0,
            "isp": "Unknown",
            "org": "",
            "timezone": ""
        }
    
    def batch_resolve(self, df: pd.DataFrame, ip_column: str = 'ip_address', 
                      max_ips: Optional[int] = None, 
                      sample_if_large: bool = True) -> pd.DataFrame:
        """
        Resolve all IPs in a dataframe and add geolocation columns.
        
        Args:
            df: DataFrame containing IP addresses
            ip_column: Column name containing IPs
            max_ips: Maximum number of IPs to resolve (for testing)
            sample_if_large: If True, sample the dataframe if it's large
            
        Returns:
            DataFrame with added geolocation columns
        """
        # Create a copy of the dataframe to avoid modifying the original
        result_df = df.copy()
        
        # Extract unique IPs to avoid resolving duplicates
        unique_ips = df[ip_column].unique()
        
        # Optionally limit the number of IPs to resolve
        if max_ips and len(unique_ips) > max_ips:
            if sample_if_large:
                print(f"Sampling {max_ips} IPs from {len(unique_ips)} unique IPs")
                import random
                unique_ips = random.sample(list(unique_ips), max_ips)
            else:
                unique_ips = unique_ips[:max_ips]
        
        print(f"Resolving {len(unique_ips)} unique IP addresses...")
        
        # Create a mapping of IP -> geo data
        ip_to_geo = {}
        for i, ip in enumerate(unique_ips):
            ip_to_geo[ip] = self.resolve_ip(ip)
            if i % 10 == 0:
                print(f"Resolved {i}/{len(unique_ips)} IPs...")
        
        # Save complete cache
        self._save_cache()
        
        # Add geo columns to the dataframe
        result_df['geo_country'] = result_df[ip_column].map(lambda ip: ip_to_geo.get(ip, {}).get('country', 'Unknown'))
        result_df['geo_city'] = result_df[ip_column].map(lambda ip: ip_to_geo.get(ip, {}).get('city', 'Unknown'))
        result_df['geo_latitude'] = result_df[ip_column].map(lambda ip: ip_to_geo.get(ip, {}).get('latitude', 0))
        result_df['geo_longitude'] = result_df[ip_column].map(lambda ip: ip_to_geo.get(ip, {}).get('longitude', 0))
        result_df['geo_isp'] = result_df[ip_column].map(lambda ip: ip_to_geo.get(ip, {}).get('isp', 'Unknown'))
        
        return result_df

if __name__ == "__main__":
    # Example usage
    import pandas as pd
    
    # Load sample logs
    try:
        logs_df = pd.read_csv('../logs/sample_logs.csv')
        
        # Initialize resolver
        resolver = GeoIPResolver()
        
        # Resolve IPs (limit to 20 for testing)
        geo_df = resolver.batch_resolve(logs_df, max_ips=20)
        
        # Display results
        print("\nSample enriched log entries:")
        print(geo_df[['user_id', 'ip_address', 'geo_country', 'geo_city', 'geo_isp']].head(10))
        
        # Save enriched data
        geo_df.to_csv('../logs/geo_enriched_logs.csv', index=False)
        print(f"Saved geo-enriched logs to ../logs/geo_enriched_logs.csv")
        
    except FileNotFoundError:
        print("Error: Sample logs file not found. Run the log generator first.")