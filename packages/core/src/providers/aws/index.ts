// AWS provider definitions and utilities

import { Resource } from '../../types/infrastructure';
import { AWSResourceType } from '../../types/aws';

export class AWSProvider {
  /**
   * Create AWS VPC resource
   */
  static createVPC(
    id: string,
    name: string,
    cidrBlock: string,
    region: string = 'us-east-1'
  ): Resource {
    return {
      id,
      name,
      type: 'vpc',
      provider: 'aws',
      properties: {
        region,
        cidrBlock,
        enableDnsHostnames: true,
        enableDnsSupport: true,
        tenancy: 'default'
      }
    };
  }

  /**
   * Create AWS Subnet resource
   */
  static createSubnet(
    id: string,
    name: string,
    vpcId: string,
    cidrBlock: string,
    subnetType: 'public' | 'private' | 'isolated',
    availabilityZone: string,
    region: string = 'us-east-1'
  ): Resource {
    return {
      id,
      name,
      type: 'subnet',
      provider: 'aws',
      parent: vpcId,
      properties: {
        region,
        availabilityZone,
        vpcId,
        cidrBlock,
        subnetType,
        mapPublicIpOnLaunch: subnetType === 'public'
      }
    };
  }

  /**
   * Create AWS EC2 instance resource
   */
  static createEC2(
    id: string,
    name: string,
    subnetId: string,
    instanceType: string = 't3.micro',
    region: string = 'us-east-1'
  ): Resource {
    return {
      id,
      name,
      type: 'ec2',
      provider: 'aws',
      parent: subnetId,
      properties: {
        region,
        instanceType,
        subnetId,
        securityGroupIds: [],
        imageId: 'ami-12345678',
        state: 'running'
      }
    };
  }

  /**
   * Create AWS RDS instance resource
   */
  static createRDS(
    id: string,
    name: string,
    subnetGroupName: string,
    engine: 'mysql' | 'postgres' | 'oracle' | 'sqlserver' = 'mysql',
    region: string = 'us-east-1'
  ): Resource {
    return {
      id,
      name,
      type: 'rds',
      provider: 'aws',
      properties: {
        region,
        engine,
        instanceClass: 'db.t3.micro',
        allocatedStorage: 20,
        subnetGroupName,
        securityGroupIds: []
      }
    };
  }

  /**
   * Create AWS S3 bucket resource
   */
  static createS3(
    id: string,
    bucketName: string,
    region: string = 'us-east-1'
  ): Resource {
    return {
      id,
      name: bucketName,
      type: 's3',
      provider: 'aws',
      properties: {
        region,
        bucketName,
        versioning: false,
        encryption: true,
        publicAccess: false
      }
    };
  }

  /**
   * Create AWS Lambda function resource
   */
  static createLambda(
    id: string,
    functionName: string,
    runtime: string = 'nodejs18.x',
    region: string = 'us-east-1'
  ): Resource {
    return {
      id,
      name: functionName,
      type: 'lambda',
      provider: 'aws',
      properties: {
        region,
        functionName,
        runtime,
        handler: 'index.handler',
        timeout: 30,
        memorySize: 128
      }
    };
  }

  /**
   * Create AWS Load Balancer resource
   */
  static createLoadBalancer(
    id: string,
    name: string,
    type: 'application' | 'network' | 'gateway' = 'application',
    subnetIds: string[],
    region: string = 'us-east-1'
  ): Resource {
    return {
      id,
      name,
      type: 'load-balancer',
      provider: 'aws',
      properties: {
        region,
        type,
        scheme: 'internet-facing',
        subnetIds,
        securityGroupIds: []
      }
    };
  }

  /**
   * Get resource type-specific default properties
   */
  static getDefaultProperties(type: AWSResourceType, region: string = 'us-east-1'): any {
    const base = { region };

    switch (type) {
      case 'vpc':
        return { ...base, enableDnsHostnames: true, enableDnsSupport: true, tenancy: 'default' };
      case 'subnet':
        return { ...base, mapPublicIpOnLaunch: false };
      case 'ec2':
        return { ...base, state: 'running', securityGroupIds: [] };
      case 'rds':
        return { ...base, securityGroupIds: [], multiAZ: false };
      case 's3':
        return { ...base, versioning: false, encryption: true };
      case 'lambda':
        return { ...base, timeout: 30, memorySize: 128 };
      default:
        return base;
    }
  }
}
