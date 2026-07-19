import re
import os

with open('header.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all blocks like:
# #### 1. `backend/app/__init__.py`
# ```python
# """..."""
# ```

pattern = re.compile(r'#### \d+\. `([^`]+)`\s*```[a-z]*\n(.*?)\n```', re.DOTALL)
matches = pattern.findall(content)

count = 0
for filepath, header in matches:
    # We only want to apply this to the files the user mentioned, or we can just apply to all 79 if they don't have the correct header.
    # To be safe, we'll apply it to all files in the match, replacing any existing header.
    filepath = filepath.strip()
    full_path = os.path.join(os.getcwd(), os.path.normpath(filepath))
    
    if not os.path.exists(full_path):
        print(f"File not found: {filepath}")
        continue
        
    with open(full_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        
    # Check if the file already has a header.
    # Python headers start with """ and end with """
    # TS/JS/CSS headers start with /** and end with */
    
    new_content = file_content
    
    if filepath.endswith('.py'):
        # Remove existing """ ... """ at the top if it exists
        if file_content.startswith('"""'):
            end_idx = file_content.find('"""', 3)
            if end_idx != -1:
                # Also remove trailing newlines after the docstring
                new_content = file_content[end_idx+3:].lstrip()
    else:
        # Remove existing /** ... */ at the top if it exists
        if file_content.startswith('/**'):
            end_idx = file_content.find('*/', 3)
            if end_idx != -1:
                new_content = file_content[end_idx+2:].lstrip()
                
    # Prepend the new header
    final_content = header.strip() + '\n\n' + new_content
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"Applied header to {filepath}")
    count += 1

print(f"Total files updated: {count}")
