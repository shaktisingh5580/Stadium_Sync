import sys

file_path = r'c:\Users\shakt\Downloads\Hack2skill\backend\app\services\gemini_client.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1-indexed lines to delete: 744 to 938
# 0-indexed: 743 to 937
new_lines = lines[:743] + lines[938:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed file!")
