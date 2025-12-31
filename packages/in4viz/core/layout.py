"""レイアウトアルゴリズムの共通実装"""
from typing import List, Dict, Tuple, Protocol


class LayoutNode(Protocol):
    """レイアウト計算用のノードプロトコル"""
    node_id: str
    x: int
    y: int
    width: int
    height: int


class LayoutEdge(Protocol):
    """レイアウト計算用のエッジプロトコル"""
    from_node_id: str
    to_node_id: str


class LayoutEngine:
    """レイアウトエンジン - バックエンド非依存のレイアウトアルゴリズム"""

    @staticmethod
    def build_hierarchy(nodes: List[LayoutNode], edges: List[LayoutEdge]) -> Dict[int, List[str]]:
        """
        エッジの関係から階層構造を構築（FK関係では参照元を参照先の近くに配置）

        Args:
            nodes: レイアウト対象のノードリスト
            edges: エッジリスト

        Returns:
            階層ごとのノードIDリスト
        """
        # 各ノードの出次数を計算（逆方向）
        out_degree = {node.node_id: 0 for node in nodes}
        for edge in edges:
            out_degree[edge.from_node_id] += 1

        # 逆トポロジカルソートで階層を決定
        hierarchy = {}
        remaining_nodes = set(node.node_id for node in nodes)
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
                for edge in edges:
                    if edge.to_node_id == node_id and edge.from_node_id in remaining_nodes:
                        out_degree[edge.from_node_id] -= 1

        return hierarchy

    @staticmethod
    def get_fk_relationships(edges: List[LayoutEdge]) -> List[Tuple[str, str]]:
        """
        FK関係のペアを取得

        Args:
            edges: エッジリスト

        Returns:
            (from_node_id, to_node_id) のタプルリスト
        """
        fk_pairs = []
        for edge in edges:
            fk_pairs.append((edge.from_node_id, edge.to_node_id))
        return fk_pairs

    @staticmethod
    def arrange_by_hierarchy(
        nodes: List[LayoutNode],
        hierarchy: Dict[int, List[str]],
        fk_pairs: List[Tuple[str, str]],
        margin_x: int = 50,
        margin_y: int = 50,
        level_width: int = 350
    ) -> Tuple[int, int]:
        """
        階層に基づいてノードを再配置（FK関係のあるノードを隣接配置）

        Args:
            nodes: レイアウト対象のノードリスト
            hierarchy: 階層構造
            fk_pairs: FK関係のペア
            margin_x: 横マージン
            margin_y: 縦マージン
            level_width: レベル間の横間隔

        Returns:
            (max_width, max_height) - 必要なキャンバスサイズ
        """
        # ノードIDからノードを取得するための辞書を作成
        node_map = {node.node_id: node for node in nodes}

        max_width = 0
        max_height = 0

        # 配置済みノードを追跡
        placed_nodes = set()

        # 全体でのY座標を管理
        global_y = margin_y

        for level, node_ids in hierarchy.items():
            x = margin_x + level * level_width

            for node_id in node_ids:
                if node_id in placed_nodes:
                    continue

                node = node_map.get(node_id)
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
                            adjacent_node = node_map.get(adjacent_node_id)
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

        return new_width, new_height

    @staticmethod
    def adjust_canvas_size_for_current_layout(
        nodes: List[LayoutNode],
        margin: int = 50
    ) -> Tuple[int, int]:
        """
        現在のレイアウトに基づいてキャンバスサイズを計算

        Args:
            nodes: レイアウト済みのノードリスト
            margin: マージン

        Returns:
            (width, height) - 必要なキャンバスサイズ
        """
        if not nodes:
            return 800, 600  # デフォルトサイズ

        max_width = 0
        max_height = 0

        for node in nodes:
            node_right = node.x + node.width
            node_bottom = node.y + node.height
            max_width = max(max_width, node_right)
            max_height = max(max_height, node_bottom)

        new_width = max_width + margin
        new_height = max_height + margin
        return new_width, new_height
