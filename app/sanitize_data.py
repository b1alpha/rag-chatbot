import os
import json
import re

source_dir = "./data/confluence_chunks"

def remove_html(text):
    return re.sub(r"<[^>]+>", "", text)

def extract_text(obj):
    texts = []
    if isinstance(obj, dict):
        for v in obj.values():
            texts.extend(extract_text(v))
    elif isinstance(obj, list):
        for item in obj:
            texts.extend(extract_text(item))
    elif isinstance(obj, str):
        texts.append(obj)
    return texts

for fname in os.listdir(source_dir):
    if fname.endswith(".json"):
        path = os.path.join(source_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                all_texts = extract_text(data)
                cleaned = [remove_html(t) for t in all_texts if t.strip()]
                if cleaned:
                    out_path = os.path.join(
                        source_dir, os.path.splitext(fname)[0] + ".txt"
                    )
                    with open(out_path, "w", encoding="utf-8") as out_f:
                        out_f.write("\n\n".join(cleaned))
                    print(f"Sanitized {fname} -> {os.path.basename(out_path)}")
            except Exception as e:
                print(f"Error processing {fname}: {e}")