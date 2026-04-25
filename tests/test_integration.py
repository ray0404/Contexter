import unittest
import os
import shutil
import tempfile
import subprocess
import sys

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.test_dir, "source")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.context_file = os.path.join(self.test_dir, "context.md")
        
        os.makedirs(self.source_dir)
        
        # Create a test file
        with open(os.path.join(self.source_dir, "test.py"), "w", encoding='utf-8') as f:
            f.write("print('Hello Integration')\n")
            
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_build_and_reconstruct(self):
        # Change cwd to the test directory to ensure relative paths are used
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        try:
            # 1. Build Context
            # Set PYTHONPATH to the original directory so modules can be found
            env = os.environ.copy()
            env["PYTHONPATH"] = original_cwd + os.pathsep + env.get("PYTHONPATH", "")

            # Use relative path "source" instead of absolute path
            subprocess.check_call(
                [sys.executable, "-m", "context_builder", "context.md", "source"],
                stdout=subprocess.DEVNULL,
                env=env
            )
            
            self.assertTrue(os.path.exists("context.md"))
            
            # 2. Reconstruct
            subprocess.check_call(
                [sys.executable, "-m", "reconstructor", "context.md", "output"],
                stdout=subprocess.DEVNULL,
                env=env
            )
            
            # 3. Verify
            # Reconstructor should create output/source/test.py
            reconstructed_file = os.path.join("output", "source", "test.py")
            self.assertTrue(os.path.exists(reconstructed_file))
            
            with open(os.path.join("source", "test.py"), 'r', encoding='utf-8') as f1:
                original = f1.read()
                
            with open(reconstructed_file, 'r', encoding='utf-8') as f2:
                reconstructed = f2.read()
                
            self.assertEqual(original.strip(), reconstructed.strip())
        finally:
            os.chdir(original_cwd)

if __name__ == '__main__':
    unittest.main()
