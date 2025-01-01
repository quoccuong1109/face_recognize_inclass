import os
from pathlib import Path

def save_to_file(content, file_index):
    with open(f'project_summary_{file_index}.txt', 'w', encoding='utf-8') as f:
        f.write(content)

def get_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def update_script():
    base_path = Path('.')
    content = ""
    char_count = 0
    file_index = 1

    important_files = ['app.py', 'requirements.txt', 'update_script.py']
    important_dirs = ['app', 'static', 'templates', 'models', 'scripts', 'routes']

    # First, list the directory structure
    for root, dirs, files in os.walk(base_path):
        # Skip .git directory
        if '.git' in root:
            continue
        
        level = root.replace(str(base_path), '').count(os.sep)
        indent = ' ' * 4 * level
        dir_name = os.path.basename(root)
        
        line = f'{indent}{dir_name}/\n'
        content += line
        char_count += len(line)

        for file in files:
            file_indent = ' ' * 4 * (level + 1)
            line = f'{file_indent}{file}\n'
            content += line
            char_count += len(line)

            if char_count > 10000:
                save_to_file(content, file_index)
                content = ""
                char_count = 0
                file_index += 1

    # Then, add the content of each file
    for root, dirs, files in os.walk(base_path):
        # Skip .git directory
        if '.git' in root:
            continue
        
        level = root.replace(str(base_path), '').count(os.sep)
        indent = ' ' * 4 * level

        for file in files:
            file_path = Path(root) / file
            file_indent = ' ' * 4 * (level + 1)

            if file.endswith('.py') or file.endswith('.html') or file.endswith('.css'):
                file_content = get_file_content(file_path)
                header = f'{file_indent}--- Start of {file} ---\n'
                footer = f'{file_indent}--- End of {file} ---\n'
                content += header + file_content + footer
                char_count += len(header) + len(file_content) + len(footer)

            if char_count > 10000:
                save_to_file(content, file_index)
                content = ""
                char_count = 0
                file_index += 1

    if content:
        save_to_file(content, file_index)

if __name__ == '__main__':
    update_script()