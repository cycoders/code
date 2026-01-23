import { spawn } from 'child_process/promises';

export async function getCurrentCommit(cwd: string): Promise<string> {
  try {
    const { stdout } = await spawn('git', ['rev-parse', 'HEAD'], {
      cwd,
      encoding: 'utf-8'
    });
    return stdout.trim();
  } catch (error) {
    throw new Error('Not a git repository or git not available');
  }
}