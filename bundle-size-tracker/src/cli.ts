import { Command } from 'commander';
import chalk from 'chalk';
import path from 'path';
import { loadConfig, getPackageManager, getBuildCommand } from './config.js';
import { runBuild } from './build.js';
import { analyzeBundles } from './analyzer.js';
import { loadHistory, saveHistory } from './storage.js';
import { getCurrentCommit } from './git.js';
import { compareTotals, findRegressedFiles } from './comparator.js';
import { printComparison, printTrend } from './visualizer.js';
import type { SizeEntry, Config } from './types.js';

const program = new Command()
  .name('bundle-size-tracker')
  .description('Tracks JS bundle sizes across git commits')
  .version('0.1.0');

program.option('-C, --cwd <path>', 'working directory', process.cwd());

program
  .command('track')
  .description('Build, analyze & save to history')
  .action(async (cmd) => {
    try {
      const cwd = path.resolve(cmd.opts().cwd);
      const config = loadConfig(cwd);
      const pkgManager = getPackageManager(cwd);
      const buildCmd = getBuildCommand(cwd, config);

      await runBuild(cwd, pkgManager, buildCmd);
      console.log(chalk.blue('Analyzing bundles...'));

      const analysis = await analyzeBundles(cwd, config);
      const commit = await getCurrentCommit(cwd);
      const entry: SizeEntry = {
        commit,
        timestamp: Date.now(),
        ...analysis
      };

      let history = await loadHistory(cwd);
      const last = history[0];
      if (last?.commit === commit) {
        Object.assign(last, entry);
      } else {
        history.unshift(entry);
      }
      await saveHistory(cwd, history);
      console.log(chalk.green('✅ Saved to history.'));
    } catch (error) {
      console.error(chalk.red(`Error: ${(error as Error).message}`));
      process.exit(1);
    }
  });

program
  .command('check')
  .description('Build & check for regressions (no save)')
  .action(async (cmd) => {
    try {
      const cwd = path.resolve(cmd.opts().cwd);
      const config = loadConfig(cwd);
      const pkgManager = getPackageManager(cwd);
      const buildCmd = getBuildCommand(cwd, config);

      await runBuild(cwd, pkgManager, buildCmd);
      console.log(chalk.blue('Analyzing bundles...'));

      const analysis = await analyzeBundles(cwd, config);
      const commit = await getCurrentCommit(cwd);
      const entry: SizeEntry = {
        commit,
        timestamp: Date.now(),
        ...analysis
      };

      const history = await loadHistory(cwd);
      if (history.length === 0) {
        console.log(chalk.yellow('No baseline. Run `track` first.'));
        return;
      }

      const baseline = history[0];
      const regressedFiles = findRegressedFiles(analysis.sizes, baseline.sizes, config.thresholds.perFile);
      printComparison(entry, baseline, regressedFiles);
    } catch (error) {
      console.error(chalk.red(`Error: ${(error as Error).message}`));
      process.exit(1);
    }
  });

program
  .command('trend')
  .description('Show historical trends')
  .action(async (cmd) => {
    try {
      const cwd = path.resolve(cmd.opts().cwd);
      const history = await loadHistory(cwd);
      printTrend(history);
    } catch (error) {
      console.error(chalk.red(`Error: ${(error as Error).message}`));
      process.exit(1);
    }
  });

program.parseAsync();