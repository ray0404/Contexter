# setup.py
# This file explicitly lists the python modules to be included in the package,
# which is required for a "flat-layout" project structure like this one.
from setuptools import setup

setup(
    py_modules=[
        'build_context_html',
        'context_builder',
        'contexter_utils',
        'html2md',
        'md2html',
        'reconstructor',
        'reconstructor_html',
        'sanitize_context',
        'smart_update',
        'sync_context',
        'update_context',
        'update_context_html',
        'updater',
        'updater_html'
    ]
)
