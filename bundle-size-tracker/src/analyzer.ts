import fs from 'fs';
import path from 'path';
import { globby } from 'globby';
import gzipSize from 'gzip-size';
import type { BundleSize, SizeEntry, Config } from './types.js';

export async function analyzeBundles(cwd: string, config: Config): Promise<Omit<SizeEntry, 'commit' | 'timestamp'>> {
  let totalRaw = 0;
  let totalGzipped = 0;
  const sizes: Record<string, BundleSize> = {};

  for (const dir of config.outputDirs) {
    const searchDir = path.join(cwd, dir);
    if (!fs.existsSync(searchDir)) continue;

    const files = await globby(config.filePatterns, { cwd: searchDir, absolute: false });
    for (const relFile of files) {
      const filePath = path.join(searchDir, relFile);
      const stat = fs.statSync(filePath);
      if (stat.isFile()) {
        const buffer = fs.readFileSync(filePath);
        const raw = Buffer.byteLength(buffer);
        const gzipped = gzipSize.sync(buffer);
        const key = `${dir}/${relFile}`;
        sizes[key] = { raw, gzipped };
        totalRaw += raw;
        totalGzipped += gzipped;
      }
    }
  }

  return {
    sizes,
    total: { raw: totalRaw, gzipped: totalGzipped }
  };
}