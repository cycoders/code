# timing-side-channel-scanner

## Why this exists
Timing side-channel attacks remain a subtle but serious class of vulnerabilities in authentication, session handling, and cryptographic code. Manual review is error-prone and existing linters rarely target comparison timing specifically.

## Features
- AST-based detection of string/bytes comparisons in hot paths
- Control-flow and early-return analysis
- Support for constant-time function allow-listing
- Actionable reports with severity and suggested fixes
- Works on single files or entire packages

## Installation
pip install -e .

## Usage
python -m timing_side_channel_scanner path/to/src

## Architecture
Thin wrapper around Python's ast module with targeted visitors and a small data-flow tracker. No external dependencies beyond the standard library.
