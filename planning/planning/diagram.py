from typing import List, Dict, Any, Tuple
from .stencil import Stencil, TableStencil


class Node:
    def __init__(self, node_id: str, stencil: Stencil, data: Dict[str, Any], x: int = 0, y: int = 0):
        self.node_id = node_id
        self.stencil = stencil
        self.data = data
        self.x = x
        self.y = y
        self.width = stencil.width
        self.height = self._calculate_height()
    
    def _calculate_height(self) -> int:
        if hasattr(self.stencil, 'calculate_height'):
            return self.stencil.calculate_height(self.data)
        return self.stencil.height
    
    def _calculate_width(self) -> int:
        if hasattr(self.stencil, 'get_width'):
            return self.stencil.get_width(self.data)
        return self.stencil.width
    
    def render(self) -> str:
        return self.stencil.render(self.data, self.x, self.y)


class ERDiagram:
    def __init__(self, canvas_width: int = 1200, canvas_height: int = 800):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.nodes: List[Node] = []
        self.next_position = [50, 50]
        self.column_width = 450
        self.row_height = 200
        
    def add_table(self, table_name: str, columns: List[Dict[str, Any]], 
                  logical_name: str = None, table_id: str = None, x: int = None, y: int = None) -> str:
        if table_id is None:
            table_id = f"table_{len(self.nodes)}"
        
        stencil = TableStencil()
        data = {
            'table_name': table_name,
            'logical_name': logical_name,
            'columns': columns
        }
        
        # 幅を事前計算
        temp_node = Node(table_id, stencil, data, 0, 0)
        node_width = temp_node._calculate_width()
        
        auto_positioned = (x is None or y is None)
        if auto_positioned:
            x, y = self._get_next_position()
            # 幅チェックして改行判定
            if x + node_width > self.canvas_width - 50:
                x = 50
                y += self.row_height
                self.next_position = [x, y]
        
        node = Node(table_id, stencil, data, x, y)
        node.width = node_width
        self.nodes.append(node)
        
        # 次の配置位置を更新（自動配置の場合のみ）
        if auto_positioned:
            self._update_next_position(node_width)
        
        return table_id
    
    def _get_next_position(self) -> Tuple[int, int]:
        x, y = self.next_position
        
        # 前回のノードの幅を考慮
        if self.nodes and x + 400 > self.canvas_width - 50:  # 仮の幅でチェック
            x = 50
            y += self.row_height
        
        self.next_position = [x, y]
        
        return x, y
    
    def _update_next_position(self, node_width: int):
        self.next_position[0] += node_width + 50  # ノード間のマージン
    
    def get_node(self, node_id: str) -> Node:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def set_node_position(self, node_id: str, x: int, y: int):
        node = self.get_node(node_id)
        if node:
            node.x = x
            node.y = y
    
    def render_svg(self) -> str:
        svg_parts = []
        
        svg_parts.append(f'<svg width="{self.canvas_width}" height="{self.canvas_height}" '
                        f'xmlns="http://www.w3.org/2000/svg">')
        
        svg_parts.append('<defs>')
        svg_parts.append('<style>')
        svg_parts.append('text { font-family: Arial, sans-serif; }')
        svg_parts.append('</style>')
        svg_parts.append('</defs>')
        
        svg_parts.append(f'<rect width="{self.canvas_width}" height="{self.canvas_height}" '
                        f'fill="#f8f9fa" stroke="none"/>')
        
        for node in self.nodes:
            svg_parts.append(node.render())
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def save_svg(self, filename: str):
        svg_content = self.render_svg()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)