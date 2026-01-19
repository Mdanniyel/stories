import os
import re

def clean_filename(filename):
    # Separate extension
    name, ext = os.path.splitext(filename)
    
    # Replace underscores with hyphens
    name = name.replace('_', '-')
    
    # Replace any character that is NOT alphanumeric (Hebrew included) with hyphen
    # Unicode range for Hebrew is \u0590-\u05FF
    # We keep English letters, numbers, and Hebrew letters.
    name = re.sub(r'[^0-9a-zA-Z\u0590-\u05FF]+', '-', name)
    
    # Collapse multiple hyphens into one
    name = re.sub(r'-+', '-', name)
    
    # Remove leading/trailing hyphens
    name = name.strip('-')
    
    return name + ext

def main():
    # Use absolute path to be safe, or relative to where script is run
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, 'src', 'content', 'stories')
    
    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        print("Please ensure you are running this script from the project root.")
        return

    print(f"Scanning directory: {target_dir}")
    
    count = 0
    errors = 0
    
    # Get list of files first to avoid modifying list while iterating
    files = os.listdir(target_dir)
    
    for filename in files:
        old_path = os.path.join(target_dir, filename)
        
        if not os.path.isfile(old_path):
            continue
            
        if filename.startswith('.'): # Skip hidden files
            continue

        new_filename = clean_filename(filename)
        
        if new_filename != filename:
            new_path = os.path.join(target_dir, new_filename)
            
            # Simple check to avoid overwriting if a file with the target name already exists
            # (unless it's a case-insensitive match on the same file system, but Python rename usually handles case change fine on Mac)
            if os.path.exists(new_path) and new_filename != filename:
                 print(f"SKIP: {filename} -> {new_filename} (Target file already exists)")
                 errors += 1
                 continue

            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")
                count += 1
            except OSError as e:
                print(f"Error renaming {filename}: {e}")
                errors += 1

    print(f"\nDone! Renamed {count} files.")
    if errors > 0:
        print(f"Encountered {errors} errors or skips.")

if __name__ == "__main__":
    main()
