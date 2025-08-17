// Basic hierarchical layout engine

import { Point, Size, Rectangle } from '../../types/common';
import { Resource, Connection, PositionedResource, PositionedConnection } from '../../types/infrastructure';
import {
  LayoutOptions,
  LayoutResult,
  LayoutEngine
} from '../../types/layout';
import { GeometryUtils } from '../geometry';

export class HierarchicalLayoutEngine implements LayoutEngine {
  calculateLayout(
    resources: Resource[],
    connections: Connection[],
    options: LayoutOptions
  ): LayoutResult {
    const startTime = performance.now();

    // Build hierarchy
    const hierarchy = this.buildHierarchy(resources);

    // Calculate positions for hierarchical layout
    const positionedResources = this.calculateHierarchicalPositions(hierarchy, options);

    // Calculate connection paths
    const positionedConnections = this.calculateConnectionPaths(
      connections,
      positionedResources,
      options
    );

    // Calculate overall bounds
    const bounds = this.calculateLayoutBounds(positionedResources);

    const endTime = performance.now();

    return {
      resources: positionedResources,
      connections: positionedConnections,
      bounds,
      algorithm: options.algorithm,
      executionTime: endTime - startTime,
      converged: true
    };
  }

  private buildHierarchy(resources: Resource[]): ResourceNode[] {
    const nodeMap = new Map<string, ResourceNode>();
    const rootNodes: ResourceNode[] = [];

    // Create nodes
    resources.forEach(resource => {
      const node: ResourceNode = {
        resource,
        children: [],
        level: 0,
        position: { x: 0, y: 0 },
        size: this.calculateResourceSize(resource)
      };
      nodeMap.set(resource.id, node);
    });

    // Build parent-child relationships and assign levels
    resources.forEach(resource => {
      const node = nodeMap.get(resource.id)!;

      if (resource.parent) {
        const parentNode = nodeMap.get(resource.parent);
        if (parentNode) {
          parentNode.children.push(node);
          node.level = parentNode.level + 1;
        } else {
          // Parent not found, treat as root
          rootNodes.push(node);
        }
      } else {
        rootNodes.push(node);
      }
    });

    // Update levels recursively
    const updateLevels = (node: ResourceNode, level: number) => {
      node.level = level;
      node.children.forEach(child => updateLevels(child, level + 1));
    };

    rootNodes.forEach(root => updateLevels(root, 0));

    return rootNodes;
  }

  private calculateHierarchicalPositions(
    hierarchy: ResourceNode[],
    options: LayoutOptions
  ): PositionedResource[] {
    const positionedResources: PositionedResource[] = [];
    const spacing = options.spacing;
    const margin = options.margin;

    let currentY = margin.top;

    // Process each root and its subtree
    hierarchy.forEach(root => {
      const subtreeHeight = this.layoutSubtree(
        root,
        margin.left,
        currentY,
        spacing,
        positionedResources
      );
      currentY += subtreeHeight + spacing.y;
    });

    return positionedResources;
  }

  private layoutSubtree(
    node: ResourceNode,
    startX: number,
    startY: number,
    spacing: Point,
    result: PositionedResource[]
  ): number {
    // Position current node
    node.position = { x: startX, y: startY };

    const bounds: Rectangle = {
      x: node.position.x,
      y: node.position.y,
      width: node.size.width,
      height: node.size.height
    };

    const positionedResource: PositionedResource = {
      ...node.resource,
      position: node.position,
      size: node.size,
      bounds,
      computedStyle: this.getResourceStyle(node.resource)
    };

    result.push(positionedResource);

    let maxHeight = node.size.height;

    if (node.children.length > 0) {
      // Layout children
      const childStartX = startX + node.size.width + spacing.x;
      let childY = startY;

      node.children.forEach(child => {
        const childHeight = this.layoutSubtree(
          child,
          childStartX,
          childY,
          spacing,
          result
        );
        childY += childHeight + spacing.y;
        maxHeight = Math.max(maxHeight, childHeight);
      });
    }

    return maxHeight;
  }

  private calculateResourceSize(resource: Resource): Size {
    // Basic size calculation - could be enhanced with actual text measurement
    const baseWidth = 120;
    const baseHeight = 60;

    // Adjust size based on resource type
    switch (resource.type) {
      case 'vpc':
        return { width: baseWidth * 2, height: baseHeight * 1.5 };
      case 'subnet':
        return { width: baseWidth * 1.5, height: baseHeight };
      case 'ec2':
      case 'rds':
        return { width: baseWidth, height: baseHeight };
      case 's3':
      case 'lambda':
        return { width: baseWidth * 0.8, height: baseHeight * 0.8 };
      default:
        return { width: baseWidth, height: baseHeight };
    }
  }

  private getResourceStyle(_resource: Resource): any {
    // Return default style - would be enhanced with theme support
    return {
      fill: '#ffffff',
      stroke: '#cccccc',
      strokeWidth: 1
    };
  }

  private calculateConnectionPaths(
    connections: Connection[],
    resources: PositionedResource[],
    _options: LayoutOptions
  ): PositionedConnection[] {
    const resourceMap = new Map<string, PositionedResource>();
    resources.forEach(resource => resourceMap.set(resource.id, resource));

    return connections.map(connection => {
      const fromResource = resourceMap.get(connection.from);
      const toResource = resourceMap.get(connection.to);

      if (!fromResource || !toResource) {
        // Invalid connection - create dummy positioned connection
        return {
          ...connection,
          path: [{ x: 0, y: 0 }, { x: 0, y: 0 }],
          bounds: { x: 0, y: 0, width: 0, height: 0 },
          computedStyle: {}
        };
      }

      // Calculate connection points (center to center for now)
      const fromPoint: Point = {
        x: fromResource.position.x + fromResource.size.width / 2,
        y: fromResource.position.y + fromResource.size.height / 2
      };

      const toPoint: Point = {
        x: toResource.position.x + toResource.size.width / 2,
        y: toResource.position.y + toResource.size.height / 2
      };

      // Create simple straight line path
      const path = [fromPoint, toPoint];
      const bounds = GeometryUtils.calculateBounds(path);

      return {
        ...connection,
        path,
        bounds,
        computedStyle: {
          stroke: '#666666',
          strokeWidth: 1
        }
      };
    });
  }

  private calculateLayoutBounds(resources: PositionedResource[]): Rectangle {
    if (resources.length === 0) {
      return { x: 0, y: 0, width: 0, height: 0 };
    }

    const points: Point[] = [];
    resources.forEach(resource => {
      points.push(resource.position);
      points.push({
        x: resource.position.x + resource.size.width,
        y: resource.position.y + resource.size.height
      });
    });

    return GeometryUtils.calculateBounds(points);
  }
}

interface ResourceNode {
  resource: Resource;
  children: ResourceNode[];
  level: number;
  position: Point;
  size: Size;
}
