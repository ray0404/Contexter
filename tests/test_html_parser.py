
import unittest
import os
import tempfile
from contexter_utils import parse_html_constructor

class TestHtmlParser(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html')
        self.temp_file.close()

    def tearDown(self):
        os.remove(self.temp_file.name)

    def write_html(self, content):
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            f.write(content)

    def test_parse_simple_file(self):
        html_content = """
        <html><body>
        <div class="file-container" data-path="test.py">
            <div class="highlight">print("hello")</div>
        </div>
        </body></html>
        """
        self.write_html(html_content)
        files = parse_html_constructor(self.temp_file.name)
        self.assertEqual(files["test.py"], 'print("hello")')

    def test_parse_skipped_file(self):
        html_content = """
        <html><body>
        <div class="skipped-container" data-path="binary.bin"></div>
        </body></html>
        """
        self.write_html(html_content)
        files = parse_html_constructor(self.temp_file.name)
        self.assertIn("binary.bin", files)
        self.assertIsNone(files["binary.bin"])

    def test_parse_mixed_files(self):
        html_content = """
        <html><body>
        <div class="file-container" data-path="a.py">
            <div class="highlight">code_a</div>
        </div>
        <div class="skipped-container" data-path="b.bin"></div>
        <div class="file-container" data-path="c.py">
            <div class="highlight">code_c</div>
        </div>
        </body></html>
        """
        self.write_html(html_content)
        files = parse_html_constructor(self.temp_file.name)
        self.assertEqual(files["a.py"], "code_a")
        self.assertIsNone(files["b.bin"])
        self.assertEqual(files["c.py"], "code_c")

    def test_parse_nested_structure(self):
        # Ensure it works regardless of nesting level (as find_all searches recursively)
        html_content = """
        <html><body>
        <div class="container">
            <div class="wrapper">
                <div class="file-container" data-path="nested.py">
                    <div class="highlight">nested</div>
                </div>
            </div>
        </div>
        </body></html>
        """
        self.write_html(html_content)
        files = parse_html_constructor(self.temp_file.name)
        self.assertEqual(files["nested.py"], "nested")

if __name__ == '__main__':
    unittest.main()
