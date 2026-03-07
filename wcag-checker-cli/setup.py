from setuptools import setup, find_packages
import os

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='wcag-checker-cli',
    version='0.1.0',
    author='Arya Sianati',
    description='Fast WCAG 2.2 accessibility auditor CLI for web pages and HTML files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'wcag-checker-cli = wcag_checker_cli.main:app',
        ],
    },
    python_requires='>=3.11',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    url='https://github.com/cycoders/code/tree/main/wcag-checker-cli',
)