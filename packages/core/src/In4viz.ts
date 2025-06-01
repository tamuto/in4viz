// Main In4viz class - the primary interface for the library

import { Infrastructure } from './types/infrastructure';
import { LayoutOptions, LayoutResult } from './types/layout';
import { RendererOptions, InteractionHandler, RenderTheme } from './types/renderer';
import { ValidationResult } from './types/common';

import { LayoutManager } from './core/layout';
import { DefaultSVGRenderer } from './core/renderer';
import { DataValidator, DataNormalizer } from './utils/data';
import { defaultTheme, awsTheme, azureTheme, gcpTheme, darkTheme } from './core/renderer/themes';

export interface In4vizOptions {
  container?: Element;
  width?: number;
  height?: number;
  theme?: RenderTheme | string;
  layout?: Partial<LayoutOptions>;
  enableInteraction?: boolean;
  enableAnimation?: boolean;
}

export class In4viz {
  private container: Element;
  private options: In4vizOptions;
  private layoutManager: LayoutManager;
  private renderer: DefaultSVGRenderer;
  private validator: DataValidator;
  private normalizer: DataNormalizer;
  private infrastructure?: Infrastructure;
  private lastLayoutResult?: LayoutResult;

  constructor(options: In4vizOptions = {}) {
    // Create default container if not provided
    this.container = options.container || this.createDefaultContainer();
    this.options = options;

    // Initialize core components
    this.layoutManager = new LayoutManager();
    this.validator = new DataValidator();
    this.normalizer = new DataNormalizer();

    // Initialize renderer
    const rendererOptions: RendererOptions = {
      container: this.container,
      width: options.width,
      height: options.height,
      theme: this.resolveTheme(options.theme),
      enableInteraction: this.isNodeJS() ? false : (options.enableInteraction ?? true),
      enableAnimation: options.enableAnimation ?? false
    };

    this.renderer = new DefaultSVGRenderer(rendererOptions);
  }

  private isNodeJS(): boolean {
    return typeof window === 'undefined' && typeof document === 'undefined';
  }

  private createDefaultContainer(): Element {
    // Create a temporary container for headless usage
    if (typeof document !== 'undefined') {
      const div = document.createElement('div');
      div.style.visibility = 'hidden';
      div.style.position = 'absolute';
      div.style.top = '-9999px';
      document.body.appendChild(div);
      return div;
    } else {
      // For Node.js environment, create a mock element
      return {
        appendChild: () => {},
        innerHTML: '',
        setAttribute: () => {},
        getAttribute: () => null,
        removeChild: () => {},
        querySelector: () => null,
        querySelectorAll: () => []
      } as any;
    }
  }

  /**
   * Set infrastructure data
   */
  setData(infrastructure: Infrastructure): ValidationResult {
    // Validate data
    const validationResult = this.validator.validate(infrastructure);

    if (!validationResult.isValid) {
      console.warn('Infrastructure data validation failed:', validationResult.errors);
      return validationResult;
    }

    // Normalize data
    this.infrastructure = this.normalizer.normalize(infrastructure);

    return validationResult;
  }

  /**
   * Render the diagram
   */
  render(infrastructure?: Infrastructure, layoutOptions?: Partial<LayoutOptions>): SVGElement {
    // If infrastructure data is provided, set it
    if (infrastructure) {
      const validationResult = this.setData(infrastructure);
      if (!validationResult.isValid) {
        throw new Error(`Invalid infrastructure data: ${validationResult.errors.join(', ')}`);
      }
    }

    if (!this.infrastructure) {
      throw new Error('No infrastructure data set. Call setData() first or provide data to render().');
    }

    // If layout options are provided, update them
    if (layoutOptions) {
      this.options.layout = { ...this.options.layout, ...layoutOptions };
    }

    // Calculate layout
    const layoutOptionsToUse = this.getLayoutOptions();
    this.lastLayoutResult = this.layoutManager.calculateLayout(
      this.infrastructure.resources,
      this.infrastructure.connections,
      layoutOptionsToUse
    );

    // Render
    return this.renderer.render(this.lastLayoutResult);
  }

  /**
   * Update layout options and re-render
   */
  setLayoutOptions(options: Partial<LayoutOptions>): void {
    this.options.layout = { ...this.options.layout, ...options };

    if (this.infrastructure) {
      this.render();
    }
  }

  /**
   * Update theme and re-render
   */
  setTheme(theme: RenderTheme | string): void {
    const resolvedTheme = this.resolveTheme(theme);
    this.renderer.updateTheme(resolvedTheme);
    this.options.theme = theme;

    if (this.infrastructure) {
      this.render();
    }
  }

  /**
   * Set interaction handlers
   */
  setInteractionHandler(handler: InteractionHandler): void {
    this.renderer.setInteractionHandler(handler);
  }

  /**
   * Render the diagram and return as SVG string
   */
  renderToString(infrastructure?: Infrastructure, layoutOptions?: Partial<LayoutOptions>): string {
    this.render(infrastructure, layoutOptions);
    return this.exportSVG();
  }

  /**
   * Export diagram as SVG string
   */
  exportSVG(): string {
    return this.renderer.exportToSVG();
  }

  /**
   * Export diagram as PNG data URL
   */
  async exportPNG(): Promise<string> {
    return this.renderer.exportToPNG();
  }

  /**
   * Get current layout result
   */
  getLayoutResult(): LayoutResult | undefined {
    return this.lastLayoutResult;
  }

  /**
   * Get infrastructure data
   */
  getData(): Infrastructure | undefined {
    return this.infrastructure;
  }

  /**
   * Validate infrastructure data without setting it
   */
  validateData(infrastructure: Infrastructure): ValidationResult {
    return this.validator.validate(infrastructure);
  }

  /**
   * Clear the diagram
   */
  clear(): void {
    this.renderer.clear();
    this.infrastructure = undefined;
    this.lastLayoutResult = undefined;
  }

  /**
   * Destroy the instance and clean up resources
   */
  destroy(): void {
    this.clear();
    this.container.innerHTML = '';
  }

  private getLayoutOptions(): LayoutOptions {
    const defaultOptions: LayoutOptions = {
      algorithm: 'hierarchical',
      spacing: { x: 120, y: 80 },
      margin: { top: 50, right: 50, bottom: 50, left: 50 },
      autoFit: true,
      preserveAspectRatio: true
    };

    return { ...defaultOptions, ...this.options.layout };
  }

  private resolveTheme(theme?: RenderTheme | string): RenderTheme {
    if (!theme) {
      return defaultTheme;
    }

    if (typeof theme === 'string') {
      // Load theme by name
      switch (theme) {
        case 'aws':
          return awsTheme;
        case 'azure':
          return azureTheme;
        case 'gcp':
          return gcpTheme;
        case 'dark':
          return darkTheme;
        default:
          return defaultTheme;
      }
    }

    return theme;
  }
}

// Static methods for convenience
export namespace In4viz {
  /**
   * Create a new In4viz instance
   */
  export function create(options: In4vizOptions): In4viz {
    return new In4viz(options);
  }

  /**
   * Validate infrastructure data
   */
  export function validate(infrastructure: Infrastructure): ValidationResult {
    const validator = new DataValidator();
    return validator.validate(infrastructure);
  }
}
