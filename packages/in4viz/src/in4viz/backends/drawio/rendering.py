from typing import List, Tuple, Optional
from ...core.models import LineType, Cardinality


class DrawioEdge:
    """draw.io用のエッジ（関係線）クラス"""

    def __init__(self, from_node_id: str, to_node_id: str, line_type: LineType = LineType.STRAIGHT, cardinality: Cardinality = None):
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.line_type = line_type
        self.cardinality = cardinality if cardinality is not None else Cardinality()
        self.waypoints: List[Tuple[int, int]] = []
        # ルーター由来のポート位置(drawio は exitX/Y, entryX/Y のセル内0〜1座標で指定)
        self.exit_x: Optional[float] = None
        self.exit_y: Optional[float] = None
        self.entry_x: Optional[float] = None
        self.entry_y: Optional[float] = None
        self.route_status: str = "ok"
        self.route_reason: str = ""

    def _map_cardinality_to_arrow(self, cardinality_str: str) -> str:
        """
        カーディナリティ文字列をdraw.ioの矢印スタイルにマッピング

        Args:
            cardinality_str: カーディナリティ文字列（"1", "0..1", "*", etc.）

        Returns:
            draw.io矢印スタイル（ERone, ERmany, ERzeroToOne, etc.）
        """
        if cardinality_str in ["*", "1..*", "0..*", "0...*", "1...*", "many"]:
            return "ERmany"
        elif cardinality_str == "0..1":
            return "ERzeroToOne"
        elif cardinality_str == "0":
            return "ERzeroToOne"
        elif cardinality_str == "1" or not cardinality_str:
            return "ERone"
        else:
            return "ERone"

    def _build_edge_style(self) -> str:
        """
        エッジのスタイル文字列を構築

        Returns:
            draw.io用のスタイル文字列
        """
        style_parts = []

        # LineTypeに応じたedgeStyle
        # ORTHOGONAL は in4viz 側で計算した waypoints を mxGeometry/Array に渡して
        # SVG と同じ経路で描画する。drawio ネイティブの orthogonalEdgeStyle は使わない。
        if self.line_type == LineType.ORTHOGONAL:
            style_parts.append("edgeStyle=none")
            style_parts.append("rounded=0")
            # ポート分配済みなら exitX/Y, entryX/Y を指定して SVG と同じ位置で接続
            if self.exit_x is not None:
                style_parts.append(f"exitX={self.exit_x:.4f}")
                style_parts.append(f"exitY={self.exit_y:.4f}")
                style_parts.append("exitDx=0")
                style_parts.append("exitDy=0")
            if self.entry_x is not None:
                style_parts.append(f"entryX={self.entry_x:.4f}")
                style_parts.append(f"entryY={self.entry_y:.4f}")
                style_parts.append("entryDx=0")
                style_parts.append("entryDy=0")
        elif self.line_type == LineType.SPLINE:
            style_parts.append("edgeStyle=elbowEdgeStyle")
            style_parts.append("curved=1")
            style_parts.append("rounded=1")
        # STRAIGHTの場合はedgeStyleを省略

        # 基本スタイル
        style_parts.append("html=1")

        # カーディナリティから矢印スタイルを決定
        if self.cardinality:
            if self.cardinality.from_side:
                start_arrow = self._map_cardinality_to_arrow(self.cardinality.from_side)
                style_parts.append(f"startArrow={start_arrow}")

            if self.cardinality.to_side:
                end_arrow = self._map_cardinality_to_arrow(self.cardinality.to_side)
                style_parts.append(f"endArrow={end_arrow}")

        return ";".join(style_parts) + ";"

    def render_mxcell_data(self, from_cell_id: str, to_cell_id: str, edge_cell_id: str) -> dict:
        """
        エッジのmxCellデータを生成

        Args:
            from_cell_id: 開始ノードのmxCell ID
            to_cell_id: 終了ノードのmxCell ID
            edge_cell_id: エッジ自身のmxCell ID

        Returns:
            mxCellデータ辞書
        """
        from .generator import DrawioGenerator

        style = self._build_edge_style()
        return DrawioGenerator.create_edge_cell(
            cell_id=edge_cell_id,
            from_cell_id=from_cell_id,
            to_cell_id=to_cell_id,
            style=style,
            waypoints=self.waypoints if self.line_type == LineType.ORTHOGONAL else None,
            route_status=self.route_status,
            route_reason=self.route_reason
        )
