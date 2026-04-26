#!/usr/bin/env python3
import argparse
import os
from contexter_utils import parse_md_constructor, parse_xml_constructor

def detect_format_and_parse(input_file):
    """Detects if the file is XML or Markdown and returns the parsed dictionary."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            first_chars = f.read(50).strip()
            
        if first_chars.startswith('<'):
            print("ℹ️  Detected format: XML")
            return parse_xml_constructor(input_file)
        else:
            print("ℹ️  Detected format: Markdown")
            return parse_md_constructor(input_file)
    except Exception as e:
        print(f"❌ Error detecting format: {e}")
        return None

def main():
   parser = argparse.ArgumentParser(description="Reconstruct a project from a Markdown or XML context file.")
   parser.add_argument("input_file", help="Path to the input context file.")
   parser.add_argument("output_dir", help="Name of the new directory to create.")
   args = parser.parse_args()

   print(f"🚀 Starting reconstruction from '{args.input_file}' into '{args.output_dir}'...")
   
   files_to_create = detect_format_and_parse(args.input_file)
   
   if files_to_create is None:
       print(f"❌ Error: Could not parse input file '{args.input_file}'. Aborting.")
       return

   os.makedirs(args.output_dir, exist_ok=True)
   files_created = 0
   placeholders = 0

   for path, content in files_to_create.items():
       # Ensure path is relative and safe
       safe_path = os.path.normpath(path.lstrip('/\\'))
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
