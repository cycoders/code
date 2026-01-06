import { Command } from 'commander';
import { readFileSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import chalk from 'chalk';
import { parseNpmLock } from './parser/npm.js';
import { parseYarnLock } from './parser/yarn.js';
import { computeDiff, LockDiff } from './diff.js';

const program = new Command()
  .name('lockdiff')
  .description('Intelligently diffs package lockfiles to highlight dependency changes')
  .version('0.1.0')
  .argument('[old]', 'Old lockfile (git[:ref:]path or file path)', undefined)
  .argument('[new]', 'New lockfile (git[:ref:]path or file path)', undefined)
  .option('-f, --format <format>', 'table or json', 'table')
  .showHelpAfterError(true)
  .action((oldInput = '', newInput = '', options) => {
    try {
      let oldRef = oldInput;
      let newRef = newInput;
      const detected = detectLockfile();
      if (!newRef) {
        if (!oldRef) {
          if (!detected) {
            console.error(chalk.red('No lockfile detected. Provide path or ensure package-lock.json/yarn.lock exists.'));
            process.exit(1);
          }
          oldRef = `HEAD~1:${detected}`;
          newRef = detected;
        } else {
          newRef = oldRef;
          oldRef = `HEAD~1:${oldRef}`;
        }
      }
      const oldContent = readLockfile(oldRef);
      const newContent = readLockfile(newRef);
      const filename = getFilename(newRef);
      const isNpm = filename.endsWith('package-lock.json');
      const isYarn = filename.endsWith('yarn.lock');
      if (!isNpm && !isYarn) {
        throw new Error('Unsupported lockfile type. Supports package-lock.json or yarn.lock');
      }
      const oldJson = isNpm ? JSON.parse(oldContent) : null;
      const newJson = isNpm ? JSON.parse(newContent) : null;
      const oldDeps = isNpm ? parseNpmLock(oldJson) : parseYarnLock(oldContent);
      const newDeps = isNpm ? parseNpmLock(newJson) : parseYarnLock(newContent);
      if (!oldDeps || !newDeps) {
        throw new Error('Failed to parse lockfile(s). Check format/version.');
      }
      const diff = computeDiff(oldDeps, newDeps);
      if (options.format === 'json') {
        console.log(JSON.stringify(diff, null, 2));
      } else {
        renderTable(diff);
      }
    } catch (error: any) {
      console.error(chalk.red('❌ ' + error.message));
      process.exit(1);
    }
  });

function detectLockfile(): string | null {
  const candidates = ['package-lock.json', 'yarn.lock'];
  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  return null;
}

function getFilename(ref: string): string {
  const colonIndex = ref.lastIndexOf(':');
  return colonIndex > -1 ? ref.slice(colonIndex + 1) : ref;
}

function readLockfile(ref: string): string {
  try {
    const parts = ref.split(':', 2);
    if (parts.length === 2) {
      return execSync(`git show ${JSON.stringify(parts[0] + ':' + parts[1])}`, { encoding: 'utf8' }).trim();
    } else {
      if (!existsSync(ref)) {
        throw new Error(`File not found: ${ref}`);
      }
      return readFileSync(ref, 'utf8');
    }
  } catch (e: any) {
    throw new Error(`Cannot read lockfile ${ref}: ${e.message}`);
  }
}

function renderTable(diff: LockDiff): void {
  if (diff.added.length === 0 && diff.removed.length === 0 && diff.updated.length === 0) {
    console.log(chalk.green('✅ No lockfile changes detected'));
    return;
  }
  const { added, removed, updated } = diff;
  if (added.length > 0) {
    console.log(chalk.bold.green('\n📦 Added packages:'));
    const table = new (await import('cli-table3')).Table({
      head: [chalk.cyan('Package'), chalk.cyan('Versions')],
      colWidths: [40, 40],
    });
    added.forEach(({ name, versions }) => {
      table.push([chalk.green.bold(name), chalk.green(versions.join(', '))]);
    });
    console.log(table.toString());
    console.log('');
  }
  if (removed.length > 0) {
    console.log(chalk.bold.red('\n🗑️  Removed packages:'));
    const table = new (await import('cli-table3')).Table({
      head: [chalk.cyan('Package'), chalk.cyan('Versions')],
      colWidths: [40, 40],
    });
    removed.forEach(({ name, versions }) => {
      table.push([chalk.red.bold(name), chalk.red(versions.join(', '))]);
    });
    console.log(table.toString());
    console.log('');
  }
  if (updated.length > 0) {
    console.log(chalk.bold.yellow('\n🔄 Updated packages:'));
    const table = new (await import('cli-table3')).Table({
      head: [chalk.cyan('Package'), chalk.cyan('Old'), chalk.cyan('New'), chalk.cyan('Bump')],
      colWidths: [30, 20, 20, 18],
    });
    updated.forEach(({ name, oldVersions, newVersions, bump }) => {
      const bumpColor = getBumpColor(bump);
      table.push([chalk.yellow(name), oldVersions.join(', '), newVersions.join(', '), bumpColor]);
    });
    console.log(table.toString());
  }
}

function getBumpColor(bump: string): string {
  const colors: Record<string, chalk.Chalk> = {
    major: chalk.red.bold('🔴 major'),
    minor: chalk.blue.bold('🔵 minor'),
    patch: chalk.green.bold('🟢 patch'),
    prerelease: chalk.magenta('🟣 prerelease'),
    'versions changed': chalk.gray('⚡ changed'),
    unchanged: chalk.gray('unchanged'),
  };
  return colors[bump] || chalk.gray(bump);
}

program.parseAsync();