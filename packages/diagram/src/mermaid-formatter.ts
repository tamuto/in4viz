import { PythonClass, PythonMethod, PythonAttribute, ParsedModule, DiagramOptions } from './types.js';

export class MermaidFormatter {
  private options: DiagramOptions;

  constructor(options: DiagramOptions) {
    this.options = options;
  }

  formatDiagram(modules: ParsedModule[]): string {
    const lines: string[] = [];
    lines.push('classDiagram');
    lines.push('');

    const allClasses = modules.flatMap(module => module.classes);
    
    for (const pythonClass of allClasses) {
      lines.push(...this.formatClass(pythonClass));
      lines.push('');
    }

    for (const pythonClass of allClasses) {
      lines.push(...this.formatRelations(pythonClass));
    }

    return lines.join('\n');
  }

  private formatClass(pythonClass: PythonClass): string[] {
    const lines: string[] = [];
    const className = pythonClass.name;
    
    lines.push(`    class ${className} {`);

    const attributes = this.options.includePrivate 
      ? pythonClass.attributes 
      : pythonClass.attributes.filter(attr => attr.visibility === 'public');

    for (const attr of attributes) {
      lines.push(`        ${this.formatAttribute(attr)}`);
    }

    const methods = this.options.includePrivate 
      ? pythonClass.methods 
      : pythonClass.methods.filter(method => method.visibility === 'public');

    for (const method of methods) {
      lines.push(`        ${this.formatMethod(method)}`);
    }

    lines.push('    }');

    if (this.options.includeDocstrings && pythonClass.docstring) {
      const docstring = this.escapeString(pythonClass.docstring);
      lines.push(`    ${className} : "${docstring}"`);
    }

    return lines;
  }

  private formatAttribute(attr: PythonAttribute): string {
    const visibility = this.getVisibilitySymbol(attr.visibility);
    const type = attr.type ? ` : ${attr.type}` : '';
    return `${visibility}${attr.name}${type}`;
  }

  private formatMethod(method: PythonMethod): string {
    const visibility = this.getVisibilitySymbol(method.visibility);
    const staticModifier = method.isStatic ? '$ ' : '';
    const params = method.parameters
      .filter(param => param.name !== 'self' && param.name !== 'cls')
      .map(param => {
        const type = param.type ? `: ${param.type}` : '';
        const defaultVal = param.defaultValue ? ` = ${param.defaultValue}` : '';
        return `${param.name}${type}${defaultVal}`;
      })
      .join(', ');
    
    const returnType = method.returnType ? ` : ${method.returnType}` : '';
    
    return `${staticModifier}${visibility}${method.name}(${params})${returnType}`;
  }

  private formatRelations(pythonClass: PythonClass): string[] {
    const lines: string[] = [];
    
    for (const baseClass of pythonClass.baseClasses) {
      if (baseClass !== 'object') {
        lines.push(`    ${baseClass} <|-- ${pythonClass.name}`);
      }
    }

    return lines;
  }

  private getVisibilitySymbol(visibility: 'public' | 'private' | 'protected'): string {
    switch (visibility) {
      case 'private':
        return '-';
      case 'protected':
        return '#';
      case 'public':
      default:
        return '+';
    }
  }

  private escapeString(str: string): string {
    return str
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/\n/g, '\\n')
      .replace(/\r/g, '\\r')
      .substring(0, 100);
  }
}