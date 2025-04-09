
import sys
import os

# Add function to directly patch the API endpoint files
def patch_files():
    # Look for potential files to patch
    candidates = []
    for root, dirs, files in os.walk('/app'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        # Look for code that might have the date index error or prediction logic
                        if "predict" in content and ("['date']" in content or "Exception" in content):
                            candidates.append((file_path, content))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    print(f"Found {len(candidates)} files that might need patching")
    
    # Import the fixed feature extraction function
    from api_direct_fix import fixed_extract_features
    
    # Patch each file
    for file_path, content in candidates:
        print(f"Examining: {file_path}")
        
        # Create a backup
        backup_path = file_path + '.bak_direct'
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"Created backup at: {backup_path}")
        
        # Add our fix at the top of the file
        fix_import = "from api_direct_fix import fixed_extract_features\n"
        
        # Look for predict endpoint or function
        if "@app.post('/predict')" in content or "def predict" in content:
            print(f"Found prediction endpoint in {file_path}, patching...")
            
            # Add import at the top
            if "from api_direct_fix import" not in content:
                # Find a good place to insert our import
                if "import" in content:
                    last_import = content.rfind("import")
                    last_import_end = content.find("\n", last_import)
                    content = content[:last_import_end+1] + "\n" + fix_import + content[last_import_end+1:]
                else:
                    content = fix_import + "\n" + content
            
            # Replace error-prone feature extraction with direct call to our function
            if "['date']" in content:
                # Look for the block of code that extracts features
                try:
                    # Common pattern: features = extract_features(log_entry)
                    if "features = " in content and "extract_features" in content:
                        content = content.replace("features = extract_features(log_entry)", 
                                                "features = fixed_extract_features(log_entry)")
                    
                    # Another pattern: df = pd.DataFrame(...)[features]
                    elif "df = pd.DataFrame" in content and "['date']" in content:
                        content = content.replace("df = pd.DataFrame([log_entry])", 
                                                "features = fixed_extract_features(log_entry)\n    df = pd.DataFrame([features])")
                    
                    # Catch-all for any other references
                    elif "['date']" in content:
                        # Insert error handling around date references
                        content = content.replace("['date']", 
                                               ".get('date', datetime.now().strftime('%Y-%m-%d'))")
                except Exception as e:
                    print(f"Error during replacement: {e}")
            
            # Save the modified file
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"Successfully patched {file_path}")
            except Exception as e:
                print(f"Error saving patched file: {e}")

# Run the patching
patch_files()
print("Direct patch complete!")
