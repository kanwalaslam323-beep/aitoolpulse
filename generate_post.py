import os
import json
import re
from datetime import datetime
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API Key not found in secrets!")

client = Groq(api_key=API_KEY)

# Fetch all available models directly from account
raw_models = client.models.list().data
all_model_ids = [m.id for m in raw_models]
print("Models reported by Groq API:", all_model_ids)

# Filter out non-chat models (audio, guardrails, vision, internal)
usable_models = [
    m for m in all_model_ids
    if not any(bad in m.lower() for bad in ["whisper", "guard", "vision", "canopylabs", "orpheus", "tts"])
]

print("Usable candidate models:", usable_models)

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

TOOL_IMAGES = [
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1677442136019-21780efad99a?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1618172193763-c511deb635ca?auto=format&fit=crop&w=900&q=80"
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

featured_img = TOOL_IMAGES[len(posts) % len(TOOL_IMAGES)]

prompt = f"""
You are an expert tech reviewer writing for AIToolPulse.
Write an in-depth, hands-on review about: "{topic_to_write}".

Structure requirements:
1. No intro fluff.
2. Review 4 real tools using <h3> for each tool title (e.g. <h3>1. ToolName</h3>).
3. Under each tool provide:
   - What it does and key capabilities (bullet points)
   - Real-world pricing details (Free tier limits vs Paid plans)
   - Pros and Cons
4. Add a comparison table comparing all 4 tools.
5. Provide a clear verdict and 2 quick FAQs.

Formatting:
- Return ONLY clean HTML tags: <h2>, <h3>, <p>, <ul>, <li>, <table>.
- Do NOT use ```html code fences.
"""

completion = None
for model_name in usable_models:
    try:
        print(f"Trying model: {model_name}...")
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        print(f"Success with model: {model_name}")
        break
    except Exception as e:
        print(f"Skipping {model_name} due to error: {e}")

if not completion:
    raise RuntimeError("None of the available Groq models succeeded.")

html_body = completion.choices[0].message.content.strip()
if html_body.startswith("```html"):
    html_body = html_body[7:]
if html_body.startswith("```"):
    html_body = html_body[3:]
if html_body.endswith("```"):
    html_body = html_body[:-3]
html_body = html_body.strip()

# AUTOMATIC INJECTION: Insert image under each <h3> heading
h3_matches = list(re.finditer(r'(</h3>)', html_body, re.IGNORECASE))
offset = 0
for idx, match in enumerate(h3_matches):
    img_url = TOOL_IMAGES[(len(posts) + idx + 1) % len(TOOL_IMAGES)]
    img_tag = f'\n<img src="{img_url}" alt="Software overview interface" style="width:100%; max-height:360px; object-fit:cover; border-radius:10px; margin:1rem 0 1.5rem; border:1px solid #334155;" loading="lazy">\n'
    insert_pos = match.end() + offset
    html_body = html_body[:insert_pos] + img_tag + html_body[insert_pos:]
    offset += len(img_tag)

date_str = datetime.now().strftime("%B %d, %Y")
slug = re.sub(r'[^a-zA-Z0-9]+', '-', topic_to_write.lower()).strip('-')

full_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{topic_to_write} - AIToolPulse</title>
  <meta name="description" content="In-depth guide and review: {topic_to_write}">
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
      <span class="card-tag">In-Depth Review</span>
      <h1>{topic_to_write}</h1>
      <p class="meta">Published on {date_str} • 6 min read</p>
      
      <img src="{featured_img}" alt="{topic_to_write}" class="featured-img" loading="eager">

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
    "readTime": 6,
    "image": featured_img,
    "summary": f"Hands-on test and detailed breakdown of {topic_to_write} with pricing, features, pros, and cons."
}

posts.insert(0, new_entry)

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2)

base_url = "https://aitoolpulse.github.io/aitoolpulse"
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

print(f"Successfully published post with images: {topic_to_write}")
