// ER図専用のクラス

import { CytoscapeCore, LayoutConfig } from '../core/CytoscapeCore';
import { ERTable, ERRelation, ERDiagram, ERNodeData, EREdgeData, ERLayoutOptions } from '../types/er';
// Cytoscape.jsのスタイル型は any で代用

export class ERDiagramRenderer {
  private core: CytoscapeCore;
  private tables: Map<string, ERTable> = new Map();
  private relations: Map<string, ERRelation> = new Map();

  constructor(container?: HTMLElement) {
    this.core = new CytoscapeCore({
      container,
      style: this.getERStyle()
    });
  }

  // ER図データの設定
  setERData(diagram: ERDiagram): void {
    this.clear();
    
    // テーブルをノードとして追加
    diagram.tables.forEach(table => {
      this.addTable(table);
    });

    // リレーションをエッジとして追加
    diagram.relations.forEach(relation => {
      this.addRelation(relation);
    });

    // デフォルトレイアウトを適用
    this.applyLayout({ algorithm: 'dagre', direction: 'TB' });
  }

  // テーブルの追加
  addTable(table: ERTable): string {
    this.tables.set(table.id, table);
    
    const nodeData: ERNodeData = {
      id: table.id,
      type: 'table',
      label: table.name,
      table: table
    };

    // テーブルの表示サイズを計算
    const { width, height } = this.calculateTableSize(table);
    
    return this.core.addNode({
      ...nodeData,
      width,
      height,
      // テーブル情報をHTMLとして格納
      html: this.generateTableHTML(table)
    });
  }

  // テーブルの削除
  removeTable(tableId: string): boolean {
    this.tables.delete(tableId);
    
    // 関連するリレーションも削除
    const relationsToRemove = Array.from(this.relations.values())
      .filter(rel => rel.from.table === tableId || rel.to.table === tableId);
    
    relationsToRemove.forEach(rel => {
      this.removeRelation(rel.id);
    });

    return this.core.removeNode(tableId);
  }

  // テーブルの更新
  updateTable(tableId: string, updates: Partial<ERTable>): boolean {
    const table = this.tables.get(tableId);
    if (!table) return false;

    const updatedTable = { ...table, ...updates };
    this.tables.set(tableId, updatedTable);

    const { width, height } = this.calculateTableSize(updatedTable);

    return this.core.updateNode(tableId, {
      label: updatedTable.name,
      table: updatedTable,
      width,
      height,
      html: this.generateTableHTML(updatedTable)
    });
  }

  // リレーションの追加
  addRelation(relation: ERRelation): string {
    this.relations.set(relation.id, relation);

    const edgeData: EREdgeData = {
      id: relation.id,
      source: relation.from.table,
      target: relation.to.table,
      type: 'relation',
      relation: relation,
      label: relation.name || `${relation.from.column} → ${relation.to.column}`
    };

    return this.core.addEdge(edgeData);
  }

  // リレーションの削除
  removeRelation(relationId: string): boolean {
    this.relations.delete(relationId);
    return this.core.removeEdge(relationId);
  }

  // リレーションの更新
  updateRelation(relationId: string, updates: Partial<ERRelation>): boolean {
    const relation = this.relations.get(relationId);
    if (!relation) return false;

    const updatedRelation = { ...relation, ...updates };
    this.relations.set(relationId, updatedRelation);

    return this.core.updateEdge(relationId, {
      relation: updatedRelation,
      label: updatedRelation.name || `${updatedRelation.from.column} → ${updatedRelation.to.column}`
    });
  }

  // レイアウトの適用
  applyLayout(options: ERLayoutOptions = {}): void {
    const layoutConfig: LayoutConfig = this.buildLayoutConfig(options);
    this.core.setLayout(layoutConfig);
  }

  // 表示操作
  fit(): void {
    this.core.fit(20);
  }

  center(): void {
    this.core.center();
  }

  zoom(level?: number): number {
    return this.core.zoom(level);
  }

  // 検索・フィルタリング
  findTables(predicate: (table: ERTable) => boolean): ERTable[] {
    return Array.from(this.tables.values()).filter(predicate);
  }

  highlightTables(tableIds: string[]): void {
    this.core.highlight(tableIds);
  }

  filterBySchema(schema: string): void {
    this.core.filter(element => {
      const data = element.data();
      if (data.type === 'table') {
        return !data.table.schema || data.table.schema === schema;
      }
      return true; // エッジは常に表示
    });
  }

  showAllTables(): void {
    this.core.filter(() => true);
  }

  // エクスポート
  async exportPNG(): Promise<string> {
    return this.core.exportPNG();
  }

  async exportJPG(): Promise<string> {
    return this.core.exportJPG();
  }

  // データの取得
  getERData(): ERDiagram {
    return {
      tables: Array.from(this.tables.values()),
      relations: Array.from(this.relations.values())
    };
  }

  // クリア
  clear(): void {
    this.tables.clear();
    this.relations.clear();
    this.core.clear();
  }

  // 破棄
  destroy(): void {
    this.clear();
    this.core.destroy();
  }

  // イベント処理
  onTableClick(callback: (table: ERTable, event?: any) => void): void {
    this.core.on('tap', 'node[type="table"]', (event: any) => {
      const tableData = event.target.data();
      const table = this.tables.get(tableData.id);
      if (table) {
        callback(table, event);
      }
    });
  }

  onRelationClick(callback: (relation: ERRelation, event?: any) => void): void {
    this.core.on('tap', 'edge[type="relation"]', (event: any) => {
      const relationData = event.target.data();
      const relation = this.relations.get(relationData.id);
      if (relation) {
        callback(relation, event);
      }
    });
  }

  // プライベートメソッド
  private calculateTableSize(table: ERTable): { width: number; height: number } {
    const baseWidth = 200;
    const baseHeight = 40; // ヘッダー高さ
    const rowHeight = 20;
    
    // テーブル名の長さに基づいて幅を調整
    const nameWidth = Math.max(baseWidth, table.name.length * 8 + 40);
    
    // カラム名の最大長に基づいて幅を調整
    const maxColumnWidth = table.columns.reduce((max, col) => {
      const columnText = `${col.name}: ${col.type}`;
      return Math.max(max, columnText.length * 6 + 60);
    }, nameWidth);

    return {
      width: Math.min(maxColumnWidth, 300), // 最大幅制限
      height: baseHeight + (table.columns.length * rowHeight)
    };
  }

  private generateTableHTML(table: ERTable): string {
    const primaryKeys = table.columns.filter(col => col.primaryKey);
    const foreignKeys = table.columns.filter(col => col.foreignKey);
    const regularColumns = table.columns.filter(col => !col.primaryKey && !col.foreignKey);

    let html = `
      <div class="er-table">
        <div class="er-table-header">${table.name}</div>
        <div class="er-table-body">
    `;

    // Primary Keys
    primaryKeys.forEach(col => {
      html += `<div class="er-column primary-key">🔑 ${col.name}: ${col.type}</div>`;
    });

    // Foreign Keys
    foreignKeys.forEach(col => {
      html += `<div class="er-column foreign-key">🔗 ${col.name}: ${col.type}</div>`;
    });

    // Regular Columns
    regularColumns.forEach(col => {
      html += `<div class="er-column">${col.name}: ${col.type}</div>`;
    });

    html += `
        </div>
      </div>
    `;

    return html;
  }

  private getERStyle(): any[] {
    return [
      {
        selector: 'node[type="table"]',
        style: {
          'shape': 'rectangle',
          'background-color': '#ffffff',
          'border-color': '#2196F3',
          'border-width': 2,
          'label': 'data(label)',
          'text-valign': 'top',
          'text-halign': 'center',
          'font-size': 14,
          'font-weight': 'bold',
          'font-family': 'Arial, sans-serif',
          'color': '#333333',
          'width': 'data(width)',
          'height': 'data(height)',
          'text-wrap': 'wrap',
          'text-max-width': 'data(width)',
          'padding': 8
        }
      },
      {
        selector: 'edge[type="relation"]',
        style: {
          'line-color': '#666666',
          'target-arrow-color': '#666666',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'width': 2,
          'label': 'data(label)',
          'font-size': 10,
          'text-rotation': 'autorotate',
          'text-background-color': '#ffffff',
          'text-background-opacity': 0.8,
          'text-background-padding': 3
        }
      },
      {
        selector: 'edge[relation.type="one-to-one"]',
        style: {
          'line-style': 'solid',
          'source-arrow-shape': 'circle',
          'target-arrow-shape': 'circle'
        }
      },
      {
        selector: 'edge[relation.type="one-to-many"]',
        style: {
          'line-style': 'solid',
          'source-arrow-shape': 'circle',
          'target-arrow-shape': 'triangle'
        }
      },
      {
        selector: 'edge[relation.type="many-to-many"]',
        style: {
          'line-style': 'solid',
          'source-arrow-shape': 'triangle',
          'target-arrow-shape': 'triangle'
        }
      },
      {
        selector: '.highlighted',
        style: {
          'background-color': '#ffeb3b',
          'border-color': '#f57f17',
          'line-color': '#ffeb3b',
          'target-arrow-color': '#ffeb3b'
        }
      },
      {
        selector: '.filtered',
        style: {
          'opacity': 0.2
        }
      }
    ];
  }

  private buildLayoutConfig(options: ERLayoutOptions): LayoutConfig {
    const defaultConfig: LayoutConfig = {
      name: 'dagre',
      rankDir: 'TB',
      animate: false,
      fit: true,
      padding: 20
    };

    switch (options.algorithm) {
      case 'dagre':
        return {
          ...defaultConfig,
          name: 'dagre',
          rankDir: options.direction || 'TB',
          animate: options.animate || false,
          fit: options.fit !== false,
          ranker: 'tight-tree',
          nodeSep: options.spacing?.nodeRepulsion || 50,
          rankSep: options.spacing?.idealEdgeLength || 75
        };
      
      case 'cose':
        return {
          ...defaultConfig,
          name: 'cose-bilkent',
          animate: options.animate || false,
          fit: options.fit !== false,
          nodeRepulsion: options.spacing?.nodeRepulsion || 4500,
          idealEdgeLength: options.spacing?.idealEdgeLength || 100,
          edgeElasticity: 0.45,
          nestingFactor: 0.1
        };
      
      case 'grid':
        return {
          ...defaultConfig,
          name: 'grid',
          animate: options.animate || false,
          fit: options.fit !== false,
          rows: Math.ceil(Math.sqrt(this.tables.size))
        };
      
      case 'circle':
        return {
          ...defaultConfig,
          name: 'circle',
          animate: options.animate || false,
          fit: options.fit !== false
        };
      
      default:
        return defaultConfig;
    }
  }
}