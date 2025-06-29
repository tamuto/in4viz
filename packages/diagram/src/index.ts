export { PythonParser } from './python-parser.js';
export { MermaidFormatter } from './mermaid-formatter.js';
export * from './types.js';

export async function generateClassDiagram(inputPath: string, outputPath: string, options?: {
  includePrivate?: boolean;
  includeDocstrings?: boolean;
}): Promise<string> {
  const { PythonParser } = await import('./python-parser.js');
  const { MermaidFormatter } = await import('./mermaid-formatter.js');
  const { promises: fs } = await import('fs');
  const path = await import('path');

  const diagramOptions = {
    inputPath: path.resolve(inputPath),
    outputPath: path.resolve(outputPath),
    includePrivate: options?.includePrivate || false,
    includeDocstrings: options?.includeDocstrings || false,
  };

  const parser = new PythonParser();
  const stats = await fs.stat(diagramOptions.inputPath);
  
  let modules;
  if (stats.isDirectory()) {
    modules = await parser.parseDirectory(diagramOptions.inputPath);
  } else if (stats.isFile() && diagramOptions.inputPath.endsWith('.py')) {
    const module = await parser.parseFile(diagramOptions.inputPath);
    modules = [module];
  } else {
    throw new Error('Input must be a Python file (.py) or directory');
  }

  const formatter = new MermaidFormatter(diagramOptions);
  const mermaidDiagram = formatter.formatDiagram(modules);

  const outputDir = path.dirname(diagramOptions.outputPath);
  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(diagramOptions.outputPath, mermaidDiagram, 'utf-8');

  return mermaidDiagram;
}