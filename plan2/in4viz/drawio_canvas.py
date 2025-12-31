from typing import List, Dict, Any
import importlib.util
from pathlib import Path

# plan1のmodels.pyを直接インポート
models_path = Path(__file__).parent.parent.parent / 'planning' / 'in4viz' / 'models.py'
spec = importlib.util.spec_from_file_location("planning_models", models_path)
planning_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planning_models)

LineType = planning_models.LineType


class DrawioCanvas:
    """draw.io用のキャンバス管理クラス"""

    def __init__(self, default_line_type: LineType = LineType.STRAIGHT):
        self.width = 1200
        self.height = 800
        self.default_line_type = default_line_type
        self.nodes: List['DrawioNode'] = []
        self.edges: List = []  # DrawioEdgeのリスト
        self.next_position = [50, 50]
        self.column_width = 450
        self.row_height = 200
        self.next_cell_id = 2  # mxCell IDの自動採番（0, 1は予約済み）

    def get_next_cell_id(self) -> str:
        """次のmxCell IDを取得"""
        cell_id = str(self.next_cell_id)
        self.next_cell_id += 1
        return cell_id

    def add_node(self, node: 'DrawioNode'):
        """ノードを追加"""
        self.nodes.append(node)

    def get_node(self, node_id: str) -> 'DrawioNode':
        """ノードIDからノードを取得"""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None


class DrawioNode:
    """draw.io用のノード（テーブル）を表すクラス"""

    def __init__(self, node_id: str, stencil, data: Dict[str, Any], x: int, y: int, cell_id: str):
        self.node_id = node_id  # テーブル物理名
        self.cell_id = cell_id  # mxCell ID
        self.stencil = stencil
        self.data = data
        self.x = x
        self.y = y
        self.width = self._calculate_width()
        self.height = self._calculate_height()

    def _calculate_height(self) -> int:
        """高さを計算"""
        if hasattr(self.stencil, 'calculate_height'):
            return self.stencil.calculate_height(self.data)
        return 100

    def _calculate_width(self) -> int:
        """幅を計算"""
        if hasattr(self.stencil, 'get_width'):
            return self.stencil.get_width(self.data)
        return 200
