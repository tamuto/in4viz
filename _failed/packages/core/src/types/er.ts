// ER図専用の型定義

export interface ERTable {
  id: string;
  name: string;
  schema?: string;
  columns: ERColumn[];
  position?: { x: number; y: number };
  metadata?: {
    comment?: string;
    engine?: string;
    charset?: string;
  };
}

export interface ERColumn {
  name: string;
  type: string;
  nullable?: boolean;
  primaryKey?: boolean;
  foreignKey?: boolean;
  unique?: boolean;
  autoIncrement?: boolean;
  defaultValue?: any;
  comment?: string;
}

export interface ERRelation {
  id: string;
  from: {
    table: string;
    column: string;
  };
  to: {
    table: string;
    column: string;
  };
  type: 'one-to-one' | 'one-to-many' | 'many-to-many';
  name?: string;
  onDelete?: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION';
  onUpdate?: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION';
}

export interface ERDiagram {
  tables: ERTable[];
  relations: ERRelation[];
  metadata?: {
    name?: string;
    version?: string;
    description?: string;
  };
}

// Cytoscape.js用のER図データ形式
export interface ERNodeData {
  id: string;
  type: 'table';
  label: string;
  table: ERTable;
}

export interface EREdgeData {
  id: string;
  source: string;
  target: string;
  type: 'relation';
  relation: ERRelation;
  label?: string;
}

// レイアウト用の設定
export interface ERLayoutOptions {
  algorithm?: 'dagre' | 'cose' | 'grid' | 'circle';
  spacing?: {
    nodeRepulsion?: number;
    idealEdgeLength?: number;
  };
  direction?: 'TB' | 'BT' | 'LR' | 'RL'; // Top-Bottom, Bottom-Top, Left-Right, Right-Left
  fit?: boolean;
  animate?: boolean;
}

// ER図のスタイル設定
export interface ERStyleConfig {
  node?: {
    width?: number;
    height?: number;
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
    fontFamily?: string;
    fontSize?: number;
    textColor?: string;
  };
  edge?: {
    width?: number;
    color?: string;
    style?: 'solid' | 'dashed' | 'dotted';
    arrowColor?: string;
    arrowSize?: number;
  };
  table?: {
    headerBackground?: string;
    headerTextColor?: string;
    rowBackground?: string;
    rowTextColor?: string;
    primaryKeyColor?: string;
    foreignKeyColor?: string;
  };
}