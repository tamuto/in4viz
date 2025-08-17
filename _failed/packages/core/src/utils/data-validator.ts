// Data validation and normalization utilities

import { Infrastructure, Resource, Connection } from '../types/infrastructure';
import { ValidationResult, ValidationError } from '../types/common';

export class DataValidator {
  validate(infrastructure: Infrastructure): ValidationResult {
    const errors: ValidationError[] = [];

    // Basic structure validation
    if (!infrastructure) {
      errors.push({
        field: 'infrastructure',
        message: 'Infrastructure object is required',
        code: 'REQUIRED'
      });
      return { isValid: false, errors };
    }

    // Validate required fields
    if (!infrastructure.id) {
      errors.push({
        field: 'id',
        message: 'Infrastructure ID is required',
        code: 'REQUIRED'
      });
    }

    if (!infrastructure.provider) {
      errors.push({
        field: 'provider',
        message: 'Provider is required',
        code: 'REQUIRED'
      });
    } else if (!['aws', 'azure', 'gcp'].includes(infrastructure.provider)) {
      errors.push({
        field: 'provider',
        message: 'Provider must be one of: aws, azure, gcp',
        code: 'INVALID_VALUE'
      });
    }

    if (!Array.isArray(infrastructure.resources)) {
      errors.push({
        field: 'resources',
        message: 'Resources must be an array',
        code: 'INVALID_TYPE'
      });
    } else {
      // Validate each resource
      infrastructure.resources.forEach((resource, index) => {
        const resourceErrors = this.validateResource(resource);
        resourceErrors.errors.forEach(error => {
          errors.push({
            ...error,
            field: `resources[${index}].${error.field}`
          });
        });
      });
    }

    if (!Array.isArray(infrastructure.connections)) {
      errors.push({
        field: 'connections',
        message: 'Connections must be an array',
        code: 'INVALID_TYPE'
      });
    } else {
      // Validate each connection
      infrastructure.connections.forEach((connection, index) => {
        const connectionErrors = this.validateConnection(connection);
        connectionErrors.errors.forEach(error => {
          errors.push({
            ...error,
            field: `connections[${index}].${error.field}`
          });
        });
      });
    }

    // Cross-reference validation
    if (Array.isArray(infrastructure.resources) && Array.isArray(infrastructure.connections)) {
      const resourceIds = new Set(infrastructure.resources.map(r => r.id));

      infrastructure.connections.forEach((connection, index) => {
        if (!resourceIds.has(connection.from)) {
          errors.push({
            field: `connections[${index}].from`,
            message: `Connection references unknown resource: ${connection.from}`,
            code: 'INVALID_REFERENCE'
          });
        }

        if (!resourceIds.has(connection.to)) {
          errors.push({
            field: `connections[${index}].to`,
            message: `Connection references unknown resource: ${connection.to}`,
            code: 'INVALID_REFERENCE'
          });
        }
      });
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  validateResource(resource: Resource): ValidationResult {
    const errors: ValidationError[] = [];

    if (!resource) {
      errors.push({
        field: 'resource',
        message: 'Resource object is required',
        code: 'REQUIRED'
      });
      return { isValid: false, errors };
    }

    // Required fields
    if (!resource.id) {
      errors.push({
        field: 'id',
        message: 'Resource ID is required',
        code: 'REQUIRED'
      });
    }

    if (!resource.type) {
      errors.push({
        field: 'type',
        message: 'Resource type is required',
        code: 'REQUIRED'
      });
    }

    if (!resource.name) {
      errors.push({
        field: 'name',
        message: 'Resource name is required',
        code: 'REQUIRED'
      });
    }

    if (!resource.provider) {
      errors.push({
        field: 'provider',
        message: 'Resource provider is required',
        code: 'REQUIRED'
      });
    } else if (!['aws', 'azure', 'gcp'].includes(resource.provider)) {
      errors.push({
        field: 'provider',
        message: 'Provider must be one of: aws, azure, gcp',
        code: 'INVALID_VALUE'
      });
    }

    if (!resource.properties || typeof resource.properties !== 'object') {
      errors.push({
        field: 'properties',
        message: 'Resource properties must be an object',
        code: 'INVALID_TYPE'
      });
    }

    // Validate position if provided
    if (resource.position) {
      if (typeof resource.position.x !== 'number' || typeof resource.position.y !== 'number') {
        errors.push({
          field: 'position',
          message: 'Position must have numeric x and y coordinates',
          code: 'INVALID_TYPE'
        });
      }
    }

    // Validate size if provided
    if (resource.size) {
      if (typeof resource.size.width !== 'number' || typeof resource.size.height !== 'number') {
        errors.push({
          field: 'size',
          message: 'Size must have numeric width and height',
          code: 'INVALID_TYPE'
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  validateConnection(connection: Connection): ValidationResult {
    const errors: ValidationError[] = [];

    if (!connection) {
      errors.push({
        field: 'connection',
        message: 'Connection object is required',
        code: 'REQUIRED'
      });
      return { isValid: false, errors };
    }

    // Required fields
    if (!connection.from) {
      errors.push({
        field: 'from',
        message: 'Connection from is required',
        code: 'REQUIRED'
      });
    }

    if (!connection.to) {
      errors.push({
        field: 'to',
        message: 'Connection to is required',
        code: 'REQUIRED'
      });
    }

    if (!connection.type) {
      errors.push({
        field: 'type',
        message: 'Connection type is required',
        code: 'REQUIRED'
      });
    } else if (!['network', 'dependency', 'data', 'security'].includes(connection.type)) {
      errors.push({
        field: 'type',
        message: 'Connection type must be one of: network, dependency, data, security',
        code: 'INVALID_VALUE'
      });
    }

    // Self-connection check
    if (connection.from === connection.to) {
      errors.push({
        field: 'connection',
        message: 'Connection cannot be from a resource to itself',
        code: 'INVALID_SELF_CONNECTION'
      });
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

export class DataNormalizer {
  normalize(infrastructure: Infrastructure): Infrastructure {
    const normalized = { ...infrastructure };

    // Normalize resources
    normalized.resources = infrastructure.resources.map(resource => this.normalizeResource(resource));

    // Normalize connections
    normalized.connections = infrastructure.connections.map(connection => this.normalizeConnection(connection));

    // Build hierarchy relationships
    this.buildHierarchy(normalized.resources);

    return normalized;
  }

  private normalizeResource(resource: Resource): Resource {
    const normalized = { ...resource };

    // Ensure properties exist
    if (!normalized.properties) {
      normalized.properties = {};
    }

    // Generate ID if missing
    if (!normalized.id) {
      normalized.id = this.generateId();
    }

    // Normalize type to lowercase
    if (normalized.type) {
      normalized.type = normalized.type.toLowerCase();
    }

    // Set default metadata
    if (!normalized.metadata) {
      normalized.metadata = {};
    }

    return normalized;
  }

  private normalizeConnection(connection: Connection): Connection {
    const normalized = { ...connection };

    // Generate ID if missing
    if (!normalized.id) {
      normalized.id = this.generateId();
    }

    // Normalize type to lowercase
    if (normalized.type) {
      normalized.type = normalized.type.toLowerCase();
    }

    // Set default bidirectional to false
    if (normalized.bidirectional === undefined) {
      normalized.bidirectional = false;
    }

    // Set default metadata
    if (!normalized.metadata) {
      normalized.metadata = {};
    }

    return normalized;
  }

  private buildHierarchy(resources: Resource[]): void {
    const resourceMap = new Map<string, Resource>();
    resources.forEach(resource => resourceMap.set(resource.id, resource));

    // Build children arrays
    resources.forEach(resource => {
      if (resource.parent) {
        const parent = resourceMap.get(resource.parent);
        if (parent) {
          if (!parent.children) {
            parent.children = [];
          }
          if (!parent.children.includes(resource.id)) {
            parent.children.push(resource.id);
          }
        }
      }
    });
  }

  private generateId(): string {
    return 'res_' + Math.random().toString(36).substr(2, 9);
  }
}
