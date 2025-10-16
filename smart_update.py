```python
#!/usr/bin/env python3
import argparse
import os
import subprocess
import shutil
import difflib
import re

from contexter_utils import DEFAULT_EXCLUDE_PATTERNS, get_language_from_path

def check_rsync():
    """Check if rsync is available in the system's PATH."""
    if not shutil.which("rsync"):
        print("❌ Error: `rsync` command not found.")
        print("Please install rsync and ensure it is in your system's PATH.")
        return False
    return True

def run_rsync(command):
    """Executes an rsync command and returns its output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing rsync: {e}")
        print(f"   Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        return None # Handled by check_rsync, but as a fallback

def parse_rsync_output(output, project_dir):
    """Parses the itemized output of rsync to categorize file changes."""
    changes = {'added': [], 'deleted': [], 'modified': []}
    # Pattern to match rsync's itemized output format, e.g., ">f.st......"
    # We only care about files (f), not directories, links, etc. for content diffing.
    change_pattern = re.compile(r"^(>f|hf)(\.|\+).*? (.*)$")
    delete_pattern = re.compile(r"^\*deleting   (.*)$")

    for line in output.splitlines():
        delete_match = delete_pattern.match(line)
        if delete_match:
            path = delete_match.group(1).strip()
            if not path.endswith('/'): # Ignore directories
                changes['deleted'].append(os.path.join(project_dir, path))
            continue

        change_match = change_pattern.match(line)
        if change_match:
            change_type, change_flags, path_str = change_match.groups()
            path = os.path.join(project_dir, path_str.strip())
            
            if '+' in change_flags:
                changes['added'].append(path)
            else:
                changes['modified'].append(path)
    return changes

def main():
    if not check_rsync():
        return

    parser = argparse.ArgumentParser(
        description="Efficiently create a patch file using rsync to detect changes."
    )
    parser.add_argument("project_dir", help="The project directory to analyze.")
    parser.add_argument("patch_output_file", help="Path to write the resulting patch file.")
    args = parser.parse_args()

    project_dir = os.path.normpath(args.project_dir)
    cache_dir = os.path.join(project_dir, ".contexter_cache")

    # Sync cache for the first time if it doesn't exist
    if not os.path.exists(cache_dir):
        print(f"🛠️  No cache found. Creating initial cache at '{cache_dir}'...")
        os.makedirs(cache_dir, exist_ok=True)
        rsync_command = ["rsync", "-a", "--delete"]
        rsync_command.extend([f"--exclude={p}" for p in DEFAULT_EXCLUDE_PATTERNS])
        rsync_command.append(f"{project_dir}/")
        rsync_command.append(f"{cache_dir}/")
        run_rsync(rsync_command)
        print("✅ Initial cache created. Run smartupdate again to detect future changes.")
        return

    print("🔍 Using rsync to find changes...")
    # Use rsync in dry-run, itemized mode to find what has changed
    rsync_dry_run_cmd = ["rsync", "-a", "-n", "-i", "--delete"]
    rsync_dry_run_cmd.extend([f"--exclude={p}" for p in DEFAULT_EXCLUDE_PATTERNS])
    rsync_dry_run_cmd.append(f"{project_dir}/")
    rsync_dry_run_cmd.append(f"{cache_dir}/")
    
    rsync_output = run_rsync(rsync_dry_run_cmd)
    if rsync_output is None:
        return

    changes = parse_rsync_output(rsync_output, project_dir)
    all_changes = changes['added'] + changes['deleted'] + changes['modified']

    if not all_changes:
        print("✨ Project is already in sync. No patch file needed.")
        return

    print("📝 Generating patch file...")
    with open(args.patch_output_file, 'w', encoding='utf-8') as outfile:
        # Handle added and modified files
        for file_path in sorted(changes['added'] + changes['modified']):
            rel_path = os.path.relpath(file_path, project_dir)
            old_file_path = os.path.join(cache_dir, rel_path)
            
            old_content = ""
            if os.path.exists(old_file_path):
                try:
                    with open(old_file_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                except (IOError, UnicodeDecodeError):
                    print(f"⚠️ Could not read old version of {rel_path}. Treating as new file.")

            new_content = ""
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        new_content = f.read()
                except (IOError, UnicodeDecodeError) as e:
                    print(f"❌ Error reading new version of {rel_path}: {e}. Skipping.")
                    continue

            diff = difflib.unified_diff(
                old_content.splitlines(), new_content.splitlines(),
                fromfile=rel_path, tofile=rel_path, lineterm=''
            )
            diff_str = "\n".join(diff)
            if diff_str:
                print(f"  - Found changes in {rel_path}")
                outfile.write(f"--- DIFF FOR: {rel_path} ---\n\n```diff\n{diff_str}\n```\n\n")

        # Handle deleted files
        for file_path in sorted(changes['deleted']):
            rel_path = os.path.relpath(file_path, project_dir)
            old_file_path = os.path.join(cache_dir, rel_path)
            old_content = ""
            if os.path.exists(old_file_path):
                try:
                    with open(old_file_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                except (IOError, UnicodeDecodeError):
                    continue # Can't create a diff for a file we can't read

            print(f"  - Detected deletion of {rel_path}")
            diff = difflib.unified_diff(
                old_content.splitlines(), [],
                fromfile=rel_path, tofile=rel_path, lineterm=''
            )
            outfile.write(f"--- DIFF FOR: {rel_path} ---\n\n```diff\n" + "\n".join(diff) + "\n```\n\n")

    print(f"\n✅ Patch file created at '{args.patch_output_file}'.")

    # Finally, update the cache for the next run
    print("🔄 Updating cache to current state...")
    rsync_update_cmd = ["rsync", "-a", "--delete"]
    rsync_update_cmd.extend([f"--exclude={p}" for p in DEFAULT_EXCLUDE_PATTERNS])
    rsync_update_cmd.append(f"{project_dir}/")
    rsync_update_cmd.append(f"{cache_dir}/")
    run_rsync(rsync_update_cmd)
    print("🎉 Cache updated.")

if __name__ == "__main__":
    main()