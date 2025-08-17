// in4viz - Infrastructure Visualization Library
// Core library entry point

// メインクラス
export { In4viz as default, In4viz } from './In4viz';

// 低次元API用の型
export type { NodeData, EdgeData, LayoutConfig } from './core/CytoscapeCore';

// ER図専用の型とクラス
export type { 
  ERTable, 
  ERColumn, 
  ERRelation, 
  ERDiagram, 
  ERLayoutOptions, 
  ERStyleConfig 
} from './types/er';

export { ERDiagramRenderer } from './diagrams/ERDiagram';

// Cytoscapeコア（上級者向け）
export { CytoscapeCore } from './core/CytoscapeCore';

// 型のみエクスポート（残存部分）
export type * from './types/common';

// Version export
export const VERSION = '0.2.0';
