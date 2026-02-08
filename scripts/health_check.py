#!/usr/bin/env python3
"""
Health Check & Monitoring
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def check_data_freshness():
    try:
        latest = Path("data/raw/latest.json")
        if not latest.exists():
            return False, "No data file"
        
        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600
        
        if age_hours < 25:
            return True, f"Data {age_hours:.1f}h old"
        else:
            return False, f"Stale ({age_hours:.1f}h)"
    except Exception as e:
        return False, f"Error: {e}"

def check_content_generation():
    try:
        content_dirs = ["content/tools", "content/comparisons"]
        newest_time = 0
        
        for dir_name in content_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                for md_file in dir_path.rglob("*.md"):
                    mtime = md_file.stat().st_mtime
                    if mtime > newest_time:
                        newest_time = mtime
        
        if newest_time > 0:
            age_hours = (datetime.now().timestamp() - newest_time) / 3600
            if age_hours < 25:
                return True, f"Content {age_hours:.1f}h old"
        
        return False, "No recent content"
    except Exception as e:
        return False, f"Error: {e}"

def check_build_status():
    public_dir = Path("public")
    index_file = public_dir / "index.html"
    
    if not public_dir.exists():
        return False, "No public dir"
    if not index_file.exists():
        return False, "No index.html"
    
    return True, "Build OK"

def send_report(checks, overall_status):
    api_key = os.getenv("SENDGRID_API_KEY")
    to_email = os.getenv("ALERT_EMAIL")
    
    if not api_key or not to_email:
        print("SendGrid not configured")
        return
    
    try:
        sg = SendGridAPIClient(api_key)
        
        status_emoji = "✅" if overall_status == "HEALTHY" else "❌"
        
        html_content = f"""
        <h2>{status_emoji} MarketPulse Report</h2>
        <p>Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
        <ul>
            <li>Data: {'✅' if checks['data'][0] else '❌'} {checks['data'][1]}</li>
            <li>Content: {'✅' if checks['content'][0] else '❌'} {checks['content'][1]}</li>
            <li>Build: {'✅' if checks['build'][0] else '❌'} {checks['build'][1]}</li>
        </ul>
        """
        
        message = Mail(
            from_email='alerts@marketpulse-ai.com',
            to_emails=to_email,
            subject=f'MarketPulse: {overall_status}',
            html_content=html_content
        )
        
        response = sg.send(message)
        print(f"Email sent: {response.status_code}")
        
    except Exception as e:
        print(f"Email failed: {e}")

def main():
    print("Running health checks...")
    
    checks = {
        'data': check_data_freshness(),
        'content': check_content_generation(),
        'build': check_build_status()
    }
    
    all_passed = all(check[0] for check in checks.values())
    overall_status = "HEALTHY" if all_passed else "ISSUES"
    
    print(f"Status: {overall_status}")
    for name, (passed, msg) in checks.items():
        print(f"{'✅' if passed else '❌'} {name}: {msg}")
    
    send_report(checks, overall_status)
    
    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
