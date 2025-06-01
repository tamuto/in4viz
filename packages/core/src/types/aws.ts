// AWS resource type definitions

import { Resource } from './infrastructure';

export type AWSResourceType =
  | 'vpc'
  | 'subnet'
  | 'internet-gateway'
  | 'nat-gateway'
  | 'route-table'
  | 'security-group'
  | 'network-acl'
  | 'ec2'
  | 'rds'
  | 's3'
  | 'lambda'
  | 'api-gateway'
  | 'load-balancer'
  | 'auto-scaling-group'
  | 'ecs'
  | 'eks'
  | 'cloudfront'
  | 'route53'
  | 'cloudwatch'
  | 'sns'
  | 'sqs'
  | 'kinesis'
  | 'dynamodb'
  | 'elasticache'
  | 'elasticsearch'
  | 'redshift';

export interface AWSResource extends Resource {
  provider: 'aws';
  type: AWSResourceType;
  properties: AWSResourceProperties;
}

export interface AWSResourceProperties extends Record<string, any> {
  region: string;
  availabilityZone?: string;
  arn?: string;
  tags?: Record<string, string>;
}

// VPC Resources
export interface VPCProperties extends AWSResourceProperties {
  cidrBlock: string;
  enableDnsHostnames?: boolean;
  enableDnsSupport?: boolean;
  tenancy?: 'default' | 'dedicated' | 'host';
}

export interface SubnetProperties extends AWSResourceProperties {
  vpcId: string;
  cidrBlock: string;
  mapPublicIpOnLaunch?: boolean;
  subnetType: 'public' | 'private' | 'isolated';
}

export interface InternetGatewayProperties extends AWSResourceProperties {
  vpcId: string;
}

export interface NATGatewayProperties extends AWSResourceProperties {
  subnetId: string;
  allocationId?: string;
  connectivityType?: 'public' | 'private';
}

export interface RouteTableProperties extends AWSResourceProperties {
  vpcId: string;
  routes?: Route[];
  associations?: string[]; // subnet IDs
}

export interface Route {
  destinationCidrBlock?: string;
  destinationIpv6CidrBlock?: string;
  gatewayId?: string;
  instanceId?: string;
  natGatewayId?: string;
  networkInterfaceId?: string;
  vpcPeeringConnectionId?: string;
}

export interface SecurityGroupProperties extends AWSResourceProperties {
  vpcId: string;
  description: string;
  ingressRules?: SecurityGroupRule[];
  egressRules?: SecurityGroupRule[];
}

export interface SecurityGroupRule {
  protocol: string;
  fromPort?: number;
  toPort?: number;
  source?: string; // CIDR or security group ID
  description?: string;
}

// Compute Resources
export interface EC2Properties extends AWSResourceProperties {
  instanceType: string;
  subnetId: string;
  securityGroupIds: string[];
  imageId: string;
  keyName?: string;
  userData?: string;
  iamInstanceProfile?: string;
  state?: 'pending' | 'running' | 'stopping' | 'stopped' | 'terminated';
  publicIp?: string;
  privateIp?: string;
}

export interface AutoScalingGroupProperties extends AWSResourceProperties {
  minSize: number;
  maxSize: number;
  desiredCapacity: number;
  subnetIds: string[];
  launchTemplate?: {
    id: string;
    version: string;
  };
  targetGroupArns?: string[];
}

// Database Resources
export interface RDSProperties extends AWSResourceProperties {
  engine: 'mysql' | 'postgres' | 'oracle' | 'sqlserver' | 'aurora' | 'aurora-mysql' | 'aurora-postgresql';
  instanceClass: string;
  allocatedStorage: number;
  multiAZ?: boolean;
  subnetGroupName?: string;
  securityGroupIds: string[];
  endpoint?: string;
  port?: number;
}

export interface DynamoDBProperties extends AWSResourceProperties {
  billingMode: 'PAY_PER_REQUEST' | 'PROVISIONED';
  readCapacity?: number;
  writeCapacity?: number;
  globalSecondaryIndexes?: Array<{
    indexName: string;
    readCapacity?: number;
    writeCapacity?: number;
  }>;
}

// Storage Resources
export interface S3Properties extends AWSResourceProperties {
  bucketName: string;
  versioning?: boolean;
  encryption?: boolean;
  publicAccess?: boolean;
  lifecycle?: Array<{
    id: string;
    status: 'Enabled' | 'Disabled';
    transitions?: Array<{
      days: number;
      storageClass: string;
    }>;
  }>;
}

// Compute Services
export interface LambdaProperties extends AWSResourceProperties {
  functionName: string;
  runtime: string;
  handler: string;
  timeout?: number;
  memorySize?: number;
  environment?: Record<string, string>;
  vpcConfig?: {
    subnetIds: string[];
    securityGroupIds: string[];
  };
}

export interface ECSProperties extends AWSResourceProperties {
  clusterName: string;
  serviceName?: string;
  taskDefinitionArn?: string;
  desiredCount?: number;
  subnetIds?: string[];
  securityGroupIds?: string[];
  launchType?: 'EC2' | 'FARGATE';
}

// Load Balancing
export interface LoadBalancerProperties extends AWSResourceProperties {
  type: 'application' | 'network' | 'gateway' | 'classic';
  scheme: 'internet-facing' | 'internal';
  subnetIds: string[];
  securityGroupIds?: string[];
  listeners?: Array<{
    port: number;
    protocol: string;
    targetGroupArn?: string;
  }>;
}

// Networking
export interface APIGatewayProperties extends AWSResourceProperties {
  apiType: 'REST' | 'HTTP' | 'WebSocket';
  name: string;
  description?: string;
  endpointConfiguration?: {
    types: Array<'EDGE' | 'REGIONAL' | 'PRIVATE'>;
  };
  stages?: Array<{
    stageName: string;
    deployment: string;
  }>;
}

// Content Delivery
export interface CloudFrontProperties extends AWSResourceProperties {
  distributionConfig: {
    origins: Array<{
      domainName: string;
      originPath?: string;
    }>;
    defaultCacheBehavior: {
      targetOriginId: string;
      viewerProtocolPolicy: 'allow-all' | 'https-only' | 'redirect-to-https';
    };
    enabled: boolean;
  };
}

// Monitoring & Management
export interface CloudWatchProperties extends AWSResourceProperties {
  namespace?: string;
  metricName?: string;
  dimensions?: Record<string, string>;
  statistic?: 'Average' | 'Sum' | 'Maximum' | 'Minimum' | 'SampleCount';
}

// Messaging
export interface SNSProperties extends AWSResourceProperties {
  topicName: string;
  displayName?: string;
  subscriptions?: Array<{
    protocol: 'email' | 'sms' | 'sqs' | 'lambda' | 'http' | 'https';
    endpoint: string;
  }>;
}

export interface SQSProperties extends AWSResourceProperties {
  queueName: string;
  queueType: 'standard' | 'fifo';
  visibilityTimeout?: number;
  messageRetentionPeriod?: number;
  maxReceiveCount?: number;
  deadLetterTargetArn?: string;
}
