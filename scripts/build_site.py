#!/usr/bin/env python3
import os
import re
from pathlib import Path
from datetime import datetime

CONTENT_DIR = Path("content")
PUBLIC_DIR = Path("public")

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
.container { max-width: 900px; margin: 0 auto; padding: 20px; }
header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; text-align: center; margin-bottom: 40px; }
header h1 { font-size: 3em; margin-bottom: 10px; font-weight: 700; }
header p { font-size: 1.3em; opacity: 0.9; }
nav { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }
nav a { margin: 0 20px; text-decoration: none; color: #667eea; font-weight: 600; font-size: 1.1em; }
nav a:hover { color: #764ba2; }
.article { background: white; margin: 20px 0; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }
.article:hover { transform: translateY(-2px); }
.article h3 { margin-bottom: 10px; font-size: 1.5em; }
.article h3 a { color: #333; text-decoration: none; }
.article h3 a:hover { color: #667eea; }
.date { color: #666; font-size: 0.9em; margin-bottom: 15px; }
.badge { display: inline-block; background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75em; font-weight: 600; margin-right: 10px; text-transform: uppercase; }
.badge-vs { background: #764ba2; }
.excerpt { color: #666; margin-top: 10px; }
.disclaimer { margin-top: 50px; padding: 20px; background: #fff3cd; border-left: 4px solid #ffc107; font-size: 0.9em; border-radius: 0 8px 8px 0; }
footer { text-align: center; padding: 40px; color: #666; margin-top: 50px; }
.stats { display: flex; justify-content: center; gap: 40px; margin: 30px 0; flex-wrap: wrap; }
.stat { text-align: center; }
.stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
.stat-label { color: #666; font-size: 0.9em; }
"""

ARTICLE_CSS = CSS + """
.container-single { max-width: 800px; margin: 0 auto; padding: 20px; background: white; min-height: 100vh; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
.nav-single { padding: 20px 0; margin-bottom: 30px; border-bottom: 2px solid #667eea; }
.nav-single a { margin-right: 20px; text-decoration: none; color: #667eea; font-weight: 600; }
h1.single { color: #333; margin-bottom: 20px; font-size: 2.5em; line-height: 1.2; }
h2 { color: #667eea; margin-top: 40px; margin-bottom: 15px; font-size: 1.8em; border-bottom: 1px solid #eee; padding-bottom: 10px; }
h3 { color: #555; margin-top: 25px; margin-bottom: 10px; }
p { margin-bottom: 15px; font-size: 1.1em; }
strong { color: #667eea; }
ul, ol { margin-bottom: 20px; padding-left: 30px; }
li { margin-bottom: 8px; }
"""

def parse_frontmatter(content):
    """Extract frontmatter and body from markdown"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm = {}
            for line in parts[1].strip().split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    fm[key.strip()] = val.strip().strip('"').strip("'")
            return fm, parts[2].strip()
    return {}, content

def md_to_html(md):
    """Simple markdown to HTML conversion"""
    html = md
    # Headers
    html = re.sub(r'^# (.+)$', r'<h1 class="single">\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # Paragraphs
    lines = html.split('\n')
    new_lines = []
    in_list = False
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                new_lines.append('<ul>')
                in_list = True
            item = line.strip()[2:]
            new_lines.append(f'<li>{item}</li>')
        else:
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            if line.strip():
                new_lines.append(f'<p>{line}</p>')
    if in_list:
        new_lines.append('</ul>')
    return '\n'.join(new_lines)

def build_site():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    (PUBLIC_DIR / "tools").mkdir(exist_ok=True)
    (PUBLIC_DIR / "comparisons").mkdir(exist_ok=True)
    
    # Build index
    articles = []
    tool_articles = []
    comparison_articles = []
    
    # Process tools
    tools_dir = CONTENT_DIR / "tools"
    if tools_dir.exists():
        for f in tools_dir.glob("*.md"):
            if f.name == "_index.md":
                continue
            content = f.read_text()
            fm, body = parse_frontmatter(content)
            if 'title' in fm:
                articles.append({
                    'title': fm.get('title', ''),
                    'date': fm.get('date', '')[:10],
                    'category': fm.get('category', 'review'),
                    'type': 'tool',
                    'filename': f.stem + '.html',
                    'frontmatter': fm,
                    'body': body
                })
                tool_articles.append({
                    'title': fm.get('title', ''),
                    'category': fm.get('category', 'review'),
                    'filename': f.stem + '.html'
                })
                
                # Create individual page
                html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{fm.get('title', '')}</title>
<style>{ARTICLE_CSS}</style>
</head>
<body>
<div class="container-single">
<div class="nav-single">
<a href="../index.html">← Home</a>
<a href="./index.html">All Reviews</a>
</div>
{md_to_html(body)}
<div class="disclaimer">
<strong>Disclosure:</strong> This review contains affiliate links. We may earn a commission at no extra cost to you.
</div>
</div>
</body>
</html>"""
                (PUBLIC_DIR / "tools" / f"{f.stem}.html").write_text(html_content)
    
    # Process comparisons
    comp_dir = CONTENT_DIR / "comparisons"
    if comp_dir.exists():
        for f in comp_dir.glob("*.md"):
            if f.name == "_index.md":
                continue
            content = f.read_text()
            fm, body = parse_frontmatter(content)
            if 'title' in fm:
                articles.append({
                    'title': fm.get('title', ''),
                    'date': fm.get('date', '')[:10],
                    'category': 'comparison',
                    'type': 'comparison',
                    'filename': f.stem + '.html',
                    'frontmatter': fm,
                    'body': body
                })
                comparison_articles.append({
                    'title': fm.get('title', ''),
                    'filename': f.stem + '.html'
                })
                
                # Create individual comparison page
                html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{fm.get('title', '')}</title>
<style>{ARTICLE_CSS}</style>
</head>
<body>
<div class="container-single">
<div class="nav-single">
<a href="../index.html">← Home</a>
<a href="./index.html">All Comparisons</a>
</div>
{md_to_html(body)}
<div class="disclaimer">
<strong>Disclosure:</strong> This comparison contains affiliate links. We may earn a commission at no extra cost to you.
</div>
</div>
</body>
</html>"""
                (PUBLIC_DIR / "comparisons" / f"{f.stem}.html").write_text(html_content)
    
    # Sort by date (newest first)
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    # Build index page
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MarketPulse AI - B2B SaaS Intelligence</title>
<style>{CSS}</style>
</head>
<body>
<header>
<h1>MarketPulse AI</h1>
<p>Automated market intelligence for B2B software buyers</p>
</header>
<div class="container">
<nav>
<a href="./index.html">Home</a>
<a href="./tools/index.html">Tool Reviews</a>
<a href="./comparisons/index.html">Comparisons</a>
</nav>
<div class="stats">
<div class="stat"><div class="stat-number">15+</div><div class="stat-label">Tools Analyzed</div></div>
<div class="stat"><div class="stat-number">Daily</div><div class="stat-label">Fresh Content</div></div>
<div class="stat"><div class="stat-number">100%</div><div class="stat-label">Data-Driven</div></div>
</div>
<h2 style="margin-bottom: 20px; color: #333;">Latest Reviews</h2>
"""
    
    for article in articles[:10]:  # Show last 10
        badge_class = "badge-vs" if article['type'] == 'comparison' else ""
        category = "VS" if article['type'] == 'comparison' else article['category']
        folder = "comparisons" if article['type'] == 'comparison' else "tools"
        excerpt = "Side-by-side comparison" if article['type'] == 'comparison' else "Comprehensive review including pricing analysis"
        
        index_html += f"""
<div class="article">
<span class="badge {badge_class}">{category}</span>
<h3><a href="{folder}/{article['filename']}">{article['title']}</a></h3>
<div class="date">Published: {article['date']}</div>
<p class="excerpt">{excerpt}</p>
</div>
"""
    
    index_html += f"""
<div class="disclaimer">
<strong>Disclosure:</strong> This site contains affiliate links. We may earn a commission when you purchase through our links, at no extra cost to you.
</div>
<footer>
<p>&copy; {datetime.now().year} MarketPulse AI. Automated market intelligence.</p>
<p style="font-size: 0.8em; margin-top: 10px;">{len(tool_articles)} reviews and counting</p>
</footer>
</div>
</body>
</html>"""
    
    (PUBLIC_DIR / "index.html").write_text(index_html)
    
    # Build tools listing page
    tools_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tool Reviews - MarketPulse AI</title>
<style>{CSS}</style>
</head>
<body>
<header>
<h1>Tool Reviews</h1>
<p>Comprehensive software analysis</p>
</header>
<div class="container">
<nav>
<a href="../index.html">← Home</a>
<a href="../comparisons/index.html">Comparisons</a>
</nav>
<h2 style="margin-bottom: 20px;">All Reviews</h2>
"""
    
    for tool in tool_articles:
        tools_html += f"""
<div class="article">
<span class="badge">{tool['category']}</span>
<h3><a href="{tool['filename']}">{tool['title']}</a></h3>
</div>
"""
    
    tools_html += """
<div class="disclaimer">
<strong>Disclosure:</strong> This site contains affiliate links. We may earn a commission when you purchase through our links, at no extra cost to you.
</div>
</div>
</body>
</html>"""
    
    (PUBLIC_DIR / "tools" / "index.html").write_text(tools_html)
    
    # Build comparisons listing page
    comp_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comparisons - MarketPulse AI</title>
<style>{CSS}</style>
</head>
<body>
<header>
<h1>Comparisons</h1>
<p>Side-by-side software analysis</p>
</header>
<div class="container">
<nav>
<a href="../index.html">← Home</a>
<a href="../tools/index.html">Tool Reviews</a>
</nav>
<h2 style="margin-bottom: 20px;">Head-to-Head Comparisons</h2>
"""
    
    for comp in comparison_articles:
        comp_html += f"""
<div class="article">
<span class="badge badge-vs">VS</span>
<h3><a href="{comp['filename']}">{comp['title']}</a></h3>
</div>
"""
    
    comp_html += """
<div class="disclaimer">
<strong>Disclosure:</strong> This site contains affiliate links. We may earn a commission when you purchase through our links, at no extra cost to you.
</div>
</div>
</body>
</html>"""
    
    (PUBLIC_DIR / "comparisons" / "index.html").write_text(comp_html)
    
    print(f"Site built: {len(tool_articles)} tools, {len(comparison_articles)} comparisons")

if __name__ == "__main__":
    build_site()
