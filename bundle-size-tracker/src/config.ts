import fs from 'fs';
import path from 'path';
import { readJsonSync, existsSync } from 'fs-extra';
import type { Config } from './types.js';

export function loadConfig(cwd: string): Config {
  const configPath = path.join(cwd, '.bundle-sizerc.json');
  if (existsSync(configPath)) {
    return readJsonSync(configPath) as Config;
  }
  return {
    buildCommand: 'build',
    outputDirs: ['dist', 'build', 'out'],
    filePatterns: ['**/*.{js,mjs,cjs}'],
    thresholds: {
      total: 0.05,
      perFile: 0.10
    }
  };
}

export function getPackageManager(cwd: string): 'npm' | 'yarn' | 'pnpm' {
  const yarnLock = path.join(cwd, 'yarn.lock');
  const pnpmLock = path.join(cwd, 'pnpm-lock.yaml');
  if (existsSync(yarnLock)) return 'yarn';
  if (existsSync(pnpmLock)) return 'pnpm';
  return 'npm';
}

export function getBuildCommand(cwd: string, config: Config): string {
  const pkgPath = path.join(cwd, 'package.json');
  if (!existsSync(pkgPath)) {
    throw new Error('No package.json found');
  }
  const pkg = readJsonSync(pkgPath);
  return config.buildCommand || Object.keys(pkg.scripts || {}).find(s => s.includes('build')) || 'build';
}