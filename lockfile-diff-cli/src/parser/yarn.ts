export function parseYarnLock(content: string): Record<string, string[]> | null {
  if (!content.trim()) return null;
  const lines = content.split(/\r?\n/);
  const deps: Record<string, string[]> = {};
  let i = 0;
  while (i < lines.length) {
    let line = lines[i].trim();
    const headerMatch = line.match(/^([\w\-\.]+)@([\w\.\-\d,\*]+):$/);
    if (headerMatch) {
      const name = headerMatch[1];
      i++;
      while (i < lines.length) {
        let vline = lines[i].trim();
        const versionMatch = vline.match(/^version\s+"([^"]+)"/);
        if (versionMatch) {
          const version = versionMatch[1];
          if (!deps[name]) {
            deps[name] = [];
          }
          if (!deps[name].includes(version)) {
            deps[name].push(version);
          }
          break;
        }
        // Next header or empty
        if (/^([\w\-\.]+)@([\w\.\-\d,\*]+):$/.test(vline) || vline === '') {
          break;
        }
        i++;
      }
    } else {
      i++;
    }
  }
  // Sort versions
  for (const versions of Object.values(deps)) {
    versions.sort((a, b) => a.localeCompare(b));
  }
  return Object.keys(deps).length > 0 ? deps : null;
}
