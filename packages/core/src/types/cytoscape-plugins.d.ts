// Cytoscape.js プラグインの型定義

declare module 'cytoscape-dagre' {
  import { Extension } from 'cytoscape';
  const dagrePlugin: Extension;
  export = dagrePlugin;
}

declare module 'cytoscape-cose-bilkent' {
  import { Extension } from 'cytoscape';
  const coseBilkentPlugin: Extension;
  export = coseBilkentPlugin;
}