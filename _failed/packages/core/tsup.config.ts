import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  sourcemap: true,
  clean: true,
  minify: false,
  // Cytoscapeを外部依存として扱う（CDNから読み込み）
  external: ['cytoscape', 'cytoscape-dagre', 'cytoscape-cose-bilkent'],
  outDir: 'dist',
  target: 'es2020',
  splitting: false,
  bundle: true,
  treeshake: true,
  // ブラウザ向けの設定
  platform: 'browser',
  // 軽量化のためCytoscapeは外部依存
  esbuildOptions(options) {
    // ブラウザ互換性のための定義
    options.define = {
      ...options.define,
      'process.env.NODE_ENV': '"production"',
      'global': 'globalThis',
      'process': 'undefined'
    };
    // Node.js組み込みモジュールの処理
    options.conditions = ['browser', 'module', 'import'];
  }
})
