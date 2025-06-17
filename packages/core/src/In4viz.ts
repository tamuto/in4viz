// 新しいIn4vizメインクラス - Cytoscape.jsベース

import { CytoscapeCore, NodeData, EdgeData, LayoutConfig } from './core/CytoscapeCore';
import { ERDiagramRenderer } from './diagrams/ERDiagram';
import { ERDiagram, ERTable, ERRelation, ERLayoutOptions } from './types/er';

export interface In4vizOptions {
  container?: HTMLElement;
  type?: 'er' | 'infrastructure' | 'generic';
  headless?: boolean;
}

export class In4viz {
  private core: CytoscapeCore;
  private erDiagram?: ERDiagramRenderer;
  private type: string;

  constructor(options: In4vizOptions = {}) {
    this.type = options.type || 'generic';

    // 基本的なCytoscapeコアを初期化
    this.core = new CytoscapeCore({
      container: options.container,
      headless: options.headless || !options.container
    });

    // 図の種類に応じて専用レンダラーを初期化
    if (this.type === 'er') {
      this.erDiagram = new ERDiagramRenderer(options.container);
    }
  }

  // === 低次元API - 基本的なノード・エッジ操作 ===

  addNode(data: NodeData): string {
    return this.core.addNode(data);
  }

  removeNode(id: string): boolean {
    return this.core.removeNode(id);
  }

  updateNode(id: string, data: Partial<NodeData>): boolean {
    return this.core.updateNode(id, data);
  }

  getNode(id: string): NodeData | null {
    return this.core.getNode(id);
  }

  getAllNodes(): NodeData[] {
    return this.core.getAllNodes();
  }

  addEdge(data: EdgeData): string {
    return this.core.addEdge(data);
  }

  removeEdge(id: string): boolean {
    return this.core.removeEdge(id);
  }

  updateEdge(id: string, data: Partial<EdgeData>): boolean {
    return this.core.updateEdge(id, data);
  }

  getEdge(id: string): EdgeData | null {
    return this.core.getEdge(id);
  }

  getAllEdges(): EdgeData[] {
    return this.core.getAllEdges();
  }

  // === レイアウト・表示操作 ===

  setLayout(config: LayoutConfig): void {
    this.core.setLayout(config);
  }

  fit(padding?: number): void {
    this.core.fit(padding);
  }

  center(): void {
    this.core.center();
  }

  zoom(level?: number): number {
    return this.core.zoom(level);
  }

  pan(position?: { x: number; y: number }): { x: number; y: number } {
    return this.core.pan(position);
  }

  // === 選択・フィルタリング ===

  select(selector: string): string[] {
    return this.core.select(selector);
  }

  highlight(nodeIds: string[]): void {
    this.core.highlight(nodeIds);
  }

  filter(predicate: (element: any) => boolean): void {
    this.core.filter(predicate);
  }

  // === ER図専用の高次元API ===

  // ER図データの設定
  setERData(diagram: ERDiagram): void {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized. Use type: "er" in constructor options.');
    }
    this.erDiagram.setERData(diagram);
  }

  // テーブル操作
  addTable(table: ERTable): string {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    return this.erDiagram.addTable(table);
  }

  removeTable(tableId: string): boolean {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    return this.erDiagram.removeTable(tableId);
  }

  updateTable(tableId: string, updates: Partial<ERTable>): boolean {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    return this.erDiagram.updateTable(tableId, updates);
  }

  // リレーション操作
  addRelation(relation: ERRelation): string {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    return this.erDiagram.addRelation(relation);
  }

  removeRelation(relationId: string): boolean {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    return this.erDiagram.removeRelation(relationId);
  }

  updateRelation(relationId: string, updates: Partial<ERRelation>): boolean {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    return this.erDiagram.updateRelation(relationId, updates);
  }

  // ER図レイアウト操作
  applyERLayout(options: ERLayoutOptions = {}): void {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    this.erDiagram.applyLayout(options);
  }

  // ER図検索・フィルタリング
  findTables(predicate: (table: ERTable) => boolean): ERTable[] {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    return this.erDiagram.findTables(predicate);
  }

  highlightTables(tableIds: string[]): void {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    this.erDiagram.highlightTables(tableIds);
  }

  filterBySchema(schema: string): void {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    this.erDiagram.filterBySchema(schema);
  }

  showAllTables(): void {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    this.erDiagram.showAllTables();
  }

  // ER図データ取得
  getERData(): ERDiagram {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    return this.erDiagram.getERData();
  }

  // === イベント処理 ===

  on(event: string, callback: (event: any) => void): void {
    this.core.on(event, callback);
  }

  off(event: string, callback?: (event: any) => void): void {
    this.core.off(event, undefined, callback);
  }

  // ER図専用イベント
  onTableClick(callback: (table: ERTable, event?: any) => void): void {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    this.erDiagram.onTableClick(callback);
  }

  onRelationClick(callback: (relation: ERRelation, event?: any) => void): void {
    if (!this.erDiagram) {
      throw new Error('ER diagram renderer not initialized.');
    }
    this.erDiagram.onRelationClick(callback);
  }

  // === エクスポート ===

  async exportPNG(): Promise<string> {
    if (this.erDiagram) {
      return this.erDiagram.exportPNG();
    }
    return this.core.exportPNG();
  }

  async exportJPG(): Promise<string> {
    if (this.erDiagram) {
      return this.erDiagram.exportJPG();
    }
    return this.core.exportJPG();
  }

  // === ユーティリティ ===

  clear(): void {
    if (this.erDiagram) {
      this.erDiagram.clear();
    } else {
      this.core.clear();
    }
  }

  destroy(): void {
    if (this.erDiagram) {
      this.erDiagram.destroy();
    }
    this.core.destroy();
  }

  // Cytoscapeインスタンスの直接アクセス（上級者向け）
  getCytoscape() {
    return this.core.getCytoscape();
  }
}

// === 便利な静的メソッド ===

export namespace In4viz {
  // ER図専用のファクトリメソッド
  export function createERDiagram(container?: HTMLElement): In4viz {
    return new In4viz({ container, type: 'er' });
  }

  // 汎用図のファクトリメソッド  
  export function createGeneric(container?: HTMLElement): In4viz {
    return new In4viz({ container, type: 'generic' });
  }

  // ヘッドレス（Node.js）モード
  export function createHeadless(type: 'er' | 'generic' = 'generic'): In4viz {
    return new In4viz({ headless: true, type });
  }
}

// デフォルトエクスポート
export default In4viz;