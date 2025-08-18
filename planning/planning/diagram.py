from typing import List, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from .stencil import Stencil, TableStencil


class LineType(Enum):
    STRAIGHT = "straight"
    CRANK = "crank"
    SPLINE = "spline"

@dataclass
class Cardinality:
    from_side: str = "1"  # "1", "0..1", "1..*", "0..*"
    to_side: str = "1"    # "1", "0..1", "1..*", "0..*"


@dataclass
class Edge:
    from_node_id: str
    to_node_id: str
    line_type: LineType = LineType.STRAIGHT
    cardinality: Cardinality = None
    
    def __post_init__(self):
        if self.cardinality is None:
            self.cardinality = Cardinality()

    def render(self, from_x: int, from_y: int, to_x: int, to_y: int, line_type: LineType, from_edge: str = None, to_edge: str = None) -> str:
        def get_perpendicular_point(x, y, edge_type, length):
            """接地面（外枠の辺）に対して垂直に伸ばした点を計算"""
            if edge_type == 'left':      # 左辺から左方向に垂直
                return x - length, y
            elif edge_type == 'right':   # 右辺から右方向に垂直
                return x + length, y
            elif edge_type == 'top':     # 上辺から上方向に垂直
                return x, y - length
            elif edge_type == 'bottom':  # 下辺から下方向に垂直
                return x, y + length
            else:
                return x, y

        def render_ie_notation_symbol(x: int, y: int, cardinality: str, edge_type: str) -> tuple:
            """IE記法でカーディナリティ記号を描画し、新しい接続点を返す"""
            symbols = []
            new_x, new_y = x, y  # デフォルトは元の接続点
            
            if cardinality == "0":
                # "0"の場合は円のみ（円の外から線を出す）
                if edge_type == 'left':
                    circle_x = x - 8
                    symbols.append(f'<circle cx="{circle_x}" cy="{y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    new_x = circle_x - 3  # 円の左端から線を出す
                elif edge_type == 'right':
                    circle_x = x + 8
                    symbols.append(f'<circle cx="{circle_x}" cy="{y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    new_x = circle_x + 3  # 円の右端から線を出す
                elif edge_type == 'top':
                    circle_y = y - 8
                    symbols.append(f'<circle cx="{x}" cy="{circle_y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    new_y = circle_y - 3  # 円の上端から線を出す
                elif edge_type == 'bottom':
                    circle_y = y + 8
                    symbols.append(f'<circle cx="{x}" cy="{circle_y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    new_y = circle_y + 3  # 円の下端から線を出す
            
            elif not cardinality or cardinality == "1":
                # "1"の場合はプラス記号（先端から線を出す）
                if edge_type == 'left':
                    cross_x = x - 8
                    symbols.append(f'<line x1="{cross_x}" y1="{y-4}" x2="{cross_x}" y2="{y+4}" stroke="black" stroke-width="2"/>')
                    symbols.append(f'<line x1="{cross_x-4}" y1="{y}" x2="{cross_x+4}" y2="{y}" stroke="black" stroke-width="2"/>')
                    new_x = cross_x - 4  # 左端から線を出す
                elif edge_type == 'right':
                    cross_x = x + 8
                    symbols.append(f'<line x1="{cross_x}" y1="{y-4}" x2="{cross_x}" y2="{y+4}" stroke="black" stroke-width="2"/>')
                    symbols.append(f'<line x1="{cross_x-4}" y1="{y}" x2="{cross_x+4}" y2="{y}" stroke="black" stroke-width="2"/>')
                    new_x = cross_x + 4  # 右端から線を出す
                elif edge_type == 'top':
                    cross_y = y - 8
                    symbols.append(f'<line x1="{x}" y1="{cross_y-4}" x2="{x}" y2="{cross_y+4}" stroke="black" stroke-width="2"/>')
                    symbols.append(f'<line x1="{x-4}" y1="{cross_y}" x2="{x+4}" y2="{cross_y}" stroke="black" stroke-width="2"/>')
                    new_y = cross_y - 4  # 上端から線を出す
                elif edge_type == 'bottom':
                    cross_y = y + 8
                    symbols.append(f'<line x1="{x}" y1="{cross_y-4}" x2="{x}" y2="{cross_y+4}" stroke="black" stroke-width="2"/>')
                    symbols.append(f'<line x1="{x-4}" y1="{cross_y}" x2="{x+4}" y2="{cross_y}" stroke="black" stroke-width="2"/>')
                    new_y = cross_y + 4  # 下端から線を出す
            
            elif cardinality == "0..1":
                # "0..1"の場合は円 + 縦線
                if edge_type == 'left':
                    circle_x = x - 8
                    line_x = x - 15
                    symbols.append(f'<circle cx="{circle_x}" cy="{y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{line_x}" y1="{y-4}" x2="{line_x}" y2="{y+4}" stroke="black" stroke-width="2"/>')
                    new_x = line_x
                elif edge_type == 'right':
                    circle_x = x + 8
                    line_x = x + 15
                    symbols.append(f'<circle cx="{circle_x}" cy="{y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{line_x}" y1="{y-4}" x2="{line_x}" y2="{y+4}" stroke="black" stroke-width="2"/>')
                    new_x = line_x
                elif edge_type == 'top':
                    circle_y = y - 8
                    line_y = y - 15
                    symbols.append(f'<circle cx="{x}" cy="{circle_y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x-4}" y1="{line_y}" x2="{x+4}" y2="{line_y}" stroke="black" stroke-width="2"/>')
                    new_y = line_y
                elif edge_type == 'bottom':
                    circle_y = y + 8
                    line_y = y + 15
                    symbols.append(f'<circle cx="{x}" cy="{circle_y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x-4}" y1="{line_y}" x2="{x+4}" y2="{line_y}" stroke="black" stroke-width="2"/>')
                    new_y = line_y
            
            elif cardinality in ["*", "1..*", "0..*", "0...*", "1...*", "many"]:
                # 多数の場合は鳥の足のみ（枠との間にスペースを設ける）
                if edge_type == 'left':
                    crow_x = x - 12  # テーブル枠外により遠く配置（スペース確保）
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x+8}" y2="{y-5}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x+8}" y2="{y+5}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x+8}" y2="{y}" stroke="black" stroke-width="1"/>')
                    new_x = crow_x
                elif edge_type == 'right':
                    crow_x = x + 12  # テーブル枠外により遠く配置（スペース確保）
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x-8}" y2="{y-5}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x-8}" y2="{y+5}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x-8}" y2="{y}" stroke="black" stroke-width="1"/>')
                    new_x = crow_x
                elif edge_type == 'top':
                    crow_y = y - 12  # テーブル枠外により遠く配置（スペース確保）
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x-5}" y2="{crow_y+8}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x+5}" y2="{crow_y+8}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x}" y2="{crow_y+8}" stroke="black" stroke-width="1"/>')
                    new_y = crow_y
                elif edge_type == 'bottom':
                    crow_y = y + 12  # テーブル枠外により遠く配置（スペース確保）
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x-5}" y2="{crow_y-8}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x+5}" y2="{crow_y-8}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x}" y2="{crow_y-8}" stroke="black" stroke-width="1"/>')
                    new_y = crow_y
            
            return '\n'.join(symbols), new_x, new_y

        # IE記号の位置計算と描画
        from_symbols = ""
        to_symbols = ""
        final_from_x, final_from_y = from_x, from_y
        final_to_x, final_to_y = to_x, to_y

        if self.cardinality:
            # from側のカーディナリティ記号
            if self.cardinality.from_side:
                from_symbols, final_from_x, final_from_y = render_ie_notation_symbol(from_x, from_y, self.cardinality.from_side, from_edge)
            
            # to側のカーディナリティ記号
            if self.cardinality.to_side:
                to_symbols, final_to_x, final_to_y = render_ie_notation_symbol(to_x, to_y, self.cardinality.to_side, to_edge)

        svg_parts = []
        
        if line_type == LineType.STRAIGHT:
            # 直線はIE記号の最終位置まで接続
            svg_parts.append(f'<line x1="{final_from_x}" y1="{final_from_y}" x2="{final_to_x}" y2="{final_to_y}" stroke="black" stroke-width="1"/>')

        elif line_type == LineType.CRANK:
            # 接点から接地面に垂直に伸ばした点を経由するクランク
            from_perp_x, from_perp_y = get_perpendicular_point(final_from_x, final_from_y, from_edge, 30)
            to_perp_x, to_perp_y = get_perpendicular_point(final_to_x, final_to_y, to_edge, 30)

            # シンプルなクランクロジック（Z字回避）
            if from_edge in ['top', 'bottom'] and to_edge in ['top', 'bottom']:
                # 上下辺同士 → from側Y座標で水平線
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = final_to_x, from_perp_y
            elif from_edge in ['left', 'right'] and to_edge in ['left', 'right']:
                # 左右辺同士 → from側X座標で垂直線
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = from_perp_x, final_to_y
            elif from_edge in ['top', 'bottom'] and to_edge in ['left', 'right']:
                # 上下→左右 → 水平線
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = to_perp_x, from_perp_y
            elif from_edge in ['left', 'right'] and to_edge in ['top', 'bottom']:
                # 左右→上下 → 垂直線
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = from_perp_x, to_perp_y
            else:
                # フォールバック
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = to_perp_x, to_perp_y

            # クランクパス: 接点→垂直伸ばし→中央線→接点
            if from_edge in ['top', 'bottom'] and to_edge in ['top', 'bottom']:
                # 上下辺同士: from側Y座標の水平線
                svg_parts.append(f'<path d="M {final_from_x} {final_from_y} L {from_perp_x} {from_perp_y} L {mid2_x} {mid2_y} L {final_to_x} {final_to_y}" stroke="black" stroke-width="1" fill="none"/>')
            elif from_edge in ['left', 'right'] and to_edge in ['left', 'right']:
                # 左右辺同士: from側X座標の垂直線
                svg_parts.append(f'<path d="M {final_from_x} {final_from_y} L {from_perp_x} {from_perp_y} L {mid2_x} {mid2_y} L {final_to_x} {final_to_y}" stroke="black" stroke-width="1" fill="none"/>')
            else:
                # 異なる辺同士: 6点パス
                svg_parts.append(f'<path d="M {final_from_x} {final_from_y} L {from_perp_x} {from_perp_y} L {mid1_x} {mid1_y} L {mid2_x} {mid2_y} L {to_perp_x} {to_perp_y} L {final_to_x} {final_to_y}" stroke="black" stroke-width="1" fill="none"/>')

        elif line_type == LineType.SPLINE:
            # 接点から接地面に垂直に伸ばした点を制御点とするスプライン
            from_perp_x, from_perp_y = get_perpendicular_point(final_from_x, final_from_y, from_edge, 50)
            to_perp_x, to_perp_y = get_perpendicular_point(final_to_x, final_to_y, to_edge, 50)

            svg_parts.append(f'<path d="M {final_from_x} {final_from_y} C {from_perp_x} {from_perp_y} {to_perp_x} {to_perp_y} {final_to_x} {final_to_y}" stroke="black" stroke-width="1" fill="none"/>')

        else:
            svg_parts.append(f'<line x1="{final_from_x}" y1="{final_from_y}" x2="{final_to_x}" y2="{final_to_y}" stroke="black" stroke-width="1"/>')

        # IE記号を追加
        if from_symbols:
            svg_parts.append(from_symbols)
        if to_symbols:
            svg_parts.append(to_symbols)

        return '\n'.join(svg_parts)


class Canvas:
    def __init__(self, width: int = 1200, height: int = 800, default_line_type: LineType = LineType.STRAIGHT):
        self.width = width
        self.height = height
        self.default_line_type = default_line_type
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.next_position = [50, 50]
        self.column_width = 450
        self.row_height = 200

    def add_node(self, node: 'Node'):
        self.nodes.append(node)

    def add_edge(self, from_node_id: str, to_node_id: str, line_type: LineType = None):
        if line_type is None:
            line_type = self.default_line_type
        edge = Edge(from_node_id, to_node_id, line_type)
        self.edges.append(edge)

    def get_node(self, node_id: str) -> 'Node':
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def _get_node_edge_points(self, from_node: 'Node', to_node: 'Node') -> Tuple[int, int, int, int, str, str]:
        """ステンシル中央に向かって線を引き、外枠で止めるポイントを計算（元の正確な実装）"""
        def get_line_rect_intersection(center_x, center_y, target_x, target_y, rect_x, rect_y, rect_w, rect_h):
            """中央から目標点への線が外枠と交わる最適な点を計算"""
            dx = target_x - center_x
            dy = target_y - center_y

            if dx == 0 and dy == 0:
                return center_x, center_y, 'center'

            # 主方向を判定して適切な辺を選択
            if abs(dx) > abs(dy):
                # 水平方向が主
                if dx > 0:
                    # 右向き → 右辺から出る
                    x = rect_x + rect_w
                    t = (x - center_x) / dx
                    y = center_y + t * dy
                    if rect_y <= y <= rect_y + rect_h:
                        return x, y, 'right'
                else:
                    # 左向き → 左辺から出る
                    x = rect_x
                    t = (x - center_x) / dx
                    y = center_y + t * dy
                    if rect_y <= y <= rect_y + rect_h:
                        return x, y, 'left'
            else:
                # 垂直方向が主
                if dy > 0:
                    # 下向き → 下辺から出る
                    y = rect_y + rect_h
                    t = (y - center_y) / dy
                    x = center_x + t * dx
                    if rect_x <= x <= rect_x + rect_w:
                        return x, y, 'bottom'
                else:
                    # 上向き → 上辺から出る
                    y = rect_y
                    t = (y - center_y) / dy
                    x = center_x + t * dx
                    if rect_x <= x <= rect_x + rect_w:
                        return x, y, 'top'

            # フォールバック：最近傍辺を強制選択
            edges = [
                (rect_x, center_y, 'left'),  # 左辺
                (rect_x + rect_w, center_y, 'right'),  # 右辺
                (center_x, rect_y, 'top'),  # 上辺
                (center_x, rect_y + rect_h, 'bottom')  # 下辺
            ]

            # 境界内にクリップ
            best_edge = None
            min_dist = float('inf')
            for edge_x, edge_y, edge_name in edges:
                clipped_x = max(rect_x, min(rect_x + rect_w, edge_x))
                clipped_y = max(rect_y, min(rect_y + rect_h, edge_y))
                dist = abs(target_x - clipped_x) + abs(target_y - clipped_y)
                if dist < min_dist:
                    min_dist = dist
                    best_edge = (clipped_x, clipped_y, edge_name)

            return best_edge[0], best_edge[1], best_edge[2]

        from_center_x = from_node.x + from_node.width // 2
        from_center_y = from_node.y + from_node.height // 2
        to_center_x = to_node.x + to_node.width // 2
        to_center_y = to_node.y + to_node.height // 2

        # fromノードの外枠交点（中央に向かう線との交点）
        from_x, from_y, from_edge = get_line_rect_intersection(
            from_center_x, from_center_y, to_center_x, to_center_y,
            from_node.x, from_node.y, from_node.width, from_node.height
        )

        # toノードの外枠交点（中央に向かう線との交点）
        to_x, to_y, to_edge = get_line_rect_intersection(
            to_center_x, to_center_y, from_center_x, from_center_y,
            to_node.x, to_node.y, to_node.width, to_node.height
        )

        return int(from_x), int(from_y), int(to_x), int(to_y), from_edge, to_edge

    def render_edges(self) -> List[str]:
        edge_parts = []
        for edge in self.edges:
            from_node = self.get_node(edge.from_node_id)
            to_node = self.get_node(edge.to_node_id)

            if from_node and to_node:
                from_x, from_y, to_x, to_y, from_edge, to_edge = self._get_node_edge_points(from_node, to_node)
                edge_parts.append(edge.render(from_x, from_y, to_x, to_y, edge.line_type, from_edge, to_edge))

        return edge_parts

    def render_arrow_marker(self) -> str:
        return '''<defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7"
                    refX="10" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="black"/>
            </marker>
        </defs>'''


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


from dataclasses import dataclass

@dataclass
class Column:
    name: str
    logical_name: str
    type: str
    primary_key: bool = False
    nullable: bool = True
    foreign_key: bool = False
    index: bool = False

@dataclass
class Table:
    name: str
    logical_name: str
    columns: List[Column]

class ERDiagram:
    def __init__(self, default_line_type: LineType = LineType.STRAIGHT):
        self.canvas = Canvas(800, 600, default_line_type)  # 初期値は動的調整で上書きされる
        self.nodes = self.canvas.nodes

    def add_table(self, table: Table, x: int = None, y: int = None) -> str:
        table_id = table.name  # 物理テーブル名をIDとして使用

        stencil = TableStencil()
        
        # Column dataclassをdict形式に変換
        columns_data = []
        for col in table.columns:
            columns_data.append({
                'name': col.name,
                'logical_name': col.logical_name,
                'type': col.type,
                'primary_key': col.primary_key,
                'nullable': col.nullable,
                'foreign_key': col.foreign_key,
                'index': col.index
            })
        
        data = {
            'table_name': table.name,
            'logical_name': table.logical_name,
            'columns': columns_data
        }

        # 幅を事前計算
        temp_node = Node(table_id, stencil, data, 0, 0)
        node_width = temp_node._calculate_width()

        auto_positioned = (x is None or y is None)
        if auto_positioned:
            x, y = self._get_next_position()
            # 幅チェックして改行判定
            if x + node_width > self.canvas.width - 50:
                x = 50
                y += self.canvas.row_height
                self.canvas.next_position = [x, y]

        node = Node(table_id, stencil, data, x, y)
        node.width = node_width
        self.canvas.add_node(node)

        # 次の配置位置を更新（自動配置の場合のみ）
        if auto_positioned:
            self._update_next_position(node_width)

        # キャンバスサイズを調整
        self._adjust_canvas_size_for_current_layout()

        return table_id

    def _get_next_position(self) -> Tuple[int, int]:
        x, y = self.canvas.next_position

        # 前回のノードの幅を考慮
        if self.nodes and x + 400 > self.canvas.width - 50:  # 仮の幅でチェック
            x = 50
            y += self.canvas.row_height

        self.canvas.next_position = [x, y]

        return x, y

    def _update_next_position(self, node_width: int):
        self.canvas.next_position[0] += node_width + 50  # ノード間のマージン

    def get_node(self, node_id: str) -> Node:
        return self.canvas.get_node(node_id)

    def set_node_position(self, node_id: str, x: int, y: int):
        node = self.get_node(node_id)
        if node:
            node.x = x
            node.y = y

    def add_edge(self, from_node_id: str, to_node_id: str, line_type: LineType = None, cardinality: Cardinality = None):
        edge = Edge(from_node_id, to_node_id, line_type or self.canvas.default_line_type, cardinality)
        self.canvas.edges.append(edge)
        # エッジ追加後にレイアウトを最適化
        self._optimize_layout_for_edges()

    def _optimize_layout_for_edges(self):
        """エッジを考慮した上から下、左から右のレイアウト最適化"""
        if not self.canvas.edges:
            # エッジがない場合でもキャンバスサイズを調整
            self._adjust_canvas_size_for_current_layout()
            return

        # エッジの関係から階層を構築
        hierarchy = self._build_hierarchy()

        # 階層に基づいて再配置
        self._arrange_by_hierarchy(hierarchy)

    def _adjust_canvas_size_for_current_layout(self):
        """現在のレイアウトに基づいてキャンバスサイズを調整"""
        if not self.nodes:
            return

        margin = 50
        max_width = 0
        max_height = 0

        for node in self.nodes:
            node_right = node.x + node.width
            node_bottom = node.y + node.height
            max_width = max(max_width, node_right)
            max_height = max(max_height, node_bottom)

        new_width = max_width + margin
        new_height = max_height + margin
        self._update_canvas_size(new_width, new_height)

    def _build_hierarchy(self) -> Dict[int, List[str]]:
        """エッジの関係から階層構造を構築（FK関係では参照元を参照先の近くに配置）"""
        # FK関係の場合は逆方向で考える（参照先 -> 参照元）
        # 各ノードの出次数を計算（逆方向）
        out_degree = {node.node_id: 0 for node in self.nodes}
        for edge in self.canvas.edges:
            out_degree[edge.from_node_id] += 1

        # 逆トポロジカルソートで階層を決定
        hierarchy = {}
        remaining_nodes = set(node.node_id for node in self.nodes)
        level = 0

        while remaining_nodes:
            # 出次数0のノード（最終参照先）を現在のレベルに配置
            current_level = []
            for node_id in list(remaining_nodes):
                if out_degree[node_id] == 0:
                    current_level.append(node_id)
                    remaining_nodes.remove(node_id)

            if not current_level:
                # 循環参照がある場合、残りのノードを次のレベルに
                current_level = list(remaining_nodes)
                remaining_nodes.clear()

            hierarchy[level] = current_level
            level += 1

            # 現在のレベルのノードを参照するノードの出次数を減らす
            for node_id in current_level:
                for edge in self.canvas.edges:
                    if edge.to_node_id == node_id and edge.from_node_id in remaining_nodes:
                        out_degree[edge.from_node_id] -= 1

        return hierarchy

    def _arrange_by_hierarchy(self, hierarchy: Dict[int, List[str]]):
        """階層に基づいてノードを再配置（FK関係のあるノードを隣接配置）"""
        margin_x = 50
        margin_y = 50
        level_width = 350  # レベル間の横間隔

        max_width = 0
        max_height = 0

        # FK関係を特定
        fk_pairs = self._get_fk_relationships()

        # 配置済みノードを追跡
        placed_nodes = set()

        # 全体でのY座標を管理
        global_y = margin_y

        for level, node_ids in hierarchy.items():
            x = margin_x + level * level_width

            for node_id in node_ids:
                if node_id in placed_nodes:
                    continue

                node = self.get_node(node_id)
                if node:
                    # 基本配置
                    node.x = x
                    node.y = global_y
                    placed_nodes.add(node_id)

                    # FK関係の相手ノードを隣接配置
                    current_max_height = node.height  # 現在行の最大高さを追跡
                    adjacent_count = 0  # 隣接配置したノード数

                    for from_node, to_node in fk_pairs:
                        adjacent_node_id = None
                        if from_node == node_id:
                            adjacent_node_id = to_node
                        elif to_node == node_id:
                            adjacent_node_id = from_node

                        if adjacent_node_id and adjacent_node_id not in placed_nodes:
                            adjacent_node = self.get_node(adjacent_node_id)
                            if adjacent_node:
                                if adjacent_count == 0:
                                    # 最初の隣接ノードは右隣に配置
                                    adjacent_x = x + node.width + 50
                                    adjacent_y = global_y
                                    current_max_height = max(current_max_height, adjacent_node.height)
                                else:
                                    # 2つ目以降は下に配置
                                    adjacent_x = x
                                    adjacent_y = global_y + current_max_height + margin_y
                                    # global_yを更新して次のノードが重ならないようにする
                                    global_y = adjacent_y
                                    current_max_height = adjacent_node.height

                                adjacent_node.x = adjacent_x
                                adjacent_node.y = adjacent_y
                                placed_nodes.add(adjacent_node_id)
                                adjacent_count += 1

                                # 隣接ノードのサイズも考慮
                                adj_right = adjacent_node.x + adjacent_node.width
                                adj_bottom = adjacent_node.y + adjacent_node.height
                                max_width = max(max_width, adj_right)
                                max_height = max(max_height, adj_bottom)

                    # 現在行の最大高さ分だけY座標を進める
                    global_y += current_max_height + margin_y

                    # 各ノードの右下座標を計算
                    node_right = node.x + node.width
                    node_bottom = node.y + node.height
                    max_width = max(max_width, node_right)
                    max_height = max(max_height, node_bottom)

        # キャンバスサイズを決定（マージンを追加）
        new_width = max_width + margin_x
        new_height = max_height + margin_y

        # キャンバスサイズを更新
        self._update_canvas_size(new_width, new_height)

    def _get_fk_relationships(self) -> List[Tuple[str, str]]:
        """FK関係のペアを取得"""
        fk_pairs = []
        for edge in self.canvas.edges:
            # エッジの方向を確認（from_node -> to_node がFK関係と仮定）
            fk_pairs.append((edge.from_node_id, edge.to_node_id))
        return fk_pairs

    def _update_canvas_size(self, width: int, height: int):
        """キャンバスサイズを更新"""
        self.canvas.width = width
        self.canvas.height = height

    def render_svg(self) -> str:
        svg_parts = []

        svg_parts.append(f'<svg width="{self.canvas.width}" height="{self.canvas.height}" '
                        f'xmlns="http://www.w3.org/2000/svg">')


        svg_parts.append('<style>')
        svg_parts.append('text { font-family: Arial, sans-serif; }')
        svg_parts.append('</style>')

        svg_parts.append(f'<rect width="{self.canvas.width}" height="{self.canvas.height}" '
                        f'fill="#f8f9fa" stroke="none"/>')

        for node in self.nodes:
            svg_parts.append(node.render())

        # エッジの描画
        edge_parts = self.canvas.render_edges()
        svg_parts.extend(edge_parts)

        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def save_svg(self, output):
        """SVGを出力する
        
        Args:
            output: ファイルパス(str)またはファイルライクオブジェクト
        """
        svg_content = self.render_svg()
        
        if isinstance(output, str):
            # ファイルパスの場合
            with open(output, 'w', encoding='utf-8') as f:
                f.write(svg_content)
        else:
            # ストリームオブジェクトの場合
            output.write(svg_content)
