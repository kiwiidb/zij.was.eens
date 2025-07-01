#!/usr/bin/env python3
"""
Script to extract information from all markdown posts in the posts directory.
"""

import os
import re
from pathlib import Path
import json

def extract_post_info(file_path):
    """Extract filename, date, and title/person info from a markdown post."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = Path(file_path).stem  # Remove .md extension
        
        # Extract date - handle both Jekyll and simple formats
        date = None
        
        # Try Jekyll front matter first
        jekyll_match = re.search(r'^date:\s*(.+)$', content, re.MULTILINE)
        if jekyll_match:
            date = jekyll_match.group(1).strip()
        else:
            # Try simple format
            date_match = re.search(r'^\*\*Date:\*\*\s*(.+)$', content, re.MULTILINE)
            if date_match:
                date = date_match.group(1).strip()
        
        # Extract title/person name
        title = None
        person_name = None
        
        # Try Jekyll title first
        jekyll_title_match = re.search(r'^title:\s*["\'](.+)["\']$', content, re.MULTILINE)
        if jekyll_title_match:
            title = jekyll_title_match.group(1).strip()
            person_name = title
        else:
            # Extract from caption - look for person names
            # Common patterns: "Vandaag X jaar geleden is [Name] geboren/overleden"
            caption_match = re.search(r'## Caption\s*\n\n(.+?)(?:\n\n|\n#|\nBron|\Z)', content, re.DOTALL)
            if caption_match:
                caption = caption_match.group(1).strip()
                
                # Try various patterns to extract names
                patterns = [
                    r'Vandaag \d+ jaar geleden is (.+?) (geboren|overleden)',
                    r'is (.+?) (geboren|overleden)',
                    r'(.+?) is geboren',
                    r'(.+?) (groeit|groeide) op',
                    r'(.+?) (studeert|studeerde)',
                    r'dit initiatief te lanceren[^,]*,(.+?) ',
                    r'om (.+?) aan jullie',
                    r'(.+?) aan jullie voor te stellen',
                ]
                
                for pattern in patterns:
                    name_match = re.search(pattern, caption, re.IGNORECASE)
                    if name_match:
                        potential_name = name_match.group(1).strip()
                        # Clean up the name - remove common prefixes/suffixes
                        potential_name = re.sub(r'^(de|het|een|ons)\s+', '', potential_name, flags=re.IGNORECASE)
                        potential_name = re.sub(r'\s+(de|het|een)$', '', potential_name, flags=re.IGNORECASE)
                        
                        # Check if it looks like a person name (starts with capital, contains space or is short)
                        if re.match(r'^[A-Z][a-zA-ZÀ-ÿ\s\-\'\.]+$', potential_name) and len(potential_name) < 100:
                            person_name = potential_name
                            break
                
                # If no clear person name, extract first sentence as summary
                if not person_name:
                    first_sentence = caption.split('.')[0] if '.' in caption else caption[:100]
                    title = first_sentence.strip()
                else:
                    title = person_name
        
        return {
            'filename': filename,
            'date': date,
            'title': title,
            'person_name': person_name,
            'format': 'jekyll' if jekyll_match or jekyll_title_match else 'simple'
        }
    
    except Exception as e:
        return {
            'filename': filename if 'filename' in locals() else Path(file_path).stem,
            'date': None,
            'title': f"ERROR: {str(e)}",
            'person_name': None,
            'format': 'error'
        }

def main():
    posts_dir = Path('/Users/kwinten/zij.was.eens/posts')
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    posts_info = []
    
    # Process all markdown files
    for md_file in posts_dir.glob('*.md'):
        info = extract_post_info(md_file)
        posts_info.append(info)
    
    # Sort by date (newest first, handling None dates)
    posts_info.sort(key=lambda x: x['date'] or '0000-00-00', reverse=True)
    
    # Print results in a structured format
    print("# Posts Information Extract")
    print(f"Total posts found: {len(posts_info)}")
    print("\n## Summary by Format:")
    
    jekyll_count = sum(1 for p in posts_info if p['format'] == 'jekyll')
    simple_count = sum(1 for p in posts_info if p['format'] == 'simple')
    error_count = sum(1 for p in posts_info if p['format'] == 'error')
    
    print(f"- Jekyll format: {jekyll_count}")
    print(f"- Simple format: {simple_count}")
    print(f"- Errors: {error_count}")
    
    print("\n## All Posts (sorted by date, newest first):")
    print("| Filename | Date | Person/Title | Format |")
    print("|----------|------|--------------|--------|")
    
    for post in posts_info:
        filename = post['filename']
        date = post['date'] or 'No date'
        title = (post['person_name'] or post['title'] or 'No title')[:50]
        if len(title) == 50:
            title += "..."
        format_type = post['format']
        
        print(f"| {filename} | {date} | {title} | {format_type} |")
    
    # Save detailed JSON for further processing
    with open('/Users/kwinten/zij.was.eens/posts_extract.json', 'w', encoding='utf-8') as f:
        json.dump(posts_info, f, indent=2, ensure_ascii=False)
    
    print(f"\n## Detailed information saved to: /Users/kwinten/zij.was.eens/posts_extract.json")

if __name__ == "__main__":
    main()