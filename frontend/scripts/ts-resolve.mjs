/**
 * Minimal module-resolution hook so `node --test` can run the TypeScript sources directly.
 *
 * Why this exists: the source uses bundler-style imports (`./types`, `@/lib/...`) because
 * that is what Next and `moduleResolution: "bundler"` expect. Node's ESM resolver requires
 * explicit extensions and knows nothing about the `@/*` alias in tsconfig. This hook
 * teaches it both, which lets the project run real tests on Node 22's built-in runner
 * rather than taking on a test framework, a transpiler and their dependency trees.
 *
 * Usage (see package.json "test"):
 *   node --experimental-strip-types --import ./scripts/ts-resolve.mjs --test "src/**\/*.test.ts"
 */

import { existsSync } from 'node:fs';
import { dirname, resolve as resolvePath } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { register } from 'node:module';

const SRC_ROOT = resolvePath(dirname(fileURLToPath(import.meta.url)), '..', 'src');

/** Extensions tried, in the order a bundler would try them. */
const CANDIDATES = ['.ts', '.tsx', '/index.ts', '/index.tsx', '.js', '.mjs'];

function firstExisting(basePath) {
  if (existsSync(basePath) && !basePath.endsWith('/')) {
    return basePath;
  }
  for (const extension of CANDIDATES) {
    const candidate = `${basePath}${extension}`;
    if (existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

export async function resolve(specifier, context, nextResolve) {
  // tsconfig paths: "@/*" -> "./src/*"
  if (specifier.startsWith('@/')) {
    const resolved = firstExisting(resolvePath(SRC_ROOT, specifier.slice(2)));
    if (resolved) {
      return { url: pathToFileURL(resolved).href, shortCircuit: true };
    }
  }

  // Extensionless relative imports.
  if (specifier.startsWith('.') && context.parentURL?.startsWith('file:')) {
    const fromDir = dirname(fileURLToPath(context.parentURL));
    const resolved = firstExisting(resolvePath(fromDir, specifier));
    if (resolved) {
      return { url: pathToFileURL(resolved).href, shortCircuit: true };
    }
  }

  return nextResolve(specifier, context);
}

register(import.meta.url, import.meta.url);
