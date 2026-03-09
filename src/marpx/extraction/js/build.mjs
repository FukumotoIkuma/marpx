import { build } from 'esbuild';
import { writeFileSync } from 'fs';

const result = await build({
  entryPoints: ['main.js'],
  bundle: true,
  write: false,
  format: 'esm',
});

let code = result.outputFiles[0].text;
// Remove any export statements added by ESM format
code = code.replace(/^export\s*\{[^}]*\};?\s*$/gm, '');

const output = `() => {\n${code}\nreturn extractSlides();\n}`;
writeFileSync(new URL('../extract_slides.bundle.js', import.meta.url), output);
