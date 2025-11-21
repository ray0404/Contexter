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

To get started with Contexter, follow these steps:

### 1. Clone the Repository

First, clone the Contexter repository from GitHub:

```bash
git clone -b cli https://github.com/ray0404/Contexter.git
cd Contexter
```

### 2. (Optional but Recommended) Set up a Python Virtual Environment

It is highly recommended to install Contexter in a virtual environment to avoid conflicts with your system's Python packages.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Contexter

You can install Contexter using `pip`.

#### Standard Installation

If you just want to use Contexter:

```bash
pip install .
```

#### Development Installation

If you plan to contribute to Contexter or want your changes to the source code immediately reflected:

```bash
pip install -e .
```

This will install the necessary dependencies from `requirements.txt` and create command-line entries for the Contexter tools.

### 4. (Optional) Create Aliases Workaround

Some environments may not correctly set up the command-line entry points. If you encounter issues running `buildcontext`, `reconstructor`, etc., you can use the `create_aliases.py` script as a workaround:

```bash
python3 create_aliases.py
source ~/.bashrc # or ~/.zshrc, depending on your shell
```
This script creates shell aliases for each Contexter command, making them accessible directly from your terminal.
