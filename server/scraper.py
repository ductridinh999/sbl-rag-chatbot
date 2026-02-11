import os
import re
import time
import requests
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

JINA_API_KEY = os.getenv("JINA_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not JINA_API_KEY or not GOOGLE_API_KEY:
    raise ValueError("Missing API Keys! Make sure they are in your .env file.")

# Index URLs
INDEX_URLS = [
    "https://www.patreon.com/posts/frequently-asked-43097481",
    "https://www.patreon.com/posts/41551479"
]

OUTPUT_FILE = "../database/knowledge_base.txt"

# Gemini 2.0 Flash for OCR
genai.configure(api_key=GOOGLE_API_KEY)
vision_model = genai.GenerativeModel('gemini-2.0-flash')

def get_markdown_from_jina(url):
    """Fetches clean Markdown from a URL using Jina Reader."""
    print(f"Fetching: {url}")

    jina_url = f"https://r.jina.ai/{url}"
    
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "X-Return-Format": "markdown"
    }
    
    try:
        response = requests.get(jina_url, headers=headers, timeout=20)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def harvest_links(index_urls):
    """
    Visits the main index pages and extracts all relevant article links.
    """
    print("\nSTARTING HARVESTER...")
    found_links = set() 

    for index_url in index_urls:
        markdown = get_markdown_from_jina(index_url)
        if not markdown:
            continue
        links = re.findall(r'\[.*?\]\((https?://.*?)\)', markdown)
        
        for link in links:
            # Only capture article links
            if "patreon.com/posts" not in link and "medium.com" not in link:
                continue
            
            if link in index_urls:
                continue
                
            found_links.add(link)

    print(f"Harvested {len(found_links)} unique article links.")
    return list(found_links)

def analyze_image_with_gemini(img_url):
    """Downloads image and asks Gemini to describe it."""
    try:
        img_response = requests.get(img_url, timeout=10)
        if img_response.status_code != 200: return ""
        
        img_data = Image.open(BytesIO(img_response.content))
        
        prompt = (
            "Analyze this image from a fitness article. "
            "If it's a data graph, extract axes and trends. "
            "If it's an anatomy diagram, name the muscles. "
            "Keep it concise."
        )
        
        response = vision_model.generate_content([prompt, img_data])
        return response.text.strip()
    except:
        return "" 

def process_articles(urls):
    """Main loop to scrape and enrich extracted links."""
    print(f"\n🚀 STARTING SCRAPING OF {len(urls)} ARTICLES...\n")
    
    # Check if file exists to avoid overwriting if restart
    mode = "a" if os.path.exists(OUTPUT_FILE) else "w"

    with open(OUTPUT_FILE, mode, encoding="utf-8") as f:
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Processing...")
            
            content = get_markdown_from_jina(url)
            if not content: continue

            images = re.findall(r'!\[(.*?)\]\((.*?)\)', content)
            
            # Only process first 3 images per article
            for alt, img_url in images[:3]: 
                if not img_url.startswith("http"): continue
                
                print(f"   > Analyzing image...")
                desc = analyze_image_with_gemini(img_url)
                
                replacement = f"\n> **[IMAGE ANALYSIS]** {desc}\n"
                content = content.replace(f"![{alt}]({img_url})", replacement)
                time.sleep(1)

            # Save to file
            entry = f"\n\n{'='*50}\nSOURCE: {url}\n{'='*50}\n\n{content}"
            f.write(entry)
            f.flush()
            
            print(f"   > Saved.")
            time.sleep(2) 

if __name__ == "__main__":
    article_links = harvest_links(INDEX_URLS)
    
    if article_links:
        process_articles(article_links)
        print(f"\nDONE! Knowledge base saved to {OUTPUT_FILE}")
    else:
        print("No links found. Check your filter logic.")