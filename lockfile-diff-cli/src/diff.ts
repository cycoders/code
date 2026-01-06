import semver from 'semver';

export interface AddedRemoved {
  name: string;
  versions: string[];
}

export interface Updated {
  name: string;
  oldVersions: string[];
  newVersions: string[];
  bump: string;
}

export interface LockDiff {
  added: AddedRemoved[];
  removed: AddedRemoved[];
  updated: Updated[];
}

function arraysEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  const sortedA = [...a].sort();
  const sortedB = [...b].sort();
  for (let i = 0; i < sortedA.length; i++) {
    if (sortedA[i] !== sortedB[i]) return false;
  }
  return true;
}

export function computeDiff(
  oldDeps: Record<string, string[]>,
  newDeps: Record<string, string[]>
): LockDiff {
  const names = new Set([...Object.keys(oldDeps), ...Object.keys(newDeps)]);
  const added: AddedRemoved[] = [];
  const removed: AddedRemoved[] = [];
  const updated: Updated[] = [];
  for (const name of names) {
    const oldV = oldDeps[name] ?? [];
    const newV = newDeps[name] ?? [];
    if (oldV.length === 0) {
      added.push({ name, versions: newV });
    } else if (newV.length === 0) {
      removed.push({ name, versions: oldV });
    } else {
      if (!arraysEqual(oldV, newV)) {
        let bump = 'versions changed';
        if (oldV.length === 1 && newV.length === 1) {
          const diff = semver.diff(oldV[0], newV[0]);
          bump = diff ?? 'unchanged';
        }
        updated.push({ name, oldVersions: oldV, newVersions: newV, bump });
      }
    }
  }
  added.sort((a, b) => a.name.localeCompare(b.name));
  removed.sort((a, b) => a.name.localeCompare(b.name));
  updated.sort((a, b) => a.name.localeCompare(b.name));
  return { added, removed, updated };
}
