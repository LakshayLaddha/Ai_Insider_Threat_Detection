from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import random
import datetime
import ipaddress
from pydantic import BaseModel

from ..database import get_db
from ..models.user import User
from ..models.activity import LoginActivity
from ..models.alert import Alert
from .auth import get_current_user

router = APIRouter()

# Simulation data models
class SimulationSettings(BaseModel):
    totalAttempts: int
    threatPercentage: float
    usernames: List[str]
    locations: List[str]
    startTime: str
    endTime: str

class LoginSimulation(BaseModel):
    isThreat: bool
    username: str = "admin@example.com"

# Country to IP range mapping (simplified)
COUNTRY_IP_RANGES = {
    "US": ["50.0.0.0/8", "23.0.0.0/8", "76.0.0.0/8"],
    "CN": ["114.0.0.0/8", "116.0.0.0/8", "220.0.0.0/8"],
    "RU": ["95.0.0.0/8", "178.0.0.0/8", "213.0.0.0/8"],
    "IN": ["103.0.0.0/8", "157.0.0.0/8", "180.0.0.0/8"],
    "BR": ["179.0.0.0/8", "191.0.0.0/8", "200.0.0.0/8"],
    "DE": ["85.0.0.0/8", "91.0.0.0/8", "217.0.0.0/8"],
    "UK": ["62.0.0.0/8", "82.0.0.0/8", "86.0.0.0/8"],
}

# User agents for simulation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36",
]

# Malicious user agents for threat simulation
SUSPICIOUS_USER_AGENTS = [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "curl/7.64.1",
    "python-requests/2.25.1",
    "wget/1.20.3",
]

def generate_ip_for_country(country_code: str) -> str:
    """Generate a random IP address from the specified country's range."""
    if country_code not in COUNTRY_IP_RANGES:
        # Default to US if country not found
        country_code = "US"
    
    # Select a random IP range for the country
    ip_range = random.choice(COUNTRY_IP_RANGES[country_code])
    
    # Parse the CIDR notation
    try:
        network = ipaddress.IPv4Network(ip_range)
        
        # Generate a random IP within that range
        # Convert to integer, add random offset, convert back to IP
        start_int = int(network.network_address)
        end_int = int(network.broadcast_address)
        random_int = random.randint(start_int, end_int)
        random_ip = str(ipaddress.IPv4Address(random_int))
        
        return random_ip
    except Exception:
        # Fallback to a simpler approach if there's an error
        return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"

def create_login_activity(
    db: Session,
    username: str,
    ip_address: str,
    user_agent: str,
    country: str,
    timestamp: datetime.datetime,
    is_success: bool,
    is_anomalous: bool
):
    """Create a login activity record in the database."""
    
    try:
        # Create LoginActivity model
        login = LoginActivity(
            user_email=username,
            ip_address=ip_address,
            user_agent=user_agent,
            country=country,
            city=f"City-{random.randint(1, 99)}",  # Simulated city
            timestamp=timestamp,
            success=is_success,
            is_anomalous=is_anomalous
        )
        
        db.add(login)
        
        # If this is an anomalous login, create an alert too
        if is_anomalous:
            alert_message = f"Suspicious login attempt for user {username} from {ip_address} ({country})"
            alert = Alert(
                alert_type="Suspicious Login",
                severity="high" if is_success else "medium",
                message=alert_message,
                source_ip=ip_address,
                location=country,
                timestamp=timestamp,
                resolved=False
            )
            db.add(alert)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error creating login activity: {e}")
        return False

@router.post("/generate")
def generate_login_data(
    settings: SimulationSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate simulated login activity data based on settings."""
    # Ensure user is an admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        # Parse time range
        start_time = datetime.datetime.fromisoformat(settings.startTime)
        end_time = datetime.datetime.fromisoformat(settings.endTime)
        if end_time <= start_time:
            raise HTTPException(status_code=400, detail="End time must be after start time")
        
        time_range_seconds = (end_time - start_time).total_seconds()
        
        # Calculate how many threats to generate
        threat_count = int(settings.totalAttempts * settings.threatPercentage / 100)
        normal_count = settings.totalAttempts - threat_count
        
        # Generate login activities
        created_threats = 0
        
        # First create normal logins
        for _ in range(normal_count):
            username = random.choice(settings.usernames)
            country = random.choice(settings.locations)
            timestamp = start_time + datetime.timedelta(seconds=random.randint(0, int(time_range_seconds)))
            ip_address = generate_ip_for_country(country)
            user_agent = random.choice(USER_AGENTS)
            
            create_login_activity(
                db=db,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                country=country,
                timestamp=timestamp,
                is_success=True,
                is_anomalous=False
            )
        
        # Then create threat logins
        for _ in range(threat_count):
            username = random.choice(settings.usernames)
            country = random.choice(settings.locations)
            timestamp = start_time + datetime.timedelta(seconds=random.randint(0, int(time_range_seconds)))
            ip_address = generate_ip_for_country(country)
            
            # Use suspicious user agent for some threats
            user_agent = random.choice(SUSPICIOUS_USER_AGENTS if random.random() < 0.7 else USER_AGENTS)
            
            # Some threats are successful logins, some are failed
            is_success = random.random() < 0.4
            
            create_login_activity(
                db=db,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                country=country,
                timestamp=timestamp,
                is_success=is_success,
                is_anomalous=True
            )
            created_threats += 1
        
        return {
            "success": True,
            "message": f"Generated {settings.totalAttempts} login records with {created_threats} threats",
            "threatCount": created_threats
        }
    
    except Exception as e:
        print(f"Error in simulator: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating data: {str(e)}")

@router.post("/login")
def simulate_login(
    data: LoginSimulation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simulate a single login event in real time."""
    # Ensure user is an admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        # Generate random parameters
        country = random.choice(["US", "CN", "RU", "IN", "BR", "DE", "UK"])
        ip_address = generate_ip_for_country(country)
        timestamp = datetime.datetime.now()
        
        if data.isThreat:
            user_agent = random.choice(SUSPICIOUS_USER_AGENTS)
            is_success = random.random() < 0.6  # 60% chance of successful threat
        else:
            user_agent = random.choice(USER_AGENTS)
            is_success = random.random() < 0.95  # 95% chance of successful normal login
        
        create_login_activity(
            db=db,
            username=data.username,
            ip_address=ip_address,
            user_agent=user_agent,
            country=country,
            timestamp=timestamp,
            is_success=is_success,
            is_anomalous=data.isThreat
        )
        
        return {"success": True, "message": "Login simulation created"}
    
    except Exception as e:
        print(f"Error simulating login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error simulating login: {str(e)}")