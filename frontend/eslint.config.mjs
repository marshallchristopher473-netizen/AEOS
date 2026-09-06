// Flat ESLint config. Next.js 16 removed the `next lint` command and the
// `eslint` option in next.config, so linting now runs through the standard
// ESLint CLI (`npm run lint` -> `eslint .`). This is the direct translation of
// the previous .eslintrc.json (`{ "extends": "next/core-web-vitals" }`);
// eslint-config-next 16 ships native flat-config arrays, so no FlatCompat
// shim is required.
import nextCoreWebVitals from 'eslint-config-next/core-web-vitals';

const eslintConfig = [
  ...nextCoreWebVitals,
  {
    ignores: ['node_modules/**', '.next/**', 'out/**', 'build/**', 'next-env.d.ts'],
  },
];

export default eslintConfig;
