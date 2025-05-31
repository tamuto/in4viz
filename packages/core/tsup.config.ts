import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  sourcemap: true,
  clean: true,
  minify: false,
  external: ['@svgdotjs/svg.js'],
  outDir: 'dist',
  target: 'es2020',
  splitting: false,
  bundle: true,
  treeshake: true,
})
