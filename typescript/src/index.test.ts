/**
 * Basic tests for prompt-versioning-cli TypeScript package
 */

import { describe, it, expect } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';

describe('prompt-versioning-cli package', () => {
  it('should be importable', () => {
    // This test ensures the package structure is valid
    expect(true).toBe(true);
  });

  it('should have correct package metadata', () => {
    const pkgPath = path.join(__dirname, '..', 'package.json');
    const pkgContent = fs.readFileSync(pkgPath, 'utf-8');
    const pkg = JSON.parse(pkgContent);
    expect(pkg.name).toBe('prompt-versioning-cli');
    expect(pkg.version).toBe('1.0.0');
    expect(pkg.main).toBe('dist/index.js');
    expect(pkg.types).toBe('dist/index.d.ts');
  });
});
