from pathlib import Path

from setuptools import find_packages, setup

this_dir = Path(__file__).parent

README = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="git-churn-analyzer",
    version="0.1.0",
    description="CLI tool to analyze git commit history for code churn hotspots",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Arya Sianati",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer",
        "rich",
        "tqdm",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-mock",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "git-churn-analyzer=git_churn_analyzer.cli:app",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Version Control",
    ],
    keywords="git churn analysis refactoring devops",
)