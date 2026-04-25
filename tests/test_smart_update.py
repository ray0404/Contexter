import unittest
import os
import sys
from unittest.mock import MagicMock

# Mock contexter_utils before importing smart_update
mock_utils = MagicMock()
sys.modules["contexter_utils"] = mock_utils
mock_utils.DEFAULT_EXCLUDE_PATTERNS = []

from smart_update import parse_rsync_output

class TestSmartUpdate(unittest.TestCase):
    def test_parse_rsync_output(self):
        project_dir = "/tmp/project"
        output = """
>f+++++++ file1.txt
>f.st...... file2.py
*deleting   file3.tmp
hf.st...... file4.js
*deleting   dir1/
>f+++++++ dir2/file5.txt
"""
        expected = {
            'added': [
                os.path.join(project_dir, "file1.txt"),
                os.path.join(project_dir, "dir2/file5.txt")
            ],
            'deleted': [
                os.path.join(project_dir, "file3.tmp")
            ],
            'modified': [
                os.path.join(project_dir, "file2.py"),
                os.path.join(project_dir, "file4.js")
            ]
        }

        result = parse_rsync_output(output, project_dir)

        # Sort results for comparison
        for key in result:
            result[key].sort()
        for key in expected:
            expected[key].sort()

        self.assertEqual(result, expected)

    def test_empty_output(self):
        project_dir = "/tmp/project"
        output = ""
        expected = {'added': [], 'deleted': [], 'modified': []}
        result = parse_rsync_output(output, project_dir)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
