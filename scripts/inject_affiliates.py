#!/usr/bin/env python3
"""
Affiliate Link Injection
"""
import re
from pathlib import Path

PUBLIC_DIR = Path("public")

AFFILIATE_MAP = {
    "notion.so": "https://www.notion.so/?r=referral",
    "airtable.com": "https://airtable.com/invite/r/referral",
    "figma.com": "https://www.figma.com/referral",
    "linear.app": "https://linear.app/referral",
    "hubspot.com": "https://www.hubspot.com/referral",
}

def inject_affiliates():
    if not PUBLIC_DIR.exists():
        print("Public directory not found")
        return
    
    updated_count = 0
    
    for html_file in PUBLIC_DIR.rglob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8')
            original = content
            
            for domain, affiliate_url in AFFILIATE_MAP.items():
                pattern = rf'href="https?://(www\.)?{re.escape(domain)}[^"]*"'
                replacement = f'href="{affiliate_url}" target="_blank" rel="nofollow sponsored"'
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            if content != original:
                html_file.write_text(content, encoding='utf-8')
                updated_count += 1
                
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
    
    print(f"Updated {updated_count} files with affiliate links")

if __name__ == "__main__":
    inject_affiliates()
