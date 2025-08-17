// Data validation and normalization utilities

import {
  Infrastructure,
  Resource,
  Connection,
  InfrastructureValidator,
  ResourceHierarchy
} from '../types/infrastructure';
import { CloudProvider, ValidationResult, ValidationError } from '../types/common';

export class DataValidator implements InfrastructureValidator {
  validate(infrastructure: Infrastructure): ValidationResult {
    const errors: ValidationError[] = [];

    // Basic structure validation
    if (!infrastructure.id) {
      errors.push({
        field: 'id',
        message: 'Infrastructure ID is required',
        code: 'REQUIRED_FIELD'
      });
    }

    if (!infrastructure.provider) {
      errors.push({
        field: 'provider',
        message: 'Provider is required',
        code: 'REQUIRED_FIELD'
      });
    } else if (!this.isValidProvider(infrastructure.provider)) {
      errors.push({
        field: 'provider',
        message: `Invalid provider: ${infrastructure.provider}`,
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
        if (!resourceErrors.isValid) {
          resourceErrors.errors.forEach((error: ValidationError) => {
            errors.push({
              ...error,
              field: `resources[${index}].${error.field}`
            });
          });
        }
      });

      // Check for duplicate resource IDs
      const resourceIds = infrastructure.resources.map(r => r.id);
      const duplicates = resourceIds.filter((id, index) => resourceIds.indexOf(id) !== index);
      if (duplicates.length > 0) {
        errors.push({
          field: 'resources',
          message: `Duplicate resource IDs found: ${duplicates.join(', ')}`,
          code: 'DUPLICATE_ID'
        });
      }
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
        if (!connectionErrors.isValid) {
          connectionErrors.errors.forEach((error: ValidationError) => {
            errors.push({
              ...error,
              field: `connections[${index}].${error.field}`
            });
          });
        }
      });

      // Validate connection references
      const resourceIds = new Set(infrastructure.resources.map(r => r.id));
      infrastructure.connections.forEach((connection, index) => {
        if (!resourceIds.has(connection.from)) {
          errors.push({
            field: `connections[${index}].from`,
            message: `Connection references non-existent resource: ${connection.from}`,
            code: 'INVALID_REFERENCE'
          });
        }
        if (!resourceIds.has(connection.to)) {
          errors.push({
            field: `connections[${index}].to`,
            message: `Connection references non-existent resource: ${connection.to}`,
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

    if (!resource.id) {
      errors.push({
        field: 'id',
        message: 'Resource ID is required',
        code: 'REQUIRED_FIELD'
      });
    }

    if (!resource.type) {
      errors.push({
        field: 'type',
        message: 'Resource type is required',
        code: 'REQUIRED_FIELD'
      });
    }

    if (!resource.name) {
      errors.push({
        field: 'name',
        message: 'Resource name is required',
        code: 'REQUIRED_FIELD'
      });
    }

    if (!resource.provider) {
      errors.push({
        field: 'provider',
        message: 'Resource provider is required',
        code: 'REQUIRED_FIELD'
      });
    } else if (!this.isValidProvider(resource.provider)) {
      errors.push({
        field: 'provider',
        message: `Invalid provider: ${resource.provider}`,
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

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  validateConnection(connection: Connection): ValidationResult {
    const errors: ValidationError[] = [];

    if (!connection.from) {
      errors.push({
        field: 'from',
        message: 'Connection source is required',
        code: 'REQUIRED_FIELD'
      });
    }

    if (!connection.to) {
      errors.push({
        field: 'to',
        message: 'Connection target is required',
        code: 'REQUIRED_FIELD'
      });
    }

    if (connection.from === connection.to) {
      errors.push({
        field: 'to',
        message: 'Connection cannot have the same source and target',
        code: 'INVALID_VALUE'
      });
    }

    if (!connection.type) {
      errors.push({
        field: 'type',
        message: 'Connection type is required',
        code: 'REQUIRED_FIELD'
      });
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  private isValidProvider(provider: string): provider is CloudProvider {
    return ['aws', 'azure', 'gcp'].includes(provider);
  }
}

export class DataNormalizer {
  /**
   * Normalize infrastructure data and build hierarchy
   */
  normalize(infrastructure: Infrastructure): Infrastructure {
    const normalized = { ...infrastructure };

    // Normalize resources
    normalized.resources = this.normalizeResources(infrastructure.resources);

    // Normalize connections
    normalized.connections = this.normalizeConnections(infrastructure.connections);

    // Build parent-child relationships
    this.buildHierarchy(normalized.resources);

    return normalized;
  }

  private normalizeResources(resources: Resource[]): Resource[] {
    return resources.map(resource => ({
      ...resource,
      children: [], // Will be populated by buildHierarchy
      properties: this.normalizeProperties(resource.properties, resource.provider, resource.type)
    }));
  }

  private normalizeConnections(connections: Connection[]): Connection[] {
    return connections.map((connection, index) => ({
      id: connection.id || `connection-${index}`,
      ...connection,
      bidirectional: connection.bidirectional ?? false
    }));
  }

  private normalizeProperties(
    properties: Record<string, any>,
    provider: CloudProvider,
    type: string
  ): Record<string, any> {
    // Provider-specific property normalization
    switch (provider) {
      case 'aws':
        return this.normalizeAWSProperties(properties, type);
      case 'azure':
        return this.normalizeAzureProperties(properties, type);
      case 'gcp':
        return this.normalizeGCPProperties(properties, type);
      default:
        return properties;
    }
  }

  private normalizeAWSProperties(properties: Record<string, any>, type: string): Record<string, any> {
    const normalized = { ...properties };

    // Ensure region is set
    if (!normalized.region) {
      normalized.region = 'us-east-1'; // Default region
    }

    // Type-specific normalization
    switch (type) {
      case 'vpc':
        if (!normalized.enableDnsHostnames) normalized.enableDnsHostnames = true;
        if (!normalized.enableDnsSupport) normalized.enableDnsSupport = true;
        if (!normalized.tenancy) normalized.tenancy = 'default';
        break;
      case 'subnet':
        if (normalized.mapPublicIpOnLaunch === undefined) {
          normalized.mapPublicIpOnLaunch = normalized.subnetType === 'public';
        }
        break;
      case 'ec2':
        if (!normalized.state) normalized.state = 'running';
        break;
    }

    return normalized;
  }

  private normalizeAzureProperties(properties: Record<string, any>, _type: string): Record<string, any> {
    // Azure-specific normalization (placeholder)
    return properties;
  }

  private normalizeGCPProperties(properties: Record<string, any>, _type: string): Record<string, any> {
    // GCP-specific normalization (placeholder)
    return properties;
  }

  /**
   * Build parent-child relationships based on parent field
   */
  private buildHierarchy(resources: Resource[]): void {
    const resourceMap = new Map<string, Resource>();
    resources.forEach(resource => {
      resourceMap.set(resource.id, resource);
      resource.children = []; // Initialize children array
    });

    resources.forEach(resource => {
      if (resource.parent) {
        const parentResource = resourceMap.get(resource.parent);
        if (parentResource && parentResource.children) {
          parentResource.children.push(resource.id);
        }
      }
    });
  }

  /**
   * Get resource hierarchy tree
   */
  getHierarchy(resources: Resource[]): ResourceHierarchy[] {
    const resourceMap = new Map<string, Resource>();
    resources.forEach(resource => resourceMap.set(resource.id, resource));

    const buildTree = (resource: Resource, depth: number = 0): ResourceHierarchy => {
      const children = (resource.children || [])
        .map(childId => resourceMap.get(childId))
        .filter(child => child !== undefined)
        .map(child => buildTree(child!, depth + 1));

      return {
        resource,
        children,
        depth
      };
    };

    // Find root resources (no parent)
    const roots = resources.filter(resource => !resource.parent);
    return roots.map(root => buildTree(root));
  }
}
