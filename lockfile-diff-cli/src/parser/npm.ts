export function parseNpmLock(json: unknown): Record<string, string[]> | null {
  if (typeof json !== 'object' || json === null || !json) return null;
  const lockfile = json as Record<string, any>;
  if (typeof lockfile.lockfileVersion !== 'number' || lockfile.lockfileVersion !== 3) {
    return null;
  }
  const deps: Record<string, string[]> = {};
  const packages = lockfile.packages || {};
  for (const pkg of Object.values(packages)) {
    const p = pkg as Record<string, any>;
    const name = p.name;
    const version = p.version;
    if (typeof name === 'string' && typeof version === 'string' && name && version) {
      if (!deps[name]) {
        deps[name] = [];
      }
      if (!deps[name].includes(version)) {
        deps[name].push(version);
      }
    }
  }
  // Dedup and sort versions
  for (const versions of Object.values(deps)) {
    versions.sort((a, b) => a.localeCompare(b));
  }
  return Object.keys(deps).length > 0 ? deps : null;
}
