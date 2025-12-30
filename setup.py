# setup.py
from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read the requirements file
with open('requirements.txt', encoding='utf-8') as f:
   requirements = f.read().splitlines()

setup(
   name='contexter',
   version='2.1.0',
   description='A suite of tools to package, reconstruct, and update software projects as single text-based context files.',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='ray0404',
   author_email='ray.valentin.04@gmail.com',
   url='[https://github.com/your-username/contexter](https://github.com/your-username/contexter)',
   py_modules=[
       'contexter_utils',
       'context_builder', 
       'reconstructor',
       'update_context',
       'updater',
       'smart_update',
       'sanitize_context',
       'md2html',
       'html2md',
       'build_context_html',
       'reconstructor_html',
       'update_context_html',
       'updater_html'
   ],
   install_requires=requirements,
   entry_points={
       'console_scripts': [
           'buildcontext=context_builder:main',
           'reconstructor=reconstructor:main',
           'updatecontext=update_context:main',
           'updater=updater:main',
           'smartupdate=smart_update:main',
           'sanitizecontext=sanitize_context:main',
           'md2html=md2html:main',
           'html2md=html2md:main',
           'buildcontexthtml=build_context_html:main',
           'reconstructorhtml=reconstructor_html:main',
           'updatecontexthtml=update_context_html:main',
           'updaterhtml=updater_html:main'
       ],
   },
   classifiers=[
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
   ],
   python_requires='>=3.7',
)
