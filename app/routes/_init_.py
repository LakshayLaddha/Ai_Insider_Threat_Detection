# Import routes to make them available
# You may need to adjust this based on your actual route imports
import importlib.util

# Try importing your routes, but don't fail if one is missing
for module in ['auth', 'users', 'activities', 'dashboard']:
    try:
        __import__(f'app.routes.{module}')
    except ImportError:
        pass