export interface PythonClass {
  name: string;
  methods: PythonMethod[];
  attributes: PythonAttribute[];
  baseClasses: string[];
  docstring?: string;
  filePath: string;
  lineNumber: number;
}

export interface PythonMethod {
  name: string;
  parameters: PythonParameter[];
  returnType?: string;
  visibility: 'public' | 'private' | 'protected';
  isStatic: boolean;
  isClassMethod: boolean;
  docstring?: string;
}

export interface PythonAttribute {
  name: string;
  type?: string;
  visibility: 'public' | 'private' | 'protected';
  defaultValue?: string;
}

export interface PythonParameter {
  name: string;
  type?: string;
  defaultValue?: string;
  isOptional: boolean;
}

export interface ParsedModule {
  classes: PythonClass[];
  filePath: string;
}

export interface DiagramOptions {
  inputPath: string;
  outputPath: string;
  includePrivate?: boolean;
  includeDocstrings?: boolean;
}