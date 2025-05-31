// in4viz React Components
// React wrapper for the core library

export { In4vizDiagram } from './components/In4vizDiagram'
export { useIn4viz } from './hooks/useIn4viz'

// Re-export core types for convenience
export type {
  Infrastructure,
  Resource,
  Connection,
  LayoutOptions,
} from '@infodb/in4viz'
