```python
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