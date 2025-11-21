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
