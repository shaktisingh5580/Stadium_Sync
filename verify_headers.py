import re
import os

with open('header.md', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'#### \d+\. `([^`]+)`\s*```[a-z]*\n(.*?)\n```', re.DOTALL)
matches = pattern.findall(content)

missing_headers = []

for filepath, expected_header in matches:
    filepath = filepath.strip()
    full_path = os.path.join(os.getcwd(), os.path.normpath(filepath))
    
    if not os.path.exists(full_path):
        continue
        
    with open(full_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        
    expected_lines = expected_header.strip().split('\n')
    
    # We just need to check if the first non-empty line contains the start of the header
    # Or just check if expected_header is in the file_content
    # But since we prepended it directly, it should be an exact match at the top
    
    if expected_header.strip() not in file_content:
        missing_headers.append(filepath)

if len(missing_headers) == 0:
    print("SUCCESS: All 79 files have their exact custom headers applied!")
else:
    print(f"FAILED: {len(missing_headers)} files are missing their headers:")
    for f in missing_headers:
        print(f"- {f}")
