// Main SVG renderer implementation

import { Point, Style } from '../../types/common';
import {
  RendererOptions,
  SVGRenderer,
  RenderTheme,
  SVGElements,
  InteractionHandler
} from '../../types/renderer';
import { PositionedResource, PositionedConnection } from '../../types/infrastructure';
import { LayoutResult } from '../../types/layout';
import { SVGUtils } from './svg-utils';
import { IconRegistry } from './icon-registry';
import { defaultTheme } from './themes';

export class DefaultSVGRenderer implements SVGRenderer {
  private container: Element;
  private options: RendererOptions;
  private theme: RenderTheme;
  private elements!: SVGElements;
  private iconRegistry: IconRegistry;
  private interactionHandler?: InteractionHandler;

  constructor(options: RendererOptions) {
    this.container = options.container;
    this.options = options;
    this.theme = options.theme || defaultTheme;
    this.iconRegistry = new IconRegistry();

    // Register default icons
    this.iconRegistry.registerAWSIcons();

    this.initializeSVG();
  }

  private initializeSVG(): void {
    // Create main SVG element
    const svg = SVGUtils.createSVGElement('svg', {
      width: this.options.width || '100%',
      height: this.options.height || '100%',
      viewBox: this.options.viewBox
        ? `${this.options.viewBox.x} ${this.options.viewBox.y} ${this.options.viewBox.width} ${this.options.viewBox.height}`
        : '0 0 800 600'
    });

    if (this.options.preserveAspectRatio) {
      svg.setAttribute('preserveAspectRatio', this.options.preserveAspectRatio);
    }

    // Create defs for markers and patterns
    const defs = SVGUtils.createSVGElement('defs');

    // Add arrow markers
    defs.appendChild(SVGUtils.createArrowMarker('arrowhead', this.theme.colors.foreground));
    defs.appendChild(SVGUtils.createArrowMarker('arrowhead-primary', this.theme.colors.primary));

    // Create layer groups
    const background = SVGUtils.createGroup({ class: 'in4viz-background' });
    const connections = SVGUtils.createGroup({ class: 'in4viz-connections' });
    const resources = SVGUtils.createGroup({ class: 'in4viz-resources' });
    const labels = SVGUtils.createGroup({ class: 'in4viz-labels' });
    const ui = SVGUtils.createGroup({ class: 'in4viz-ui' });

    // Add background if specified
    if (this.options.background || this.theme.colors.background) {
      const bgRect = SVGUtils.createRect(
        { x: 0, y: 0, width: 800, height: 600 },
        { fill: this.options.background || this.theme.colors.background }
      );
      background.appendChild(bgRect);
    }

    // Assemble SVG
    svg.appendChild(defs);
    svg.appendChild(background);
    svg.appendChild(connections);
    svg.appendChild(resources);
    svg.appendChild(labels);
    svg.appendChild(ui);

    this.elements = {
      svg,
      defs,
      background,
      connections,
      resources,
      labels,
      ui
    };

    // Clear container and add SVG
    this.container.innerHTML = '';
    this.container.appendChild(svg);

    // Setup interactions if enabled and in browser environment
    if (this.options.enableInteraction && typeof window !== 'undefined') {
      this.setupInteractions();
    }
  }

  render(layoutResult: LayoutResult): SVGElement {
    // Clear existing content
    this.clear();

    // Update viewBox based on layout bounds if auto-fit enabled
    if (this.options.width === undefined || this.options.height === undefined) {
      const bounds = layoutResult.bounds;
      const margin = 50;
      const viewBox = {
        x: bounds.x - margin,
        y: bounds.y - margin,
        width: bounds.width + 2 * margin,
        height: bounds.height + 2 * margin
      };

      this.elements.svg.setAttribute(
        'viewBox',
        `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`
      );
    }

    // Render connections first (so they appear behind resources)
    layoutResult.connections.forEach(connection => {
      const connectionElement = this.renderConnection(connection);
      this.elements.connections.appendChild(connectionElement);
    });

    // Render resources
    layoutResult.resources.forEach(resource => {
      const resourceElement = this.renderResource(resource);
      this.elements.resources.appendChild(resourceElement);
    });

    return this.elements.svg;
  }

  renderResource(resource: PositionedResource): SVGElement {
    const group = SVGUtils.createGroup({
      class: 'in4viz-resource',
      'data-resource-id': resource.id,
      'data-resource-type': resource.type
    });

    const style = {
      ...this.theme.defaults.resource,
      ...resource.computedStyle
    };

    // Create main shape
    const shape = this.createResourceShape(resource, style);
    group.appendChild(shape);

    // Add icon if available
    const icon = this.iconRegistry.get(resource.type);
    if (icon) {
      const iconSize = 24;
      const iconX = resource.position.x + 8;
      const iconY = resource.position.y + 8;

      SVGUtils.setAttributes(icon, {
        x: iconX,
        y: iconY,
        width: iconSize,
        height: iconSize
      });

      group.appendChild(icon);
    }

    // Add label
    const label = this.renderResourceLabel(resource, style);
    group.appendChild(label);

    return group;
  }

  renderConnection(connection: PositionedConnection): SVGElement {
    const group = SVGUtils.createGroup({
      class: 'in4viz-connection',
      'data-connection-id': connection.id || '',
      'data-connection-type': connection.type
    });

    const style = {
      ...this.theme.defaults.connection,
      ...connection.computedStyle
    };

    // Create connection path
    const path = this.createConnectionPath(connection, style);
    group.appendChild(path);

    // Add label if present
    if (connection.label) {
      const labelPos = this.calculateConnectionLabelPosition(connection);
      const label = this.renderLabel(connection.label, labelPos, style);
      group.appendChild(label);
    }

    return group;
  }

  renderLabel(text: string, position: Point, style: Style = {}): SVGElement {
    return SVGUtils.createText(text, position, {
      ...this.theme.defaults.label,
      ...style
    });
  }

  clear(): void {
    this.elements.connections.innerHTML = '';
    this.elements.resources.innerHTML = '';
    this.elements.labels.innerHTML = '';
    this.elements.ui.innerHTML = '';
  }

  updateTheme(theme: RenderTheme): void {
    this.theme = theme;
    // Force re-render if there's existing content
    // This would typically be called by the main In4viz class
  }

  exportToSVG(): string {
    // For Node.js environment, use toString method of mock element
    if (typeof XMLSerializer === 'undefined') {
      return (this.elements.svg as any).toString();
    }

    // For browser environment, use XMLSerializer
    return new XMLSerializer().serializeToString(this.elements.svg);
  }

  async exportToPNG(): Promise<string> {
    return new Promise((resolve, reject) => {
      const svgData = this.exportToSVG();
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        reject(new Error('Cannot get 2D context'));
        return;
      }

      const img = new Image();
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        resolve(canvas.toDataURL('image/png'));
      };

      img.onerror = reject;
      img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
    });
  }

  private createResourceShape(resource: PositionedResource, style: Style): SVGElement {
    const bounds = resource.bounds;

    if (style.borderRadius && style.borderRadius > 0) {
      // Create rounded rectangle using path
      const pathData = SVGUtils.createRoundedRectPath(bounds, style.borderRadius);
      return SVGUtils.createPath(pathData, style);
    } else {
      // Create regular rectangle
      return SVGUtils.createRect(bounds, style);
    }
  }

  private renderResourceLabel(resource: PositionedResource, style: Style): SVGElement {
    const labelX = resource.position.x + resource.size.width / 2;
    const labelY = resource.position.y + resource.size.height - 8;

    return SVGUtils.createText(resource.name, { x: labelX, y: labelY }, {
      fontSize: style.fontSize,
      fontFamily: style.fontFamily,
      fill: this.theme.colors.text,
      textAnchor: 'middle'
    } as any);
  }

  private createConnectionPath(connection: PositionedConnection, style: Style): SVGElement {
    if (connection.path.length < 2) {
      // Fallback to direct line
      return SVGUtils.createLine(connection.path[0] || {x: 0, y: 0}, connection.path[1] || {x: 0, y: 0}, style);
    }

    if (connection.path.length === 2) {
      // Simple line
      return SVGUtils.createLine(connection.path[0], connection.path[1], {
        ...style,
        markerEnd: 'url(#arrowhead)'
      });
    } else {
      // Complex path
      return SVGUtils.createPolyline(connection.path, {
        ...style,
        markerEnd: 'url(#arrowhead)'
      });
    }
  }

  private calculateConnectionLabelPosition(connection: PositionedConnection): Point {
    const path = connection.path;
    if (path.length >= 2) {
      const midIndex = Math.floor(path.length / 2);
      const midPoint = path[midIndex];
      return { x: midPoint.x, y: midPoint.y - 5 };
    }
    return { x: 0, y: 0 };
  }

  private setupInteractions(): void {
    // Basic click and hover handling
    this.elements.svg.addEventListener('click', (event) => {
      const target = event.target as SVGElement;
      const resourceElement = target.closest('.in4viz-resource');
      const connectionElement = target.closest('.in4viz-connection');

      if (resourceElement && this.interactionHandler?.onResourceClick) {
        // TODO: Find actual resource object and call handler
        // const resourceId = resourceElement.getAttribute('data-resource-id');
        // this.interactionHandler.onResourceClick(resource, event);
      } else if (connectionElement && this.interactionHandler?.onConnectionClick) {
        // TODO: Find actual connection object and call handler
        // const connectionId = connectionElement.getAttribute('data-connection-id');
        // this.interactionHandler.onConnectionClick(connection, event);
      } else if (this.interactionHandler?.onCanvasClick) {
        const rect = this.elements.svg.getBoundingClientRect();
        const point = {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top
        };
        this.interactionHandler.onCanvasClick(point, event);
      }
    });
  }

  setInteractionHandler(handler: InteractionHandler): void {
    this.interactionHandler = handler;
  }
}
