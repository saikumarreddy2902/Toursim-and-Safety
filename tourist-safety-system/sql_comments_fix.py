#!/usr/bin/env python3
"""
SQL Comments Final Fix - Find and fix all type ignore comments inside SQL strings
"""

import re
import os
from typing import Match

def fix_all_sql_comments(file_path: str) -> int:
    """Fix all SQL statements with misplaced type ignore comments"""
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes = 0
    
    # Pattern to find SQL strings that end with comments before the closing quotes
    # Looking for patterns like:  )  # type: ignore\n    ''')
    pattern = r'(\)\s+# type: ignore\s*\n\s*\'\'\')'
    
    def replace_func(match: Match[str]) -> str:
        nonlocal fixes
        fixes += 1
        return ")\n    ''')  # type: ignore"
    
    content = re.sub(pattern, replace_func, content)
    
    # Also fix any remaining patterns where the comment is on a line inside SQL
    # Look for CREATE TABLE patterns with embedded comments
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '# type: ignore' in line and ('CREATE TABLE' in lines[max(0, i-10):i] or 
                                        'INSERT INTO' in lines[max(0, i-10):i] or
                                        'SELECT' in lines[max(0, i-10):i]):
            # Check if this line is inside a SQL string (between ''' markers)
            before_context = '\n'.join(lines[max(0, i-20):i])
            after_context = '\n'.join(lines[i:min(len(lines), i+5)])
            
            # Count triple quotes before this line to see if we're inside a string
            triple_quotes_before = before_context.count("'''")
            triple_quotes_after = after_context.count("'''")
            
            # If odd number of triple quotes before and at least one after, we're likely inside a string
            if triple_quotes_before % 2 == 1 and triple_quotes_after > 0:
                # Remove the type ignore comment from this line
                lines[i] = re.sub(r'\s*# type: ignore.*$', '', line)
                fixes += 1
                
                # Find the closing ''' and add the comment there
                for j in range(i+1, min(len(lines), i+10)):
                    if "'''" in lines[j] and '# type: ignore' not in lines[j]:
                        lines[j] = lines[j].rstrip() + "  # type: ignore"
                        break
    
    content = '\n'.join(lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return fixes

def main():
    """Fix all SQL comment issues"""
    print("🔧 Fixing ALL SQL type ignore comment issues...")
    
    fixes = fix_all_sql_comments('backend/app.py')
    print(f"   Applied {fixes} SQL comment fixes")
    
    print(f"\n✅ All SQL comment issues should now be resolved!")

if __name__ == "__main__":
    main()