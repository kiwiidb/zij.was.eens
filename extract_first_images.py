#!/usr/bin/env python3
"""
Script to extract the first image path from each post in the _posts directory.
"""

import os
import re
from pathlib import Path

def extract_first_image(file_path):
    """Extract the first image path from a markdown post file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for markdown image syntax: ![alt text](image_path)
        markdown_pattern = r'!\[.*?\]\((/zij\.was\.eens/images/[^)]+)\)'
        markdown_matches = re.findall(markdown_pattern, content)
        
        if markdown_matches:
            return markdown_matches[0]
        
        # Look for HTML img tags: <img src="image_path">
        html_pattern = r'<img[^>]+src=["\']([^"\']*images/[^"\']+)["\'][^>]*>'
        html_matches = re.findall(html_pattern, content)
        
        if html_matches:
            return html_matches[0]
        
        return None
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def main():
    """Main function to process all posts and extract first images."""
    posts_dir = Path("_posts")
    
    if not posts_dir.exists():
        print("_posts directory not found!")
        return
    
    results = []
    
    # Get all markdown files in _posts directory
    post_files = sorted(posts_dir.glob("*.md"))
    
    for post_file in post_files:
        # Skip index.md as requested
        if post_file.name == "index.md":
            continue
        
        first_image = extract_first_image(post_file)
        
        results.append({
            'post_file': post_file.name,
            'first_image': first_image
        })
    
    # Print results in a clear format
    print("POST FILE AND FIRST IMAGE ANALYSIS")
    print("=" * 60)
    print(f"{'Post Filename':<45} {'First Image Path'}")
    print("-" * 60)
    
    for result in results:
        post_name = result['post_file']
        image_path = result['first_image'] if result['first_image'] else "NO IMAGE FOUND"
        print(f"{post_name:<45} {image_path}")
    
    # Summary statistics
    posts_with_images = sum(1 for r in results if r['first_image'])
    posts_without_images = len(results) - posts_with_images
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"Total posts processed: {len(results)}")
    print(f"Posts with images: {posts_with_images}")
    print(f"Posts without images: {posts_without_images}")

if __name__ == "__main__":
    main()