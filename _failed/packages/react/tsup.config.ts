import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.tsx'],
  format: ['cjs', 'esm'],
  dts: true,
  sourcemap: true,
  clean: true,
  minify: false,
  external: ['react', 'react-dom', '@infodb/in4viz'],
  outDir: 'dist',
  target: 'es2020',
  splitting: false,
  bundle: true,
  treeshake: true,
  jsx: 'react-jsx',
})
