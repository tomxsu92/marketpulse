#!/usr/bin/env python3
"""
MarketPulse Data Fetcher
Collects pricing and market data from public sources
"""
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data/raw")
HISTORY_DIR = Path("data/history")
DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

TARGET_TOOLS = [
    {
        "name": "Notion",
        "category": "project-management",
        "affiliate_url": "https://www.notion.so/?r=referral",
        "pricing_url": "https://www.notion.so/pricing",
        "alternatives": ["Evernote", "OneNote", "Roam Research"]
    },
    {
        "name": "Airtable",
        "category": "database",
        "affiliate_url": "https://airtable.com/invite/r/referral",
        "pricing_url": "https://www.airtable.com/pricing",
        "alternatives": ["Google Sheets", "Smartsheet", "Monday.com"]
    },
    {
        "name": "Figma",
        "category": "design",
        "affiliate_url": "https://www.figma.com/referral",
        "pricing_url": "https://www.figma.com/pricing",
        "alternatives": ["Sketch", "Adobe XD", "InVision"]
    },
    {
        "name": "Linear",
        "category": "issue-tracking",
        "affiliate_url": "https://linear.app/referral",
        "pricing_url": "https://linear.app/pricing",
        "alternatives": ["Jira", "Asana", "Trello"]
    },
    {
        "name": "HubSpot",
        "category": "crm",
        "affiliate_url": "https://www.hubspot.com/referral",
        "pricing_url": "https://www.hubspot.com/pricing/marketing",
        "alternatives": ["Salesforce", "Pipedrive", "Zoho CRM"]
    }
]

def fetch_github_trends():
    try:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": "topic:saas stars:>500 pushed:>2024-01-01",
            "sort": "updated",
            "order": "desc",
            "per_page": 5
        }
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            items = response.json().get("items", [])
            return [{
                "name": item["name"],
                "description": item["description"],
                "stars": item["stargazers_count"],
                "url": item["html_url"],
                "updated": item["updated_at"]
            } for item in items]
        return []
    except Exception as e:
        print(f"GitHub fetch error: {e}")
        return []

def generate_mock_pricing_data(tool):
    return {
        "tool": tool["name"],
        "category": tool["category"],
        "affiliate_url": tool["affiliate_url"],
        "pricing_url": tool["pricing_url"],
        "alternatives": tool["alternatives"],
        "timestamp": datetime.utcnow().isoformat(),
        "pricing_tiers": [
            {"name": "Free", "price": 0, "features": ["Basic features", "Limited storage"]},
            {"name": "Pro", "price": "Variable", "features": ["Advanced features", "Priority support"]},
            {"name": "Enterprise", "price": "Custom", "features": ["SSO", "Advanced security", "Dedicated support"]}
        ],
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d")
    }

def main():
    print("Starting data fetch...")
    
    all_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "tools": [],
        "trends": {
            "github": fetch_github_trends(),
            "product_hunt": []
        }
    }
    
    for tool in TARGET_TOOLS:
        print(f"Processing {tool['name']}...")
        tool_data = generate_mock_pricing_data(tool)
        all_data["tools"].append(tool_data)
        time.sleep(1)
    
    date_str = datetime.utcnow().strftime("%Y%m%d")
    output_file = DATA_DIR / f"market_data_{date_str}.json"
    
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    with open(DATA_DIR / "latest.json", 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"Data saved: {output_file}")

if __name__ == "__main__":
    main()
