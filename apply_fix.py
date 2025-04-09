import os
import sys
import re

# Find the Python file that contains the feature engineering code
python_files = []
for root, dirs, files in os.walk('/app'):
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))

# Look for feature engineering code patterns in each file
feature_files = []
for file_path in python_files:
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Look for typical feature engineering patterns
            if ('feature_engineering' in content or 
                'extract_features' in content or
                'preprocess_log' in content or
                'transform_log' in content or
                ("['date']" in content and 'not in index' in content)):
                feature_files.append((file_path, content))
    except:
        pass

print(f"Found {len(feature_files)} potential feature engineering files")

# Import our fixed feature engineering code
from feature_engineering_fix import extract_features

# Create a backup of the original file and apply our fix
for file_path, content in feature_files:
    print(f"Examining {file_path}")
    
    # Create backup
    backup_path = file_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Look for relevant functions to replace
    modified = False
    
    # Pattern 1: Replace an extract_features function
    if 'def extract_features' in content:
        print("Found extract_features function, replacing...")
        new_content = re.sub(
            r'def extract_features\([^)]*\):.*?(?=def|\Z)', 
            'def extract_features(log_entry):\n    # Fixed function imported from feature_engineering_fix\n    from feature_engineering_fix import extract_features as fixed_extract_features\n    return fixed_extract_features(log_entry)\n\n', 
            content, 
            flags=re.DOTALL
        )
        modified = True
    
    # Pattern 2: Look for the specific date index error and fix it
    elif "['date']" in content and 'not in index' in content:
        print("Found date index error, adding fix...")
        # Add import at the top of the file
        if 'from feature_engineering_fix import extract_features' not in content:
            import_line = 'from feature_engineering_fix import extract_features\n'
            if 'import ' in content:
                # Add after the last import
                last_import = content.rfind('import ')
                last_import_line_end = content.find('\n', last_import)
                new_content = content[:last_import_line_end + 1] + '\n' + import_line + content[last_import_line_end + 1:]
            else:
                # Add at the top
                new_content = import_line + content
            modified = True
    
    # If we modified the file, write the changes
    if modified:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Applied fix to {file_path}")