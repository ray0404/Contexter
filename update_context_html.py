```python
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