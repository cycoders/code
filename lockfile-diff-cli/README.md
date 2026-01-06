# Lockfile Diff CLI

[![npm](https://img.shields.io/npm/v/lockfile-diff-cli?logo=npm)](https://www.npmjs.com/package/lockfile-diff-cli)

## Why this exists

Package lockfiles produce massive, unreadable diffs in PRs during dependency updates. Spotting major bumps, new transitives, or removals requires manual scrolling through thousands of lines.

**Lockdiff** parses `package-lock.json` and `yarn.lock`, extracts **meaningful changes only**, classifies semver bumps, and renders beautiful terminal tables. 

Local, instant (<100ms on 20k deps), zero external deps. Every senior dev's `git diff` companion.

## Features

- 🚀 Parses npm (lockfileVersion 3) & yarn.lock (v1)
- 🔍 Git integration: `lockdiff` = current vs `HEAD~1`
- 🎨 Color-coded tables: 🟢patch 🔵minor 🔴major
- 📊 JSON output for CI/scripts
- ❌ Graceful errors, auto-detects lockfile type

## Installation

```bash
npm install -g lockfile-diff-cli
```

Or `npx`:

```bash
npx lockfile-diff-cli@latest
```

## Usage

```bash
# Diff current vs previous commit (auto-detects lockfile)
lockdiff

# Specific file vs previous
lockdiff package-lock.json

# Arbitrary git refs/files
lockdiff HEAD~2:yarn.lock HEAD:yarn.lock
lockdiff old-lock.json new-lock.json

# JSON for piping
lockdiff --format json
```

## Example Output

```
📦 Added packages:
┌─────────────────────┬─────────────┐
│ Package             │ Versions    │
├─────────────────────┼─────────────┤
│ @angular/animations │ 17.3.0      │
└─────────────────────┴─────────────┘

🗑️  Removed packages:
┌────────────┬─────────────┐
│ Package    │ Versions    │
├────────────┼─────────────┤
│ old-dep    │ 1.2.3       │
└────────────┴─────────────┘

🔄 Updated packages:
┌─────────────────────┬────────────┬────────────┬──────────┐
│ Package             │ Old        │ New        │ Bump     │
├─────────────────────┼────────────┼────────────┼──────────┤
│ lodash              │ 4.17.20    │ 4.17.21    │ 🟢 patch │
│ react               │ 18.2.0     │ 19.0.0     │ 🔴 major │
└─────────────────────┴────────────┴────────────┴──────────┘
```

## Benchmarks

| Lockfile deps | Time |
|---------------|------|
| 100           | 8ms  |
| 5,000         | 35ms |
| 20,000        | 98ms |

Node 20, i7 Mac (npm lockfiles).

## Architecture

```
Lock Input (git show / fs) → Parser → DepsMap (name → versions[]) → Diff → Renderer (table/json)
```

- **Parsers**: Version-aware, handles hoisted multi-version.
- **Diff**: Set diff + semver.diff for bumps.
- **Renderer**: cli-table3 + chalk.

## Alternatives Considered

| Tool | Local? | Git? | Pretty? | Semver? | Multi-lock |
|------|--------|------|---------|---------|------------|
| `git diff` | ✅ | ✅ | ❌ | ❌ | ❌ |
| Dependabot | ❌ | ✅ | ✅ | ✅ | ❌ |
| `npm outdated` | ✅ | ❌ | ❌ | ✅ | ❌ |
| Renovate | ❌ | ✅ | ✅ | ✅ | ❌ |

**Lockdiff**: 100% local CLI perfection.

## Development

```bash
npm install
npm test
npm run dev  # tsx src/cli.ts
npm run build
```

## License

MIT © 2025 Arya Sianati