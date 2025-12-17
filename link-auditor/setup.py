from setuptools import setup, find_packages

import os

from pathlib import Path

this_dir = Path(__file__).parent
version = (this_dir / "src" / "link_auditor" / "__init__.py").read_text().split('__version__ = "')[1].split('"')[0]

setup(
    name="link-auditor",
    version=version,
    description="High-performance CLI for auditing broken links in Markdown HTML files websites and sitemaps with concurrent async fetching retries and rich reporting",
    long_description=(this_dir / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Arya Sianati",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "httpx>=0.25.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "markdown>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-httpx>=0.24.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "link-auditor=link_auditor.cli:app",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
)