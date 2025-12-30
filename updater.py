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
