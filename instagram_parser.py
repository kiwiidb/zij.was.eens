#!/usr/bin/env python3
import json
import requests
import os
import glob
from pathlib import Path
import time

def download_image(url, filename):
    """Download an image from URL and save it to filename"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def sanitize_filename(text, max_length=50):
    """Create a safe filename from text"""
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    filename = ''.join(c if c in safe_chars else '_' for c in text)
    return filename[:max_length]

def parse_profile_json(json_file_path):
    """Parse the Instagram profile JSON and extract media data"""
    
    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract timeline media
    timeline_media = data.get('edge_owner_to_timeline_media', {})
    edges = timeline_media.get('edges', [])
    
    if not edges:
        print("No media posts found in the profile data")
        return
    
    print(f"Found {len(edges)} posts to process")
    
    # Create directories
    images_dir = Path("images")
    posts_dir = Path("posts")
    images_dir.mkdir(exist_ok=True)
    posts_dir.mkdir(exist_ok=True)
    
    for i, edge in enumerate(edges):
        node = edge.get('node', {})
        
        # Extract caption
        caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
        caption_text = ""
        if caption_edges:
            caption_text = caption_edges[0].get('node', {}).get('text', '')
        
        # Get post metadata
        shortcode = node.get('shortcode', f'post_{i}')
        timestamp = node.get('taken_at_timestamp', 0)
        
        print(f"\nProcessing post {i+1}: {shortcode}")
        
        # Start markdown content for this post
        markdown_content = f"# {shortcode}\n\n"
        
        if timestamp:
            from datetime import datetime
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            markdown_content += f"**Date:** {date_str}\n\n"
        
        # Extract images from edge_sidecar_to_children or use main display_url
        image_urls = []
        
        # Check if it's a sidecar post (multiple images)
        sidecar_edges = node.get('edge_sidecar_to_children', {}).get('edges', [])
        if sidecar_edges:
            # Multiple images in sidecar
            for child_edge in sidecar_edges:
                child_node = child_edge.get('node', {})
                display_url = child_node.get('display_url', '')
                if display_url:
                    image_urls.append(display_url)
        else:
            # Single image post
            display_url = node.get('display_url', '')
            if display_url:
                image_urls.append(display_url)
        
        # Download images
        post_images = []
        for j, url in enumerate(image_urls):
            if url:
                # Create filename
                extension = '.jpg'  # Default extension
                if 'webp' in url:
                    extension = '.webp'
                elif 'png' in url:
                    extension = '.png'
                
                filename = f"{sanitize_filename(shortcode)}_{j}{extension}"
                filepath = images_dir / filename
                
                # Download image
                if download_image(url, filepath):
                    post_images.append(filename)
                
                # Be respectful to the server
                time.sleep(0.5)
        
        # Add images to markdown
        if post_images:
            markdown_content += "## Images\n\n"
            for img_filename in post_images:
                markdown_content += f"![Image](../images/{img_filename})\n\n"
        
        # Add caption to markdown
        if caption_text:
            markdown_content += "## Caption\n\n"
            markdown_content += caption_text + "\n\n"
        
        # Save individual post markdown file
        post_filename = f"{sanitize_filename(shortcode)}.md"
        post_filepath = posts_dir / post_filename
        
        with open(post_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created: {post_filepath}")
    
    print(f"\nProcessing complete!")
    print(f"- Downloaded images saved to: {images_dir.absolute()}")
    print(f"- Individual post markdown files saved to: {posts_dir.absolute()}")

def parse_posts_json_files(posts_json_dir):
    """Parse posts_json files and extract media data"""
    
    json_files = glob.glob(os.path.join(posts_json_dir, "*.json"))
    if not json_files:
        print(f"No JSON files found in {posts_json_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Create directories
    images_dir = Path("images_posts_json")
    posts_dir = Path("posts_posts_json")
    images_dir.mkdir(exist_ok=True)
    posts_dir.mkdir(exist_ok=True)
    
    total_posts = 0
    
    for json_file in json_files:
        print(f"\nProcessing file: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract edges from the nested structure
        connection = data.get('data', {}).get('xdt_api__v1__feed__user_timeline_graphql_connection', {})
        edges = connection.get('edges', [])
        
        if not edges:
            print(f"No posts found in {json_file}")
            continue
        
        print(f"Found {len(edges)} posts in this file")
        
        for i, edge in enumerate(edges):
            node = edge.get('node', {})
            
            # Extract caption
            caption_obj = node.get('caption', {})
            caption_text = caption_obj.get('text', '') if caption_obj else ''
            
            # Get post metadata
            code = node.get('code', f'post_{total_posts}')
            taken_at = node.get('taken_at', 0)
            
            print(f"Processing post: {code}")
            
            # Start markdown content for this post
            markdown_content = f"# {code}\n\n"
            
            if taken_at:
                from datetime import datetime
                date_str = datetime.fromtimestamp(taken_at).strftime('%Y-%m-%d %H:%M:%S')
                markdown_content += f"**Date:** {date_str}\n\n"
            
            # Extract images
            image_urls = []
            
            # Check if it has carousel_media (multiple images)
            carousel_media = node.get('carousel_media', [])
            if carousel_media:
                # Multiple images in carousel
                for media_item in carousel_media:
                    image_versions = media_item.get('image_versions2', {})
                    candidates = image_versions.get('candidates', [])
                    if candidates:
                        # Use the first (highest quality) candidate
                        image_url = candidates[0].get('url', '')
                        if image_url:
                            image_urls.append(image_url)
            else:
                # Single image post
                image_versions = node.get('image_versions2', {})
                candidates = image_versions.get('candidates', [])
                if candidates:
                    # Use the first (highest quality) candidate
                    image_url = candidates[0].get('url', '')
                    if image_url:
                        image_urls.append(image_url)
            
            # Download images
            post_images = []
            for j, url in enumerate(image_urls):
                if url:
                    # Create filename
                    extension = '.jpg'  # Default extension
                    if 'webp' in url:
                        extension = '.webp'
                    elif 'png' in url:
                        extension = '.png'
                    
                    filename = f"{sanitize_filename(code)}_{j}{extension}"
                    filepath = images_dir / filename
                    
                    # Download image
                    if download_image(url, filepath):
                        post_images.append(filename)
                    
                    # Be respectful to the server
                    time.sleep(0.5)
            
            # Add images to markdown
            if post_images:
                markdown_content += "## Images\n\n"
                for img_filename in post_images:
                    markdown_content += f"![Image](../images_posts_json/{img_filename})\n\n"
            
            # Add caption to markdown
            if caption_text:
                markdown_content += "## Caption\n\n"
                markdown_content += caption_text + "\n\n"
            
            # Save individual post markdown file
            post_filename = f"{sanitize_filename(code)}.md"
            post_filepath = posts_dir / post_filename
            
            with open(post_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Created: {post_filepath}")
            total_posts += 1
    
    print(f"\nProcessing complete for posts_json!")
    print(f"- Processed {total_posts} total posts")
    print(f"- Downloaded images saved to: {images_dir.absolute()}")
    print(f"- Individual post markdown files saved to: {posts_dir.absolute()}")

if __name__ == "__main__":
    # Parse profile.json if it exists
    profile_json_path = "profile.json"
    if os.path.exists(profile_json_path):
        print("=== Processing profile.json ===")
        parse_profile_json(profile_json_path)
    else:
        print(f"profile.json not found, skipping...")
    
    # Parse posts_json directory if it exists
    posts_json_dir = "posts_json"
    if os.path.exists(posts_json_dir) and os.path.isdir(posts_json_dir):
        print("\n=== Processing posts_json files ===")
        parse_posts_json_files(posts_json_dir)
    else:
        print(f"posts_json directory not found, skipping...")
    
    print("\n=== All processing complete! ===")
    