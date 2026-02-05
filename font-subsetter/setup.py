from setuptools import setup, find_namespace_packages

import os
from pathlib import Path

this_dir = Path(__file__).parent

setup(
    name="font-subsetter",
    version="0.1.0",
    author="Arya Sianati",
    description="Scan web projects to subset fonts by used glyphs",
    long_description=(this_dir / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "typer",
        "rich",
        "fonttools>=4.40.0",
        "beautifulsoup4",
        "cssutils",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "mypy",
            "pre-commit",
        ],
    },
    entry_points={
        "console_scripts": [
            "font-subsetter = font_subsetter.cli:app",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)