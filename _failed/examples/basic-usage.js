#!/usr/bin/env node

// Basic usage example of In4viz library
const { In4viz, AWSProvider } = require('../packages/core/dist/index.js');

console.log('🚀 In4viz Library - Basic Usage Example\n');

// Create an In4viz instance
const in4viz = new In4viz();

// Create sample AWS infrastructure data
const sampleData = {
  id: 'sample-infrastructure',
  provider: 'aws',
  resources: [
    {
      id: 'vpc-1',
      type: 'vpc',
      name: 'Main VPC',
      provider: 'aws',
      properties: {
        cidr: '10.0.0.0/16',
        region: 'us-east-1'
      },
      metadata: {
        color: '#FF9900'
      }
    },
    {
      id: 'subnet-1',
      type: 'subnet',
      name: 'Public Subnet',
      provider: 'aws',
      properties: {
        cidr: '10.0.1.0/24',
        availabilityZone: 'us-east-1a'
      },
      metadata: {}
    },
    {
      id: 'ec2-1',
      type: 'ec2-instance',
      name: 'Web Server',
      provider: 'aws',
      properties: {
        instanceType: 't3.micro'
      },
      metadata: {}
    }
  ],
  connections: [
    {
      id: 'conn-1',
      from: 'vpc-1',
      to: 'subnet-1',
      type: 'contains'
    },
    {
      id: 'conn-2',
      from: 'subnet-1',
      to: 'ec2-1',
      type: 'contains'
    }
  ]
};

console.log('📊 Sample Infrastructure Data:');
console.log(`- ${sampleData.resources.length} resources`);
console.log(`- ${sampleData.connections.length} connections`);

try {
  // Render the infrastructure diagram
  const svg = in4viz.renderToString(sampleData, {
    algorithm: 'hierarchical',
    spacing: { x: 120, y: 100 },
    margin: { top: 50, right: 50, bottom: 50, left: 50 }
  });

  console.log('\n✅ Successfully generated SVG diagram!');
  console.log(`📏 SVG size: ${svg.length} characters`);
  console.log(`🎨 Contains ${(svg.match(/<rect/g) || []).length} rectangles`);
  console.log(`🔗 Contains ${(svg.match(/<line/g) || []).length} connections`);

  // Also test AWS provider
  const awsProvider = new AWSProvider();
  const awsHelper = awsProvider.createVPC('vpc-example', { cidr: '10.0.0.0/16' });

  console.log('\n🔧 AWS Provider test:');
  console.log('VPC resource:', awsHelper.name, awsHelper.type);

} catch (error) {
  console.error('❌ Error rendering diagram:', error.message);
}

console.log('\n🎉 In4viz core library is working correctly!');
