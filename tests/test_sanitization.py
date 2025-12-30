import unittest
import os
import tempfile
from sanitize_context import sanitize_file

class TestSanitization(unittest.TestCase):
    
    def test_sanitize_missing_fences(self):
        # Emulate malformed AI output: missing opening/closing fences
        malformed_content = """Here is the file you asked for:

--- FILE: script.py ---
print("hello")

And here is another one:
--- FILE: styles.css ---
body { color: red; }
"""
        expected_content_snippet = '````python\nprint("hello")\n````'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as infile:
            infile.write(malformed_content)
            input_path = infile.name
            
        output_path = input_path + ".sanitized"
        
        try:
            sanitize_file(input_path, output_path)
            
            with open(output_path, 'r') as f:
                sanitized_content = f.read()
                
            self.assertIn("--- FILE: script.py ---", sanitized_content)
            self.assertIn("````python", sanitized_content)
            self.assertIn('print("hello")', sanitized_content)
            # Check that it closed the block before the next header
            self.assertIn("````\n\n--- FILE: styles.css ---", sanitized_content)

        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)

if __name__ == '__main__':
    unittest.main()
