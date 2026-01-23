import { spawn } from 'child_process';
import chalk from 'chalk';
import type { Config } from './types.js';

export function runBuild(cwd: string, pkgManager: 'npm' | 'yarn' | 'pnpm', buildCmd: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const cmd = pkgManager === 'yarn' ? 'yarn' : pkgManager;
    const args = pkgManager === 'yarn' ? [buildCmd] : ['run', buildCmd];
    console.log(chalk.blue(`Running ${cmd} ${args.join(' ')}...`));
    const proc = spawn(cmd, args, { cwd, stdio: 'inherit' });
    proc.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Build failed with exit code ${code}`));
      }
    });
    proc.on('error', reject);
  });
}