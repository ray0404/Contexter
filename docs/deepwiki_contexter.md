[ray0404/Contexter](https://github.com/ray0404/Contexter "Open repository")

Last indexed: 2 November 2025 ([79ebf7](https://github.com/ray0404/Contexter/commits/79ebf745))

# Contents

- [Overview](/ray0404/Contexter/1-overview)
- [Getting Started](/ray0404/Contexter/2-getting-started)
- [Installation](/ray0404/Contexter/2.1-installation)
- [Quick Start Guide](/ray0404/Contexter/2.2-quick-start-guide)
- [Command Overview](/ray0404/Contexter/2.3-command-overview)
- [Core Concepts](/ray0404/Contexter/3-core-concepts)
- [Context Files](/ray0404/Contexter/3.1-context-files)
- [Packaging and Reconstruction](/ray0404/Contexter/3.2-packaging-and-reconstruction)
- [Update Management](/ray0404/Contexter/3.3-update-management)
- [Exclusion Patterns](/ray0404/Contexter/3.4-exclusion-patterns)
- [Workflows](/ray0404/Contexter/4-workflows)
- [Basic Packaging Workflow](/ray0404/Contexter/4.1-basic-packaging-workflow)
- [AI Integration Workflow](/ray0404/Contexter/4.2-ai-integration-workflow)
- [Version Control with Patches](/ray0404/Contexter/4.3-version-control-with-patches)
- [Format Conversion Workflow](/ray0404/Contexter/4.4-format-conversion-workflow)
- [Command Reference](/ray0404/Contexter/5-command-reference)
- [Building Commands](/ray0404/Contexter/5.1-building-commands)
- [buildcontext](/ray0404/Contexter/5.1.1-buildcontext)
- [buildcontexthtml](/ray0404/Contexter/5.1.2-buildcontexthtml)
- [Reconstruction Commands](/ray0404/Contexter/5.2-reconstruction-commands)
- [reconstructor](/ray0404/Contexter/5.2.1-reconstructor)
- [reconstructorhtml](/ray0404/Contexter/5.2.2-reconstructorhtml)
- [Update Commands](/ray0404/Contexter/5.3-update-commands)
- [updatecontext](/ray0404/Contexter/5.3.1-updatecontext)
- [updater](/ray0404/Contexter/5.3.2-updater)
- [smartupdate](/ray0404/Contexter/5.3.3-smartupdate)
- [updatecontexthtml](/ray0404/Contexter/5.3.4-updatecontexthtml)
- [updaterhtml](/ray0404/Contexter/5.3.5-updaterhtml)
- [Utility Commands](/ray0404/Contexter/5.4-utility-commands)
- [sanitizecontext](/ray0404/Contexter/5.4.1-sanitizecontext)
- [md2html](/ray0404/Contexter/5.4.2-md2html)
- [html2md](/ray0404/Contexter/5.4.3-html2md)
- [Architecture](/ray0404/Contexter/6-architecture)
- [System Architecture](/ray0404/Contexter/6.1-system-architecture)
- [Module Organization](/ray0404/Contexter/6.2-module-organization)
- [Utility Layer (contexter\_utils)](/ray0404/Contexter/6.3-utility-layer-(contexter_utils))
- [Dependencies](/ray0404/Contexter/6.4-dependencies)
- [Technical Details](/ray0404/Contexter/7-technical-details)
- [Markdown Context Format](/ray0404/Contexter/7.1-markdown-context-format)
- [HTML Context Format](/ray0404/Contexter/7.2-html-context-format)
- [Patch File Format](/ray0404/Contexter/7.3-patch-file-format)
- [Binary File Handling](/ray0404/Contexter/7.4-binary-file-handling)

---

# Overview

Relevant source files

- [README.md](https://github.com/ray0404/Contexter/blob/79ebf745/README.md)
- [pyproject.toml](https://github.com/ray0404/Contexter/blob/79ebf745/pyproject.toml)
- [setup.py](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py)

## Purpose and Scope

This document provides a high-level introduction to the Contexter system, explaining its core purpose, architecture, and capabilities. Contexter is a Python-based command-line tool suite for packaging software projects into single text-based context files (Markdown or HTML format), reconstructing projects from these files, and managing incremental updates through a patch-based system.

This overview establishes the foundational concepts and system architecture. For detailed installation instructions, see [Installation](/ray0404/Contexter/2.1-installation). For individual command documentation, see [Command Reference](/ray0404/Contexter/5-command-reference). For technical implementation details, see [Architecture](/ray0404/Contexter/6-architecture).

**Sources:** [README.md1-8](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L1-L8)

## What is Contexter?

Contexter converts directory structures containing multiple files into single, portable text documents called **context files**. These context files preserve the complete project structure, file contents, and directory hierarchy in a human-readable format. The system supports bidirectional operations: directories can be packaged into context files, and context files can be reconstructed back into working directories.

The system supports two context file formats:

- **Markdown (`.md`)**: Primary format with full feature support including AI workflow integration
- **HTML (`.html`)**: Alternative format optimized for web viewing and distribution

**Primary Use Cases:**

- Sharing complete projects with AI models (ChatGPT, Claude, etc.) for code generation or review
- Creating text-based backups that are diff-friendly and version-control compatible
- Transferring projects between machines without compression artifacts
- Managing incremental updates through patch files
- Converting AI-generated code into working project structures

**Sources:** [README.md1-8](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L1-L8) [pyproject.toml7-9](https://github.com/ray0404/Contexter/blob/79ebf745/pyproject.toml#L7-L9)

## System Architecture Overview

### Command Structure

Contexter provides 12 command-line entry points, organized into four functional categories:

**Command to Entry Point Mapping:**

| Command | Entry Point Module | Function |
| --- | --- | --- |
| `buildcontext` | `context_builder.py` | `main()` |
| `reconstructor` | `reconstructor.py` | `main()` |
| `updatecontext` | `update_context.py` | `main()` |
| `updater` | `updater.py` | `main()` |
| `smartupdate` | `smart_update.py` | `main()` |
| `sanitizecontext` | `sanitize_context.py` | `main()` |
| `md2html` | `md2html.py` | `main()` |
| `html2md` | `html2md.py` | `main()` |
| `buildcontexthtml` | `build_context_html.py` | `main()` |
| `reconstructorhtml` | `reconstructor_html.py` | `main()` |
| `updatecontexthtml` | `update_context_html.py` | `main()` |
| `updaterhtml` | `updater_html.py` | `main()` |

**Sources:** [setup.py39-54](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L39-L54) [README.md20-36](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L20-L36)

### Module Organization

Contexter implements a strict layered architecture with 1:1 mapping between CLI commands and implementation modules:

All implementation modules are registered as Python modules in `setup.py` and share common functionality through `contexter_utils.py`.

**Sources:** [setup.py23-37](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L23-L37) [setup.py39-54](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L39-L54)

## Core Operations

### Build Operation

The build operation converts a directory structure into a single context file. The `buildcontext` command (implemented in `context_builder.py`) and `buildcontexthtml` command (implemented in `build_context_html.py`) perform this operation for Markdown and HTML formats respectively.

**Process Flow:**

1. Scan the target directory recursively
2. Apply exclusion patterns (e.g., `.git`, `node_modules`, `__pycache__`)
3. Detect binary files and represent them as placeholders
4. Format text files with syntax highlighting (using `Pygments` for language detection)
5. Aggregate all files into a single output file with directory structure preserved

**Sources:** [README.md24](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L24-L24) [README.md30](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L30-L30) [setup.py41](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L41-L41) [setup.py49](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L49-L49)

### Reconstruction Operation

The reconstruction operation parses a context file and recreates the original directory structure with all files. The `reconstructor` command (implemented in `reconstructor.py`) and `reconstructorhtml` command (implemented in `reconstructor_html.py`) perform this operation.

**Process Flow:**

1. Parse the context file to extract file paths and contents
2. Create the directory structure
3. Write individual files to their respective paths
4. Preserve relative paths from the original structure

**Sources:** [README.md25](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L25-L25) [README.md31](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L31-L31) [setup.py42](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L42-L42) [setup.py50](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L50-L50)

### Update Operation

The update system provides three commands for Markdown contexts and two for HTML contexts:

**Markdown Update Commands:**

- `updatecontext`: Standard diff-based patch generation (implemented in `update_context.py`)
- `updater`: Applies patches to Markdown context files (implemented in `updater.py`)
- `smartupdate`: rsync-based high-efficiency patch generation (implemented in `smart_update.py`)

**HTML Update Commands:**

- `updatecontexthtml`: Patch generation for HTML contexts (implemented in `update_context_html.py`)
- `updaterhtml`: Applies patches to HTML context files (implemented in `updater_html.py`)

The `smartupdate` command is marked as **Recommended** in the documentation for its superior performance with large projects.

**Sources:** [README.md27-29](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L27-L29) [README.md32-33](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L32-L33) [setup.py43-45](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L43-L45) [setup.py51-52](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L51-L52)

## Key Features

### Dual-Format Support

Contexter maintains parallel implementations for Markdown and HTML formats:

| Feature | Markdown | HTML |
| --- | --- | --- |
| Build | ✓ (`buildcontext`) | ✓ (`buildcontexthtml`) |
| Reconstruct | ✓ (`reconstructor`) | ✓ (`reconstructorhtml`) |
| Update/Patch | ✓ (3 commands) | ✓ (2 commands) |
| AI Sanitization | ✓ (`sanitizecontext`) | ✗ |
| Format Conversion | Bidirectional via `md2html` and `html2md` |  |

**Sources:** [README.md20-36](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L20-L36) [setup.py39-54](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L39-L54)

### AI Workflow Integration (New in v2.0.0)

The `sanitizecontext` command (implemented in `sanitize_context.py`) addresses a specific problem: AI models often generate code without proper Markdown code fences (```` ``` ````). This command:

1. Detects missing code fence markers
2. Identifies code blocks based on indentation and structure
3. Infers programming languages for proper syntax highlighting
4. Outputs a properly formatted context file ready for `reconstructor`

**Workflow:**

```px-2
AI Output → sanitizecontext → Clean Context → reconstructor → Working Project
```

This feature positions Contexter as an AI-to-project conversion tool, enabling direct use of AI-generated code without manual formatting fixes.

**Sources:** [README.md9-18](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L9-L18) [README.md26](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L26-L26) [setup.py46](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L46-L46)

### Cross-Format Operations

The system supports format conversion through dedicated utilities:

- `md2html` (implemented in `md2html.py`): Converts Markdown context files to HTML
- `html2md` (implemented in `html2md.py`): Converts HTML context files to Markdown

These converters enable workflows where projects are built in one format and distributed in another (e.g., build in Markdown for development, convert to HTML for web publishing).

**Sources:** [README.md34-35](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L34-L35) [setup.py47-48](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L47-L48)

## Dependencies

Contexter relies on five external Python libraries:

| Library | Purpose |
| --- | --- |
| `markdown` | Parse Markdown context files and generate HTML |
| `Pygments` | Syntax highlighting and language detection for code blocks |
| `beautifulsoup4` | Parse and manipulate HTML context files |
| `markdownify` | Convert HTML content to Markdown format |
| `patch` | Generate and apply unified diff patches for update operations |

All dependencies are specified in `requirements.txt` and declared in both `setup.py` and `pyproject.toml`.

**Sources:** [pyproject.toml23-29](https://github.com/ray0404/Contexter/blob/79ebf745/pyproject.toml#L23-L29) [setup.py10-12](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L10-L12)

## Version and Compatibility

Contexter version 2.1.0 (as specified in `setup.py`) requires Python 3.7 or higher. The package is distributed with:

- Project name: `contexter`
- Author: ray0404
- License: MIT License
- Classifiers: Python 3, OSI Approved License, OS Independent, Build Tools, Utilities

The version number in `pyproject.toml` is 2.0.0, while `setup.py` specifies 2.1.0, indicating recent development activity.

**Sources:** [setup.py16](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L16-L16) [setup.py60](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L60-L60) [pyproject.toml9](https://github.com/ray0404/Contexter/blob/79ebf745/pyproject.toml#L9-L9) [pyproject.toml15](https://github.com/ray0404/Contexter/blob/79ebf745/pyproject.toml#L15-L15)

## Installation Methods

Contexter can be installed using pip from the source directory:

**Standard Installation:**

**Development (Editable) Installation:**

The installation process:

1. Reads dependencies from `requirements.txt`
2. Installs all required libraries
3. Registers 12 console script entry points
4. Makes commands available system-wide

For detailed installation procedures, see [Installation](/ray0404/Contexter/2.1-installation).

**Sources:** [README.md39-60](https://github.com/ray0404/Contexter/blob/79ebf745/README.md#L39-L60) [setup.py10-14](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L10-L14) [setup.py38-54](https://github.com/ray0404/Contexter/blob/79ebf745/setup.py#L38-L54)

Dismiss

Refresh this wiki

Enter email to refresh

### On this page

- [Overview](#overview)
- [Purpose and Scope](#purpose-and-scope)
- [What is Contexter?](#what-is-contexter)
- [System Architecture Overview](#system-architecture-overview)
- [Command Structure](#command-structure)
- [Module Organization](#module-organization)
- [Core Operations](#core-operations)
- [Build Operation](#build-operation)
- [Reconstruction Operation](#reconstruction-operation)
- [Update Operation](#update-operation)
- [Key Features](#key-features)
- [Dual-Format Support](#dual-format-support)
- [AI Workflow Integration (New in v2.0.0)](#ai-workflow-integration-new-in-v200)
- [Cross-Format Operations](#cross-format-operations)
- [Dependencies](#dependencies)
- [Version and Compatibility](#version-and-compatibility)
- [Installation Methods](#installation-methods)
