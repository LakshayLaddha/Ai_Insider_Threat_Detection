
import os
import sys
import re
import importlib
import traceback

# Add current directory to path
sys.path.append('/app')
print("Current directory files:", os.listdir('/app'))

def update_main():
    # Path to main.py
    main_path = os.path.join('/app', 'main.py')
    
    if not os.path.exists(main_path):
        print(f"Main app file not found at: {main_path}")
        # Try to look for it elsewhere
        for root, dirs, files in os.walk('/app'):
            if 'main.py' in files:
                main_path = os.path.join(root, 'main.py')
                print(f"Found main.py at: {main_path}")
                break
    
    if not os.path.exists(main_path):
        print("Could not find main.py anywhere in the app directory")
        return False
    
    # Create a backup
    with open(main_path, 'r') as f:
        original_content = f.read()
    
    # Save backup
    backup_path = main_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(original_content)
    print(f"Created backup at {backup_path}")
    
    # Check if 'fixed_router' is already imported
    if 'from fixed_router import router' in original_content:
        print("Fixed router already imported, skipping update")
        return True
    
    # Find import statements to add our import after
    import_loc = -1
    app_loc = -1
    include_router_loc = -1
    
    lines = original_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            import_loc = i
        if 'FastAPI(' in line:
            app_loc = i
        if '.include_router(' in line:
            include_router_loc = i
    
    if import_loc >= 0:
        # Add our import after the last import
        lines.insert(import_loc + 1, 'from fixed_router import router as fixed_router')
        
        # If we found where routers are included, add ours
        if include_router_loc >= 0:
            lines.insert(include_router_loc + 1, 'app.include_router(fixed_router)')
        # Otherwise add it after app creation
        elif app_loc >= 0:
            lines.insert(app_loc + 1, 'app.include_router(fixed_router)')
        else:
            # Last resort - add at the end
            lines.append('# Adding fixed router')
            lines.append('try:')
            lines.append('    app.include_router(fixed_router)')
            lines.append('except Exception as e:')
            lines.append('    print(f"Error including fixed router: {e}")')
        
        # Write updated content
        with open(main_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print("Successfully updated main.py to include fixed router")
        return True
    else:
        print("Could not find appropriate place to insert import in main.py")
        return False

# Run the update
update_main()
