// Infrastructure data structure definitions

import { Point, Size, Rectangle, CloudProvider, ConnectionType, ValidationResult } from './common';

export interface Infrastructure {
  id: string;
  name?: string;
  provider: CloudProvider;
  resources: Resource[];
  connections: Connection[];
  metadata?: Record<string, any>;
  version?: string;
  created?: Date;
  modified?: Date;
}

export interface Resource {
  id: string;
  type: string;
  name: string;
  provider: CloudProvider;
  properties: Record<string, any>;
  parent?: string;
  children?: string[];
  position?: Point;
  size?: Size;
  style?: ResourceStyle;
  metadata?: Record<string, any>;
  tags?: Record<string, string>;
}

export interface Connection {
  id?: string;
  from: string;
  to: string;
  type: ConnectionType;
  bidirectional?: boolean;
  properties?: Record<string, any>;
  style?: ConnectionStyle;
  metadata?: Record<string, any>;
  label?: string;
}

export interface ResourceStyle {
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  opacity?: number;
  borderRadius?: number;
  shadow?: boolean;
  icon?: IconStyle;
  label?: LabelStyle;
}

export interface ConnectionStyle {
  stroke?: string;
  strokeWidth?: number;
  strokeDasharray?: string;
  opacity?: number;
  markerEnd?: string;
  markerStart?: string;
  label?: LabelStyle;
}

export interface IconStyle {
  size?: number;
  color?: string;
  url?: string;
  position?: 'top-left' | 'top-right' | 'center' | 'bottom-left' | 'bottom-right';
}

export interface LabelStyle {
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: string | number;
  color?: string;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  offset?: Point;
  background?: string;
  padding?: number;
}

// Positioned variants (after layout calculation)
export interface PositionedResource extends Resource {
  position: Point;
  size: Size;
  bounds: Rectangle;
  computedStyle: ResourceStyle;
}

export interface PositionedConnection extends Connection {
  path: Point[];
  bounds: Rectangle;
  computedStyle: ConnectionStyle;
}

// Infrastructure hierarchy helpers
export interface ResourceHierarchy {
  resource: Resource;
  children: ResourceHierarchy[];
  depth: number;
}

// Validation interfaces
export interface InfrastructureValidator {
  validate(infrastructure: Infrastructure): ValidationResult;
  validateResource(resource: Resource): ValidationResult;
  validateConnection(connection: Connection): ValidationResult;
}
