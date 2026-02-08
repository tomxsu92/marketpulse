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

def save_content(subdir, filename
