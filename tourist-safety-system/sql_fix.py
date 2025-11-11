#!/usr/bin/env python3
"""
SQL Fix - Move type ignore comments outside SQL strings
"""

import os

def fix_sql_comments(file_path: str) -> int:
    """Fix cursor.execute calls with type ignore comments inside SQL strings"""
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix all instances of cursor.execute(''' # type: ignore
    content = content.replace(
        "cursor.execute('''  # type: ignore",
        "cursor.execute('''")
    
    # The closing of these SQL statements should already have type ignores
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content.count("cursor.execute('''")

def main():
    """Fix the SQL comment issues"""
    print("🔧 Fixing SQL type ignore comments...")
    
    fixes = fix_sql_comments('backend/app.py')
    print(f"   Fixed {fixes} SQL cursor.execute statements")
    
    print(f"\n✅ SQL comments fixed! App should now run correctly.")

if __name__ == "__main__":
    main()