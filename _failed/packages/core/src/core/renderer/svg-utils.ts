// SVG rendering utilities

import { Point, Rectangle, Style } from '../../types/common';

export class SVGUtils {
  /**
   * Create mock document for Node.js environment
   */
  private static createMockDocument() {
    return {
      createElementNS: (namespace: string, tagName: string) => {
        const element: any = {
          tagName: tagName.toUpperCase(),
          namespace,
          attributes: new Map(),
          children: [],
          textContent: '',
          innerHTML: '',
          style: {},

          setAttribute: function(name: string, value: string) {
            this.attributes.set(name, value);
          },

          getAttribute: function(name: string) {
            return this.attributes.get(name) || null;
          },

          appendChild: function(child: any) {
            this.children.push(child);
            return child;
          },

          removeChild: function(child: any) {
            const index = this.children.indexOf(child);
            if (index > -1) {
              this.children.splice(index, 1);
            }
            return child;
          },

          toString: function() {
            const entries = Array.from(this.attributes.entries()) as [string, string][];
            const attrs = entries
              .map(([key, value]) => `${key}="${value}"`)
              .join(' ');

            const attrsStr = attrs ? ` ${attrs}` : '';

            if (this.children.length === 0 && !this.textContent) {
              return `<${this.tagName.toLowerCase()}${attrsStr}/>`;
            }

            const content = this.textContent || this.children.map((c: any) => c.toString()).join('');
            return `<${this.tagName.toLowerCase()}${attrsStr}>${content}</${this.tagName.toLowerCase()}>`;
          }
        };

        return element;
      }
    };
  }

  /**
   * Get document object (real or mock)
   */
  private static getDocument() {
    if (typeof document !== 'undefined') {
      return document;
    }
    return this.createMockDocument();
  }

  /**
   * Create SVG element with namespace
   */
  static createSVGElement<K extends keyof SVGElementTagNameMap>(
    tagName: K,
    attributes?: Record<string, string | number>
  ): SVGElementTagNameMap[K] {
    const doc = this.getDocument();
    const element = doc.createElementNS('http://www.w3.org/2000/svg', tagName);

    if (attributes) {
      Object.entries(attributes).forEach(([key, value]) => {
        element.setAttribute(key, String(value));
      });
    }

    return element as SVGElementTagNameMap[K];
  }

  /**
   * Set multiple attributes on an SVG element
   */
  static setAttributes(element: SVGElement, attributes: Record<string, string | number>): void {
    Object.entries(attributes).forEach(([key, value]) => {
      element.setAttribute(key, String(value));
    });
  }

  /**
   * Apply style object to SVG element
   */
  static applyStyle(element: SVGElement, style: Style): void {
    const styleMap: Record<keyof Style, string> = {
      fill: 'fill',
      stroke: 'stroke',
      strokeWidth: 'stroke-width',
      opacity: 'opacity',
      fontSize: 'font-size',
      fontFamily: 'font-family',
      fontWeight: 'font-weight',
      borderRadius: 'border-radius',
      markerEnd: 'marker-end',
      markerStart: 'marker-start',
      textAnchor: 'text-anchor'
    };

    Object.entries(style).forEach(([key, value]) => {
      if (value !== undefined) {
        const svgProperty = styleMap[key as keyof Style];
        if (svgProperty) {
          element.setAttribute(svgProperty, String(value));
        }
      }
    });
  }

  /**
   * Create a rectangle element
   */
  static createRect(bounds: Rectangle, style: Style = {}): SVGRectElement {
    const rect = this.createSVGElement('rect', {
      x: bounds.x,
      y: bounds.y,
      width: bounds.width,
      height: bounds.height
    });

    this.applyStyle(rect, {
      fill: '#ffffff',
      stroke: '#cccccc',
      strokeWidth: 1,
      ...style
    });

    return rect;
  }

  /**
   * Create a circle element
   */
  static createCircle(center: Point, radius: number, style: Style = {}): SVGCircleElement {
    const circle = this.createSVGElement('circle', {
      cx: center.x,
      cy: center.y,
      r: radius
    });

    this.applyStyle(circle, {
      fill: '#ffffff',
      stroke: '#cccccc',
      strokeWidth: 1,
      ...style
    });

    return circle;
  }

  /**
   * Create a line element
   */
  static createLine(from: Point, to: Point, style: Style = {}): SVGLineElement {
    const line = this.createSVGElement('line', {
      x1: from.x,
      y1: from.y,
      x2: to.x,
      y2: to.y
    });

    this.applyStyle(line, {
      stroke: '#cccccc',
      strokeWidth: 1,
      ...style
    });

    return line;
  }

  /**
   * Create a polyline element
   */
  static createPolyline(points: Point[], style: Style = {}): SVGPolylineElement {
    const pointsString = points.map(p => `${p.x},${p.y}`).join(' ');

    const polyline = this.createSVGElement('polyline', {
      points: pointsString
    });

    this.applyStyle(polyline, {
      fill: 'none',
      stroke: '#cccccc',
      strokeWidth: 1,
      ...style
    });

    return polyline;
  }

  /**
   * Create a path element
   */
  static createPath(pathData: string, style: Style = {}): SVGPathElement {
    const path = this.createSVGElement('path', {
      d: pathData
    });

    this.applyStyle(path, {
      fill: 'none',
      stroke: '#cccccc',
      strokeWidth: 1,
      ...style
    });

    return path;
  }

  /**
   * Create a text element
   */
  static createText(
    text: string,
    position: Point,
    style: Style = {}
  ): SVGTextElement {
    const textElement = this.createSVGElement('text', {
      x: position.x,
      y: position.y
    });

    textElement.textContent = text;

    this.applyStyle(textElement, {
      fontSize: 12,
      fontFamily: 'Arial, sans-serif',
      fill: '#333333',
      ...style
    });

    return textElement;
  }

  /**
   * Create a group element
   */
  static createGroup(attributes?: Record<string, string | number>): SVGGElement {
    return this.createSVGElement('g', attributes);
  }

  /**
   * Create marker for arrow heads
   */
  static createArrowMarker(id: string, color: string = '#666666'): SVGMarkerElement {
    const marker = this.createSVGElement('marker', {
      id,
      markerWidth: 10,
      markerHeight: 7,
      refX: 9,
      refY: 3.5,
      orient: 'auto'
    });

    const polygon = this.createSVGElement('polygon', {
      points: '0 0, 10 3.5, 0 7'
    });

    this.applyStyle(polygon, {
      fill: color
    });

    marker.appendChild(polygon);
    return marker;
  }

  /**
   * Generate path data for curved connections
   */
  static generateCurvePath(from: Point, to: Point, curvature: number = 0.3): string {
    const dx = to.x - from.x;
    const distance = Math.sqrt(dx * dx + (to.y - from.y) * (to.y - from.y));
    const controlOffset = distance * curvature;

    const cp1 = { x: from.x + controlOffset, y: from.y };
    const cp2 = { x: to.x - controlOffset, y: to.y };

    return `M ${from.x},${from.y} C ${cp1.x},${cp1.y} ${cp2.x},${cp2.y} ${to.x},${to.y}`;
  }

  /**
   * Generate path data for orthogonal connections
   */
  static generateOrthogonalPath(from: Point, to: Point): string {
    const midX = from.x + (to.x - from.x) / 2;

    return `M ${from.x},${from.y} L ${midX},${from.y} L ${midX},${to.y} L ${to.x},${to.y}`;
  }

  /**
   * Calculate text anchor based on position
   */
  static getTextAnchor(position: string): string {
    switch (position) {
      case 'left':
        return 'start';
      case 'right':
        return 'end';
      case 'center':
      default:
        return 'middle';
    }
  }

  /**
   * Create rounded rectangle path
   */
  static createRoundedRectPath(bounds: Rectangle, radius: number): string {
    const { x, y, width, height } = bounds;
    const r = Math.min(radius, width / 2, height / 2);

    return `
      M ${x + r},${y}
      L ${x + width - r},${y}
      Q ${x + width},${y} ${x + width},${y + r}
      L ${x + width},${y + height - r}
      Q ${x + width},${y + height} ${x + width - r},${y + height}
      L ${x + r},${y + height}
      Q ${x},${y + height} ${x},${y + height - r}
      L ${x},${y + r}
      Q ${x},${y} ${x + r},${y}
      Z
    `;
  }
}
