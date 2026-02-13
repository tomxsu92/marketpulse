#!/usr/bin/env python3
import os
import json
import random
from datetime import datetime
from pathlib import Path
from groq import Groq

CONTENT_DIR = Path("content")
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_data():
    try:
        with open("data/raw/latest.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("No data file found")
        return {"tools": []}

def generate_tool_review(tool_data):
    prompt = f"""Write a comprehensive, SEO-optimized review of {tool_data['tool']} for B2B SaaS buyers in 2024.

Requirements:
- Length: 1000-1200 words
- Include: Executive Summary, Features, Pricing, Pros/Cons, Best Use Cases, Alternatives
- SEO Keywords: "{tool_data['tool']} pricing", "{tool_data['tool']} review 2024", "best {tool_data['category']} software"
- Format: Markdown with H2 and H3 headers
- Disclaimer at end: "*This review contains affiliate links. We may earn a commission at no extra cost to you.*"

Data: {json.dumps(tool_data, indent=2)}
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Generation failed: {e}")
        return None

def generate_comparison(tool_a, tool_b):
    prompt = f"""Create a detailed comparison: {tool_a['tool']} vs {tool_b['tool']}

Structure:
1. At-a-Glance Comparison
2. Feature Comparison
3. Pricing Face-Off
4. Who Should Choose Each
5. Final Recommendation

SEO Keywords: "{tool_a['tool']} vs {tool_b['tool']}", "{tool_a['tool']} alternative"
Length: 1200-1500 words
Disclaimer: "*We may earn affiliate commissions from links in this comparison.*"
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Comparison failed: {e}")
        return None

def save_content(subdir, filename, content, metadata):
    dir_path = CONTENT_DIR / subdir
    dir_path.mkdir(parents=True, exist_ok=True)
    
    fm_lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            fm_lines.append(f"{key}:")
            for item in value:
                fm_lines.append(f"  - {item}")
        else:
            fm_lines.append(f"{key}: {value}")
    fm_lines.append("---\n")
    
    frontmatter = "\n".join(fm_lines)
    filepath = dir_path / f"{filename}.md"
    
    # Check if file already exists (avoid duplicates)
    if filepath.exists():
        print(f"File already exists: {filepath}, skipping")
        return None
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    
    print(f"Generated: {filepath}")
    return filepath

def main():
    print("Starting content generation...")
    
    data = load_data()
    tools = data.get("tools", [])
    
    if not tools:
        print("No tools to process")
        return
    
    # RANDOM SELECTION - Pick tools we haven't reviewed yet
    existing_reviews = list((CONTENT_DIR / "tools").glob("*.md"))
    existing_names = [f.stem.replace("-review", "") for f in existing_reviews if f.name != "_index.md"]
    
    print(f"Existing reviews: {existing_names}")
    
    # Filter out already reviewed tools
    available_tools = [t for t in tools if t['tool'].lower().replace(" ", "-") not in existing_names]
    
    if not available_tools:
        print("All tools have been reviewed! Starting over with random selection.")
        available_tools = tools
    
    # Pick random tool from available
    import random
    tool = random.choice(available_tools)
    print(f"Selected tool: {tool['tool']} (from {len(available_tools)} available)")
    
    # Generate review
    review_content = generate_tool_review(tool)
    if review_content:
        slug = tool['tool'].lower().replace(" ", "-")
        save_content(
            "tools",
            f"{slug}-review",
            review_content,
            {
                "title": f"{tool['tool']} Review & Pricing Guide ({datetime.now().year})",
                "date": datetime.utcnow().isoformat(),
                "draft": False,
                "tool": tool['tool'],
                "category": tool['category'],
                "affiliate_url": tool['affiliate_url'],
                "tags": [tool['category'], "review", "saas"],
                "description": f"Comprehensive {tool['tool']} review including pricing, features, and alternatives."
            }
        )
    
    # Generate comparison with random other tool
    if len(tools) >= 2:
        other_tools = [t for t in tools if t['tool'] != tool['tool']]
        if other_tools:
            other_tool = random.choice(other_tools)
            print(f"Creating comparison: {tool['tool']} vs {other_tool['tool']}")
            
            comparison_content = generate_comparison(tool, other_tool)
            if comparison_content:
                # Check if comparison already exists
                comp_slug = f"{tool['tool']}-vs-{other_tool['tool']}".lower().replace(" ", "-")
                comp_path = CONTENT_DIR / "comparisons" / f"{comp_slug}.md"
                
                if not comp_path.exists():
                    save_content(
                        "comparisons",
                        comp_slug,
                        comparison_content,
                        {
                            "title": f"{tool['tool']} vs {other_tool['tool']}: Complete Comparison ({datetime.now().year})",
                            "date": datetime.utcnow().isoformat(),
                            "draft": False,
                            "tools": [tool['tool'], other_tool['tool']],
                            "tags": ["comparison", "versus", tool['category']],
                            "description": f"Side-by-side comparison of {tool['tool']} and {other_tool['tool']}."
                        }
                    )
                else:
                    print(f"Comparison already exists: {comp_path}")

if __name__ == "__main__":
    main()
