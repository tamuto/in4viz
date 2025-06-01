// Icon registry for managing resource icons

export class IconRegistry {
  private icons = new Map<string, string | SVGElement>();

  /**
   * Register an icon for a resource type
   */
  register(type: string, iconData: string | SVGElement): void {
    this.icons.set(type.toLowerCase(), iconData);
  }

  /**
   * Get icon for a resource type
   */
  get(type: string): SVGElement | null {
    const iconData = this.icons.get(type.toLowerCase());

    if (!iconData) {
      return null;
    }

    if (typeof iconData === 'string') {
      // Create SVG element from string
      const parser = new DOMParser();
      const doc = parser.parseFromString(iconData, 'image/svg+xml');
      const svgElement = doc.documentElement as any;

      if (svgElement instanceof SVGElement) {
        return svgElement.cloneNode(true) as SVGElement;
      }
      return null;
    }

    return iconData.cloneNode(true) as SVGElement;
  }

  /**
   * Check if icon exists for type
   */
  has(type: string): boolean {
    return this.icons.has(type.toLowerCase());
  }

  /**
   * List all registered icon types
   */
  list(): string[] {
    return Array.from(this.icons.keys());
  }

  /**
   * Remove an icon
   */
  remove(type: string): boolean {
    return this.icons.delete(type.toLowerCase());
  }

  /**
   * Clear all icons
   */
  clear(): void {
    this.icons.clear();
  }

  /**
   * Register default AWS icons
   */
  registerAWSIcons(): void {
    // Basic AWS icons as simple geometric shapes
    // In production, these would be proper AWS service icons

    this.register('vpc', this.createBasicIcon('rect', '#FF9900', 'VPC'));
    this.register('subnet', this.createBasicIcon('rect', '#4285F4', 'Sub'));
    this.register('ec2', this.createBasicIcon('rect', '#FF6B35', 'EC2'));
    this.register('rds', this.createBasicIcon('cylinder', '#336791', 'RDS'));
    this.register('s3', this.createBasicIcon('bucket', '#3F8624', 'S3'));
    this.register('lambda', this.createBasicIcon('triangle', '#FF9900', 'λ'));
    this.register('load-balancer', this.createBasicIcon('circle', '#FF6B35', 'LB'));
    this.register('api-gateway', this.createBasicIcon('hexagon', '#FF9900', 'API'));
    this.register('cloudfront', this.createBasicIcon('globe', '#FF9900', 'CF'));
    this.register('route53', this.createBasicIcon('diamond', '#FF9900', 'R53'));
    this.register('sns', this.createBasicIcon('bell', '#FF9900', 'SNS'));
    this.register('sqs', this.createBasicIcon('queue', '#FF9900', 'SQS'));
    this.register('dynamodb', this.createBasicIcon('table', '#4285F4', 'DDB'));
    this.register('internet-gateway', this.createBasicIcon('gateway', '#FF9900', 'IGW'));
    this.register('nat-gateway', this.createBasicIcon('gateway', '#4285F4', 'NAT'));
    this.register('security-group', this.createBasicIcon('shield', '#FF6B35', 'SG'));
  }

  /**
   * Create a basic icon with simple geometric shape
   */
  private createBasicIcon(shape: string, color: string, text: string): string {
    const size = 24;
    let shapeElement = '';

    switch (shape) {
      case 'rect':
        shapeElement = `<rect x="2" y="2" width="20" height="20" rx="2" fill="${color}" stroke="#fff" stroke-width="1"/>`;
        break;
      case 'circle':
        shapeElement = `<circle cx="12" cy="12" r="10" fill="${color}" stroke="#fff" stroke-width="1"/>`;
        break;
      case 'triangle':
        shapeElement = `<polygon points="12,2 22,20 2,20" fill="${color}" stroke="#fff" stroke-width="1"/>`;
        break;
      case 'cylinder':
        shapeElement = `
          <ellipse cx="12" cy="6" rx="8" ry="3" fill="${color}" stroke="#fff" stroke-width="1"/>
          <rect x="4" y="6" width="16" height="12" fill="${color}" stroke="none"/>
          <ellipse cx="12" cy="18" rx="8" ry="3" fill="${color}" stroke="#fff" stroke-width="1"/>
        `;
        break;
      case 'hexagon':
        shapeElement = `<polygon points="12,2 20,6 20,18 12,22 4,18 4,6" fill="${color}" stroke="#fff" stroke-width="1"/>`;
        break;
      case 'diamond':
        shapeElement = `<polygon points="12,2 22,12 12,22 2,12" fill="${color}" stroke="#fff" stroke-width="1"/>`;
        break;
      case 'bucket':
        shapeElement = `<path d="M4 6 L20 6 L18 20 L6 20 Z" fill="${color}" stroke="#fff" stroke-width="1"/>`;
        break;
      case 'globe':
        shapeElement = `
          <circle cx="12" cy="12" r="10" fill="${color}" stroke="#fff" stroke-width="1"/>
          <path d="M2 12 L22 12 M12 2 C8 6 8 18 12 22 M12 2 C16 6 16 18 12 22"
                stroke="#fff" stroke-width="1" fill="none"/>
        `;
        break;
      case 'bell':
        shapeElement = `<path d="M8 17 C8 19 10 21 12 21 C14 21 16 19 16 17 M18 8 C18 6 18 4 16 2 C14 1 10 1 8 2 C6 4 6 6 6 8 C6 10 5 11 4 12 L20 12 C19 11 18 10 18 8 Z" fill="${color}" stroke="#fff" stroke-width="1"/>`;
        break;
      case 'queue':
        shapeElement = `
          <rect x="2" y="4" width="20" height="4" fill="${color}" stroke="#fff" stroke-width="1"/>
          <rect x="2" y="10" width="20" height="4" fill="${color}" stroke="#fff" stroke-width="1"/>
          <rect x="2" y="16" width="20" height="4" fill="${color}" stroke="#fff" stroke-width="1"/>
        `;
        break;
      case 'table':
        shapeElement = `
          <rect x="2" y="4" width="20" height="16" fill="${color}" stroke="#fff" stroke-width="1"/>
          <line x1="2" y1="8" x2="22" y2="8" stroke="#fff" stroke-width="1"/>
          <line x1="8" y1="4" x2="8" y2="20" stroke="#fff" stroke-width="1"/>
        `;
        break;
      case 'gateway':
        shapeElement = `
          <rect x="2" y="8" width="6" height="8" fill="${color}" stroke="#fff" stroke-width="1"/>
          <rect x="16" y="8" width="6" height="8" fill="${color}" stroke="#fff" stroke-width="1"/>
          <rect x="8" y="10" width="8" height="4" fill="${color}" stroke="#fff" stroke-width="1"/>
        `;
        break;
      case 'shield':
        shapeElement = `<path d="M12 2 L4 6 L4 12 C4 16 8 20 12 22 C16 20 20 16 20 12 L20 6 Z" fill="${color}" stroke="#fff" stroke-width="1"/>`;
        break;
      default:
        shapeElement = `<rect x="2" y="2" width="20" height="20" rx="2" fill="${color}" stroke="#fff" stroke-width="1"/>`;
    }

    return `
      <svg width="${size}" height="${size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        ${shapeElement}
        <text x="12" y="16" text-anchor="middle" fill="#fff" font-size="6" font-family="Arial, sans-serif" font-weight="bold">
          ${text}
        </text>
      </svg>
    `;
  }
}
