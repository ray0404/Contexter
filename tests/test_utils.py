import unittest
import os
import tempfile
from contexter_utils import is_binary, get_language_from_path, generate_file_tree, DEFAULT_EXCLUDE_PATTERNS, get_matcher

class TestContexterUtils(unittest.TestCase):

    def test_get_matcher(self):
        matcher = get_matcher(["*.txt", "secret*"])
        self.assertTrue(matcher("test.txt"))
        self.assertTrue(matcher("secret_file"))
        self.assertFalse(matcher("test.py"))
        self.assertFalse(matcher("another_file"))

    def test_get_language_from_path(self):
        self.assertEqual(get_language_from_path("script.py"), "python")
        self.assertEqual(get_language_from_path("index.js"), "javascript")
        self.assertEqual(get_language_from_path("style.css"), "css")
        self.assertEqual(get_language_from_path("Dockerfile"), "dockerfile")
        self.assertEqual(get_language_from_path("unknown.xyz"), "xyz")
        self.assertEqual(get_language_from_path("Makefile"), "makefile")

    def test_is_binary_text(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("Hello world")
            tmp_path = tmp.name
        try:
            self.assertFalse(is_binary(tmp_path))
        finally:
            os.remove(tmp_path)

    def test_is_binary_binary(self):
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
            tmp.write(b'\x00\x01\x02')
            tmp_path = tmp.name
        try:
            self.assertTrue(is_binary(tmp_path))
        finally:
            os.remove(tmp_path)

    def test_generate_file_tree(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.makedirs(os.path.join(tmp_dir, "src"))
            with open(os.path.join(tmp_dir, "src", "main.py"), 'w') as f:
                f.write("print('hi')")
            with open(os.path.join(tmp_dir, "README.md"), 'w') as f:
                f.write("# Test")
            
            tree = generate_file_tree(tmp_dir, DEFAULT_EXCLUDE_PATTERNS)
            self.assertIn("src/", tree)
            self.assertIn("main.py", tree)
            self.assertIn("README.md", tree)

    def test_generate_file_tree_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.makedirs(os.path.join(tmp_dir, "src"))
            os.makedirs(os.path.join(tmp_dir, ".git"))
            with open(os.path.join(tmp_dir, "src", "main.py"), 'w') as f:
                f.write("print('hi')")
            with open(os.path.join(tmp_dir, ".git", "config"), 'w') as f:
                f.write("config")

            tree = generate_file_tree(tmp_dir, DEFAULT_EXCLUDE_PATTERNS)
            self.assertIn("src/", tree)
            self.assertIn("main.py", tree)
            self.assertNotIn(".git/", tree)
            self.assertNotIn("config", tree)

if __name__ == '__main__':
    unittest.main()
