import { describe, it, expect, vi } from 'vitest';
import { loadConfig, getPackageManager } from '../src/config.js';
import * as fsExtra from 'fs-extra';

const mockExists = vi.mocked(fsExtra.existsSync);
const mockReadJson = vi.mocked(fsExtra.readJsonSync);

describe('config', () => {
  it('loads default config', () => {
    mockExists.mockReturnValue(false);
    const config = loadConfig('/fake');
    expect(config.outputDirs).toEqual(['dist', 'build', 'out']);
  });

  it('loads custom config', () => {
    mockExists.mockReturnValue(true);
    mockReadJson.mockReturnValue({ outputDirs: ['custom'] });
    const config = loadConfig('/fake');
    expect(config.outputDirs).toEqual(['custom']);
  });

  it('detects yarn', () => {
    mockExists.mockImplementation(p => p.includes('yarn.lock'));
    expect(getPackageManager('/fake')).toBe('yarn');
  });

  it('detects pnpm', () => {
    mockExists.mockImplementation(p => p.includes('pnpm-lock.yaml'));
    expect(getPackageManager('/fake')).toBe('pnpm');
  });

  it('defaults to npm', () => {
    mockExists.mockReturnValue(false);
    expect(getPackageManager('/fake')).toBe('npm');
  });
});