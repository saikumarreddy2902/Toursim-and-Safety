#!/usr/bin/env python3
"""
Fix SQL Comments - Remove extra closing parentheses
"""

import os

def fix_sql_parentheses(file_path: str) -> int:
    """Fix all the SQL comment lines with extra closing parentheses"""
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all instances of the malformed pattern
    original_content = content
    content = content.replace("''')  # type: ignore)", "''')  # type: ignore")
    
    fixes = original_content.count("''')  # type: ignore)") - content.count("''')  # type: ignore)")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return fixes

def main():
    """Fix the SQL parentheses issues"""
    print("🔧 Fixing SQL comment parentheses...")
    
    fixes = fix_sql_parentheses('backend/app.py')
    print(f"   Fixed {fixes} SQL comment parentheses")
    
    print(f"\n✅ All SQL comment parentheses fixed!")

if __name__ == "__main__":
    main()