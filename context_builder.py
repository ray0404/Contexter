#!/usr/bin/env python3
import argparse
import os
import fnmatch
import shutil
import subprocess
import tempfile
import sys
from xml.sax.saxutils import escape
from contexter_utils import (
   DEFAULT_EXCLUDE_PATTERNS, is_binary, generate_file_tree, get_language_from_path,
   estimate_token_count, scan_for_secrets, compress_code, get_matcher
)

def fetch_remote_repo(remote_url, quiet=False):
    """Clones a remote repo to a temporary directory and returns the path."""
    # Handle user/repo shorthand for GitHub
    if not remote_url.startswith('http') and not remote_url.startswith('git@'):
        if len(remote_url.split('/')) == 2:
            remote_url = f"https://github.com/{remote_url}.git"
    
    temp_dir = tempfile.mkdtemp(prefix="contexter_repo_")
    if not quiet:
        print(f"🌍 Cloning remote repository: {remote_url}...", file=sys.stderr)
    try:
        subprocess.check_call(["git", "clone", "--depth", "1", remote_url, temp_dir], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return temp_dir
    except subprocess.CalledProcessError:
        shutil.rmtree(temp_dir)
        raise Exception(f"Failed to clone repository: {remote_url}")

def process_file_content(path, content, args):
    """Applies transformations (compression, security check) to content."""
    warnings = []
    
    if not args.no_security:
        sec_warnings = scan_for_secrets(content, path)
        if sec_warnings:
            warnings.extend(sec_warnings)
            print(f"🚨 Security Warning: {sec_warnings}", file=sys.stderr)

    if args.compress:
        content = compress_code(content, path)
        
    return content, warnings

def process_path_for_xml(path, outfile, exclude_patterns, processed_files, args, stats, matcher=None, base_path=None):
   """Recursively processes a path and writes to the XML file."""
   norm_path = os.path.normpath(path)
   if norm_path in processed_files:
       return
   
   processed_files.add(norm_path)

   if matcher is None:
       matcher = get_matcher(exclude_patterns)

   if os.path.isdir(norm_path):
       if not args.quiet:
           print(f"📂 Processing directory: {norm_path}", file=sys.stderr)
       is_top_level = len(processed_files) == 1
       if is_top_level:
           tree = generate_file_tree(norm_path, exclude_patterns)
           outfile.write(f"  <directory_structure>\n{escape(tree)}\n  </directory_structure>\n")

       for root, dirs, files in os.walk(norm_path, topdown=True):
           dirs[:] = sorted([d for d in dirs if not matcher(d)])
           files = sorted([f for f in files if not matcher(f)])
           for filename in files:
               file_path = os.path.join(root, filename)
               process_path_for_xml(file_path, outfile, exclude_patterns, processed_files, args, stats, matcher, base_path)

   elif os.path.isfile(norm_path):
       display_path = os.path.relpath(norm_path, base_path) if base_path else norm_path
       
       if is_binary(norm_path):
           if not args.quiet:
               print(f"⚫ Skipping (binary): {norm_path}", file=sys.stderr)
           outfile.write(f'  <file path="{escape(display_path)}" is_binary="true" />\n')
           return
       try:
           with open(norm_path, 'r', encoding='utf-8', errors='ignore') as infile:
               content = infile.read()
               
               content, warnings = process_file_content(norm_path, content, args)
               
               tokens = estimate_token_count(content)
               stats['tokens'] += tokens
               stats['files'] += 1
               
               outfile.write(f'  <file path="{escape(display_path)}">{escape(content)}</file>\n')
               if not args.quiet:
                   print(f"✅ Processed: {norm_path} ({tokens} tokens)", file=sys.stderr)
       except Exception as e:
           print(f"❌ Error reading file {norm_path}: {e}", file=sys.stderr)

def process_path_for_md(path, outfile, exclude_patterns, processed_files, args, stats, matcher=None, base_path=None):
   """Recursively processes a path and writes to the MD file, avoiding duplicates."""
   norm_path = os.path.normpath(path)
   if norm_path in processed_files:
       return
   
   processed_files.add(norm_path)

   if matcher is None:
       matcher = get_matcher(exclude_patterns)

   if os.path.isdir(norm_path):
       if not args.quiet:
           print(f"📂 Processing directory: {norm_path}", file=sys.stderr)
       is_top_level = len(processed_files) == 1
       if is_top_level:
           tree = generate_file_tree(norm_path, exclude_patterns)
           outfile.write(f"--- DIRECTORY STRUCTURE: {os.path.basename(norm_path)} ---\n\n````\n{tree}\n````\n\n")

       for root, dirs, files in os.walk(norm_path, topdown=True):
           dirs[:] = sorted([d for d in dirs if not matcher(d)])
           files = sorted([f for f in files if not matcher(f)])
           for filename in files:
               file_path = os.path.join(root, filename)
               process_path_for_md(file_path, outfile, exclude_patterns, processed_files, args, stats, matcher, base_path)

   elif os.path.isfile(norm_path):
       display_path = os.path.relpath(norm_path, base_path) if base_path else norm_path

       if is_binary(norm_path):
           if not args.quiet:
               print(f"⚫ Skipping (binary): {norm_path}", file=sys.stderr)
           outfile.write(f"--- SKIPPED (BINARY): {display_path} ---\n\n")
           return
       try:
           with open(norm_path, 'r', encoding='utf-8', errors='ignore') as infile:
               content = infile.read()
               
               content, warnings = process_file_content(norm_path, content, args)
               
               tokens = estimate_token_count(content)
               stats['tokens'] += tokens
               stats['files'] += 1
               
               lang = get_language_from_path(norm_path)
               outfile.write(f"--- FILE: {display_path} ---\n\n")
               outfile.write(f"````{lang}\n{content.strip()}\n````\n\n")
               if not args.quiet:
                   print(f"✅ Processed: {norm_path} ({tokens} tokens)", file=sys.stderr)
       except Exception as e:
           print(f"❌ Error reading file {norm_path}: {e}", file=sys.stderr)

def main():
   parser = argparse.ArgumentParser(description="Combine source files into a single context file.")
   parser.add_argument("output_file", nargs='?', help="Path to the output file (optional if --stdout is used).")
   parser.add_argument("paths", nargs='*', help="One or more file or directory paths to include.")
   parser.add_argument("--exclude", action="append", default=[], help="Patterns to exclude.")
   parser.add_argument("--format", choices=['markdown', 'xml'], default='markdown', help="Output format (default: markdown).")
   parser.add_argument("--compress", action="store_true", help="Compress code by removing comments/docstrings.")
   parser.add_argument("--no-security", action="store_true", help="Disable security checks for secrets.")
   parser.add_argument("--remote", help="Remote Git repository URL or user/repo (e.g., 'yamadashy/repomix').")
   parser.add_argument("--stdout", action="store_true", help="Output content directly to terminal (standard output).")
   parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress messages.")
   args = parser.parse_args()
   
   # If stdout is used, enable quiet mode by default to keep the output clean
   if args.stdout:
       args.quiet = True

   # Handle argument shift when --stdout is used
   # If --stdout is set, the first positional argument (parsed as output_file) 
   # should be treated as a source path.
   if args.stdout and args.output_file:
       args.paths.insert(0, args.output_file)
       args.output_file = None

   if not args.paths and not args.remote:
       parser.error("You must provide at least one path OR a --remote repository.")
   
   if not args.output_file and not args.stdout:
       parser.error("You must provide an output_file OR use the --stdout flag.")
   
   exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + args.exclude
   matcher = get_matcher(exclude_patterns)
   processed_files = set()
   stats = {'tokens': 0, 'files': 0}
   
   temp_repo_dir = None
   source_paths = args.paths
   
   try:
       if args.remote:
           temp_repo_dir = fetch_remote_repo(args.remote, quiet=args.quiet)
           if not source_paths:
               source_paths = [temp_repo_dir]
           if ".git*" not in exclude_patterns:
               exclude_patterns.append(".git*")
               matcher = get_matcher(exclude_patterns)

       # Use sys.stdout if --stdout, otherwise open file
       if args.stdout:
           outfile = sys.stdout
       else:
           outfile = open(args.output_file, 'w', encoding='utf-8')

       try:
           if args.format == 'xml':
               outfile.write('<contexter_output>\n')

           for path in source_paths:
               norm_path = os.path.normpath(path)
               if not os.path.exists(norm_path):
                   if not args.quiet:
                       print(f"⚠️ Warning: Path not found, skipping: {norm_path}", file=sys.stderr)
                   continue
               
               base_path = temp_repo_dir if args.remote else None

               if not matcher(os.path.basename(norm_path)):
                   if args.format == 'xml':
                       process_path_for_xml(norm_path, outfile, exclude_patterns, processed_files, args, stats, matcher, base_path)
                   else:
                       process_path_for_md(norm_path, outfile, exclude_patterns, processed_files, args, stats, matcher, base_path)

           if args.format == 'xml':
               outfile.write('</contexter_output>\n')
       finally:
           if not args.stdout:
               outfile.close()

       if not args.quiet:
           print(f"\n🎉 Success! All paths processed.", file=sys.stderr)
           if not args.stdout:
               print(f"📄 Output saved to: '{args.output_file}'", file=sys.stderr)
           print(f"📊 Summary: {stats['files']} files, ~{stats['tokens']} tokens.", file=sys.stderr)
       
   except Exception as e:
       print(f"\n❌ Error: {e}", file=sys.stderr)
   finally:
       if temp_repo_dir and os.path.exists(temp_repo_dir):
           if not args.quiet:
               print("🧹 Cleaning up temporary repository...", file=sys.stderr)
           shutil.rmtree(temp_repo_dir)

if __name__ == "__main__":
   main()
