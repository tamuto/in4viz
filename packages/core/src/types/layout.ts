// Layout engine type definitions

import { Point, Rectangle, LayoutAlgorithm } from './common';
import { Resource, Connection, PositionedResource, PositionedConnection } from './infrastructure';

export interface LayoutOptions {
  algorithm: LayoutAlgorithm;
  spacing: {
    x: number;
    y: number;
  };
  margin: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  autoFit: boolean;
  preserveAspectRatio: boolean;
  constraints?: LayoutConstraints;
}

export interface LayoutConstraints {
  minSpacing?: Point;
  maxSpacing?: Point;
  fixedPositions?: Record<string, Point>;
  groupConstraints?: GroupConstraint[];
  boundaryConstraints?: BoundaryConstraint[];
}

export interface GroupConstraint {
  resourceIds: string[];
  type: 'horizontal' | 'vertical' | 'grid' | 'circular';
  spacing?: number;
  alignment?: 'start' | 'center' | 'end';
}

export interface BoundaryConstraint {
  resourceId: string;
  boundary: Rectangle;
  type: 'inside' | 'outside';
}

export interface LayoutResult {
  resources: PositionedResource[];
  connections: PositionedConnection[];
  bounds: Rectangle;
  algorithm: LayoutAlgorithm;
  executionTime: number;
  iterations?: number;
  converged?: boolean;
}

export interface LayoutEngine {
  calculateLayout(
    resources: Resource[],
    connections: Connection[],
    options: LayoutOptions
  ): LayoutResult;
}

// Hierarchical layout specific types
export interface HierarchicalLayoutOptions extends LayoutOptions {
  levelSeparation: number;
  nodeSeparation: number;
  direction: 'top-down' | 'bottom-up' | 'left-right' | 'right-left';
  layerSpacing: number;
}

// Force-directed layout specific types
export interface ForceDirectedLayoutOptions extends LayoutOptions {
  iterations: number;
  springLength: number;
  springStrength: number;
  repulsionStrength: number;
  damping: number;
  centerForce: number;
  temperature: number;
  coolingFactor: number;
}

// Layout utilities
export interface LayoutUtils {
  calculateBounds(positions: PositionedResource[]): Rectangle;
  detectOverlaps(resources: PositionedResource[]): Array<[string, string]>;
  optimizeSpacing(resources: PositionedResource[], spacing: Point): PositionedResource[];
  validateLayout(result: LayoutResult): boolean;
}
