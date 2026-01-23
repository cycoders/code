import path from 'path';
import { readJson, writeJson, ensureFile } from 'fs-extra';
import type { SizeEntry } from './types.js';

const DATA_FILE = '.bundle-sizes.json';

export async function loadHistory(cwd: string): Promise<SizeEntry[]> {
  const filePath = path.join(cwd, DATA_FILE);
  await ensureFile(filePath);
  try {
    return (await readJson(filePath)) || [];
  } catch {
    return [];
  }
}

export async function saveHistory(cwd: string, history: SizeEntry[]): Promise<void> {
  const filePath = path.join(cwd, DATA_FILE);
  await writeJson(filePath, history, { spaces: 2 });
}