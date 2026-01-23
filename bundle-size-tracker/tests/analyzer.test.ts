import { describe, it, expect, vi, beforeEach } from 'vitest';
import { analyzeBundles } from '../src/analyzer.js';
import * as fs from 'fs-extra';
import * as gzipSizeMod from 'gzip-size';
import { globby } from 'globby';

const mockFs = vi.mocked(fs);
const mockGzipSize = vi.mocked(gzipSizeMod);

const mockConfig = {
  outputDirs: ['dist'],
  filePatterns: ['**/*.js'],
  thresholds: { total: 0, perFile: 0 }
};

describe('analyzeBundles', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockFs.existsSync.mockReturnValue(true);
    mockFs.statSync.mockReturnValue({ size: 1000, isFile: () => true } as any);
    mockFs.readFileSync.mockReturnValue(Buffer.from('test'));
    mockGzipSize.sync.mockReturnValue(500);
    vi.mocked(globby).mockResolvedValue(['app.js']);
  });

  it('computes sizes correctly', async () => {
    const result = await analyzeBundles('/fake', mockConfig);
    expect(result.total.raw).toBe(1000);
    expect(result.total.gzipped).toBe(500);
    expect(Object.keys(result.sizes)).toContain('dist/app.js');
  });

  it('handles no matching files', async () => {
    vi.mocked(globby).mockResolvedValue([]);
    const result = await analyzeBundles('/fake', mockConfig);
    expect(result.total.raw).toBe(0);
    expect(result.total.gzipped).toBe(0);
  });

  it('skips non-existent dirs', async () => {
    mockFs.existsSync.mockReturnValueOnce(false);
    const result = await analyzeBundles('/fake', mockConfig);
    expect(result.total.gzipped).toBe(0);
  });

  it('handles multiple files', async () => {
    vi.mocked(globby).mockResolvedValue(['app.js', 'vendor.js']);
    mockFs.readFileSync.mockReturnValueOnce(Buffer.from('a')).mockReturnValueOnce(Buffer.from('b'));
    mockFs.statSync.mockReturnValueOnce({ size: 1000, isFile: () => true } as any).mockReturnValueOnce({ size: 2000, isFile: () => true } as any);
    mockGzipSize.sync.mockReturnValueOnce(500).mockReturnValueOnce(1000);
    const result = await analyzeBundles('/fake', mockConfig);
    expect(result.total.raw).toBe(3000);
    expect(result.total.gzipped).toBe(1500);
  });

  it('ignores non-files', async () => {
    mockFs.statSync.mockReturnValue({ isFile: () => false } as any);
    const result = await analyzeBundles('/fake', mockConfig);
    expect(result.total.gzipped).toBe(0);
  });
});