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