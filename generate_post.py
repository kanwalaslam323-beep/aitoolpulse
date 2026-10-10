import os
import json
import re
from datetime import datetime
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API Key not found in secrets!")

client = Groq(api_key=API_KEY)

raw_models = client.models.list().data
all_model_ids = [m.id for m in raw_models]

usable_models = [
    m for m in all_model_ids
    if not any(bad in m.lower() for bad in ["whisper", "guard", "vision", "canopylabs", "orpheus", "tts"])
]

TOPICS = [
    "Top 5 Free AI Tools for Video Editing Without Watermark",
    "Best AI Presentation Makers to Create Slides in Minutes",
    "How to Use AI to Automate Daily Workflows",
    "Top AI Tools for Content Writers and Bloggers in 2026",
    "Best Free AI Voice Generators for Realistic Speech",
    "Top AI Image Generators That Are Actually Free",
    "How to Build a No-Code Website Using Modern AI Builders",
    "Best AI Resume Builders to Land High-Paying Remote Jobs",
    "Top AI Chrome Extensions to Boost Your Daily Productivity",
    "Best AI Tools for Students to Summarize Research Papers"
]

def load_posts():
    if os.path.exists("posts.json"):
        with open("posts.json", "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

posts = load_posts()
existing_titles = [p.get("title", "") for p in posts]

topic_to_write = None
for t in TOPICS:
    if t not in existing_titles:
        topic_to_write = t
        break

if not topic_to_write:
    topic_to_write = f"Must-Have AI Productivity Tools: Edition {len(posts) + 1}"

prompt = f"""
You are a professional tech writer for AIToolPulse.
Write a clear, comprehensive review article on: "{topic_to_write}".

Structure:
1. Short overview introduction (2 paragraphs).
2. Review 4 real tools. Format each tool title with <h2> (e.g. <h2>1. ToolName</h2>).
3. Under each tool include:
   - Overview & key capabilities (bullet points)
   - Real-world pricing details (Free tier vs Paid plans)
   - Pros and Cons
4. Add a clean comparison table comparing all 4 tools.
5. Provide a practical final verdict and 2 quick FAQs.

Formatting:
- Return ONLY clean HTML tags: <h2>, <h3>, <p>, <ul>, <li>, <table>, <tr>, <th>, <td>.
- Do NOT include any <img> tags or image placeholders.
- Do NOT use markdown code fences like ```html.
"""

completion = None
for model_name in usable_models:
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        break
    except Exception:
        continue

if not completion:
    raise RuntimeError("Model execution failed.")

html_body = completion.choices[0].message.content.strip()
if html_body.startswith("```html"):
    html_body = html_body[7:]
if html_body.startswith("```"):
    html_body = html_body[3:]
if html_body.endswith("```"):
    html_body = html_body[:-3]
html_body = html_body.strip()

# Agar kahin se koi ghalat img tag aa bhi jaye to usay nikal do
html_body = re.sub(r'<img[^>]*>', '', html_body)

date_str = datetime.now().strftime("%B %d, %Y")
slug = re.sub(r'[^a-zA-Z0-9]+', '-', topic_to_write.lower()).strip('-')

full_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{topic_to_write} - AIToolPulse</title>
  <meta name="description" content="Detailed guide and review: {topic_to_write}">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <div class="container nav-container">
      <a href="index.html" class="logo">⚡ AI<span>ToolPulse</span></a>
      <nav>
        <a href="index.html">Home</a>
        <a href="about.html">About</a>
        <a href="privacy.html">Privacy</a>
        <a href="contact.html">Contact</a>
      </nav>
    </div>
  </header>

  <main class="container">
    <article class="post-content">
      <span class="card-tag">Guide &amp; Review</span>
      <h1>{topic_to_write}</h1>
      <p class="meta" style="color: #94a3b8; margin: 0.5rem 0 1.5rem;">Published on {date_str} • 5 min read</p>
      <hr style="border: none; border-top: 1px solid #334155; margin-bottom: 2rem;">

      {html_body}
    </article>
  </main>

  <footer>
    <div class="container footer-content">
      <p>© 2026 AIToolPulse. All rights reserved.</p>
      <div class="footer-links">
        <a href="about.html">About</a>
        <a href="privacy.html">Privacy Policy</a>
        <a href="contact.html">Contact</a>
      </div>
    </div>
  </footer>
</body>
</html>
"""

with open(f"{slug}.html", "w", encoding="utf-8") as f:
    f.write(full_page_html)

new_entry = {
    "title": topic_to_write,
    "slug": slug,
    "date": date_str,
    "readTime": 5,
    "summary": f"In-depth breakdown of {topic_to_write} covering core features, free tier limits, pros, and cons."
}

posts.insert(0, new_entry)

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2)

base_url = "https://kanwalaslam323-beep.github.io/aitoolpulse"
sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{base_url}/about.html</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>{base_url}/contact.html</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>{base_url}/privacy.html</loc>
    <priority>0.8</priority>
  </url>
"""

for p in posts:
    sitemap_content += f"""  <url>
    <loc>{base_url}/{p['slug']}.html</loc>
    <priority>0.9</priority>
  </url>
"""

sitemap_content += "</urlset>"

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap_content)

print(f"Published clean text-first article: {topic_to_write}")
