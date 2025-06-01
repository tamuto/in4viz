// GCP resource type definitions (placeholder for future implementation)

import { Resource } from './infrastructure';

export type GCPResourceType =
  | 'project'
  | 'vpc-network'
  | 'subnet'
  | 'compute-instance'
  | 'cloud-storage'
  | 'cloud-sql'
  | 'cloud-function'
  | 'kubernetes-cluster'
  | 'load-balancer';

export interface GCPResource extends Resource {
  provider: 'gcp';
  type: GCPResourceType;
  properties: GCPResourceProperties;
}

export interface GCPResourceProperties {
  project: string;
  zone?: string;
  region?: string;
  labels?: Record<string, string>;
}

// Basic implementations - will be expanded in Phase 2
export interface VPCNetworkProperties extends GCPResourceProperties {
  autoCreateSubnetworks: boolean;
  routingMode: 'REGIONAL' | 'GLOBAL';
}

export interface ComputeInstanceProperties extends GCPResourceProperties {
  machineType: string;
  subnetwork: string;
  osImage: string;
}
