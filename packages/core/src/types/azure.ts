// Azure resource type definitions (placeholder for future implementation)

import { Resource } from './infrastructure';

export type AzureResourceType =
  | 'resource-group'
  | 'virtual-network'
  | 'subnet'
  | 'virtual-machine'
  | 'storage-account'
  | 'sql-database'
  | 'app-service'
  | 'function-app'
  | 'load-balancer'
  | 'application-gateway';

export interface AzureResource extends Resource {
  provider: 'azure';
  type: AzureResourceType;
  properties: AzureResourceProperties;
}

export interface AzureResourceProperties {
  resourceGroup: string;
  location: string;
  subscriptionId?: string;
  tags?: Record<string, string>;
}

// Basic implementations - will be expanded in Phase 2
export interface VirtualNetworkProperties extends AzureResourceProperties {
  addressSpace: string[];
}

export interface VirtualMachineProperties extends AzureResourceProperties {
  size: string;
  osType: 'Windows' | 'Linux';
  subnetId: string;
}
