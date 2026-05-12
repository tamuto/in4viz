"""障害物回避エッジルーティング

レイアウト確定後のノード配置を入力に、各エッジが他ノードの矩形を
貫通しないように waypoints(中継点)を計算する。

アルゴリズム:
    1. 各エッジの両端で box の進入面(top/right/bottom/left)を決定
    2. (node, side) ごとにエッジを集めて辺上に等間隔でポート分配
       (相手側の中心位置でソートし、線同士が交差しにくい順に並べる)
    3. L字経路(2セグメント)を2パターン試す
    4. ダメなら Z字経路(3セグメント)を複数オフセットで試す
    5. すべて失敗すれば waypoints=[] (直線にフォールバック)

外部の障害物との交差判定のみ行い、エッジ同士の交差は許容する。
"""
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Protocol


@dataclass
class RouteResult:
    """1エッジ分のルーティング結果"""
    from_point: Tuple[int, int]
    to_point: Tuple[int, int]
    from_side: str  # 'top' | 'right' | 'bottom' | 'left'
    to_side: str
    waypoints: List[Tuple[int, int]] = field(default_factory=list)


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


def _port_at(rect: Tuple[int, int, int, int], side: str, ratio: float) -> Tuple[int, int]:
    """進入辺上の指定比率位置(ratio: 0.0〜1.0)の座標を返す"""
    rx, ry, rw, rh = rect
    if side == 'top':
        return (int(rx + rw * ratio), ry)
    if side == 'bottom':
        return (int(rx + rw * ratio), ry + rh)
    if side == 'left':
        return (rx, int(ry + rh * ratio))
    return (rx + rw, int(ry + rh * ratio))  # right


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


def _side_orient(side: str) -> str:
    """進入辺の向き: 'h' = 水平(left/right) / 'v' = 垂直(top/bottom)"""
    return 'h' if side in ('left', 'right') else 'v'


def _try_l_paths(
    src_port: Tuple[int, int],
    dst_port: Tuple[int, int],
    src_side: str,
    dst_side: str,
    obstacles: List[Tuple[int, int, int, int]],
    padding: int
) -> List[Tuple[int, int]] | None:
    """L字経路。両端の向きが直交している場合のみ綺麗に書ける。

    例: src='right'(水平出口) + dst='top'(垂直入口) → 水平先行L字
    """
    sx, sy = src_port
    dx, dy = dst_port

    if _side_orient(src_side) == 'h':
        # 水平先行 L: (sx, sy) → (dx, sy) → (dx, dy)
        path = [(sx, sy), (dx, sy), (dx, dy)]
    else:
        # 垂直先行 L: (sx, sy) → (sx, dy) → (dx, dy)
        path = [(sx, sy), (sx, dy), (dx, dy)]

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
    """Z字経路を複数オフセットで試す。

    両端の向きが同じ(平行)場合に必須。
    src_side が水平向き(left/right) なら 水平→垂直→水平 の3セグメント、
    垂直向き(top/bottom) なら 垂直→水平→垂直 の3セグメントを生成する。
    """
    sx, sy = src_port
    dx, dy = dst_port
    horizontal_first = _side_orient(src_side) == 'h'

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


def _choose_path(
    src_port: Tuple[int, int],
    dst_port: Tuple[int, int],
    src_side: str,
    dst_side: str,
    obstacles: List[Tuple[int, int, int, int]],
    padding: int
) -> List[Tuple[int, int]]:
    """進入辺の向きに応じて L 字 / Z 字を選択。失敗時は直線にフォールバック。"""
    src_orient = _side_orient(src_side)
    dst_orient = _side_orient(dst_side)

    if src_orient != dst_orient:
        # 両端の向きが直交: L 字優先
        path = _try_l_paths(src_port, dst_port, src_side, dst_side, obstacles, padding)
        if path is not None:
            return path
        # L が障害物にぶつかれば Z にフォールバック
        path = _try_z_paths(src_port, dst_port, src_side, obstacles, padding)
        return path if path is not None else []
    else:
        # 両端の向きが同じ(平行): L だと必ず斜めセグメントが残るので Z 字必須
        path = _try_z_paths(src_port, dst_port, src_side, obstacles, padding)
        return path if path is not None else []


class EdgeRouter:
    """エッジ経路計算"""

    @staticmethod
    def route(
        nodes: List[RouteNode],
        edges: List[RouteEdge],
        padding: int = 12
    ) -> List[RouteResult]:
        """各エッジのルート(始点・終点・進入辺・waypoints)を返す。

        Args:
            nodes: 配置済みノード
            edges: ルーティング対象エッジ
            padding: 障害物との余白(px)

        Returns:
            edges と同じ順序の RouteResult リスト。
            同一ノードペアの並列エッジも個別のポート位置を持つ。
            経路が見つからない場合は waypoints=[] (直線フォールバック)。
        """
        rect_map: Dict[str, Tuple[int, int, int, int]] = {
            n.node_id: (n.x, n.y, n.width, n.height) for n in nodes
        }

        # Pass 1: 各エッジの両端の進入辺(side)を決定し、相手中心位置を記録
        edge_info: List[Dict | None] = []
        for edge in edges:
            src_id = edge.from_node_id
            dst_id = edge.to_node_id
            if src_id not in rect_map or dst_id not in rect_map:
                edge_info.append(None)
                continue
            src_rect = rect_map[src_id]
            dst_rect = rect_map[dst_id]
            src_cx = src_rect[0] + src_rect[2] / 2
            src_cy = src_rect[1] + src_rect[3] / 2
            dst_cx = dst_rect[0] + dst_rect[2] / 2
            dst_cy = dst_rect[1] + dst_rect[3] / 2
            edge_info.append({
                'src_id': src_id, 'dst_id': dst_id,
                'src_side': _pick_side(src_rect, dst_cx, dst_cy),
                'dst_side': _pick_side(dst_rect, src_cx, src_cy),
                'src_counterpart': (dst_cx, dst_cy),
                'dst_counterpart': (src_cx, src_cy),
            })

        # Pass 2: (node_id, side) ごとに集約。相手座標でソートして等間隔ポート位置を割当
        groups: Dict[Tuple[str, str], List[Tuple[int, str, Tuple[float, float]]]] = defaultdict(list)
        for idx, info in enumerate(edge_info):
            if info is None:
                continue
            groups[(info['src_id'], info['src_side'])].append((idx, 'src', info['src_counterpart']))
            groups[(info['dst_id'], info['dst_side'])].append((idx, 'dst', info['dst_counterpart']))

        port_assignment: Dict[Tuple[int, str], Tuple[int, int]] = {}
        for (node_id, side), entries in groups.items():
            # top/bottom 辺なら相手x、left/right 辺なら相手y でソート
            sort_axis = 0 if side in ('top', 'bottom') else 1
            entries.sort(key=lambda e: e[2][sort_axis])
            n = len(entries)
            rect = rect_map[node_id]
            for i, (edge_idx, role, _) in enumerate(entries):
                ratio = (i + 1) / (n + 1)
                port_assignment[(edge_idx, role)] = _port_at(rect, side, ratio)

        # Pass 3: 各エッジについて分配済みポートで経路探索(edges と同じ順序で返す)
        result: List[RouteResult] = []
        for idx, info in enumerate(edge_info):
            if info is None:
                # 不正なエッジ: ダミーの結果を返す(呼び出し側で扱う)
                result.append(RouteResult(
                    from_point=(0, 0), to_point=(0, 0),
                    from_side='right', to_side='left', waypoints=[]
                ))
                continue

            src_port = port_assignment[(idx, 'src')]
            dst_port = port_assignment[(idx, 'dst')]

            obstacles = [
                r for nid, r in rect_map.items()
                if nid != info['src_id'] and nid != info['dst_id']
            ]

            waypoints = _choose_path(
                src_port, dst_port,
                info['src_side'], info['dst_side'],
                obstacles, padding
            )

            result.append(RouteResult(
                from_point=src_port,
                to_point=dst_port,
                from_side=info['src_side'],
                to_side=info['dst_side'],
                waypoints=waypoints
            ))
        return result
