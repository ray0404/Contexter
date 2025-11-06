import os
import re
from pathlib import Path
import fnmatch
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict

# --- 1. Pydantic Models (Structured Responses) ---
# We need clear, structured responses for your no-console environment.

class FileOpResult(BaseModel):
    """Generic result for an operation that creates or modifies a file."""
    success: bool = Field(..., description="Whether the operation was successful.")
    message: str = Field(..., description="A status message or error details.")
    output_file_path: str | None = Field(default=None, description="The absolute path to the generated/modified file.")
    files_processed: int = Field(default=0, description="The number of files read or written.")

class ReconstructResult(BaseModel):
    """Result for a reconstructor operation."""
    success: bool = Field(..., description="Whether the reconstruction was successful.")
    message: str = Field(..., description="A status message or error details.")
    output_directory: str | None = Field(default=None, description="The absolute path to the output directory.")
    files_created: int = Field(default=0, description="The number of files created.")

# --- 2. FastMCP Server Instance ---

mcp = FastMCP(
    name="Contexter Server (Full Suite)",
    instructions="A complete suite of tools for building, updating, converting, and reconstructing AI context files from project directories."
)


# --- 3. Core Logic (Refactored from contexter_utils.py) ---
# These "private" helpers are used by all the tools.

def _get_ignore_patterns(src_path: Path, ignore_file_name: str, extra_ignores: List[str] = []) -> List[str]:
    """Loads ignore patterns from the ignore file and adds defaults."""
    ignore_file_path = src_path / ignore_file_name
    patterns = []
    if ignore_file_path.exists():
        with open(ignore_file_path, 'r', encoding='utf-8') as f:
            patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    patterns.extend([".git/*", ignore_file_name] + extra_ignores)
    return patterns

def _scan_directory(src_path: Path, ignore_patterns: List[str]) -> List[Path]:
    """Scans the directory and returns a list of all files that are NOT ignored."""
    included_files = []
    for root, dirs, files in os.walk(src_path, topdown=True):
        current_path = Path(root)
        dirs[:] = [
            d for d in dirs 
            if not any(fnmatch.fnmatch(current_path.joinpath(d).relative_to(src_path), p) for p in ignore_patterns)
        ]
        for file in files:
            file_path = current_path / file
            rel_path = file_path.relative_to(src_path)
            if not any(fnmatch.fnmatch(rel_path, p) for p in ignore_patterns):
                included_files.append(file_path)
    return included_files

def _read_file_content(file_path: Path) -> str | None:
    """Safely reads a file's content, ignoring read errors."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return None

def _write_context_md(file_paths: List[Path], src_path: Path, out_path: Path) -> int:
    """Writes a list of files to a Markdown context file."""
    count = 0
    with open(out_path, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# Project Context: {src_path.name}\n\n")
        for file_path in file_paths:
            content = _read_file_content(file_path)
            if content is not None:
                rel_path = file_path.relative_to(src_path)
                outfile.write(f"## `{rel_path}`\n\n")
                outfile.write("```\n")
                outfile.write(content.strip() + "\n")
                outfile.write("```\n\n")
                count += 1
    return count

def _write_context_html(file_paths: List[Path], src_path: Path, out_path: Path) -> int:
    """Writes a list of files to an HTML context file."""
    import markdown2 # Use the library for robust conversion
    count = 0
    with open(out_path, 'w', encoding='utf-8') as outfile:
        outfile.write(f"<html><head><title>Project Context: {src_path.name}</title></head><body>\n")
        outfile.write(f"<h1>Project Context: {src_path.name}</h1>\n\n")
        for file_path in file_paths:
            content = _read_file_content(file_path)
            if content is not None:
                rel_path = file_path.relative_to(src_path)
                # Create Markdown for this one file
                file_md = f"## `{rel_path}`\n\n```\n{content.strip()}\n```"
                # Convert just this block to HTML
                file_html = markdown2.markdown(file_md, extras=["fenced-code-blocks"])
                outfile.write(file_html + "\n\n")
                count += 1
        outfile.write("</body></html>")
    return count

def _parse_context_md(content: str) -> Dict[str, str]:
    """Parses a context.md file and returns a dict of {filepath: content}."""
    # Regex: Find ## `filepath` followed by ```...content...```
    pattern = re.compile(r"## `(.+?)`\n\n```.*?\n(.*?)\n```", re.DOTALL)
    files = {}
    for match in pattern.finditer(content):
        filepath, file_content = match.groups()
        files[filepath.strip()] = file_content
    return files

def _parse_context_html(content: str) -> Dict[str, str]:
    """Parses a context.html file and returns a dict of {filepath: content}."""
    # This regex assumes the format written by _write_context_html
    # It looks for <h2><code>filepath</code></h2> followed by <pre><code>content</code></pre>
    pattern = re.compile(r'<h2><code>(.+?)</code></h2>\s*<div class="codehilite"><pre><span></span><code>(.*?)\n</code></pre></div>', re.DOTALL)
    files = {}
    for match in pattern.finditer(content):
        filepath, file_content = match.groups()
        # Need to decode HTML entities
        import html
        files[filepath.strip()] = html.unescape(file_content)
    return files

def _get_current_file_content_map(src_path: Path, ignore_patterns: List[str]) -> Dict[str, str]:
    """Scans dir and returns a dict of {rel_path: content}."""
    file_paths = _scan_directory(src_path, ignore_patterns)
    content_map = {}
    for file_path in file_paths:
        content = _read_file_content(file_path)
        if content is not None:
            rel_path = str(file_path.relative_to(src_path))
            content_map[rel_path] = content
    return content_map


# --- 4. MCP Tools (Refactored from your .py files) ---

# --- Tools from context_builder.py and update_context.py ---
@mcp.tool
def build_context_md(
    source_directory: str,
    output_file: str = "context.md",
    ignore_file: str = ".gitignore"
) -> FileOpResult:
    """
    (From context_builder.py)
    Scans a directory and builds a *new* context.md file from scratch.
    This will overwrite any existing file.
    """
    try:
        src_path = Path(source_directory).resolve()
        out_path = Path(output_file).resolve()
        if not src_path.is_dir():
            return FileOpResult(success=False, message=f"Error: Source directory not found at {src_path}")

        ignore_patterns = _get_ignore_patterns(src_path, ignore_file, [out_path.name])
        file_paths = _scan_directory(src_path, ignore_patterns)
        count = _write_context_md(file_paths, src_path, out_path)
        
        return FileOpResult(
            success=True,
            message=f"Successfully built context from {count} files.",
            output_file_path=str(out_path),
            files_processed=count
        )
    except Exception as e:
        return FileOpResult(success=False, message=f"A critical error occurred: {str(e)}")

@mcp.tool
def update_context_md(
    source_directory: str,
    output_file: str = "context.md",
    ignore_file: str = ".gitignore"
) -> FileOpResult:
    """
    (From update_context.py)
    Updates an existing context.md file by completely rebuilding it.
    This is an alias for build_context_md.
    """
    return build_context_md(source_directory, output_file, ignore_file)

# --- Tools from build_context_html.py and update_context_html.py ---
@mcp.tool
def build_context_html(
    source_directory: str,
    output_file: str = "context.html",
    ignore_file: str = ".gitignore"
) -> FileOpResult:
    """
    (From build_context_html.py)
    Scans a directory and builds a *new* context.html file from scratch.
    This will overwrite any existing file.
    """
    try:
        src_path = Path(source_directory).resolve()
        out_path = Path(output_file).resolve()
        if not src_path.is_dir():
            return FileOpResult(success=False, message=f"Error: Source directory not found at {src_path}")

        ignore_patterns = _get_ignore_patterns(src_path, ignore_file, [out_path.name])
        file_paths = _scan_directory(src_path, ignore_patterns)
        count = _write_context_html(file_paths, src_path, out_path)
        
        return FileOpResult(
            success=True,
            message=f"Successfully built HTML context from {count} files.",
            output_file_path=str(out_path),
            files_processed=count
        )
    except Exception as e:
        return FileOpResult(success=False, message=f"A critical error occurred: {str(e)}")

@mcp.tool
def update_context_html(
    source_directory: str,
    output_file: str = "context.html",
    ignore_file: str = ".gitignore"
) -> FileOpResult:
    """
    (From update_context_html.py)
    Updates an existing context.html file by completely rebuilding it.
    This is an alias for build_context_html.
    """
    return build_context_html(source_directory, output_file, ignore_file)

# --- Tools from smart_update.py and updater_html.py ---
@mcp.tool
def smart_update_md(
    source_directory: str,
    context_file: str = "context.md",
    ignore_file: str = ".gitignore"
) -> FileOpResult:
    """
    (From smart_update.py)
    "Smart" update. Scans directory and compares against the *existing*
    context.md file. Only rebuilds the file if changes are detected.
    """
    try:
        src_path = Path(source_directory).resolve()
        ctx_path = Path(context_file).resolve()
        if not src_path.is_dir():
            return FileOpResult(success=False, message=f"Error: Source directory not found at {src_path}")
        if not ctx_path.exists():
            return FileOpResult(success=False, message="Context file not found. Use 'build_context_md' first.")

        # 1. Get old files from context.md
        old_content = _read_file_content(ctx_path)
        old_files = _parse_context_md(old_content)
        
        # 2. Get current files from disk
        ignore_patterns = _get_ignore_patterns(src_path, ignore_file, [ctx_path.name])
        current_files = _get_current_file_content_map(src_path, ignore_patterns)
        
        # 3. Compare
        if old_files == current_files:
            return FileOpResult(
                success=True, 
                message="No changes detected. Context file is already up-to-date.",
                output_file_path=str(ctx_path),
                files_processed=0
            )
        
        # 4. Rebuild if different
        return build_context_md(source_directory, context_file, ignore_file)

    except Exception as e:
        return FileOpResult(success=False, message=f"A critical error occurred: {str(e)}")

@mcp.tool
def smart_update_html(
    source_directory: str,
    context_html_file: str = "context.html",
    ignore_file: str = ".gitignore"
) -> FileOpResult:
    """
    (From updater_html.py)
    "Smart" update for HTML. Scans directory and compares against the *existing*
    context.html file. Only rebuilds the file if changes are detected.
    """
    try:
        src_path = Path(source_directory).resolve()
        ctx_path = Path(context_html_file).resolve()
        if not src_path.is_dir():
            return FileOpResult(success=False, message=f"Error: Source directory not found at {src_path}")
        if not ctx_path.exists():
            return FileOpResult(success=False, message="Context HTML file not found. Use 'build_context_html' first.")

        old_content = _read_file_content(ctx_path)
        old_files = _parse_context_html(old_content)
        
        ignore_patterns = _get_ignore_patterns(src_path, ignore_file, [ctx_path.name])
        current_files = _get_current_file_content_map(src_path, ignore_patterns)
        
        if old_files == current_files:
            return FileOpResult(
                success=True, 
                message="No changes detected. Context HTML file is up-to-date.",
                output_file_path=str(ctx_path),
                files_processed=0
            )
        
        return build_context_html(source_directory, context_html_file, ignore_file)

    except Exception as e:
        return FileOpResult(success=False, message=f"A critical error occurred: {str(e)}")

# --- Tools from md2html.py and html2md.py ---
@mcp.tool
def convert_md_to_html(input_md_file: str, output_html_file: str) -> FileOpResult:
    """
    (From md2html.py)
    Converts an existing Markdown file to an HTML file.
    """
    try:
        import markdown2
        in_path = Path(input_md_file).resolve()
        out_path = Path(output_html_file).resolve()
        if not in_path.exists():
            return FileOpResult(success=False, message=f"Input file not found: {in_path}")
        
        content = _read_file_content(in_path)
        html_content = markdown2.markdown(content, extras=["fenced-code-blocks", "tables"])
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return FileOpResult(success=True, message="Conversion successful.", output_file_path=str(out_path), files_processed=1)
    except Exception as e:
        return FileOpResult(success=False, message=f"A critical error occurred: {str(e)}")

@mcp.tool
def convert_html_to_md(input_html_file: str, output_md_file: str) -> FileOpResult:
    """
    (From html2md.py)
    Converts an existing HTML file to a Markdown file.
    """
    try:
        import html2text
        in_path = Path(input_html_file).resolve()
        out_path = Path(output_md_file).resolve()
        if not in_path.exists():
            return FileOpResult(success=False, message=f"Input file not found: {in_path}")
        
        content = _read_file_content(in_path)
        md_content = html2text.html2text(content)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        return FileOpResult(success=True, message="Conversion successful.", output_file_path=str(out_path), files_processed=1)
    except Exception as e:
        return FileOpResult(success=False, message=f"A critical error occurred: {str(e)}")

# --- Tools from reconstructor.py and reconstructor_html.py ---
@mcp.tool
def reconstruct_from_md(input_md_file: str, output_directory: str) -> ReconstructResult:
    """
    (From reconstructor.py)
    Reconstructs the original project directory structure from a context.md file.
    """
    try:
        in_path = Path(input_md_file).resolve()
        out_dir = Path(output_directory).resolve()
        if not in_path.exists():
            return ReconstructResult(success=False, message=f"Input file not found: {in_path}")
        
        out_dir.mkdir(parents=True, exist_ok=True)
        
        content = _read_file_content(in_path)
        files_to_create = _parse_context_md(content)
        
        count = 0
        for rel_path, file_content in files_to_create.items():
            abs_path = out_dir / rel_path
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            count += 1
            
        return ReconstructResult(
            success=True,
            message=f"Successfully reconstructed {count} files.",
            output_directory=str(out_dir),
            files_created=count
        )
    except Exception as e:
        return ReconstructResult(success=False, message=f"A critical error occurred: {str(e)}")

@mcp.tool
def reconstruct_from_html(input_html_file: str, output_directory: str) -> ReconstructResult:
    """
    (From reconstructor_html.py)
    Reconstructs the original project directory structure from a context.html file.
    """
    try:
        in_path = Path(input_html_file).resolve()
        out_dir = Path(output_directory).resolve()
        if not in_path.exists():
            return ReconstructResult(success=False, message=f"Input file not found: {in_path}")
        
        out_dir.mkdir(parents=True, exist_ok=True)
        
        content = _read_file_content(in_path)
        files_to_create = _parse_context_html(content)
        
        if not files_to_create:
            return ReconstructResult(success=False, message="Could not parse any files from the HTML. The format might be incorrect.")

        count = 0
        for rel_path, file_content in files_to_create.items():
            abs_path = out_dir / rel_path
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            count += 1
            
        return ReconstructResult(
            success=True,
            message=f"Successfully reconstructed {count} files.",
            output_directory=str(out_dir),
            files_created=count
        )
    except Exception as e:
        return ReconstructResult(success=False, message=f"A critical error occurred: {str(e)}")

# --- Tool from sanitize_context.py ---
@mcp.tool
def sanitize_context_file(input_file: str, output_file: str) -> FileOpResult:
    """
    (From sanitize_context.py)
    Reads a context file, removes non-UTF-8 characters, and normalizes
    line endings. Writes to a new 'sanitized' file.
    """
    try:
        in_path = Path(input_file).resolve()
        out_path = Path(output_file).resolve()
        if not in_path.exists():
            return FileOpResult(success=False, message=f"Input file not found: {in_path}")

        # Reading with errors='ignore' is the sanitization
        content = _read_file_content(in_path) 
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return FileOpResult(
            success=True, 
            message="File successfully sanitized.", 
            output_file_path=str(out_path),
            files_processed=1
        )
    except Exception as e:
        return FileOpResult(success=False, message=f"A critical error occurred: {str(e)}")
