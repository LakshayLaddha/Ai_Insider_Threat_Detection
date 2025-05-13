import logging
import ipinfo
from typing import Optional, Dict, Any, Tuple

from ..config import settings

logger = logging.getLogger(__name__)


class IPInfoService:
    """Service for getting location data from IP addresses using IPinfo."""
    
    def __init__(self, api_token: str = settings.IPINFO_API_TOKEN):
        """
        Initialize IPInfo service with API token.
        
        Args:
            api_token: IPinfo API token
        """
        self.api_token = api_token
        self.handler = ipinfo.getHandler(api_token)
        logger.info("IPInfo service initialized")
    
    def get_location_data(self, ip_address: str) -> Dict[str, Any]:
        """
        Get location data for an IP address.
        
        Args:
            ip_address: IP address to look up.
            
        Returns:
            Dictionary with location information.
        """
        result = {
            "country": None,
            "city": None,
            "latitude": None,
            "longitude": None
        }
        
        try:
            # Skip lookup for private/local IP addresses
            if ip_address in ("127.0.0.1", "localhost", "::1") or ip_address.startswith("192.168.") or ip_address.startswith("10."):
                return result
            
            # Get details from IPinfo
            details = self.handler.getDetails(ip_address)
            
            # Extract location information
            result["country"] = details.country_name
            result["city"] = details.city
            
            # Extract coordinates if available
            if hasattr(details, 'latitude') and hasattr(details, 'longitude'):
                result["latitude"] = float(details.latitude) if details.latitude else None
                result["longitude"] = float(details.longitude) if details.longitude else None
            elif hasattr(details, 'loc') and details.loc:
                try:
                    lat, lon = details.loc.split(',')
                    result["latitude"] = float(lat)
                    result["longitude"] = float(lon)
                except (ValueError, TypeError):
                    pass
                    
            return result
        except Exception as e:
            logger.error(f"Error looking up IP address {ip_address}: {str(e)}")
            return result
    
    def is_unusual_location(self, ip_address: str, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if the location is unusual for this user.
        
        Args:
            ip_address: Current IP address.
            user_id: User ID to check against.
            
        Returns:
            Tuple of (is_unusual, reason)
        """
        # TODO: Implement logic to check if location is unusual based on user's history
        # For now, just return a placeholder
        return False, None


# Singleton instance
geoip_service = IPInfoService()