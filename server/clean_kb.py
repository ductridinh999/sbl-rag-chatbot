import re
import os

def clean_knowledge_base(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into articles by the source marker
    articles = re.split(r'(={50}\nSOURCE: .*?\n={50})', content)
    
    cleaned_articles = []
    
    # The first element might be empty or preamble, skip if empty
    i = 0
    if not articles[0].strip():
        i = 1
        
    while i < len(articles):
        header = articles[i]
        body = articles[i+1] if i+1 < len(articles) else ""
        
        # --- CLEANING BODY ---
        
        # 1. Remove navigation/UI links and buttons
        body = re.sub(r'\[Skip navigation\].*?\n', '', body)
        body = re.sub(r'Join for free', '', body, flags=re.IGNORECASE)
        body = re.sub(r'Log in', '', body, flags=re.IGNORECASE)
        body = re.sub(r'Share', '', body, flags=re.IGNORECASE)
        body = re.sub(r'\[Home\].*?\n', '', body)
        body = re.sub(r'\[Posts\].*?\n', '', body)
        body = re.sub(r'\[Collections\].*?\n', '', body)
        body = re.sub(r'\[More\].*?\n', '', body)
        
        # 1.1 Remove empty markdown links and lingering URL artifacts
        body = re.sub(r'\[\s*\]\(https?://.*?\)', '', body, flags=re.DOTALL)
        body = re.sub(r'\[\s+\]\(https?://.*?\)', '', body, flags=re.DOTALL)
        body = re.sub(r'\[\s*\]', '', body)
        body = re.sub(r'\*   \*   \*   \*', '', body)
        body = re.sub(r'\*   \*   \*', '', body)
        body = re.sub(r'·', '', body)
        body = re.sub(r'\b1y\b', '', body) # remove "1y" (1 year ago)
        body = re.sub(r'\bAUTHOR\b', '', body)
        body = re.sub(r'Collapse replies', '', body)
        body = re.sub(r'----------', '', body)
        body = re.sub(r'\d+ comments', '', body)
        
        # 1.2 Remove Patreon creator profile/campaign links and repetitive titles
        body = re.sub(r'\[.*?\]\(https?://www.patreon.com/SandCResearch.*?\)', '', body, flags=re.DOTALL)
        body = re.sub(r'\[.*?\]\(https?://www.patreon.com/posts/.*?\)', '', body, flags=re.DOTALL)
        body = re.sub(r'\[.*?\]\(https?://www.patreon.com/login.*?\)', '', body, flags=re.DOTALL)
        body = re.sub(r'!\[.*?\]\(https?://c10.patreonusercontent.com/.*?\)', '', body)
        
        # 1.3 Remove lines that are just empty brackets or links or symbols
        body = re.sub(r'^\s*\[\s*\]\s*$', '', body, flags=re.MULTILINE)
        body = re.sub(r'^\s*\(\s*\)\s*$', '', body, flags=re.MULTILINE)
        body = re.sub(r'^\s*!\s*$', '', body, flags=re.MULTILINE)
        body = re.sub(r'^\s*\\s*$', '', body, flags=re.MULTILINE)
        
        # 1.4 Deduplicate identical blocks (simple approach for repetitive titles)
        lines = body.split('\n')
        seen = []
        for line in lines:
            trimmed = line.strip()
            if trimmed and trimmed in seen and len(trimmed) > 10: # Only deduplicate long-ish lines
                continue
            seen.append(line)
        body = '\n'.join(seen)
        
        # 2. Remove repetitive profile/creator info and generic Patreon UI elements
        body = re.sub(r'### Chris Beardsley', '', body)
        body = re.sub(r'\*   \[Home\].*?\n', '', body)
        body = re.sub(r'\*   \[Posts\].*?\n', '', body)
        body = re.sub(r'\*   \[Collections\].*?\n', '', body)
        
        # 3. Remove "New" badges and dates that appear in isolation
        body = re.sub(r'\bNew\b', '', body)
        body = re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\b', '', body)
        
        # 4. Remove standalone numbers (like comment counts, like counts)
        # Only if they are on their own line or surrounded by whitespace
        body = re.sub(r'^\s*\d+\s*$', '', body, flags=re.MULTILINE)
        
        # 5. Remove "Tags" section and following links
        body = re.sub(r'Tags\s*\n\s*\[article\].*?\n', '', body, flags=re.IGNORECASE)
        
        # 6. Remove image markdown but KEEP [IMAGE ANALYSIS] descriptions
        # First, remove normal image tags that don't have our analysis
        body = re.sub(r'!\[Image \d+\]\(.*?\)', '', body)
        # Remove empty image analysis blocks if they are empty
        body = re.sub(r'> \*\*\[IMAGE ANALYSIS\]\*\*\s*\n', '', body)
        
        # 7. Cleanup extra newlines (more than 2)
        body = re.sub(r'\n{3,}', '\n\n', body)
        
        # 7.1 Remove leading/trailing dots and whitespace on individual lines
        body = re.sub(r'^\s*\.\s*$', '', body, flags=re.MULTILINE)
        body = re.sub(r'^\s*\* \* \*\s*$', '', body, flags=re.MULTILINE)
        
        # 8. Final pass on extra newlines
        body = re.sub(r'\n{3,}', '\n\n', body)
        body = body.strip()
        
        cleaned_articles.append(f"{header}\n\n{body}\n")
        i += 2

    final_content = "\n".join(cleaned_articles)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"✅ Cleaned content saved to {output_file}")

if __name__ == "__main__":
    # First clean to a temporary file, then overwrite the original if desired
    # For safety, we'll overwrite knowledge_base.txt as requested to "clear" it
    clean_knowledge_base("../database/knowledge_base.txt", "../database/knowledge_base.txt")
