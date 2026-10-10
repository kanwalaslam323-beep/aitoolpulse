import os
import json
import re
from datetime import datetime
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API Key not found in secrets!")

client = Groq(api_key=API_KEY)

# Dynamically pick the first available active chat model
available_models = [m.id for m in client.models.list().data]
preferred = [
    m for m in available_models 
    if any(k in m.lower() for k in ["llama", "mixtral", "gemma"]) 
    and not any(x in m.lower() for x in ["whisper", "guard", "vision"])
]
selected_model = preferred[0] if preferred else available_models[0]
print(f"Selected active model: {selected_model}")

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

# High quality curated tech images mapping
IMAGE_POOL = [
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1677442136019-21780efad99a?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1618172193763-c511deb635ca?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
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

# Select rotating featured image
img_idx = len(posts) % len(IMAGE_POOL)
post_image = IMAGE_POOL[img_idx]

prompt = f"""
You are an expert tech reviewer and SEO writer for AIToolPulse.
Write an in-depth, human-style blog post about: "{topic_to_write}".

Structure requirements:
1. No fluff or generic intro - jump straight into practical value.
2. Review 3 to 4 real tools with:
   - Tool Name (<h3>)
   - Visual banner: Include an image tag right under the tool heading using Unsplash tech photos with descriptive alt text:
     `<img src="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80" alt="Tool interface preview" style="width:100%; border-radius:8px; margin:1rem 0;" loading="lazy">` (vary the photo IDs slightly or use standard tech/software query tags).
   - Core Features (bullet points)
   - Pricing / Free details
   - Pros & Cons
3. Practical comparison table comparing all tools.
4. Quick verdict and 2 practical FAQs.

Formatting:
- Return ONLY clean HTML content that goes inside an article container.
- Use <h2>, <h3>, <p>, <ul>, <li>, <img>, and <table> tags.
- Do NOT include ```html markdown code blocks. Start directly with HTML elements.
"""

completion = client.chat.completions.create(
    model=selected_model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

html_body = completion.choices[0].message.content.strip()
if html_body.startswith("```html"):
    html_body = html_body[7:]
if html_body.startswith("```"):
    html_body = html_body[3:]
if html_body.endswith("```"):
    html_body = html_body[:-3]
html_body = html_body.strip()

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
      <span class="card-tag">Comprehensive Guide</span>
      <h1>{topic_to_write}</h1>
      <p class="meta">Published on {date_str} • 6 min read</p>
      
      <img src="{post_image}" alt="{topic_to_write}" class="featured-img" loading="eager">

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
    "image": post_image,
    "summary": f"In-depth breakdown of {topic_to_write} featuring real test results, pricing comparison, pros, and cons."
}

posts.insert(0, new_entry)

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2)

# Generate/Update sitemap.xml automatically
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

print(f"Successfully generated article with internal images: {topic_to_write}")
