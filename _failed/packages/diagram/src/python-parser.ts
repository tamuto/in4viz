import { spawn } from 'child_process';
import { ParsedModule } from './types.js';

const PYTHON_AST_SCRIPT = `
import ast
import sys
import json
import os

def get_visibility(name):
    if name.startswith('__') and name.endswith('__'):
        return 'public'
    elif name.startswith('__'):
        return 'private'
    elif name.startswith('_'):
        return 'protected'
    else:
        return 'public'

def extract_docstring(node):
    if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and
        node.body and isinstance(node.body[0], ast.Expr) and
        isinstance(node.body[0].value, ast.Constant) and
        isinstance(node.body[0].value.value, str)):
        return node.body[0].value.value
    return None

def parse_parameter(arg):
    param = {
        'name': arg.arg,
        'type': None,
        'defaultValue': None,
        'isOptional': False
    }
    
    if arg.annotation:
        param['type'] = ast.unparse(arg.annotation)
    
    return param

def parse_method(node, defaults_offset=0):
    method = {
        'name': node.name,
        'parameters': [],
        'returnType': None,
        'visibility': get_visibility(node.name),
        'isStatic': False,
        'isClassMethod': False,
        'docstring': extract_docstring(node)
    }
    
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            if decorator.id == 'staticmethod':
                method['isStatic'] = True
            elif decorator.id == 'classmethod':
                method['isClassMethod'] = True
    
    if node.returns:
        method['returnType'] = ast.unparse(node.returns)
    
    defaults = node.args.defaults
    num_args = len(node.args.args)
    num_defaults = len(defaults)
    
    for i, arg in enumerate(node.args.args):
        param = parse_parameter(arg)
        
        default_index = i - (num_args - num_defaults)
        if default_index >= 0:
            param['defaultValue'] = ast.unparse(defaults[default_index])
            param['isOptional'] = True
        
        method['parameters'].append(param)
    
    return method

def parse_class(node, filepath):
    class_info = {
        'name': node.name,
        'methods': [],
        'attributes': [],
        'baseClasses': [],
        'docstring': extract_docstring(node),
        'filePath': filepath,
        'lineNumber': node.lineno
    }
    
    for base in node.bases:
        if isinstance(base, ast.Name):
            class_info['baseClasses'].append(base.id)
        elif isinstance(base, ast.Attribute):
            class_info['baseClasses'].append(ast.unparse(base))
    
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method = parse_method(item)
            class_info['methods'].append(method)
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            attr = {
                'name': item.target.id,
                'type': ast.unparse(item.annotation) if item.annotation else None,
                'visibility': get_visibility(item.target.id),
                'defaultValue': ast.unparse(item.value) if item.value else None
            }
            class_info['attributes'].append(attr)
        elif isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    attr = {
                        'name': target.id,
                        'type': None,
                        'visibility': get_visibility(target.id),
                        'defaultValue': ast.unparse(item.value)
                    }
                    class_info['attributes'].append(attr)
    
    return class_info

def parse_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=filepath)
        
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(parse_class(node, filepath))
        
        return {
            'classes': classes,
            'filePath': filepath
        }
    except Exception as e:
        return {
            'error': str(e),
            'filePath': filepath
        }

if __name__ == '__main__':
    filepath = sys.argv[1]
    result = parse_file(filepath)
    print(json.dumps(result, indent=2, ensure_ascii=False))
`;

export class PythonParser {
  private pythonScript: string;

  constructor() {
    this.pythonScript = PYTHON_AST_SCRIPT;
  }

  async parseFile(filePath: string): Promise<ParsedModule> {
    return new Promise((resolve, reject) => {
      const python = spawn('python3', ['-c', this.pythonScript, filePath]);
      
      let stdout = '';
      let stderr = '';

      python.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      python.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python script failed with code ${code}: ${stderr}`));
          return;
        }

        try {
          const result = JSON.parse(stdout);
          if (result.error) {
            reject(new Error(`Python parsing error: ${result.error}`));
            return;
          }
          resolve(result as ParsedModule);
        } catch (error) {
          reject(new Error(`Failed to parse JSON output: ${error}`));
        }
      });

      python.on('error', (error) => {
        reject(new Error(`Failed to spawn Python process: ${error.message}`));
      });
    });
  }

  async parseDirectory(directoryPath: string): Promise<ParsedModule[]> {
    const glob = await import('fast-glob');
    const pythonFiles = await glob.default('**/*.py', {
      cwd: directoryPath,
      absolute: true,
      ignore: ['**/__pycache__/**', '**/venv/**', '**/env/**', '**/.venv/**']
    });

    const results: ParsedModule[] = [];
    
    for (const filePath of pythonFiles) {
      try {
        const module = await this.parseFile(filePath);
        if (module.classes.length > 0) {
          results.push(module);
        }
      } catch (error) {
        console.warn(`Warning: Failed to parse ${filePath}: ${error}`);
      }
    }

    return results;
  }
}