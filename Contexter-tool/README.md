```markdown
# Contexter

Contexter is a powerful suite of Python command-line tools for packaging, reconstructing, and updating software projects as single, portable Markdown or HTML files. This workflow is perfect for sharing entire projects with AI models, creating simple text-based backups, or transferring projects between machines.

## New in This Version: AI Workflow ✅

We've added a `sanitizecontext` command to fix common formatting errors when you copy a full project context from an AI chat. Since AI models can sometimes forget to add code fences (````), this tool makes the output instantly usable.

**New Workflow:**
1.  Paste the AI's response into `ai_output.md`.
2.  Run: `sanitize_context ai_output.md clean_project.md`
3.  Reconstruct: `reconstructor clean_project.md ./my-new-project`

## Command Reference

| Command             | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| Command             | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| `context_builder`   | Packages a directory into a single Markdown file.                        |
| `reconstructor`     | Rebuilds a project from a Markdown context file.                         |
| `sanitize_context`  | **(New)** Fixes AI-generated Markdown to be a valid Contexter file.        |
| `update_context`    | Creates a patch file by comparing two `.md` context files.               |
| `updater`           | Applies a patch file to an `.md` context file.                           |
| `smart_update`      | **(Recommended)** Creates a patch using `rsync` for high efficiency.     |
| `build_context_html`| Packages a directory into a single HTML file.                            |
| `reconstructor_html`| Rebuilds a project from an HTML context file.                            |
| `update_context_html`| Creates a patch (`.md` or `.html`) from two `.html` files.               |
| `updater_html`      | Applies a patch (`.md` or `.html`) to an `.html` file.                   |
| `md2html`           | A utility to convert any Markdown file to HTML.                          |
| `html2md`           | A utility to convert any HTML file to Markdown.                          |

For detailed usage, run any command with the `-h` or `--help` flag.