// Common type definitions

export interface Point {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Bounds extends Rectangle {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

export interface Margin {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export interface Padding extends Margin {}

export interface Style {
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  opacity?: number;
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: string | number;
  borderRadius?: number;
  markerEnd?: string;
  markerStart?: string;
  textAnchor?: string;
}

export type CloudProvider = 'aws' | 'azure' | 'gcp';

export type ConnectionType = 'network' | 'dependency' | 'data' | 'security';

export type LayoutAlgorithm = 'hierarchical' | 'force-directed' | 'constraint-based' | 'manual';

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}
