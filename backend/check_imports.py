import ast
import os
import sys
import glob

stdlib_modules = set(sys.stdlib_module_names)

def get_imports(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return set()
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.add(node.module.split('.')[0])
    return imports

all_imports = set()
for root, _, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            all_imports.update(get_imports(os.path.join(root, file)))

external_imports = all_imports - stdlib_modules - {'app'}

print("External imports found:")
for imp in sorted(external_imports):
    print(imp)
