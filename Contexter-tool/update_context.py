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
