import ipinfo
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

access_token = os.getenv("IPINFO_TOKEN")
handler = ipinfo.getHandler(access_token)

def get_ip_info(ip_address):
    details = handler.getDetails(ip_address)
    return {
        "ip": ip_address,
        "city": details.city,
        "region": details.region,
        "country": details.country_name,
        "location": details.loc
    }
