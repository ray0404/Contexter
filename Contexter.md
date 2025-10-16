--- DIRECTORY STRUCTURE: ContexterGem ---

````
ContexterGem/
├── README.md
├── build_context_html.py
├── context_builder.py
├── contexter.egg-info-PKG-INFO
├── contexter_utils.py
├── html2md.py
├── install.sh
├── md2html.py
├── project.toml
├── pyproject.toml
├── reconstructor.py
├── reconstructor_html.py
├── requirements.txt
├── sanitize_context.py
├── setup.py
├── smart_update.py
├── update_context.py
├── update_context_html.py
├── updater.py
├── updater_html.py
├── contexter.egg-info/
│   ├── SOURCES.txt
│   ├── dependency_links.txt
│   ├── entry_points.txt
│   ├── requires.txt
│   ├── top_level.txt
````

--- FILE: ContexterGem/README.md ---

````markdown
```markdown
# Contexter

Contexter is a powerful suite of Python command-line tools for packaging, reconstructing, and updating software projects as single, portable Markdown or HTML files. This workflow is perfect for sharing entire projects with AI models, creating simple text-based backups, or transferring projects between machines.

## New in This Version: AI Workflow ✅

We've added a `sanitizecontext` command to fix common formatting errors when you copy a full project context from an AI chat. Since AI models can sometimes forget to add code fences (````), this tool makes the output instantly usable.

**New Workflow:**
1.  Paste the AI's response into `ai_output.md`.
2.  Run: `sanitize_context ai_output.md clean_project.md`
3.  Reconstruct: `reconstructor clean_project.md ./my-new-project`

## Command Reference

| Command             | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| Command             | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| `context_builder`   | Packages a directory into a single Markdown file.                        |
| `reconstructor`     | Rebuilds a project from a Markdown context file.                         |
| `sanitize_context`  | **(New)** Fixes AI-generated Markdown to be a valid Contexter file.        |
| `update_context`    | Creates a patch file by comparing two `.md` context files.               |
| `updater`           | Applies a patch file to an `.md` context file.                           |
| `smart_update`      | **(Recommended)** Creates a patch using `rsync` for high efficiency.     |
| `build_context_html`| Packages a directory into a single HTML file.                            |
| `reconstructor_html`| Rebuilds a project from an HTML context file.                            |
| `update_context_html`| Creates a patch (`.md` or `.html`) from two `.html` files.               |
| `updater_html`      | Applies a patch (`.md` or `.html`) to an `.html` file.                   |
| `md2html`           | A utility to convert any Markdown file to HTML.                          |
| `html2md`           | A utility to convert any HTML file to Markdown.                          |

For detailed usage, run any command with the `-h` or `--help` flag.
````

--- FILE: ContexterGem/build_context_html.py ---

````python
#!/usr/bin/env python3
import argparse
import os
import fnmatch
from contexter_utils import (
   DEFAULT_EXCLUDE_PATTERNS, is_binary, generate_file_tree, rebuild_html_constructor
)

def main():
   parser = argparse.ArgumentParser(description="Combine project files into a single, styled HTML file.")
   parser.add_argument("output_file", help="Path for the output HTML file.")
   parser.add_argument("paths", nargs='+', help="File and/or directory paths to include.")
   parser.add_argument("--exclude", action="append", default=[], help="Patterns to exclude.")
   args = parser.parse_args()
   
   exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + args.exclude
   files_to_include = {}
   tree_content = ""

   for path in args.paths:
       norm_path = os.path.normpath(path)
       if not os.path.exists(norm_path):
           print(f"⚠️ Warning: Path not found, skipping: {norm_path}")
           continue
       
       if any(fnmatch.fnmatch(os.path.basename(norm_path), p) for p in exclude_patterns):
           continue

       if os.path.isdir(norm_path):
           print(f"📂 Processing directory: {norm_path}")
           tree_content += generate_file_tree(norm_path, exclude_patterns) + "\n\n"
           for root, dirs, files in os.walk(norm_path, topdown=True):
               dirs[:] = sorted([d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)])
               for filename in sorted(files):
                   if any(fnmatch.fnmatch(filename, p) for p in exclude_patterns): continue
                   file_path = os.path.join(root, filename)
                   if is_binary(file_path):
                       print(f"⚫ Skipping (binary): {file_path}")
                       files_to_include[file_path] = None
                   else:
                       try:
                           with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                               files_to_include[file_path] = f.read()
                           print(f"✅ Processed: {file_path}")
                       except Exception as e:
                           print(f"❌ Error reading file {file_path}: {e}")
       elif os.path.isfile(norm_path):
            # Logic to handle single files, similar to directory walk
           if is_binary(norm_path):
               files_to_include[norm_path] = None
           else:
               with open(norm_path, 'r', encoding='utf-8', errors='ignore') as f:
                   files_to_include[norm_path] = f.read()
   
   rebuild_html_constructor(args.output_file, files_to_include, tree_content.strip())
   print(f"\n🎉 Success! HTML context file created at '{args.output_file}'.")

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/context_builder.py ---

````python
#!/usr/bin/env python3
import argparse
import os
import fnmatch
from contexter_utils import (
   DEFAULT_EXCLUDE_PATTERNS, is_binary, generate_file_tree, get_language_from_path
)

def process_path_for_md(path, outfile, exclude_patterns, processed_files):
   """Recursively processes a path and writes to the MD file, avoiding duplicates."""
   norm_path = os.path.normpath(path)
   if norm_path in processed_files:
       return
   
   processed_files.add(norm_path)

   if os.path.isdir(norm_path):
       print(f"📂 Processing directory: {norm_path}")
       # Generate and write tree structure only for the top-level directory
       is_top_level = len(processed_files) == 1
       if is_top_level:
           tree = generate_file_tree(norm_path, exclude_patterns)
           outfile.write(f"""--- DIRECTORY STRUCTURE: {os.path.basename(norm_path)} ---\n\n````\n{tree}\n````\n\n""")

       # Walk through the directory
       for root, dirs, files in os.walk(norm_path, topdown=True):
           dirs[:] = sorted([d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)])
           files = sorted([f for f in files if not any(fnmatch.fnmatch(f, p) for p in exclude_patterns)])
           for filename in files:
               file_path = os.path.join(root, filename)
               process_path_for_md(file_path, outfile, exclude_patterns, processed_files)

   elif os.path.isfile(norm_path):
       if is_binary(norm_path):
           print(f"⚫ Skipping (binary): {norm_path}")
           outfile.write(f"--- SKIPPED (BINARY): {norm_path} ---\n\n")
           return
       try:
           with open(norm_path, 'r', encoding='utf-8', errors='ignore') as infile:
               content = infile.read()
               lang = get_language_from_path(norm_path)
               outfile.write(f"""--- FILE: {norm_path} ---\n\n````{lang}\n{content.strip()}\n````\n\n""")
               print(f"✅ Processed: {norm_path}")
       except Exception as e:
           print(f"❌ Error reading file {norm_path}: {e}")

def main():
   parser = argparse.ArgumentParser(description="Combine source files into a single Markdown context file.")
   parser.add_argument("output_file", help="Path to the output markdown file.")
   parser.add_argument("paths", nargs='+', help="One or more file or directory paths to include.")
   parser.add_argument("--exclude", action="append", default=[], help="Patterns to exclude.")
   args = parser.parse_args()
   
   exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + args.exclude
   processed_files = set()
   
   with open(args.output_file, 'w', encoding='utf-8') as outfile:
       for path in args.paths:
           norm_path = os.path.normpath(path)
           if not os.path.exists(norm_path):
               print(f"⚠️ Warning: Path not found, skipping: {norm_path}")
               continue
           
           is_excluded = any(fnmatch.fnmatch(os.path.basename(norm_path), p) for p in exclude_patterns)
           if not is_excluded:
               process_path_for_md(norm_path, outfile, exclude_patterns, processed_files)

   print(f"\n🎉 Success! All paths processed into '{args.output_file}'.")

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/contexter.egg-info-PKG-INFO ---

````egg-info-pkg-info
Metadata-Version: 2.4
Name: contexter
Version: 4.0.0
Summary: A suite of tools to package, reconstruct, and update software projects as single text-based context files (MD or HTML).
Author-email: Your Name <you@example.com>
Project-URL: Homepage, https://github.com/your-username/contexter
Project-URL: Bug Tracker, https://github.com/your-username/contexter/issues
Classifier: Programming Language :: Python :: 3
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Topic :: Software Development :: Build Tools
Classifier: Topic :: Utilities
Requires-Python: >=3.7
Description-Content-Type: text/markdown
Requires-Dist: markdown
Requires-Dist: Pygments
Requires-Dist: markdownify
Requires-Dist: beautifulsoup4
Requires-Dist: patch

```markdown
# Contexter

Contexter is a powerful suite of Python command-line tools for packaging, reconstructing, and updating software projects as single, portable Markdown or HTML files. This workflow is perfect for sharing entire projects with AI models, creating simple text-based backups, or transferring projects between machines.

## New in This Version: AI Workflow ✅

We've added a `sanitizecontext` command to fix common formatting errors when you copy a full project context from an AI chat. Since AI models can sometimes forget to add code fences (````), this tool makes the output instantly usable.

**New Workflow:**
1.  Paste the AI's response into `ai_output.md`.
2.  Run: `sanitize_context ai_output.md clean_project.md`
3.  Reconstruct: `reconstructor clean_project.md ./my-new-project`

## Command Reference

| Command             | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| Command             | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| `context_builder`   | Packages a directory into a single Markdown file.                        |
| `reconstructor`     | Rebuilds a project from a Markdown context file.                         |
| `sanitize_context`  | **(New)** Fixes AI-generated Markdown to be a valid Contexter file.        |
| `update_context`    | Creates a patch file by comparing two `.md` context files.               |
| `updater`           | Applies a patch file to an `.md` context file.                           |
| `smart_update`      | **(Recommended)** Creates a patch using `rsync` for high efficiency.     |
| `build_context_html`| Packages a directory into a single HTML file.                            |
| `reconstructor_html`| Rebuilds a project from an HTML context file.                            |
| `update_context_html`| Creates a patch (`.md` or `.html`) from two `.html` files.               |
| `updater_html`      | Applies a patch (`.md` or `.html`) to an `.html` file.                   |
| `md2html`           | A utility to convert any Markdown file to HTML.                          |
| `html2md`           | A utility to convert any HTML file to Markdown.                          |

For detailed usage, run any command with the `-h` or `--help` flag.
````

--- FILE: ContexterGem/contexter_utils.py ---

````python
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
   header_pattern = re.compile(r"^--- (FILE|SKIPPED \(BINARY\)): (.*) ---")
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
   diff_header_pattern = re.compile(r"^--- DIFF FOR: (.*) ---")
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
   """ ]
   
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
````

--- FILE: ContexterGem/html2md.py ---

````python
#!/usr/bin/env python3
import argparse
from markdownify import markdownify as md

def convert_html_to_md(input_file, output_file):
   """Converts an HTML file back to a Markdown file."""
   print(f"🚀 Converting '{input_file}' to '{output_file}'...")
   try:
       with open(input_file, 'r', encoding='utf-8') as f:
           html_content = f.read()
       md_content = md(html_content, heading_style="ATX")
       with open(output_file, 'w', encoding='utf-8') as f:
           f.write(md_content)
       print(f"✅ Success! File converted to '{output_file}'.")
   except FileNotFoundError:
       print(f"❌ Error: Input file '{input_file}' not found.")
   except Exception as e:
       print(f"❌ An unexpected error occurred: {e}")

def main():
   parser = argparse.ArgumentParser(description="Convert an HTML file to a Markdown file.")
   parser.add_argument("input_file", help="Path to the input HTML file.")
   parser.add_argument("output_file", help="Path for the output Markdown file.")
   args = parser.parse_args()
   convert_html_to_md(args.input_file, args.output_file)

if __name__ == "__main__":
   main()
````

--- SKIPPED (BINARY): ContexterGem/install.sh ---

--- FILE: ContexterGem/md2html.py ---

````python
#!/usr/bin/env python3
import argparse
import markdown
from pygments.formatters import HtmlFormatter

def convert_md_to_html(input_file, output_file):
   """Converts a Markdown file to a styled HTML file with syntax highlighting."""
   print(f"🚀 Converting '{input_file}' to '{output_file}'...")
   try:
       with open(input_file, 'r', encoding='utf-8') as f:
           md_content = f.read()

       html_content = markdown.markdown(
           md_content,
           extensions=['fenced_code', 'codehilite', 'tables']
       )
       
       css_style = """
       <style>
           body { font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; }
           pre { background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
           code { font-family: monospace; }
           h1, h2, h3 { border-bottom: 1px solid #ddd; padding-bottom: 5px; }
           table { border-collapse: collapse; width: 100%; }
           th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
           th { background-color: #f2f2f2; }
       </style>
       """
       pygments_css = HtmlFormatter().get_style_defs('.codehilite')
       css_style += f"<style>{pygments_css}</style>"

       full_html = f"""
       <!DOCTYPE html><html lang="en"><head>
           <meta charset="UTF-8"><title>{input_file}</title>{css_style}
       </head><body>{html_content}</body></html>
       """
       with open(output_file, 'w', encoding='utf-8') as f:
           f.write(full_html)
       print(f"✅ Success! File converted to '{output_file}'.")
   except FileNotFoundError:
       print(f"❌ Error: Input file '{input_file}' not found.")
   except Exception as e:
       print(f"❌ An unexpected error occurred: {e}")

def main():
   parser = argparse.ArgumentParser(description="Convert a Markdown file to a styled HTML file.")
   parser.add_argument("input_file", help="Path to the input Markdown file.")
   parser.add_argument("output_file", help="Path for the output HTML file.")
   args = parser.parse_args()
   convert_md_to_html(args.input_file, args.output_file)

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/project.toml ---

````toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "contexter"
version = "2.1.0"
authors = [
 { name="Your Name", email="you@example.com" },
]
description = "A suite of tools to package, reconstruct, and update software projects as single text-based context files (MD or HTML)."
readme = "README.md"
requires-python = ">=3.7"
classifiers = [
   "Programming Language :: Python :: 3",
   "License :: OSI Approved :: MIT License",
   "Operating System :: OS Independent",
   "Topic :: Software Development :: Build Tools",
   "Topic :: Utilities",
]
dependencies = [
   "markdown",
   "Pygments",
   "markdownify",
   "beautifulsoup4",
   "patch",
]

[project.urls]
"Homepage" = "https://github.com/your-username/contexter"
"Bug Tracker" = "https://github.com/your-username/contexter/issues"

# This new section defines all the command-line tools
[project.scripts]
buildcontext = "context_builder:main"
reconstructor = "reconstructor:main"
updatecontext = "update_context:main"
updater = "updater:main"
smartupdate = "smart_update:main"
sanitizecontext = "sanitize_context:main"
sync = "sync_context:main"
md2html = "md2html:main"
html2md = "html2md:main"
buildcontexthtml = "build_context_html:main"
reconstructorhtml = "reconstructor_html:main"
updatecontexthtml = "update_context_html:main"
updaterhtml = "updater_html:main"
````

--- FILE: ContexterGem/pyproject.toml ---

````toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "contexter"
version = "4.0.0"
authors = [
 { name="Your Name", email="you@example.com" },
]
description = "A suite of tools to package, reconstruct, and update software projects as single text-based context files (MD or HTML)."
readme = "README.md"
requires-python = ">=3.7"
classifiers = [
   "Programming Language :: Python :: 3",
   "License :: OSI Approved :: MIT License",
   "Operating System :: OS Independent",
   "Topic :: Software Development :: Build Tools",
   "Topic :: Utilities",
]
dependencies = [
   "markdown",
   "Pygments",
   "markdownify",
   "beautifulsoup4",
   "patch",
]

[project.urls]
"Homepage" = "https://github.com/your-username/contexter"
"Bug Tracker" = "https://github.com/your-username/contexter/issues"

[project.scripts]
build_context_html = "build_context_html:main"
context_builder = "context_builder:main"
html2md = "html2md:main"
md2html = "md2html:main"
reconstructor = "reconstructor:main"
reconstructor_html = "reconstructor_html:main"
sanitize_context = "sanitize_context:main"
smart_update = "smart_update:main"
update_context = "update_context:main"
update_context_html = "update_context_html:main"
updater = "updater:main"
updater_html = "updater_html:main"
````

--- FILE: ContexterGem/reconstructor.py ---

````python
#!/usr/bin/env python3
import argparse
import os
from contexter_utils import parse_md_constructor

def main():
   parser = argparse.ArgumentParser(description="Reconstruct a project from a Markdown context file.")
   parser.add_argument("input_file", help="Path to the input markdown file.")
   parser.add_argument("output_dir", help="Name of the new directory to create.")
   args = parser.parse_args()

   print(f"🚀 Starting reconstruction from '{args.input_file}' into '{args.output_dir}'...")
   files_to_create = parse_md_constructor(args.input_file)
   
   if files_to_create is None:
       print(f"❌ Error: Could not parse input file '{args.input_file}'. Aborting.")
       return

   os.makedirs(args.output_dir, exist_ok=True)
   files_created = 0
   placeholders = 0

   for path, content in files_to_create.items():
       # Ensure path is relative and safe
       if path.startswith('/') or path.startswith('\\'):
           safe_path = os.path.normpath(path[1:])
       else:
           safe_path = os.path.normpath(path)
       full_path = os.path.join(args.output_dir, safe_path)
       try:
           os.makedirs(os.path.dirname(full_path), exist_ok=True)
           if content is not None:
               with open(full_path, 'w', encoding='utf-8') as f:
                   f.write(content)
               print(f"✅ Wrote file: {full_path}")
               files_created += 1
           else: # Binary placeholder
               # Create an empty file as a placeholder
               with open(full_path, 'w') as f:
                   pass
               print(f"⚫ Created placeholder for binary: {full_path}")
               placeholders += 1
       except Exception as e:
           print(f"❌ Error writing file {full_path}: {e}")

   print("\n🎉 Reconstruction complete!")
   print(f"   - Files created: {files_created}")
   print(f"   - Binary placeholders created: {placeholders}")

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/reconstructor_html.py ---

````python
#!/usr/bin/env python3
import argparse
import os
from contexter_utils import parse_html_constructor

def main():
   parser = argparse.ArgumentParser(description="Reconstruct a project from an HTML context file.")
   parser.add_argument("input_file", help="Path to the input HTML file.")
   parser.add_argument("output_dir", help="Name of the new directory to create.")
   args = parser.parse_args()

   print(f"🚀 Starting reconstruction from '{args.input_file}' into '{args.output_dir}'...")
   files_to_create = parse_html_constructor(args.input_file)

   if files_to_create is None:
       print(f"❌ Error: Could not parse input file '{args.input_file}'. Aborting.")
       return

   os.makedirs(args.output_dir, exist_ok=True)
   files_created = 0
   placeholders = 0

   for path, content in files_to_create.items():
       if path.startswith('/') or path.startswith('\\'):
           safe_path = os.path.normpath(path[1:])
       else:
           safe_path = os.path.normpath(path)
       full_path = os.path.join(args.output_dir, safe_path)
       try:
           os.makedirs(os.path.dirname(full_path), exist_ok=True)
           if content is not None:
               with open(full_path, 'w', encoding='utf-8') as f:
                   f.write(content)
               print(f"✅ Wrote file: {full_path}")
               files_created += 1
           else: # Binary placeholder
               with open(full_path, 'w') as f:
                   pass
               print(f"⚫ Created placeholder for binary: {full_path}")
               placeholders += 1
       except Exception as e:
           print(f"❌ Error writing file {full_path}: {e}")

   print("\n🎉 Reconstruction complete!")
   print(f"   - Files created: {files_created}")
   print(f"   - Binary placeholders created: {placeholders}")

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/requirements.txt ---

````txt
markdown
Pygments
markdownify
beautifulsoup4
patch
````

--- FILE: ContexterGem/sanitize_context.py ---

````python
#!/usr/bin/env python3
import argparse
import re
from contexter_utils import get_language_from_path

def sanitize_file(input_path, output_path):
    """Reads a potentially malformed constructor file and writes a valid one."""
    
    header_pattern = re.compile(r"^(--- (?:FILE|SKIPPED \(BINARY\)|DIRECTORY STRUCTURE): .* ---)$$")
    file_header_pattern = re.compile(r"^--- FILE: (.*) ---")
    fence_pattern = re.compile(r"^````.*")

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"❌ Error: Input file not found at '{input_path}'")
        return

    sanitized_lines = []
    in_file_block = False
    current_filepath = None

    for i, line in enumerate(lines):
        header_match = header_pattern.match(line.strip())
        
        # If we find any header, it marks the end of the previous file's content
        if header_match:
            if in_file_block:
                # Add a closing fence if the previous line wasn't one already
                if sanitized_lines and not fence_pattern.match(sanitized_lines[-1].strip()):
                    sanitized_lines.append("````\n\n")
                in_file_block = False

            sanitized_lines.append(line)
            file_header_match = file_header_pattern.match(line.strip())

            if file_header_match:
                in_file_block = True
                current_filepath = file_header_match.group(1).strip()
                # Check the next line to see if a fence is missing
                if i + 1 < len(lines) and not fence_pattern.match(lines[i+1].strip()):
                    lang = get_language_from_path(current_filepath)
                    sanitized_lines.append(f"````{lang}\n")
            
        else:
            sanitized_lines.append(line)

    # After the loop, if we were still in a file block, close it
    if in_file_block:
        if sanitized_lines and not fence_pattern.match(sanitized_lines[-1].strip()):
            sanitized_lines.append("````\n")

    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.writelines(sanitized_lines)

    print(f"✅ Success! Sanitized file written to '{output_path}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Sanitize a Markdown constructor file from an AI to ensure it's valid."
    )
    parser.add_argument("input_file", help="Path to the potentially malformed input file.")
    parser.add_argument("output_file", help="Path to write the sanitized, valid output file.")
    args = parser.parse_args()
    sanitize_file(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
````

--- FILE: ContexterGem/setup.py ---

````python
# setup.py
# This file explicitly lists the python modules to be included in the package,
# which is required for a "flat-layout" project structure like this one.
from setuptools import setup

setup(
    py_modules=[
        'build_context_html',
        'context_builder',
        'contexter_utils',
        'html2md',
        'md2html',
        'reconstructor',
        'reconstructor_html',
        'sanitize_context',
        'smart_update',
        'sync_context',
        'update_context',
        'update_context_html',
        'updater',
        'updater_html'
    ]
)
````

--- FILE: ContexterGem/smart_update.py ---

````python
#!/usr/bin/env python3
import argparse
import os
import subprocess
import shutil
import difflib
import re

from contexter_utils import DEFAULT_EXCLUDE_PATTERNS, get_language_from_path

def check_rsync():
    """Check if rsync is available in the system's PATH."""
    if not shutil.which("rsync"):
        print("❌ Error: `rsync` command not found.")
        print("Please install rsync and ensure it is in your system's PATH.")
        return False
    return True

def run_rsync(command):
    """Executes an rsync command and returns its output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing rsync: {e}")
        print(f"   Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        return None # Handled by check_rsync, but as a fallback

def parse_rsync_output(output, project_dir):
    """Parses the itemized output of rsync to categorize file changes."""
    changes = {'added': [], 'deleted': [], 'modified': []}
    # Pattern to match rsync's itemized output format, e.g., ">f.st......"
    # We only care about files (f), not directories, links, etc. for content diffing.
    change_pattern = re.compile(r"^(>f|hf)(\.|+).*? (.*)$")
    delete_pattern = re.compile(r"^\*deleting   (.*)$")

    for line in output.splitlines():
        delete_match = delete_pattern.match(line)
        if delete_match:
            path = delete_match.group(1).strip()
            if not path.endswith('/'): # Ignore directories
                changes['deleted'].append(os.path.join(project_dir, path))
            continue

        change_match = change_pattern.match(line)
        if change_match:
            change_type, change_flags, path_str = change_match.groups()
            path = os.path.join(project_dir, path_str.strip())
            
            if '+' in change_flags:
                changes['added'].append(path)
            else:
                changes['modified'].append(path)
    return changes

def main():
    if not check_rsync():
        return

    parser = argparse.ArgumentParser(
        description="Efficiently create a patch file using rsync to detect changes."
    )
    parser.add_argument("project_dir", help="The project directory to analyze.")
    parser.add_argument("patch_output_file", help="Path to write the resulting patch file.")
    args = parser.parse_args()

    project_dir = os.path.normpath(args.project_dir)
    cache_dir = os.path.join(project_dir, ".contexter_cache")

    # Sync cache for the first time if it doesn't exist
    if not os.path.exists(cache_dir):
        print(f"🛠️  No cache found. Creating initial cache at '{cache_dir}'...")
        os.makedirs(cache_dir, exist_ok=True)
        rsync_command = ["rsync", "-a", "--delete"]
        rsync_command.extend([f"--exclude={p}" for p in DEFAULT_EXCLUDE_PATTERNS])
        rsync_command.append(f"{project_dir}/")
        rsync_command.append(f"{cache_dir}/")
        run_rsync(rsync_command)
        print("✅ Initial cache created. Run smartupdate again to detect future changes.")
        return

    print("🔍 Using rsync to find changes...")
    # Use rsync in dry-run, itemized mode to find what has changed
    rsync_dry_run_cmd = ["rsync", "-a", "-n", "-i", "--delete"]
    rsync_dry_run_cmd.extend([f"--exclude={p}" for p in DEFAULT_EXCLUDE_PATTERNS])
    rsync_dry_run_cmd.append(f"{project_dir}/")
    rsync_dry_run_cmd.append(f"{cache_dir}/")
    
    rsync_output = run_rsync(rsync_dry_run_cmd)
    if rsync_output is None:
        return

    changes = parse_rsync_output(rsync_output, project_dir)
    all_changes = changes['added'] + changes['deleted'] + changes['modified']

    if not all_changes:
        print("✨ Project is already in sync. No patch file needed.")
        return

    print("📝 Generating patch file...")
    with open(args.patch_output_file, 'w', encoding='utf-8') as outfile:
        # Handle added and modified files
        for file_path in sorted(changes['added'] + changes['modified']):
            rel_path = os.path.relpath(file_path, project_dir)
            old_file_path = os.path.join(cache_dir, rel_path)
            
            old_content = ""
            if os.path.exists(old_file_path):
                try:
                    with open(old_file_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                except (IOError, UnicodeDecodeError):
                    print(f"⚠️ Could not read old version of {rel_path}. Treating as new file.")

            new_content = ""
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        new_content = f.read()
                except (IOError, UnicodeDecodeError) as e:
                    print(f"❌ Error reading new version of {rel_path}: {e}. Skipping.")
                    continue

            diff = difflib.unified_diff(
                old_content.splitlines(), new_content.splitlines(),
                fromfile=rel_path, tofile=rel_path, lineterm=''
            )
            diff_str = "\n".join(diff)
            if diff_str:
                print(f"  - Found changes in {rel_path}")
                outfile.write(f"--- DIFF FOR: {rel_path} ---\n\n```diff\n{diff_str}\n```\n\n")

        # Handle deleted files
        for file_path in sorted(changes['deleted']):
            rel_path = os.path.relpath(file_path, project_dir)
            old_file_path = os.path.join(cache_dir, rel_path)
            old_content = ""
            if os.path.exists(old_file_path):
                try:
                    with open(old_file_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                except (IOError, UnicodeDecodeError):
                    continue # Can't create a diff for a file we can't read

            print(f"  - Detected deletion of {rel_path}")
            diff = difflib.unified_diff(
                old_content.splitlines(), [],
                fromfile=rel_path, tofile=rel_path, lineterm=''
            )
            outfile.write(f"--- DIFF FOR: {rel_path} ---\n\n```diff\n" + "\n".join(diff) + "\n```\n\n")

    print(f"\n✅ Patch file created at '{args.patch_output_file}'.")

    # Finally, update the cache for the next run
    print("🔄 Updating cache to current state...")
    rsync_update_cmd = ["rsync", "-a", "--delete"]
    rsync_update_cmd.extend([f"--exclude={p}" for p in DEFAULT_EXCLUDE_PATTERNS])
    rsync_update_cmd.append(f"{project_dir}/")
    rsync_update_cmd.append(f"{cache_dir}/")
    run_rsync(rsync_update_cmd)
    print("🎉 Cache updated.")

if __name__ == "__main__":
    main()
````

--- FILE: ContexterGem/update_context.py ---

````python
#!/usr/bin/env python3
import argparse
import difflib
from contexter_utils import parse_md_constructor

def main():
   parser = argparse.ArgumentParser(description="Create a patch file by comparing two Markdown constructor files.")
   parser.add_argument("original_md", help="Path to the original constructor file.")
   parser.add_argument("modified_md", help="Path to the modified constructor file.")
   parser.add_argument("update_output_md", help="Path to write the resulting patch file.")
   args = parser.parse_args()

   print("Parsing original and modified constructor files...")
   original_files = parse_md_constructor(args.original_md)
   modified_files = parse_md_constructor(args.modified_md)

   if original_files is None or modified_files is None: return

   print("Comparing files and generating diffs...")
   with open(args.update_output_md, 'w', encoding='utf-8') as outfile:
       all_keys = sorted(list(set(original_files.keys()) | set(modified_files.keys())))
       for file_path in all_keys:
           # Provide empty string for files that are None (binary) or missing
           original_content = original_files.get(file_path) or ""
           modified_content = modified_files.get(file_path) or ""
           
           if original_content != modified_content:
               print(f"  - Found changes in {file_path}")
               diff = difflib.unified_diff(
                   original_content.splitlines(), modified_content.splitlines(),
                   fromfile=file_path, tofile=file_path, lineterm=''
               )
               outfile.write(f"--- DIFF FOR: {file_path} ---\n\n```diff\n" + "\n".join(diff) + "\n```\n\n")

   print(f"\n🎉 Success! Update file created at '{args.update_output_md}'")

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/update_context_html.py ---

````python
#!/usr/bin/env python3
import argparse
import difflib
import html
from contexter_utils import parse_html_constructor

def write_md_patch(output_path, diffs):
   """Writes the diffs to a Markdown formatted patch file."""
   with open(output_path, 'w', encoding='utf-8') as f:
       for file_path, diff_content in diffs.items():
           f.write(f"--- DIFF FOR: {file_path} ---\n\n")
           f.write("```diff\n")
           f.write(diff_content)
           f.write("\n```\n\n")

def write_html_patch(output_path, diffs):
   """Writes the diffs to a styled HTML formatted patch file."""
   css_style = """
   <style>
       body { font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 1000px; margin: 0 auto; }
       .diff-container { border: 1px solid #ddd; border-radius: 8px; margin-bottom: 2rem; }
       h2 { background-color: #f7f7f7; padding: 0.75rem 1rem; margin: 0; border-bottom: 1px solid #ddd; font-size: 1.1rem; }
       .path { font-family: monospace; color: #a72d2d; }
       pre { margin: 0; padding: 1rem; overflow-x: auto; white-space: pre-wrap; font-family: monospace; font-size: 0.9em; }
       .line.add { background-color: #e6ffed; display: block; }
       .line.rem { background-color: #ffeef0; display: block; text-decoration: line-through; }
       .line.context { display: block; color: #666; }
   </style>
   """
   html_parts = [f"<!DOCTYPE html><html lang='en'><head><title>Update Patch</title>{css_style}</head><body><h1>Project Update Patch</h1>"]

   for file_path, diff_content in diffs.items():
       html_parts.append(f'<div class="diff-container" data-path="{html.escape(file_path)}">')
       html_parts.append(f'<h2>DIFF FOR: <span class="path">{html.escape(file_path)}</span></h2>')
       
       formatted_lines = []
       for line in diff_content.split('\n'):
           escaped_line = html.escape(line)
           if line.startswith('+'):
               formatted_lines.append(f'<span class="line add">{escaped_line}</span>')
           elif line.startswith('-'):
               formatted_lines.append(f'<span class="line rem">{escaped_line}</span>')
           else:
               formatted_lines.append(f'<span class="line context">{escaped_line}</span>')
       
       html_parts.append(f'<pre><code>{"".join(formatted_lines)}</code></pre>')
       html_parts.append('</div>')

   html_parts.append("</body></html>")
   with open(output_path, 'w', encoding='utf-8') as f:
       f.write("".join(html_parts))

def main():
   parser = argparse.ArgumentParser(description="Create a patch file by comparing two HTML constructor files.")
   parser.add_argument("original_html", help="Path to the original HTML constructor file.")
   parser.add_argument("modified_html", help="Path to the modified HTML constructor file.")
   parser.add_argument("output_file", help="Path for the output patch file.")
   parser.add_argument("--format", choices=['md', 'html'], default='md', help="The output format for the patch file (default: md).")
   args = parser.parse_args()
   
   original_files = parse_html_constructor(args.original_html)
   modified_files = parse_html_constructor(args.modified_html)

   if original_files is None or modified_files is None: return

   print("⚖️  Comparing files and generating diffs...")
   diffs = {}
   all_keys = sorted(list(set(original_files.keys()) | set(modified_files.keys())))

   for file_path in all_keys:
       original_content = original_files.get(file_path, [])
       modified_content = modified_files.get(file_path, [])
       
       if original_content != modified_content:
           print(f"  - Found changes in {file_path}")
           diff_lines = list(difflib.unified_diff(
               original_content, modified_content,
               fromfile=file_path, tofile=file_path, lineterm=''
           ))
           if diff_lines:
               diffs[file_path] = "\n".join(diff_lines)

   if args.format == 'html':
       write_html_patch(args.output_file, diffs)
   else:
       write_md_patch(args.output_file, diffs)
   
   print(f"\n🎉 Success! Update file created at '{args.output_file}' in {args.format.upper()} format.")

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/updater.py ---

````python
#!/usr/bin/env python3
import argparse
import os
from contexter_utils import parse_md_constructor, parse_patch_file, get_language_from_path

def main():
   parser = argparse.ArgumentParser(description="Apply a patch file to a Markdown constructor file.")
   parser.add_argument("original_md", help="Path to the original constructor file.")
   parser.add_argument("update_md", help="Path to the update/patch file.")
   parser.add_argument("-o", "--output", help="Path for the new file. Defaults to overwriting the original.")
   parser.add_argument("--overwrite", action="store_true", help="Overwrite the original file (default behavior).")
   args = parser.parse_args()

   output_path = args.output if args.output else args.original_md

   print("Parsing original constructor and update files...")
   original_files = parse_md_constructor(args.original_md)
   patches_to_apply = parse_patch_file(args.update_md)

   if original_files is None or patches_to_apply is None: 
       print("❌ Error: Could not parse one or more input files. Aborting.")
       return

   updated_files = original_files.copy()

   for path, patch_set in patches_to_apply.items():
       # Handle newly added files
       if path not in updated_files:
           print(f"  - Applying patch to add new file {path}...")
           patched_content = patch_set.apply(b"") # Apply patch to empty content
           updated_files[path] = patched_content.decode('utf-8')
       # Handle file deletions
       elif not patch_set.hunks: # Empty patch implies deletion
            print(f"  - Applying patch to delete file {path}...")
            del updated_files[path]
       # Handle modifications
       elif path in updated_files and updated_files[path] is not None:
           print(f"  - Applying patch to modify {path}...")
           original_content = updated_files[path].encode('utf-8')
           patched_content = patch_set.apply(original_content)
           updated_files[path] = patched_content.decode('utf-8')
       else:
           print(f"⚠️ Warning: File '{path}' from patch not found or is binary in original. Skipping.")

   print(f"Rebuilding constructor file at '{output_path}'...")
   with open(output_path, 'w', encoding='utf-8') as f:
       # Write tree structure if it exists (placeholder for now)
       # This simple updater doesn't regenerate the tree.
       # For a perfect tree, one would rebuild from the patched file system.

       for path, content in sorted(updated_files.items()):
           if content is None:
               f.write(f"--- SKIPPED (BINARY): {path} ---\n\n")
           else:
               lang = get_language_from_path(path)
               f.write(f"--- FILE: {path} ---\n\n````{lang}\n{content.strip()}\n````\n\n")

   print("\n🎉 Success! Updates have been applied.")

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/updater_html.py ---

````python
#!/usr/bin/env python3
import argparse
import os
from contexter_utils import (
   parse_html_constructor, parse_patch_file, rebuild_html_constructor
)

def main():
   parser = argparse.ArgumentParser(description="Apply a patch file (MD or HTML) to an HTML constructor file.")
   parser.add_argument("original_html", help="Path to the original HTML constructor file.")
   parser.add_argument("update_file", help="Path to the update/patch file (can be .md or .html).")
   parser.add_argument("-o", "--output", help="Path for the new HTML constructor file.", default=None)
   parser.add_argument("--overwrite", action="store_true", help="Overwrite the original HTML file.")
   args = parser.parse_args()

   output_path = args.original_html if args.overwrite else args.output if args.output else args.original_html.replace('.html', '_v2.html')

   print("📄 Parsing original HTML constructor and update file...")
   original_files = parse_html_constructor(args.original_html)
   patches_to_apply = parse_patch_file(args.update_file)
   
   if original_files is None or patches_to_apply is None:
       print("❌ Error: Could not parse one or more input files. Aborting.")
       return
   
   updated_files = original_files.copy()

   for path, patch_set in patches_to_apply.items():
        # Handle additions
       if path not in updated_files:
           print(f"  - Applying patch to add new file {path}...")
           patched_content = patch_set.apply(b"")
           updated_files[path] = patched_content.decode('utf-8')
       # Handle deletions
       elif not patch_set.hunks:
            print(f"  - Applying patch to delete file {path}...")
            del updated_files[path]
       # Handle modifications
       elif path in updated_files and updated_files[path] is not None:
           print(f"  - Applying patch to modify {path}...")
           original_content = updated_files[path].encode('utf-8')
           patched_content = patch_set.apply(original_content)
           updated_files[path] = patched_content.decode('utf-8')
       else:
            print(f"⚠️ Warning: File '{path}' from patch not found or is binary in original HTML. Skipping.")

   print(f" Rebuilding HTML file at '{output_path}'...")
   rebuild_html_constructor(output_path, updated_files)
   print("\n🎉 Success! HTML updates have been applied.")

if __name__ == "__main__":
   main()
````

--- FILE: ContexterGem/contexter.egg-info/SOURCES.txt ---

````txt
README.md
build_context_html.py
context_builder.py
contexter_utils.py
html2md.py
md2html.py
pyproject.toml
reconstructor.py
reconstructor_html.py
sanitize_context.py
setup.py
smart_update.py
update_context.py
update_context_html.py
updater.py
updater_html.py
contexter.egg-info/PKG-INFO
contexter.egg-info/SOURCES.txt
contexter.egg-info/dependency_links.txt
contexter.egg-info/entry_points.txt
contexter.egg-info/requires.txt
contexter.egg-info/top_level.txt
````

--- FILE: ContexterGem/contexter.egg-info/dependency_links.txt ---

````txt

````

--- FILE: ContexterGem/contexter.egg-info/entry_points.txt ---

````txt
[console_scripts]
build_context_html = build_context_html:main
context_builder = context_builder:main
html2md = html2md:main
md2html = md2html:main
reconstructor = reconstructor:main
reconstructor_html = reconstructor_html:main
sanitize_context = sanitize_context:main
smart_update = smart_update:main
update_context = update_context:main
update_context_html = update_context_html:main
updater = updater:main
updater_html = updater_html:main
````

--- FILE: ContexterGem/contexter.egg-info/requires.txt ---

````txt
markdown
Pygments
markdownify
beautifulsoup4
patch
````

--- FILE: ContexterGem/contexter.egg-info/top_level.txt ---

````txt
build_context_html
context_builder
contexter_utils
html2md
md2html
reconstructor
reconstructor_html
sanitize_context
smart_update
sync_context
update_context
update_context_html
updater
updater_html
````

