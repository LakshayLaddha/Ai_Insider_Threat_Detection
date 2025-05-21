# Import models so they are registered with SQLAlchemy
from .user import User
from .activity import LoginActivity, FileActivity
from .alert import Alert  # This now correctly points to alert.py