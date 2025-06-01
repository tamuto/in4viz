// Layout manager - orchestrates different layout algorithms

import { Resource, Connection } from '../../types/infrastructure';
import { LayoutOptions, LayoutResult, LayoutEngine } from '../../types/layout';
import { HierarchicalLayoutEngine } from './hierarchical';

export class LayoutManager {
  private engines: Map<string, LayoutEngine>;

  constructor() {
    this.engines = new Map();

    // Register default layout engines
    this.engines.set('hierarchical', new HierarchicalLayoutEngine());
  }

  /**
   * Calculate layout using specified algorithm
   */
  calculateLayout(
    resources: Resource[],
    connections: Connection[],
    options: LayoutOptions
  ): LayoutResult {
    const engine = this.engines.get(options.algorithm);

    if (!engine) {
      throw new Error(`Unknown layout algorithm: ${options.algorithm}`);
    }

    // Validate inputs
    this.validateInputs(resources, connections);

    // Apply default options
    const fullOptions = this.applyDefaultOptions(options);

    // Calculate layout
    const result = engine.calculateLayout(resources, connections, fullOptions);

    // Post-process result if needed
    return this.postProcessLayout(result, fullOptions);
  }

  /**
   * Register a custom layout engine
   */
  registerEngine(name: string, engine: LayoutEngine): void {
    this.engines.set(name, engine);
  }

  /**
   * Get list of available layout algorithms
   */
  getAvailableAlgorithms(): string[] {
    return Array.from(this.engines.keys());
  }

  private validateInputs(resources: Resource[], connections: Connection[]): void {
    if (!Array.isArray(resources)) {
      throw new Error('Resources must be an array');
    }

    if (!Array.isArray(connections)) {
      throw new Error('Connections must be an array');
    }

    // Check for missing resource references in connections
    const resourceIds = new Set(resources.map(r => r.id));
    connections.forEach(connection => {
      if (!resourceIds.has(connection.from)) {
        throw new Error(`Connection references unknown resource: ${connection.from}`);
      }
      if (!resourceIds.has(connection.to)) {
        throw new Error(`Connection references unknown resource: ${connection.to}`);
      }
    });
  }

  private applyDefaultOptions(options: LayoutOptions): LayoutOptions {
    return {
      ...options,
      algorithm: options.algorithm ?? 'hierarchical',
      spacing: options.spacing ?? { x: 100, y: 80 },
      margin: options.margin ?? { top: 50, right: 50, bottom: 50, left: 50 },
      autoFit: options.autoFit ?? true,
      preserveAspectRatio: options.preserveAspectRatio ?? true
    };
  }

  private postProcessLayout(result: LayoutResult, options: LayoutOptions): LayoutResult {
    if (options.autoFit && result.resources.length > 0) {
      // Adjust bounds to include margins
      const margin = options.margin;
      result.bounds = {
        x: result.bounds.x - margin.left,
        y: result.bounds.y - margin.top,
        width: result.bounds.width + margin.left + margin.right,
        height: result.bounds.height + margin.top + margin.bottom
      };
    }

    return result;
  }
}
