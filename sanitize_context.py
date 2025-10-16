```python
#!/usr/bin/env python3
import argparse
import re
from contexter_utils import get_language_from_path

def sanitize_file(input_path, output_path):
    """Reads a potentially malformed constructor file and writes a valid one."""
    
    header_pattern = re.compile(r"^(--- (?:FILE|SKIPPED \(BINARY\)|DIRECTORY STRUCTURE): .* ---)$")
    file_header_pattern = re.compile(r"^--- FILE: (.*) ---$")
    fence_pattern = re.compile(r"^````.*")

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"❌ Error: Input file not found at '{input_path}'")
        return

    sanitized_lines = []
    in_file_block = False
    current_filepath = None

    for i, line in enumerate(lines):
        header_match = header_pattern.match(line.strip())
        
        # If we find any header, it marks the end of the previous file's content
        if header_match:
            if in_file_block:
                # Add a closing fence if the previous line wasn't one already
                if sanitized_lines and not fence_pattern.match(sanitized_lines[-1].strip()):
                    sanitized_lines.append("````\n\n")
                in_file_block = False

            sanitized_lines.append(line)
            file_header_match = file_header_pattern.match(line.strip())

            if file_header_match:
                in_file_block = True
                current_filepath = file_header_match.group(1).strip()
                # Check the next line to see if a fence is missing
                if i + 1 < len(lines) and not fence_pattern.match(lines[i+1].strip()):
                    lang = get_language_from_path(current_filepath)
                    sanitized_lines.append(f"````{lang}\n")
            
        else:
            sanitized_lines.append(line)

    # After the loop, if we were still in a file block, close it
    if in_file_block:
        if sanitized_lines and not fence_pattern.match(sanitized_lines[-1].strip()):
            sanitized_lines.append("````\n")

    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.writelines(sanitized_lines)

    print(f"✅ Success! Sanitized file written to '{output_path}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Sanitize a Markdown constructor file from an AI to ensure it's valid."
    )
    parser.add_argument("input_file", help="Path to the potentially malformed input file.")
    parser.add_argument("output_file", help="Path to write the sanitized, valid output file.")
    args = parser.parse_args()
    sanitize_file(args.input_file, args.output_file)

if __name__ == "__main__":
    main()