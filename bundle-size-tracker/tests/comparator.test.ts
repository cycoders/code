import { describe, it, expect } from 'vitest';
import { compareTotals, findRegressedFiles } from '../src/comparator.js';

describe('comparator', () => {
  it('detects positive regression', () => {
    const cmp = compareTotals({ raw: 0, gzipped: 1100 }, { raw: 0, gzipped: 1000 }, 0.05);
    expect(cmp.isRegression).toBe(true);
    expect(cmp.deltaPct).toBeCloseTo(0.1);
  });

  it('no regression on small growth', () => {
    const cmp = compareTotals({ raw: 0, gzipped: 1040 }, { raw: 0, gzipped: 1000 }, 0.05);
    expect(cmp.isRegression).toBe(false);
  });

  it('negative delta ok', () => {
    const cmp = compareTotals({ raw: 0, gzipped: 900 }, { raw: 0, gzipped: 1000 }, 0.05);
    expect(cmp.isRegression).toBe(false);
  });

  it('finds per-file regressions', () => {
    const curr = { 'dist/app.js': { raw: 0, gzipped: 1100 } };
    const base = { 'dist/app.js': { raw: 0, gzipped: 1000 } };
    const regs = findRegressedFiles(curr, base, 0.05);
    expect(regs).toContain('dist/app.js (+10.0%)');
  });

  it('ignores new files', () => {
    const curr = { 'dist/new.js': { raw: 0, gzipped: 100 } };
    const base = {};
    const regs = findRegressedFiles(curr, base, 0.05);
    expect(regs).toHaveLength(0);
  });
});