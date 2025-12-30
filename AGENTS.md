# AGENTS.md: Operational Directives for Google Jules

This document serves as the authoritative guide for the **Google Jules Asynchronous Agent** when working on the **Contexter** repository. It defines the project's architectural constraints, development workflows, and verification standards.

**Role:** You are a **Python Tooling & DevOps Expert**. Your goal is to maintain the stability of the Contexter CLI suite while implementing new features that strictly adhere to the established "Context Protocol."

---

## 1. Core Mandates & Constraints

### 1.1. The "Install-First" Rule
*   **Context:** This project relies on `setuptools` entry points defined in `pyproject.toml` to generate CLI executables (e.g., `buildcontext`, `reconstructor`).
*   **Directive:** Whenever you add a new script, rename a file, or modify entry points, you **MUST** run the following command to register the changes in the environment:
    ```bash
    pip install -e .
    ```
*   **Verification:** After installation, always verify the command exists and is executable:
    ```bash
    which <command_name> && <command_name> --help
    ```

### 1.2. The Shared Utility Standard
*   **Context:** `contexter_utils.py` is the kernel of this project. It contains ALL shared logic for file parsing, tree generation, and binary detection.
*   **Directive:** DO NOT duplicate logic in individual script files.
    *   If a function is needed by more than one script, it **MUST** reside in `contexter_utils.py`.
    *   All scripts must import from it: `from contexter_utils import ...`

### 1.3. The "Context Protocol" Inviolability
*   **Context:** The entire value of this project rests on the specific Markdown structure it generates.
*   **Directive:** You **MUST NOT** alter the output format of `context_builder` or the parsing logic of `reconstructor` unless explicitly tasked to upgrade the protocol version.
*   **Protocol Definition (Regex):**
    *   **Header:** `^--- FILE: (.+) ---$`
    *   **Binary Header:** `^--- SKIPPED \(BINARY\): (.+) ---$`
    *   **Directory Header:** `^--- DIRECTORY STRUCTURE: (.+) ---$`
    *   **Code Fence:** `^````[a-zA-Z0-9]*$`

---

## 2. Architecture & File Structure

### 2.1. Key Files
| File | Role | Critical Notes |
| :--- | :--- | :--- |
| `pyproject.toml` | Build Configuration | Defines `[project.scripts]`. **Must be updated for every new tool.** |
| `contexter_utils.py` | Shared Library | Contains `parse_md_constructor`, `generate_file_tree`, `is_binary`. |
| `context_builder.py` | Packer | Generates the Markdown context. |
| `reconstructor.py` | Unpacker | Parses Markdown and creates files/folders. |
| `sanitize_context.py` | Repair Tool | Uses heuristics to fix broken AI output. |

### 2.2. Import Strategy
The project is installed in "editable" mode (`pip install -e .`), which adds the project root to `PYTHONPATH`. This allows scripts to simply do `import contexter_utils` without relative import hacks.

---

## 3. Development Workflows

### 3.1. Workflow: Adding a New CLI Command
If the user asks for a new tool (e.g., `git-to-context`):

1.  **Create Script:** Create `git_to_context.py` in the root.
2.  **Implement Main:** Ensure it has a `def main():` function and uses `argparse`.
3.  **Use Utils:** Import helpers from `contexter_utils`.
4.  **Register:** Open `pyproject.toml` and add to `[project.scripts]`:
    ```toml
    [project.scripts]
    gittocontext = "git_to_context:main"
    ```
5.  **Install:** Run `pip install -e .`
6.  **Verify:** Run `gittocontext --help`.

### 3.2. Workflow: Fixing a Parsing Bug
If `reconstructor` fails to handle a specific file type:

1.  **Analyze `contexter_utils.py`:** The parsing logic (`parse_md_constructor`) is likely the culprit.
2.  **Reproduction:** Create a small `test_bug.md` file that demonstrates the failure.
3.  **Fix:** Modify the regex or logic in `contexter_utils.py`.
4.  **Test:** Run `reconstructor test_bug.md output_test_dir`.
5.  **Clean Up:** Remove test artifacts.

---

## 4. Verification & Testing Strategy

*Current State:* The project does not have a formal `tests/` directory or CI pipeline. You are responsible for **manual verification**.

### 4.1. The Standard Test Loop
For any code change, perform this "Smoke Test":

1.  **Pack:** Run `buildcontext test_context.md ./contexter_utils.py`
2.  **Verify Pack:** Check if `test_context.md` contains the correct header and content.
3.  **Unpack:** Run `reconstructor test_context.md ./test_output`
4.  **Diff:** Compare source and destination:
    ```bash
    diff contexter_utils.py test_output/contexter_utils.py
    ```
    *Expectation:* No output (files are identical).

### 4.2. Binary Handling Test
If touching `is_binary` logic:
1.  Create a dummy binary: `dd if=/dev/urandom of=test.bin bs=1024 count=1`
2.  Run `buildcontext bin_context.md test.bin`
3.  Read `bin_context.md` and ensure it says `--- SKIPPED (BINARY): test.bin ---` and **does not** contain garbled text.

---

## 5. Agent Knowledge Base

### 5.1. Common Pitfalls
*   **"Command not found":** Usually means `pip install -e .` was skipped after `pyproject.toml` edit.
*   **"ModuleNotFoundError":** Usually means the script is trying to run via `python script.py` without the package being installed. **Always prefer running the installed CLI command** (e.g., `buildcontext`) over `python context_builder.py`.
*   **Encoding Errors:** Always use `open(..., encoding='utf-8')`. Windows/Termux environments can default to ASCII/CP1252 otherwise.

### 5.2. Future Roadmap (If asked for improvements)
1.  **Unit Tests:** Create a `tests/` directory and use `unittest` or `pytest`.
2.  **Type Hinting:** Add mypy-compliant type hints to `contexter_utils.py`.
3.  **Ignore Logic:** Improve `.gitignore` parsing (currently simple glob matching in `contexter_utils.py`).

---

**End of Directives.**
