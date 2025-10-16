# Contexter

Contexter is a powerful suite of Python command-line tools for packaging, 
reconstructing, and updating software projects as single, portable Markdown or 
HTML files. This workflow is perfect for sharing entire projects with AI 
models, creating simple text-based backups, or transferring projects between 
machines.

## New in This Version: AI Workflow ✅

We've added a `sanitizecontext` command to fix common formatting errors when 
you copy a full project context from an AI chat. Since AI models can sometimes 
forget to add code fences (````), this tool makes the output instantly usable.

**New Workflow:**
1.  Paste the AI's response into `ai_output.md`.
2.  Run: `sanitizecontext ai_output.md clean_project.md`
3.  Reconstruct: `reconstructor clean_project.md ./my-new-project`

## Command Reference

| Command             | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| `buildcontext`      | Packages a directory into a single Markdown file.                        |
| `reconstructor`     | Rebuilds a project from a Markdown context file.                         |
| `sanitizecontext`   | **(New)** Fixes AI-generated Markdown to be a valid Contexter file.        |
| `updatecontext`     | Creates a patch file by comparing two `.md` context files.               |
| `updater`           | Applies a patch file to an `.md` context file.                           |
| `smartupdate`       | **(Recommended)** Creates a patch using `rsync` for high efficiency.     |
| `buildcontexthtml`  | Packages a directory into a single HTML file.                            |
| `reconstructorhtml` | Rebuilds a project from an HTML context file.                            |
| `updatecontexthtml` | Creates a patch (`.md` or `.html`) from two `.html` files.               |
| `updaterhtml`       | Applies a patch (`.md` or `.html`) to an `.html` file.                   |
| `md2html`           | A utility to convert any Markdown file to HTML.                          |
| `html2md`           | A utility to convert any HTML file to Markdown.                          |

For detailed usage, run any command with the `-h` or `--help` flag.

## Installation

You can install Contexter using `pip`. It is recommended to install it in a 
virtual environment.

### Standard Installation

```bash
pip install .
```

### Development Installation

If you want to edit the source code and have your changes immediately 
reflected, use the "editable" install mode:

```bash
pip install -e .
```

This will install the necessary dependencies from `requirements.txt` and 
create command-line entries for the Contexter tools.
