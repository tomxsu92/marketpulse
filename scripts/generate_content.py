#!/usr/bin/env python3
"""
AI Content Generation Engine
Uses Groq API to generate SEO-optimized content
"""
import os
import json
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
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    
    print(f"Generated: {filepath}")

def main():
    print("Starting content generation...")
    
    data = load_data()
    tools = data.get("tools", [])
    
    if not tools:
        print("No tools to process")
        return
    
    tool = tools[0]
    print(f"Generating review for {tool['tool']}...")
    
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
    
    if len(tools) >= 2:
        print("Generating comparison...")
        comparison_content = generate_comparison(tools[0], tools[1])
        if comparison_content:
            slug = f"{tools[0]['tool']}-vs-{tools[1]['tool']}".lower().replace(" ", "-")
            save_content(
                "comparisons",
                slug,
                comparison_content,
                {
                    "title": f"{tools[0]['tool']} vs {tools[1]['tool']}: Complete Comparison ({datetime.now().year})",
                    "date": datetime.utcnow().isoformat(),
                    "draft": False,
                    "tools": [tools[0]['tool'], tools[1]['tool']],
                    "tags": ["comparison", "versus", tools[0]['category']],
                    "description": f"Side-by-side comparison of {tools[0]['tool']} and {tools[1]['tool']}."
                }
            )

if __name__ == "__main__":
    main()
