
import unittest
import os
import shutil
import tempfile
import sys
from io import StringIO
from unittest.mock import patch as mock_patch

# Import the module under test
# We need to add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import context_tracker

class TestContextTracker(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a dummy smart_update.py so the tracker can find it
        # This dummy script needs to behave like smartupdate (create cache, diff)
        # However, testing full integration with rsync is heavy.
        # But context_tracker logic depends on the output/behavior of smart_update.
        # So we will try to rely on the REAL smart_update.py if possible by symlinking it?
        # Or just copying it.
        
        src_smart_update = os.path.join(self.original_cwd, "smart_update.py")
        src_utils = os.path.join(self.original_cwd, "contexter_utils.py")
        
        if os.path.exists(src_smart_update):
            shutil.copy(src_smart_update, "smart_update.py")
        if os.path.exists(src_utils):
            shutil.copy(src_utils, "contexter_utils.py")
            
        # Create a dummy file
        with open("test.txt", "w") as f:
            f.write("initial content\n")
            
        # Capture stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        sys.stdout = sys.__stdout__

    def test_init_and_status(self):
        # Initial status should say "No cache"
        context_tracker.cmd_status()
        self.assertIn("No cache found", self.captured_output.getvalue())
        
        # Initialize via commit (first run creates cache)
        # We need to ensure we have 'smart_update.py' or 'smartupdate' command.
        # The setUp copied it.
        
        # BUT, smartupdate needs 'rsync'. Assuming env has it.
        context_tracker.cmd_commit("Initial init")
        
        # First run of smartupdate returns "No changes" usually (cache creation)
        # or maybe "Initial cache created"
        output = self.captured_output.getvalue()
        # smartupdate prints to stdout, which we capture?
        # subprocess.run in context_tracker captures stdout, but context_tracker prints its own messages.
        
        # Check if history dir created
        self.assertTrue(os.path.exists(".contexter_history"))
        self.assertTrue(os.path.exists(".contexter_cache"))

    def test_commit_flow(self):
        # 1. Initialize
        context_tracker.cmd_commit("Init")
        
        # 2. Modify file
        with open("test.txt", "w") as f:
            f.write("modified content\n")
            
        # 3. Commit change
        context_tracker.cmd_commit("Changed file")
        
        # Verify patch created
        files = os.listdir(".contexter_history")
        patches = [f for f in files if f.endswith(".md")]
        self.assertTrue(len(patches) > 0)
        
        # 4. Check Log
        self.captured_output.truncate(0)
        self.captured_output.seek(0)
        context_tracker.cmd_log()
        self.assertIn("Changed file", self.captured_output.getvalue())

    def test_revert_flow(self):
        # 1. Init
        context_tracker.cmd_commit("Init")
        
        # 2. Modify
        with open("test.txt", "w") as f:
            f.write("modified content\n")
            
        # 3. Commit
        context_tracker.cmd_commit("Changed file")
        
        # 4. Revert
        # We need to find the commit ID (index 0 is latest)
        self.captured_output.truncate(0)
        self.captured_output.seek(0)
        
        # Check if patch command exists in env
        if not shutil.which("patch"):
            print("Skipping revert test (patch command missing)")
            return

        context_tracker.cmd_revert("0")
        
        # Check content
        with open("test.txt", "r") as f:
            content = f.read()
        
        self.assertEqual(content, "initial content\n")

if __name__ == '__main__':
    unittest.main()
