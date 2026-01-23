import type { BundleSize, SizeEntry, Config } from './types.js';

export function compareTotals(curr: BundleSize, base: BundleSize, threshold: number): { deltaBytes: number; deltaPct: number; isRegression: boolean } {
  const deltaBytes = curr.gzipped - base.gzipped;
  const deltaPct = base.gzipped > 0 ? deltaBytes / base.gzipped : 0;
  return { deltaBytes, deltaPct, isRegression: deltaPct > threshold };
}

export function findRegressedFiles(currSizes: Record<string, BundleSize>, baseSizes: Record<string, BundleSize>, threshold: number): string[] {
  const regressed: string[] = [];
  for (const [file, curr] of Object.entries(currSizes)) {
    const base = baseSizes[file];
    if (base) {
      const deltaPct = (curr.gzipped - base.gzipped) / base.gzipped;
      if (deltaPct > threshold) {
        regressed.push(`${file} (+${(deltaPct * 100).toFixed(1)}%)`);
      }
    }
  }
  return regressed;
}