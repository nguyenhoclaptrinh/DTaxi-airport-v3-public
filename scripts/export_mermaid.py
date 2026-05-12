import zlib
import base64
import urllib.request
import os
import re

def get_mermaid_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Tim block mermaid
        match = re.search(r'```mermaid\s+(.*?)\s+```', content, re.DOTALL)
        if match:
            return match.group(1).strip()
    return None

def export_mermaid_kroki():
    input_file = "docs/040-Diagrams/Main_Flow.md"
    mermaid_code = get_mermaid_from_file(input_file)
    
    if not mermaid_code:
        print(f"Khong tim thay code Mermaid trong {input_file}")
        return

    # Kroki algorithm: UTF-8 -> Zlib Compress -> Base64 URL Safe
    payload = mermaid_code.encode('utf-8')
    compressed = zlib.compress(payload, 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    
    url = f"https://kroki.io/mermaid/png/{encoded}"
    
    print(f"Dang tai anh tu Kroki cho file: {input_file}")
    print(f"URL: {url}")
    
    try:
        output_path = "docs/040-Diagrams/Main_Flow.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())
        print(f"Da luu anh vao: {output_path}")
    except Exception as e:
        print(f"Loi khi tai anh: {e}")

if __name__ == "__main__":
    export_mermaid_kroki()
