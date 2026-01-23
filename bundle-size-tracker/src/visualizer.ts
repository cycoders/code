import chalk from 'chalk';
import Table from 'cli-table3';
import type { SizeEntry } from './types.js';

const SPARK_BLOCKS = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];

function sparkline(values: number[]): string {
  if (values.length === 0) return '';
  const recent = values.slice(-10);
  const min = Math.min(...recent);
  const max = Math.max(...recent);
  const range = max - min || 1;
  return recent.map(v => {
    const norm = Math.floor(((v - min) / range) * (SPARK_BLOCKS.length - 1));
    return SPARK_BLOCKS[norm];
  }).join('');
}

export function printComparison(curr: SizeEntry, base: SizeEntry, regressedFiles: string[]) {
  const cmp = compareTotals(curr.total, base.total, 0.05);
  console.log(chalk.bold('\nBundle Size Comparison:'));
  console.log(`Previous: ${(base.total.gzipped / 1024).toFixed(1)}kB`);
  console.log(`Current:  ${(curr.total.gzipped / 1024).toFixed(1)}kB`);
  const sign = cmp.deltaPct > 0 ? chalk.red('↑') : chalk.green('↓');
  console.log(`${sign} ${Math.abs(cmp.deltaPct * 100).toFixed(1)}% (${(cmp.deltaBytes / 1024).toFixed(0)}kB)`);

  if (cmp.isRegression) {
    console.log(chalk.red('🚨 Regression detected!'));
  } else {
    console.log(chalk.green('✅ All good.'));
  }

  if (regressedFiles.length > 0) {
    console.log(chalk.red('\nRegressed files:'));
    regressedFiles.forEach(f => console.log('  ' + f));
  }
}

export function printTrend(history: SizeEntry[]) {
  if (history.length === 0) {
    console.log(chalk.gray('No history. Run `bundle-size-tracker track`.\n'));
    return;
  }

  const table = new Table({
    head: ['Commit', 'Date', 'GZ kB', 'Δ%'],
    style: { head: [], border: [] }
  });

  const recent = history.slice(0, 10);
  for (let i = 0; i < recent.length; i++) {
    const entry = recent[i];
    const prev = recent[i + 1];
    let deltaStr = '—';
    if (prev) {
      const deltaPct = ((entry.total.gzipped - prev.total.gzipped) / prev.total.gzipped) * 100;
      const color = deltaPct > 5 ? chalk.red : deltaPct < -5 ? chalk.green : chalk.gray;
      deltaStr = color(deltaPct > 0 ? `+${deltaPct.toFixed(1)}` : deltaPct.toFixed(1));
    }
    table.push([
      entry.commit.slice(0, 8),
      new Date(entry.timestamp).toISOString().slice(0, 10),
      (entry.total.gzipped / 1024).toFixed(1),
      deltaStr
    ]);
  }
  console.log(table.toString());

  const trendSpark = sparkline(history.slice(0, 10).map(e => e.total.gzipped));
  console.log(chalk.gray(`\nTrend (last 10): ${trendSpark}`));
}