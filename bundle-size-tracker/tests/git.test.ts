import { describe, it, expect, vi } from 'vitest';
import { spawn } from 'child_process/promises';
import { getCurrentCommit } from '../src/git.js';

vi.mock('child_process/promises');

const mockSpawn = vi.mocked(spawn);

describe('git', () => {
  it('returns commit sha', async () => {
    mockSpawn.mockResolvedValue({ stdout: 'abc123\n' } as any);
    const commit = await getCurrentCommit('/fake');
    expect(commit).toBe('abc123');
  });

  it('throws on git error', async () => {
    mockSpawn.mockRejectedValue(new Error('git fail'));
    await expect(getCurrentCommit('/fake')).rejects.toThrow('Not a git repository');
  });
});