// Default theme definitions

import { RenderTheme } from '../../types/renderer';

export const defaultTheme: RenderTheme = {
  colors: {
    primary: '#007acc',
    secondary: '#0066a8',
    success: '#28a745',
    warning: '#ffc107',
    error: '#dc3545',
    background: '#ffffff',
    foreground: '#333333',
    border: '#cccccc',
    text: '#333333'
  },
  fonts: {
    primary: 'Arial, sans-serif',
    secondary: 'Helvetica, sans-serif',
    monospace: 'Monaco, Consolas, monospace'
  },
  sizes: {
    small: 10,
    medium: 12,
    large: 16
  },
  defaults: {
    resource: {
      fill: '#ffffff',
      stroke: '#cccccc',
      strokeWidth: 1,
      fontSize: 12,
      fontFamily: 'Arial, sans-serif'
    },
    connection: {
      stroke: '#666666',
      strokeWidth: 1,
      fontSize: 10,
      fontFamily: 'Arial, sans-serif'
    },
    label: {
      fontSize: 12,
      fontFamily: 'Arial, sans-serif',
      fill: '#333333'
    }
  }
};

export const awsTheme: RenderTheme = {
  ...defaultTheme,
  colors: {
    ...defaultTheme.colors,
    primary: '#FF9900',
    secondary: '#232F3E',
    background: '#FAFAFA'
  },
  defaults: {
    ...defaultTheme.defaults,
    resource: {
      ...defaultTheme.defaults.resource,
      fill: '#ffffff',
      stroke: '#FF9900',
      strokeWidth: 2
    }
  }
};

export const azureTheme: RenderTheme = {
  ...defaultTheme,
  colors: {
    ...defaultTheme.colors,
    primary: '#0078D4',
    secondary: '#106EBE',
    background: '#F8F9FA'
  },
  defaults: {
    ...defaultTheme.defaults,
    resource: {
      ...defaultTheme.defaults.resource,
      fill: '#ffffff',
      stroke: '#0078D4',
      strokeWidth: 2
    }
  }
};

export const gcpTheme: RenderTheme = {
  ...defaultTheme,
  colors: {
    ...defaultTheme.colors,
    primary: '#4285F4',
    secondary: '#34A853',
    background: '#F8F9FA'
  },
  defaults: {
    ...defaultTheme.defaults,
    resource: {
      ...defaultTheme.defaults.resource,
      fill: '#ffffff',
      stroke: '#4285F4',
      strokeWidth: 2
    }
  }
};

export const darkTheme: RenderTheme = {
  colors: {
    primary: '#58a6ff',
    secondary: '#388bfd',
    success: '#3fb950',
    warning: '#d29922',
    error: '#f85149',
    background: '#0d1117',
    foreground: '#f0f6fc',
    border: '#30363d',
    text: '#f0f6fc'
  },
  fonts: {
    primary: 'Arial, sans-serif',
    secondary: 'Helvetica, sans-serif',
    monospace: 'Monaco, Consolas, monospace'
  },
  sizes: {
    small: 10,
    medium: 12,
    large: 16
  },
  defaults: {
    resource: {
      fill: '#21262d',
      stroke: '#30363d',
      strokeWidth: 1,
      fontSize: 12,
      fontFamily: 'Arial, sans-serif'
    },
    connection: {
      stroke: '#7d8590',
      strokeWidth: 1,
      fontSize: 10,
      fontFamily: 'Arial, sans-serif'
    },
    label: {
      fontSize: 12,
      fontFamily: 'Arial, sans-serif',
      fill: '#f0f6fc'
    }
  }
};

export const themes = {
  default: defaultTheme,
  aws: awsTheme,
  azure: azureTheme,
  gcp: gcpTheme,
  dark: darkTheme
};

export type ThemeName = keyof typeof themes;
