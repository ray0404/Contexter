```python
```Python
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