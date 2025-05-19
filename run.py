import uvicorn
import os
from geo import get_ip_info  # Import your geo.py function

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    # Test: Fetch geolocation of a sample IP (e.g., 8.8.8.8) before starting the server
    ip_info = get_ip_info("8.8.8.8")
    print(f"Sample IP Info: {ip_info}")  # Print geolocation info to verify

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
