```python
# contexter_utils.py
"""
Central utility module for the Contexter tool suite.
Contains shared functions for file processing, parsing, and building context files.
"""

import os
import fnmatch
import mimetypes
import patch
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, find_lexer_class_by_name
from pygments.formatters import HtmlFormatter
import re
import html

# --- Constants ---
DEFAULT_EXCLUDE_PATTERNS = [
   ".git*", "node_modules", "__pycache__", "*.pyc", "*.pyo", "dist", "build",
   ".venv", "venv", "*.lock", ".DS_Store", "*.log", ".contexter_cache"
]

# --- File System Utilities ---

def is_binary(file_path):
   """Checks if a file is binary using MIME types and a content heuristic."""
   mime_type, _ = mimetypes.guess_type(file_path)
   if mime_type and not mime_type.startswith('text/'):
       if any(sub in mime_type for sub in ["javascript", "json", "xml", "sql", "toml", "yaml"]):
           return False
       return True
   try:
       with open(file_path, 'rb') as f:
           return b'\0' in f.read(1024)
   except IOError:
       return True
   return False

def generate_file_tree(start_path, exclude_patterns):
   """Generates a string representation of the file tree."""
   tree_lines = []
   # Normalize start_path to ensure consistent trailing slash behavior
   start_path = os.path.normpath(start_path)
   for root, dirs, files in os.walk(start_path, topdown=True):
       # Exclude directories and files based on patterns
       dirs[:] = sorted([d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)])
       files = sorted([f for f in files if not any(fnmatch.fnmatch(f, p) for p in exclude_patterns)])

       relative_root = os.path.relpath(root, start_path)
       if relative_root == ".":
           level = 0
       else:
           level = relative_root.count(os.sep) + 1

       indent = '│   ' * (level - 1)
       if level > 0:
           tree_lines.append(f"{indent}├── {os.path.basename(root)}/")

       sub_indent = '│   ' * level
       for i, f in enumerate(files):
           tree_lines.append(f"{sub_indent}├── {f}")

   return f"{os.path.basename(start_path)}/\n" + "\n".join(tree_lines)


# --- Parsing Utilities ---

def parse_md_constructor(file_path):
   """Parses a Markdown constructor file into a dictionary of {filepath: content_string or None for binary}."""
   files = {}
   current_file = None
   in_code_block = False
   content_lines = []
   header_pattern = re.compile(r"^--- (FILE|SKIPPED \(BINARY\)): (.*) ---$")
   try:
       with open(file_path, 'r', encoding='utf-8') as f:
           for line in f:
               match = header_pattern.match(line.strip())
               if match:
                   if current_file: # Save previous file
                       files[current_file] = "\n".join(content_lines)
                   
                   file_type, path = match.groups()
                   current_file = path.strip()
                   content_lines = []
                   in_code_block = False

                   if file_type == 'SKIPPED (BINARY)':
                       files[current_file] = None
                       current_file = None # Reset
               
               elif current_file:
                   if not in_code_block and line.strip().startswith('````'):
                       in_code_block = True
                   elif in_code_block and line.strip() == '````':
                       # End of block, save content
                       files[current_file] = "\n".join(content_lines)
                       current_file = None # Reset
                       in_code_block = False
                   elif in_code_block:
                       content_lines.append(line.rstrip('\n'))

           if current_file and in_code_block: # Save the last file if loop ends
               files[current_file] = "\n".join(content_lines)
   except FileNotFoundError: return None
   return files


def parse_html_constructor(file_path):
   """Parses an HTML constructor file into a dictionary of {filepath: content_string or None for binary}."""
   files = {}
   try:
       with open(file_path, 'r', encoding='utf-8') as f:
           soup = BeautifulSoup(f, 'html.parser')
   except FileNotFoundError: return None
   
   for container in soup.find_all('div', class_='file-container'):
       path = container.get('data-path')
       if path:
           code_block = container.find('div', class_='highlight')
           if code_block: files[path] = code_block.get_text()

   for container in soup.find_all('div', class_='skipped-container'):
       path = container.get('data-path')
       if path: files[path] = None

   return files

def parse_patch_file(patch_file_path):
   """Auto-detects and parses a patch file (MD or HTML) into a patch dictionary."""
   if patch_file_path.lower().endswith('.html'):
       parser = _parse_html_patch
   else:
       parser = _parse_md_patch
   return parser(patch_file_path)

def _parse_md_patch(file_path):
   """Parses a Markdown patch file."""
   patches = {}
   current_file = None
   diff_lines = []
   diff_header_pattern = re.compile(r"^--- DIFF FOR: (.*) ---$")
   try:
       with open(file_path, 'r', encoding='utf-8') as f:
           for line in f:
               match = diff_header_pattern.match(line.strip())
               if match:
                   if current_file: patches[current_file] = patch.fromstring("\n".join(diff_lines).encode('utf-8'))
                   current_file = match.group(1).strip()
                   diff_lines = []
                   next(f, None)
               elif line.strip() == '```' and current_file:
                   patches[current_file] = patch.fromstring("\n".join(diff_lines).encode('utf-8'))
                   current_file = None
               elif current_file:
                   diff_lines.append(line)
           if current_file: patches[current_file] = patch.fromstring("\n".join(diff_lines).encode('utf-8'))
   except FileNotFoundError: return None
   return patches

def _parse_html_patch(file_path):
   """Parses an HTML patch file."""
   patches = {}
   try:
       with open(file_path, 'r', encoding='utf-8') as f:
           soup = BeautifulSoup(f, 'html.parser')
   except FileNotFoundError: return None
   
   for container in soup.find_all('div', class_='diff-container'):
       path = container.get('data-path')
       diff_pre = container.find('pre')
       if path and diff_pre:
           patches[path] = patch.fromstring(diff_pre.get_text().encode('utf-8'))
   return patches

# --- Rebuilding Utilities ---

def rebuild_html_constructor(output_path, files_dict, tree_content=None):
   """Rebuilds a complete HTML constructor from a dictionary of file contents."""
   pygments_css = HtmlFormatter(style='default').get_style_defs('.highlight')
   html_parts = [f"""
   <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Project Context</title>
   <style>
       body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; padding: 1rem; color: #333; }}
       .container {{ max-width: 1200px; margin: 0 auto; }}
       .file-container, .skipped-container, .tree-container {{ border: 1px solid #ddd; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
       h2, h3 {{ background-color: #f7f7f7; padding: 0.75rem 1rem; margin: 0; border-bottom: 1px solid #ddd; font-size: 1.1rem; }}
       .path {{ font-family: "Courier New", Courier, monospace; color: #a72d2d; font-weight: bold; }}
       .highlight pre {{ margin: 0; padding: 1rem; overflow-x: auto; }}
       {pygments_css}
   </style></head><body><div class="container"><h1>Project Context</h1>
   """]
   
   if tree_content:
       html_parts.append('<div class="tree-container">')
       html_parts.append(f'<h2><span class="path">DIRECTORY STRUCTURE</span></h2>')
       html_parts.append(f'<div class="highlight"><pre>{html.escape(tree_content)}</pre></div></div>')

   for path, content in sorted(files_dict.items()):
       if content is None:
           html_parts.append(f'<div class="skipped-container" data-path="{path}"><h3>SKIPPED (BINARY): <span class="path">{path}</span></h3></div>')
       else:
           lang = get_language_from_path(path)
           try:
               lexer = get_lexer_by_name(lang, stripall=True)
           except:
               lexer = guess_lexer(content)
           formatter = HtmlFormatter(linenos=True, cssclass="highlight")
           highlighted_code = highlight(content, lexer, formatter)
           html_parts.append(f'<div class="file-container" data-path="{path}"><h2>FILE: <span class="path">{path}</span></h2>{highlighted_code}</div>')
   
   html_parts.append("</div></body></html>")
   with open(output_path, 'w', encoding='utf-8') as f:
       f.write("".join(html_parts))

def get_language_from_path(file_path):
   """Gets a language identifier from a file path for Markdown/Pygments."""
   filename = os.path.basename(file_path).lower()
   if filename == 'dockerfile': return 'dockerfile'
   if filename == 'makefile': return 'makefile'
   
   ext = os.path.splitext(filename)[1].lower()
   if not ext: return 'text'
   
   # Common mappings
   lang_map = {
       '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
       '.java': 'java', '.c': 'c', '.cpp': 'cpp', '.cs': 'csharp',
       '.go': 'go', '.rs': 'rust', '.rb': 'ruby', '.php': 'php',
       '.html': 'html', '.css': 'css', '.scss': 'scss', '.md': 'markdown',
       '.json': 'json', '.xml': 'xml', '.yaml': 'yaml', '.toml': 'toml',
       '.sh': 'bash', '.ps1': 'powershell', '.sql': 'sql'
   }
   return lang_map.get(ext, ext[1:])