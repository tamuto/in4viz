#!/usr/bin/env node

import { Command } from 'commander';
import { promises as fs } from 'fs';
import path from 'path';
import { PythonParser } from './python-parser.js';
import { MermaidFormatter } from './mermaid-formatter.js';
import { DiagramOptions } from './types.js';

const program = new Command();

program
  .name('diagram')
  .description('Generate Mermaid class diagrams from Python source code')
  .version('0.0.1');

program
  .argument('<input>', 'Python source directory or file path')
  .argument('<output>', 'Output Mermaid file path')
  .option('-p, --include-private', 'Include private methods and attributes', false)
  .option('-d, --include-docstrings', 'Include class docstrings in diagram', false)
  .action(async (input: string, output: string, options: { includePrivate?: boolean; includeDocstrings?: boolean }) => {
    try {
      const inputPath = path.resolve(input);
      const outputPath = path.resolve(output);

      const stats = await fs.stat(inputPath);
      
      const diagramOptions: DiagramOptions = {
        inputPath,
        outputPath,
        includePrivate: options.includePrivate || false,
        includeDocstrings: options.includeDocstrings || false,
      };

      console.log(`Parsing Python source from: ${inputPath}`);
      
      const parser = new PythonParser();
      let modules;

      if (stats.isDirectory()) {
        modules = await parser.parseDirectory(inputPath);
      } else if (stats.isFile() && inputPath.endsWith('.py')) {
        const module = await parser.parseFile(inputPath);
        modules = [module];
      } else {
        throw new Error('Input must be a Python file (.py) or directory');
      }

      if (modules.length === 0) {
        console.warn('No Python classes found in the specified path');
        return;
      }

      const totalClasses = modules.reduce((sum, module) => sum + module.classes.length, 0);
      console.log(`Found ${totalClasses} classes in ${modules.length} files`);

      const formatter = new MermaidFormatter(diagramOptions);
      const mermaidDiagram = formatter.formatDiagram(modules);

      const outputDir = path.dirname(outputPath);
      await fs.mkdir(outputDir, { recursive: true });
      await fs.writeFile(outputPath, mermaidDiagram, 'utf-8');

      console.log(`Mermaid class diagram saved to: ${outputPath}`);
    } catch (error) {
      console.error('Error:', error instanceof Error ? error.message : error);
      process.exit(1);
    }
  });

program.parse();