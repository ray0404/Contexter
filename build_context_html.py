#!/usr/bin/env python3
import argparse
import os
from contexter_utils import (
   DEFAULT_EXCLUDE_PATTERNS, safe_read_text, generate_file_tree, rebuild_html_constructor, get_matcher
)

def main():
   parser = argparse.ArgumentParser(description="Combine project files into a single, styled HTML file.")
   parser.add_argument("output_file", help="Path for the output HTML file.")
   parser.add_argument("paths", nargs='+', help="File and/or directory paths to include.")
   parser.add_argument("--exclude", action="append", default=[], help="Patterns to exclude.")
   args = parser.parse_args()
   
   exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + args.exclude
   files_to_include = {}
   tree_content_parts = []
   is_excluded = get_matcher(exclude_patterns)

   for path in args.paths:
       norm_path = os.path.normpath(path)
       if not os.path.exists(norm_path):
           print(f"⚠️ Warning: Path not found, skipping: {norm_path}")
           continue
       
       if is_excluded(os.path.basename(norm_path)):
           continue

       if os.path.isdir(norm_path):
           print(f"📂 Processing directory: {norm_path}")
           tree_content_parts.append(generate_file_tree(norm_path, exclude_patterns, is_excluded) + "\n\n")
           for root, dirs, files in os.walk(norm_path, topdown=True):
               dirs[:] = sorted([d for d in dirs if not is_excluded(d)])
               for filename in sorted(files):
                   if is_excluded(filename): continue
                   file_path = os.path.join(root, filename)
                   is_bin, content = safe_read_text(file_path)
                   if is_bin:
                       print(f"⚫ Skipping (binary): {file_path}")
                       files_to_include[file_path] = None
                   else:
                       files_to_include[file_path] = content
                       print(f"✅ Processed: {file_path}")
       elif os.path.isfile(norm_path):
            # Logic to handle single files, similar to directory walk
           is_bin, content = safe_read_text(norm_path)
           if is_bin:
               files_to_include[norm_path] = None
           else:
               files_to_include[norm_path] = content
   
   rebuild_html_constructor(args.output_file, files_to_include, "".join(tree_content_parts).strip())
   print(f"\n🎉 Success! HTML context file created at '{args.output_file}'.")

if __name__ == "__main__":
   main()
