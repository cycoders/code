# git-hooks-manager

## Why this exists
Teams waste hours debugging inconsistent local git hooks and broken pre-commit pipelines. git-hooks-manager provides a single source of truth for hook definitions, automatically installs them, validates their syntax, and keeps every clone in sync without requiring global git configuration changes.

## Features
- Declarative YAML/JSON hook definitions with dependency management
- Automatic installation into .git/hooks with executable permissions
- Pre-flight validation of hook scripts and shebangs
- Dry-run mode and diff of pending hook changes
- Support for shared hook libraries via git submodules or URLs
- Progress reporting and graceful error recovery

## Installation
pip install git-hooks-manager

## Usage
```bash
ghm init
ghm install --config hooks.yaml
ghm validate
ghm sync --dry-run
```

## Architecture
Core logic lives in src/git_hooks_manager/. Hook resolution, validation, and installation are cleanly separated. All I/O uses pathlib and rich for output.

## Alternatives considered
pre-commit (framework) and husky (Node) were evaluated but lack cross-repo centralized management and Python-native hook validation.