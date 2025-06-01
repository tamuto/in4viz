// Renderer type definitions

import { Point, Size, Rectangle, Style } from './common';
import { PositionedResource, PositionedConnection } from './infrastructure';
import { LayoutResult } from './layout';

export interface RendererOptions {
  container: Element;
  width?: number;
  height?: number;
  viewBox?: Rectangle;
  preserveAspectRatio?: string;
  background?: string;
  theme?: RenderTheme;
  enableInteraction?: boolean;
  enableAnimation?: boolean;
}

export interface RenderTheme {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    background: string;
    foreground: string;
    border: string;
    text: string;
  };
  fonts: {
    primary: string;
    secondary: string;
    monospace: string;
  };
  sizes: {
    small: number;
    medium: number;
    large: number;
  };
  defaults: {
    resource: Style;
    connection: Style;
    label: Style;
  };
}

export interface SVGRenderer {
  render(layoutResult: LayoutResult): SVGElement;
  renderResource(resource: PositionedResource): SVGElement;
  renderConnection(connection: PositionedConnection): SVGElement;
  renderLabel(text: string, position: Point, style?: Style): SVGElement;
  clear(): void;
  updateTheme(theme: RenderTheme): void;
  exportToSVG(): string;
  exportToPNG(): Promise<string>;
}

export interface InteractionHandler {
  onResourceClick?: (resource: PositionedResource, event: MouseEvent) => void;
  onResourceHover?: (resource: PositionedResource, event: MouseEvent) => void;
  onConnectionClick?: (connection: PositionedConnection, event: MouseEvent) => void;
  onConnectionHover?: (connection: PositionedConnection, event: MouseEvent) => void;
  onCanvasClick?: (position: Point, event: MouseEvent) => void;
  onZoom?: (scale: number, center: Point) => void;
  onPan?: (offset: Point) => void;
}

export interface AnimationOptions {
  duration: number;
  easing: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
  delay?: number;
}

// SVG specific interfaces
export interface SVGElements {
  svg: SVGSVGElement;
  defs: SVGDefsElement;
  background: SVGGElement;
  connections: SVGGElement;
  resources: SVGGElement;
  labels: SVGGElement;
  ui: SVGGElement;
}

export interface IIconRegistry {
  register(type: string, iconData: string | SVGElement): void;
  get(type: string): SVGElement | null;
  has(type: string): boolean;
  list(): string[];
}

export interface IGeometryUtils {
  calculateTextSize(text: string, style: Style): Size;
  calculateConnectionPath(from: Point, to: Point, type: string): Point[];
  isPointInRectangle(point: Point, rectangle: Rectangle): boolean;
  getIntersectionPoint(line1: [Point, Point], line2: [Point, Point]): Point | null;
}
