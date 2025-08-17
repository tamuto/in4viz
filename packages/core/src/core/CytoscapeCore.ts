// Cytoscape.js の核となるラッパークラス

import cytoscape, { Core, NodeDefinition, EdgeDefinition } from 'cytoscape';
// 直接プラグインをインポート（ブラウザ互換性のため）
import dagre from 'cytoscape-dagre';
import coseBilkent from 'cytoscape-cose-bilkent';

// プラグインの登録
let pluginsLoaded = false;

const loadPlugins = () => {
  if (pluginsLoaded) return;
  
  try {
    cytoscape.use(dagre);
    console.log('cytoscape-dagre plugin loaded');
  } catch (e) {
    console.warn('cytoscape-dagre plugin could not be loaded:', e);
  }
  
  try {
    cytoscape.use(coseBilkent);
    console.log('cytoscape-cose-bilkent plugin loaded');
  } catch (e) {
    console.warn('cytoscape-cose-bilkent plugin could not be loaded:', e);
  }
  
  pluginsLoaded = true;
};

export interface CytoscapeOptions {
  container?: HTMLElement;
  headless?: boolean;
  style?: any[];
  elements?: (NodeDefinition | EdgeDefinition)[];
  layout?: any;
  minZoom?: number;
  maxZoom?: number;
  zoomingEnabled?: boolean;
  panningEnabled?: boolean;
}

export interface NodeData {
  id: string;
  type?: string;
  label?: string;
  [key: string]: any;
}

export interface EdgeData {
  id: string;
  source: string;
  target: string;
  type?: string;
  label?: string;
  [key: string]: any;
}

export interface LayoutConfig {
  name: string;
  [key: string]: any;
}

export class CytoscapeCore {
  private cy: Core;

  constructor(options: CytoscapeOptions = {}) {
    // プラグインを同期的に読み込み
    loadPlugins();
    
    // デフォルト設定
    const defaultOptions: CytoscapeOptions = {
      headless: !options.container,
      minZoom: 0.1,
      maxZoom: 3,
      zoomingEnabled: true,
      panningEnabled: true,
      style: this.getDefaultStyle(),
      layout: { name: 'grid' },
      ...options
    };

    this.cy = cytoscape(defaultOptions);
    this.setupEventHandlers();
  }

  // ノード操作
  addNode(data: NodeData): string {
    const nodeId = data.id || this.generateId();
    this.cy.add({
      group: 'nodes',
      data: { ...data, id: nodeId }
    });
    return nodeId;
  }

  removeNode(id: string): boolean {
    const node = this.cy.getElementById(id);
    if (node.length > 0) {
      this.cy.remove(node);
      return true;
    }
    return false;
  }

  updateNode(id: string, data: Partial<NodeData>): boolean {
    const node = this.cy.getElementById(id);
    if (node.length > 0) {
      Object.entries(data).forEach(([key, value]) => {
        node.data(key, value);
      });
      return true;
    }
    return false;
  }

  getNode(id: string): NodeData | null {
    const node = this.cy.getElementById(id);
    return node.length > 0 ? node.data() : null;
  }

  getAllNodes(): NodeData[] {
    return this.cy.nodes().map(node => node.data());
  }

  // エッジ操作
  addEdge(data: EdgeData): string {
    const edgeId = data.id || this.generateId();
    this.cy.add({
      group: 'edges',
      data: { ...data, id: edgeId }
    });
    return edgeId;
  }

  removeEdge(id: string): boolean {
    const edge = this.cy.getElementById(id);
    if (edge.length > 0) {
      this.cy.remove(edge);
      return true;
    }
    return false;
  }

  updateEdge(id: string, data: Partial<EdgeData>): boolean {
    const edge = this.cy.getElementById(id);
    if (edge.length > 0) {
      Object.entries(data).forEach(([key, value]) => {
        edge.data(key, value);
      });
      return true;
    }
    return false;
  }

  getEdge(id: string): EdgeData | null {
    const edge = this.cy.getElementById(id);
    return edge.length > 0 ? edge.data() : null;
  }

  getAllEdges(): EdgeData[] {
    return this.cy.edges().map(edge => edge.data());
  }

  // レイアウト操作
  setLayout(config: LayoutConfig): void {
    const layout = this.cy.layout(config);
    layout.run();
  }

  // 表示操作
  fit(padding?: number): void {
    this.cy.fit(undefined, padding);
  }

  center(): void {
    this.cy.center();
  }

  zoom(level?: number): number {
    if (level !== undefined) {
      this.cy.zoom(level);
      return level;
    }
    return this.cy.zoom();
  }

  pan(position?: { x: number; y: number }): { x: number; y: number } {
    if (position) {
      this.cy.pan(position);
      return position;
    }
    return this.cy.pan();
  }

  // 選択・フィルタリング
  select(selector: string): string[] {
    return this.cy.$(selector).map(ele => ele.id());
  }

  highlight(nodeIds: string[]): void {
    this.cy.elements().removeClass('highlighted');
    nodeIds.forEach(id => {
      this.cy.getElementById(id).addClass('highlighted');
    });
  }

  filter(predicate: (element: any) => boolean): void {
    this.cy.elements().forEach(ele => {
      if (predicate(ele)) {
        ele.removeClass('filtered');
      } else {
        ele.addClass('filtered');
      }
    });
  }

  // スタイル操作
  setStyle(style: any[]): void {
    this.cy.style(style);
  }

  // データのクリア
  clear(): void {
    this.cy.elements().remove();
  }

  // Cytoscapeインスタンスの取得（上級者向け）
  getCytoscape(): Core {
    return this.cy;
  }

  // 破棄
  destroy(): void {
    this.cy.destroy();
  }

  // エクスポート
  exportPNG(): Promise<string> {
    return new Promise((resolve, reject) => {
      try {
        const png = this.cy.png({ scale: 2 });
        resolve(png);
      } catch (error) {
        reject(error);
      }
    });
  }

  exportJPG(): Promise<string> {
    return new Promise((resolve, reject) => {
      try {
        const jpg = this.cy.jpg({ scale: 2 });
        resolve(jpg);
      } catch (error) {
        reject(error);
      }
    });
  }

  // イベント処理
  on(event: string, selector: string, callback: (event: any) => void): void;
  on(event: string, callback: (event: any) => void): void;
  on(event: string, selectorOrCallback: string | ((event: any) => void), callback?: (event: any) => void): void {
    if (typeof selectorOrCallback === 'string' && callback) {
      (this.cy as any).on(event, selectorOrCallback, callback);
    } else if (typeof selectorOrCallback === 'function') {
      (this.cy as any).on(event, selectorOrCallback);
    }
  }

  off(event: string, selector?: string, callback?: (event: any) => void): void {
    if (selector && callback) {
      (this.cy as any).off(event, selector, callback);
    } else if (typeof selector === 'function') {
      (this.cy as any).off(event, selector);
    } else {
      (this.cy as any).off(event);
    }
  }

  private generateId(): string {
    return 'ele_' + Math.random().toString(36).substr(2, 9);
  }

  private getDefaultStyle(): any[] {
    return [
      {
        selector: 'node',
        style: {
          'background-color': '#ffffff',
          'border-color': '#cccccc',
          'border-width': 1,
          'label': 'data(label)',
          'text-valign': 'center',
          'text-halign': 'center',
          'font-size': 12,
          'font-family': 'Arial, sans-serif',
          'width': 'mapData(width, 0, 200, 20, 200)',
          'height': 'mapData(height, 0, 100, 20, 100)'
        }
      },
      {
        selector: 'edge',
        style: {
          'line-color': '#cccccc',
          'target-arrow-color': '#cccccc',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'width': 1,
          'label': 'data(label)',
          'font-size': 10,
          'text-rotation': 'autorotate'
        }
      },
      {
        selector: '.highlighted',
        style: {
          'background-color': '#ffeb3b',
          'line-color': '#ffeb3b',
          'target-arrow-color': '#ffeb3b'
        }
      },
      {
        selector: '.filtered',
        style: {
          'opacity': 0.3
        }
      }
    ];
  }

  private setupEventHandlers(): void {
    // 基本的なイベントハンドリング設定
    this.cy.on('tap', 'node', (event) => {
      const node = event.target;
      console.log('Node clicked:', node.data());
    });

    this.cy.on('tap', 'edge', (event) => {
      const edge = event.target;
      console.log('Edge clicked:', edge.data());
    });
  }
}