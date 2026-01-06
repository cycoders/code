import { expect, test, describe } from 'vitest';
import { parseNpmLock } from '../src/parser/npm.js';
import { parseYarnLock } from '../src/parser/yarn.js';
import { computeDiff, LockDiff, AddedRemoved, Updated } from '../src/diff.js';

describe('NPM Parser', () => {
  test('parses valid lockfile v3', () => {
    const json = {
      lockfileVersion: 3,
      packages: {
        '': {},
        lodash: { name: 'lodash', version: '4.17.20' },
        foo: { name: 'foo', version: '1.0.0' },
      },
    };
    const deps = parseNpmLock(json);
    expect(deps).toEqual({
      lodash: ['4.17.20'],
      foo: ['1.0.0'],
    });
  });

  test('handles multi-version', () => {
    const json = {
      lockfileVersion: 3,
      packages: {
        '': {},
        lodash: { name: 'lodash', version: '4.17.20' },
        'lodash/sub': { name: 'lodash', version: '4.17.21' },
      },
    };
    const deps = parseNpmLock(json);
    expect(deps).toEqual({
      lodash: ['4.17.20', '4.17.21'],
    });
  });

  test('rejects invalid', () => {
    expect(parseNpmLock({ lockfileVersion: 2 })).toBeNull();
    expect(parseNpmLock({})).toBeNull();
    expect(parseNpmLock(null)).toBeNull();
  });
});

describe('Yarn Parser', () => {
  test('parses valid yarn.lock', () => {
    const content = `
lodash@4.17.20:
  version "4.17.20"

foo@1.0.0:
  version "1.0.0"`;
    const deps = parseYarnLock(content);
    expect(deps).toEqual({
      lodash: ['4.17.20'],
      foo: ['1.0.0'],
    });
  });

  test('rejects empty/invalid', () => {
    expect(parseYarnLock('')).toBeNull();
    expect(parseYarnLock('invalid')).toBeNull();
  });
});

describe('Diff Computation', () => {
  test('detects added', () => {
    const oldDeps = { lodash: ['4.17.20'] };
    const newDeps = { lodash: ['4.17.20'], foo: ['1.0.0'] };
    const diff = computeDiff(oldDeps, newDeps);
    expect(diff.added).toEqual([{ name: 'foo', versions: ['1.0.0'] } as AddedRemoved]);
    expect(diff.removed).toEqual([]);
    expect(diff.updated).toEqual([]);
  });

  test('detects removed', () => {
    const oldDeps = { lodash: ['4.17.20'], foo: ['1.0.0'] };
    const newDeps = { lodash: ['4.17.20'] };
    const diff = computeDiff(oldDeps, newDeps);
    expect(diff.removed).toEqual([{ name: 'foo', versions: ['1.0.0'] } as AddedRemoved]);
  });

  test('classifies patch bump', () => {
    const oldDeps = { foo: ['1.0.0'] };
    const newDeps = { foo: ['1.0.1'] };
    const diff = computeDiff(oldDeps, newDeps);
    expect(diff.updated[0]).toMatchObject({ name: 'foo', bump: 'patch' });
  });

  test('classifies minor bump', () => {
    const oldDeps = { foo: ['1.0.0'] };
    const newDeps = { foo: ['1.1.0'] };
    const diff = computeDiff(oldDeps, newDeps);
    expect(diff.updated[0]).toMatchObject({ bump: 'minor' });
  });

  test('classifies major bump', () => {
    const oldDeps = { foo: ['1.0.0'] };
    const newDeps = { foo: ['2.0.0'] };
    const diff = computeDiff(oldDeps, newDeps);
    expect(diff.updated[0]).toMatchObject({ bump: 'major' });
  });

  test('handles multi-version change', () => {
    const oldDeps = { foo: ['1.0.0'] };
    const newDeps = { foo: ['1.0.0', '1.1.0'] };
    const diff = computeDiff(oldDeps, newDeps) as any;
    expect(diff.updated[0].bump).toBe('versions changed');
  });

  test('no change', () => {
    const deps = { foo: ['1.0.0'] };
    const diff = computeDiff(deps, deps);
    expect(diff).toEqual({ added: [], removed: [], updated: [] });
  });
});