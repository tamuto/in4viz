// Geometry calculation utilities

import { Point, Size, Rectangle } from '../../types/common';
import { Style } from '../../types/common';

export class GeometryUtils {
  /**
   * Calculate approximate text size based on font properties
   */
  static calculateTextSize(text: string, style: Style = {}): Size {
    const fontSize = style.fontSize || 14;
    // Note: fontFamily and fontWeight could be used for more precise calculations
    // but for now we use a simple approximation

    // Approximate character width based on font size
    // This is a rough estimation - for precise measurements, we'd need canvas.measureText()
    const avgCharWidth = fontSize * 0.6;
    const lineHeight = fontSize * 1.2;

    const lines = text.split('\n');
    const maxLineLength = Math.max(...lines.map(line => line.length));

    return {
      width: maxLineLength * avgCharWidth,
      height: lines.length * lineHeight
    };
  }

  /**
   * Calculate connection path between two points
   */
  static calculateConnectionPath(from: Point, to: Point, type: string = 'straight'): Point[] {
    switch (type) {
      case 'straight':
        return [from, to];

      case 'orthogonal':
        return this.calculateOrthogonalPath(from, to);

      case 'curved':
        return this.calculateCurvedPath(from, to);

      default:
        return [from, to];
    }
  }

  /**
   * Calculate orthogonal (L-shaped) path
   */
  private static calculateOrthogonalPath(from: Point, to: Point): Point[] {
    const midX = from.x + (to.x - from.x) / 2;

    return [
      from,
      { x: midX, y: from.y },
      { x: midX, y: to.y },
      to
    ];
  }

  /**
   * Calculate curved path using bezier curve control points
   */
  private static calculateCurvedPath(from: Point, to: Point): Point[] {
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Control point offset (adjust curve)
    const controlOffset = Math.min(distance * 0.3, 50);

    const cp1: Point = {
      x: from.x + controlOffset,
      y: from.y
    };

    const cp2: Point = {
      x: to.x - controlOffset,
      y: to.y
    };

    // Return bezier curve points (simplified to 4 points)
    return [from, cp1, cp2, to];
  }

  /**
   * Check if a point is inside a rectangle
   */
  static isPointInRectangle(point: Point, rectangle: Rectangle): boolean {
    return point.x >= rectangle.x &&
           point.x <= rectangle.x + rectangle.width &&
           point.y >= rectangle.y &&
           point.y <= rectangle.y + rectangle.height;
  }

  /**
   * Calculate intersection point between two lines
   */
  static getIntersectionPoint(
    line1: [Point, Point],
    line2: [Point, Point]
  ): Point | null {
    const [p1, p2] = line1;
    const [p3, p4] = line2;

    const denominator = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x);

    if (Math.abs(denominator) < 1e-10) {
      return null; // Lines are parallel
    }

    const t = ((p1.x - p3.x) * (p3.y - p4.y) - (p1.y - p3.y) * (p3.x - p4.x)) / denominator;
    const u = -((p1.x - p2.x) * (p1.y - p3.y) - (p1.y - p2.y) * (p1.x - p3.x)) / denominator;

    if (t >= 0 && t <= 1 && u >= 0 && u <= 1) {
      return {
        x: p1.x + t * (p2.x - p1.x),
        y: p1.y + t * (p2.y - p1.y)
      };
    }

    return null; // No intersection within line segments
  }

  /**
   * Calculate bounding rectangle for a set of points
   */
  static calculateBounds(points: Point[]): Rectangle {
    if (points.length === 0) {
      return { x: 0, y: 0, width: 0, height: 0 };
    }

    let minX = points[0].x;
    let minY = points[0].y;
    let maxX = points[0].x;
    let maxY = points[0].y;

    for (const point of points) {
      minX = Math.min(minX, point.x);
      minY = Math.min(minY, point.y);
      maxX = Math.max(maxX, point.x);
      maxY = Math.max(maxY, point.y);
    }

    return {
      x: minX,
      y: minY,
      width: maxX - minX,
      height: maxY - minY
    };
  }

  /**
   * Calculate distance between two points
   */
  static distance(p1: Point, p2: Point): number {
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * Calculate angle between two points in radians
   */
  static angle(from: Point, to: Point): number {
    return Math.atan2(to.y - from.y, to.x - from.x);
  }

  /**
   * Rotate a point around a center point
   */
  static rotatePoint(point: Point, center: Point, angle: number): Point {
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);
    const dx = point.x - center.x;
    const dy = point.y - center.y;

    return {
      x: center.x + dx * cos - dy * sin,
      y: center.y + dx * sin + dy * cos
    };
  }

  /**
   * Check if two rectangles intersect
   */
  static rectanglesIntersect(rect1: Rectangle, rect2: Rectangle): boolean {
    return !(rect1.x + rect1.width < rect2.x ||
             rect2.x + rect2.width < rect1.x ||
             rect1.y + rect1.height < rect2.y ||
             rect2.y + rect2.height < rect1.y);
  }

  /**
   * Expand rectangle by margin
   */
  static expandRectangle(rect: Rectangle, margin: number): Rectangle {
    return {
      x: rect.x - margin,
      y: rect.y - margin,
      width: rect.width + 2 * margin,
      height: rect.height + 2 * margin
    };
  }
}
