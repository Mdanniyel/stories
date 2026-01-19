import os
import re
import shutil
from datetime import datetime

def extract_year_from_file(filepath):
    """
    Reads the file and attempts to extract the date from the frontmatter.
    Returns the year as a string, or 'unknown' if not found/parseable.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for date: "YYYY-MM-DD" or date: YYYY-MM-DD
        match = re.search(r'^date:\s*["\']?(\d{4})-\d{2}-\d{2}["\']?', content, re.MULTILINE)
        if match:
            return match.group(1)
        
        return 'unknown'
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 'unknown'

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stories_dir = os.path.join(base_dir, 'src', 'content', 'stories')

    if not os.path.exists(stories_dir):
        print(f"Directory not found: {stories_dir}")
        return

    print(f"Scanning directory: {stories_dir}")

    # Get list of items in the directory
    items = os.listdir(stories_dir)
    
    count_moved = 0
    count_errors = 0

    for item in items:
        item_path = os.path.join(stories_dir, item)
        
        # Skip if it's a directory (we only want to move files)
        if os.path.isdir(item_path):
            continue

        # Skip non-markdown files (optional, but good practice)
        if not item.endswith('.md'):
            continue
            
        year = extract_year_from_file(item_path)
        
        # Create year directory if it doesn't exist
        year_dir = os.path.join(stories_dir, year)
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
            
        new_path = os.path.join(year_dir, item)
        
        try:
            shutil.move(item_path, new_path)
            # print(f"Moved: {item} -> {year}/{item}") # Commented out to reduce noise
            count_moved += 1
        except Exception as e:
            print(f"Error moving {item}: {e}")
            count_errors += 1

    print(f"\nDone! Moved {count_moved} files.")
    if count_errors > 0:
        print(f"Encountered {count_errors} errors.")

if __name__ == "__main__":
    main()
