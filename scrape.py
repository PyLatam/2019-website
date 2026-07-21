#!/usr/bin/env python3
import os
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# Configuration
START_URL = "https://2019.pylatam.org/"
DOMAINS = {"2019.pylatam.org", "pylatam.us.aldryn.io"}
DIST_DIR = os.path.abspath("dist")

# Keep track of state
crawled_pages = set()
downloaded_assets = set()
pages_to_crawl = [START_URL, "https://2019.pylatam.org/en/"]
assets_to_download = set()

# Regex to find url(...) in CSS
CSS_URL_REGEX = re.compile(r'url\s*\(\s*[\'"]?([^\'"\)]+)[\'"]?\s*\)', re.IGNORECASE)

class WebHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.assets = set()

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Extract links
        if tag == 'a' and 'href' in attrs_dict:
            self.links.add(attrs_dict['href'])
            
        # Extract assets
        if tag == 'link' and 'href' in attrs_dict:
            self.assets.add(attrs_dict['href'])
        if tag in ('img', 'script', 'iframe') and 'src' in attrs_dict:
            self.assets.add(attrs_dict['src'])
        if tag == 'source' and 'srcset' in attrs_dict:
            srcset = attrs_dict['srcset']
            for part in srcset.split(','):
                part = part.strip().split(' ')[0]
                if part:
                    self.assets.add(part)
        
        # Meta tags
        if tag == 'meta' and attrs_dict.get('property') in ('og:image', 'og:url') and 'content' in attrs_dict:
            self.assets.add(attrs_dict['content'])
        if tag == 'meta' and attrs_dict.get('name') in ('twitter:image',) and 'content' in attrs_dict:
            self.assets.add(attrs_dict['content'])

        # Inline style attributes
        if 'style' in attrs_dict:
            for url in CSS_URL_REGEX.findall(attrs_dict['style']):
                self.assets.add(url)

def fetch_url(url):
    # Use standard browser User-Agent to avoid blocks
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read(), response.getcode(), response.info(), response.geturl()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None, None, None

def is_internal_url(url):
    parsed = urllib.parse.urlparse(url)
    if not parsed.netloc:
        return True
    return parsed.netloc in DOMAINS

def should_download_asset(url):
    parsed = urllib.parse.urlparse(url)
    # Don't download external scripts/CDNs/fonts
    if parsed.netloc and parsed.netloc not in DOMAINS:
        return False
    # Avoid mailto, tel, or fragment links
    if parsed.scheme in ('mailto', 'tel') or url.startswith('#'):
        return False
    return True

def clean_url(url, base_url):
    # Resolve relative URL against base_url
    full_url = urllib.parse.urljoin(base_url, url)
    # Remove fragments
    parsed = urllib.parse.urlparse(full_url)
    cleaned = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ''))
    return cleaned

def get_local_path(url):
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    if not path or path == '/':
        return os.path.join(DIST_DIR, 'index.html')
    
    # Strip leading slash
    rel_path = path.lstrip('/')
    
    # If the path has a trailing slash or does not look like a file with an extension,
    # save it as index.html inside a directory of that name.
    _, ext = os.path.splitext(rel_path)
    if path.endswith('/') or not ext:
        return os.path.join(DIST_DIR, rel_path, 'index.html')
    else:
        return os.path.join(DIST_DIR, rel_path)

def clean_content_domains(content_bytes):
    try:
        text = content_bytes.decode('utf-8', errors='ignore')
    except Exception:
        return content_bytes
        
    # Replace absolute domains with root-relative paths
    text = text.replace('https://2019.pylatam.org', '')
    text = text.replace('http://2019.pylatam.org', '')
    text = text.replace('http://pylatam.us.aldryn.io', '')
    text = text.replace('https://pylatam.us.aldryn.io', '')
    
    return text.encode('utf-8')

def scan_css_for_assets(css_bytes, css_url):
    try:
        css_text = css_bytes.decode('utf-8', errors='ignore')
    except Exception:
        return []
    
    found_urls = CSS_URL_REGEX.findall(css_text)
    resolved_urls = []
    for u in found_urls:
        # Strip quotes and spaces
        u = u.strip('\'" ')
        if not u or u.startswith('data:'):
            continue
        abs_url = urllib.parse.urljoin(css_url, u)
        resolved_urls.append(abs_url)
    return resolved_urls

def save_file(local_path, content_bytes):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, 'wb') as f:
        f.write(content_bytes)

def main():
    print("Starting site scraper...")
    print(f"Target: {START_URL}")
    print(f"Output directory: {DIST_DIR}")
    
    # 1. Crawl all HTML pages recursively
    while pages_to_crawl:
        current_url = pages_to_crawl.pop(0)
        if current_url in crawled_pages:
            continue
            
        print(f"Crawling page: {current_url}")
        crawled_pages.add(current_url)
        
        content_bytes, code, info, final_url = fetch_url(current_url)
        if content_bytes is None:
            continue
            
        content_type = info.get_content_type()
        
        # If it is indeed an HTML page
        if 'text/html' in content_type:
            # Parse links and assets
            parser = WebHTMLParser()
            try:
                parser.feed(content_bytes.decode('utf-8', errors='ignore'))
            except Exception as e:
                print(f"Error parsing HTML of {current_url}: {e}")
                
            # Process links for crawling
            for link in parser.links:
                cleaned_link = clean_url(link, final_url)
                if is_internal_url(cleaned_link) and cleaned_link not in crawled_pages and cleaned_link not in pages_to_crawl:
                    # Make sure it's not a known asset extension (to avoid treating files as pages before fetching)
                    path = urllib.parse.urlparse(cleaned_link).path
                    _, ext = os.path.splitext(path)
                    if ext.lower() not in ('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.woff', '.woff2', '.ttf'):
                        pages_to_crawl.append(cleaned_link)
                    else:
                        assets_to_download.add(cleaned_link)
            
            # Process assets
            for asset in parser.assets:
                cleaned_asset = clean_url(asset, final_url)
                if should_download_asset(cleaned_asset):
                    assets_to_download.add(cleaned_asset)
            
            # Clean absolute domains in the page content
            cleaned_content = clean_content_domains(content_bytes)
            
            # Save local file
            local_path = get_local_path(final_url)
            save_file(local_path, cleaned_content)
            print(f"Saved page to: {local_path}")
        else:
            # If we crawled a URL that was not HTML, treat it as an asset and save it
            local_path = get_local_path(final_url)
            save_file(local_path, content_bytes)
            print(f"Saved non-HTML page to: {local_path}")

    # 2. Download all collected assets
    print(f"\nCrawled {len(crawled_pages)} pages. Now downloading assets...")
    
    download_queue = list(assets_to_download)
    while download_queue:
        asset_url = download_queue.pop(0)
        if asset_url in downloaded_assets:
            continue
            
        print(f"Downloading asset: {asset_url}")
        downloaded_assets.add(asset_url)
        
        content_bytes, code, info, final_url = fetch_url(asset_url)
        if content_bytes is None:
            continue
            
        # If it's a stylesheet, scan it for other assets (fonts, images)
        content_type = info.get_content_type()
        if 'text/css' in content_type:
            nested_assets = scan_css_for_assets(content_bytes, final_url)
            for na in nested_assets:
                if should_download_asset(na) and na not in downloaded_assets and na not in download_queue:
                    download_queue.append(na)
            # Also clean absolute domains inside CSS
            content_bytes = clean_content_domains(content_bytes)
            
        # Save local file
        local_path = get_local_path(final_url)
        save_file(local_path, content_bytes)
        print(f"Saved asset to: {local_path}")

    # 3. Create CNAME file for GitHub Pages custom domain
    cname_path = os.path.join(DIST_DIR, 'CNAME')
    with open(cname_path, 'w') as f:
        f.write("2019.pylatam.org\n")
    print(f"\nCreated CNAME file with '2019.pylatam.org' at: {cname_path}")

    # 4. Create .nojekyll file to prevent GitHub Pages from ignoring files starting with underscores
    nojekyll_path = os.path.join(DIST_DIR, '.nojekyll')
    with open(nojekyll_path, 'w') as f:
        pass
    print(f"Created .nojekyll file at: {nojekyll_path}")

    print("\nScraping completed successfully!")

if __name__ == "__main__":
    main()
