"""障害物回避エッジルーティング

レイアウト確定後のノード配置を入力に、各エッジが他ノードの矩形を
貫通しないように waypoints(中継点)を計算する。

アルゴリズム:
    1. 各エッジの両端で box の進入面(top/right/bottom/left)を決定
    2. L字経路(2セグメント)を2パターン試す
    3. ダメなら Z字経路(3セグメント)を複数オフセットで試す
    4. すべて失敗すれば waypoints=[] (直線にフォールバック)

外部の障害物との交差判定のみ行い、エッジ同士の交差は許容する。
"""
from typing import List, Dict, Tuple, Protocol


class RouteNode(Protocol):
    """ルーティング計算用のノードプロトコル"""
    node_id: str
    x: int
    y: int
    width: int
    height: int


class RouteEdge(Protocol):
    """ルーティング計算用のエッジプロトコル"""
    from_node_id: str
    to_node_id: str


# 進入辺の方向
_SIDES = ('top', 'right', 'bottom', 'left')


def _pick_side(rect: Tuple[int, int, int, int], target_cx: float, target_cy: float) -> str:
    """rect の中心から target に向かう方向で進入辺を選ぶ"""
    rx, ry, rw, rh = rect
    cx = rx + rw / 2
    cy = ry + rh / 2
    dx = target_cx - cx
    dy = target_cy - cy
    if abs(dx) >= abs(dy):
        return 'right' if dx > 0 else 'left'
    return 'bottom' if dy > 0 else 'top'


def _port_point(rect: Tuple[int, int, int, int], side: str) -> Tuple[int, int]:
    """進入辺の中点座標"""
    rx, ry, rw, rh = rect
    if side == 'top':
        return (rx + rw // 2, ry)
    if side == 'bottom':
        return (rx + rw // 2, ry + rh)
    if side == 'left':
        return (rx, ry + rh // 2)
    return (rx + rw, ry + rh // 2)  # right


def _segments_from_points(points: List[Tuple[int, int]]) -> List[Tuple[int, int, int, int]]:
    """点列を線分列に変換"""
    return [
        (points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
        for i in range(len(points) - 1)
    ]


def _segment_intersects_rect(
    x1: int, y1: int, x2: int, y2: int,
    rx: int, ry: int, rw: int, rh: int,
    padding: int
) -> bool:
    """軸並行(水平/垂直)線分と矩形の交差判定。

    waypoints は orthogonal なので segment は必ず水平 or 垂直。
    """
    pad_left = rx - padding
    pad_right = rx + rw + padding
    pad_top = ry - padding
    pad_bottom = ry + rh + padding

    if y1 == y2:  # 水平セグメント
        if y1 < pad_top or y1 > pad_bottom:
            return False
        seg_min_x = min(x1, x2)
        seg_max_x = max(x1, x2)
        # 線分と矩形の x 範囲が重なる(端点接触は除く)
        return seg_min_x < pad_right and seg_max_x > pad_left
    if x1 == x2:  # 垂直セグメント
        if x1 < pad_left or x1 > pad_right:
            return False
        seg_min_y = min(y1, y2)
        seg_max_y = max(y1, y2)
        return seg_min_y < pad_bottom and seg_max_y > pad_top
    # 非軸並行は想定外。安全側で False
    return False


def _path_clear(
    path: List[Tuple[int, int]],
    obstacles: List[Tuple[int, int, int, int]],
    padding: int
) -> bool:
    """経路がすべての障害物を回避できているか"""
    for seg in _segments_from_points(path):
        x1, y1, x2, y2 = seg
        for obs in obstacles:
            if _segment_intersects_rect(x1, y1, x2, y2, *obs, padding=padding):
                return False
    return True


def _try_l_paths(
    src_port: Tuple[int, int],
    dst_port: Tuple[int, int],
    src_side: str,
    dst_side: str,
    obstacles: List[Tuple[int, int, int, int]],
    padding: int
) -> List[Tuple[int, int]] | None:
    """L字経路を2パターン試す"""
    sx, sy = src_port
    dx, dy = dst_port
    # 水平先行 → 垂直
    candidate_a = [(sx, sy), (dx, sy), (dx, dy)]
    # 垂直先行 → 水平
    candidate_b = [(sx, sy), (sx, dy), (dx, dy)]

    # 出口方向と整合する候補を優先(top/bottomから出るなら垂直先行が自然)
    if src_side in ('top', 'bottom'):
        candidates = [candidate_b, candidate_a]
    else:
        candidates = [candidate_a, candidate_b]

    for path in candidates:
        if _path_clear(path, obstacles, padding):
            return path[1:-1]  # 中間点のみ waypoints として返す
    return None


def _try_z_paths(
    src_port: Tuple[int, int],
    dst_port: Tuple[int, int],
    src_side: str,
    obstacles: List[Tuple[int, int, int, int]],
    padding: int
) -> List[Tuple[int, int]] | None:
    """Z字経路を複数オフセットで試す"""
    sx, sy = src_port
    dx, dy = dst_port
    horizontal_first = src_side in ('left', 'right')

    # 中継位置(垂直/水平方向)を sport〜dport の間で複数試す
    offsets = [0.5, 0.3, 0.7, 0.15, 0.85]
    for ratio in offsets:
        if horizontal_first:
            mid_x = int(sx + (dx - sx) * ratio)
            path = [(sx, sy), (mid_x, sy), (mid_x, dy), (dx, dy)]
        else:
            mid_y = int(sy + (dy - sy) * ratio)
            path = [(sx, sy), (sx, mid_y), (dx, mid_y), (dx, dy)]
        if _path_clear(path, obstacles, padding):
            return path[1:-1]
    return None


class EdgeRouter:
    """エッジ経路計算"""

    @staticmethod
    def route(
        nodes: List[RouteNode],
        edges: List[RouteEdge],
        padding: int = 12
    ) -> Dict[Tuple[str, str], List[Tuple[int, int]]]:
        """各エッジの waypoints を返す。

        Args:
            nodes: 配置済みノード
            edges: ルーティング対象エッジ
            padding: 障害物との余白(px)

        Returns:
            (from_node_id, to_node_id) → waypoints のマップ。
            waypoints は中間点のみ(始点・終点は含まない)。
            経路が見つからない場合は空リスト(直線フォールバック)。
        """
        rect_map: Dict[str, Tuple[int, int, int, int]] = {
            n.node_id: (n.x, n.y, n.width, n.height) for n in nodes
        }

        result: Dict[Tuple[str, str], List[Tuple[int, int]]] = {}
        for edge in edges:
            src_id = edge.from_node_id
            dst_id = edge.to_node_id
            if src_id not in rect_map or dst_id not in rect_map:
                result[(src_id, dst_id)] = []
                continue

            src_rect = rect_map[src_id]
            dst_rect = rect_map[dst_id]
            dst_cx = dst_rect[0] + dst_rect[2] / 2
            dst_cy = dst_rect[1] + dst_rect[3] / 2
            src_cx = src_rect[0] + src_rect[2] / 2
            src_cy = src_rect[1] + src_rect[3] / 2

            src_side = _pick_side(src_rect, dst_cx, dst_cy)
            dst_side = _pick_side(dst_rect, src_cx, src_cy)
            src_port = _port_point(src_rect, src_side)
            dst_port = _port_point(dst_rect, dst_side)

            # 自分と相手を除外した障害物
            obstacles = [
                r for nid, r in rect_map.items() if nid != src_id and nid != dst_id
            ]

            waypoints = _try_l_paths(src_port, dst_port, src_side, dst_side, obstacles, padding)
            if waypoints is None:
                waypoints = _try_z_paths(src_port, dst_port, src_side, obstacles, padding)
            if waypoints is None:
                waypoints = []  # フォールバック: 直線

            result[(src_id, dst_id)] = waypoints
        return result
