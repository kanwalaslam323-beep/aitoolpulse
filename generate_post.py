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

FEATURED_IMAGES = [
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1677442136019-21780efad99a?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
]

BODY_IMAGES = [
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=900&q=80"
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

featured_img = FEATURED_IMAGES[len(posts) % len(FEATURED_IMAGES)]

prompt = f"""
You are a senior tech writer for AIToolPulse. Write an honest, in-depth review on: "{topic_to_write}".

Guidelines:
1. Start directly with an insightful introductory summary (2 short paragraphs).
2. Review 4 real software/tools. Use <h2> for each tool name (e.g. <h2>1. Runway ML</h2>).
3. Under each tool include:
   - What makes it unique & key features (bullet points)
   - Pricing & free limitations
   - Real-world Pros and Cons
4. Add a comparison <table> comparing all 4 tools.
5. End with a Final Verdict paragraph and 2 FAQs.

Output ONLY valid HTML elements (<h2>, <p>, <ul>, <li>, <table>, <tr>, <th>, <td>). No markdown backticks.
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

# Clean mid-article injection: sirf 1 balanced image darmiyan mein insert hogi
p_matches = list(re.finditer(r'(</p>)', html_body, re.IGNORECASE))
if len(p_matches) >= 6:
    mid_idx = len(p_matches) // 2
    mid_img = BODY_IMAGES[len(posts) % len(BODY_IMAGES)]
    img_tag = f'\n<div class="article-media"><img src="{mid_img}" alt="AI software workflow insights" loading="lazy"></div>\n'
    insert_pos = p_matches[mid_idx].end()
    html_body = html_body[:insert_pos] + img_tag + html_body[insert_pos:]

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
      <span class="card-tag">Guide &amp; Analysis</span>
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
    "summary": f"Hands-on breakdown of {topic_to_write} covering core features, free vs paid tiers, and practical trade-offs."
}

posts.insert(0, new_entry)

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2)

base_url = "[https://kanwalaslam323-beep.github.io/aitoolpulse](https://kanwalaslam323-beep.github.io/aitoolpulse)"
sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">
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

print(f"Generated clean post layout: {topic_to_write}")
