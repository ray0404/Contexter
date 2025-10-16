```python
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