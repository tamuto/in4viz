"""障害物回避エッジルーティング

レイアウト確定後のノード配置を入力に、各エッジが他ノードの矩形を
貫通しないように waypoints(中継点)を計算する。

アルゴリズム:
    1. 各エッジの両端で box の進入面(top/right/bottom/left)を決定
    2. (node, side) ごとにエッジを集めて辺上に等間隔でポート分配
       (相手側の中心位置でソートし、線同士が交差しにくい順に並べる)
    3. 障害物矩形の外周と既存エッジ周辺レーンから候補座標を作る
    4. 候補座標グリッド上で A* 探索し、ノード矩形を避ける経路を選ぶ
    5. 既存エッジとの重なり・交差は soft obstacle としてコストを加算する

既存エッジは通行禁止にはせず、重なりを避けやすくするための追加コストとして扱う。
"""
from collections import defaultdict
from dataclasses import dataclass, field
import heapq
from typing import List, Dict, Tuple, Protocol, Optional


@dataclass
class RouteResult:
    """1エッジ分のルーティング結果"""
    from_point: Tuple[int, int]
    to_point: Tuple[int, int]
    from_side: str  # 'top' | 'right' | 'bottom' | 'left'
    to_side: str
    waypoints: List[Tuple[int, int]] = field(default_factory=list)
    route_status: str = "ok"
    route_reason: str = ""


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


def _outside_point(point: Tuple[int, int], side: str, distance: int) -> Tuple[int, int]:
    """ポートの接続辺から外側へ少し出た点を返す。"""
    x, y = point
    if side == 'left':
        return x - distance, y
    if side == 'right':
        return x + distance, y
    if side == 'top':
        return x, y - distance
    return x, y + distance


def _point_in_rect(point: Tuple[int, int], rect: Tuple[int, int, int, int], padding: int) -> bool:
    x, y = point
    rx, ry, rw, rh = rect
    return (
        rx - padding < x < rx + rw + padding
        and ry - padding < y < ry + rh + padding
    )


def _segment_direction(
    x1: int, y1: int, x2: int, y2: int
) -> Optional[str]:
    if x1 == x2 and y1 != y2:
        return 'v'
    if y1 == y2 and x1 != x2:
        return 'h'
    return None


def _overlap_length(a1: int, a2: int, b1: int, b2: int) -> int:
    return max(0, min(max(a1, a2), max(b1, b2)) - max(min(a1, a2), min(b1, b2)))


def _between(value: int, start: int, end: int) -> bool:
    return min(start, end) < value < max(start, end)


def _soft_segment_cost(
    segment: Tuple[int, int, int, int],
    existing_segments: List[Tuple[int, int, int, int]]
) -> float:
    """既存エッジとの重なり・交差に対する追加コスト。通行禁止にはしない。"""
    x1, y1, x2, y2 = segment
    direction = _segment_direction(x1, y1, x2, y2)
    if direction is None:
        return 0.0

    cost = 0.0
    for ex1, ey1, ex2, ey2 in existing_segments:
        existing_direction = _segment_direction(ex1, ey1, ex2, ey2)
        if existing_direction is None:
            continue

        if direction == existing_direction:
            if direction == 'h' and y1 == ey1:
                overlap = _overlap_length(x1, x2, ex1, ex2)
                if overlap:
                    cost += 400 + overlap * 25
            elif direction == 'v' and x1 == ex1:
                overlap = _overlap_length(y1, y2, ey1, ey2)
                if overlap:
                    cost += 400 + overlap * 25
        elif direction == 'h':
            if _between(ex1, x1, x2) and _between(y1, ey1, ey2):
                cost += 80
        else:
            if _between(x1, ex1, ex2) and _between(ey1, y1, y2):
                cost += 80
    return cost


def _simplify_path(points: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not points:
        return []

    deduped: List[Tuple[int, int]] = []
    for point in points:
        if not deduped or deduped[-1] != point:
            deduped.append(point)

    simplified: List[Tuple[int, int]] = []
    for point in deduped:
        simplified.append(point)
        while len(simplified) >= 3:
            a, b, c = simplified[-3], simplified[-2], simplified[-1]
            if (a[0] == b[0] == c[0]) or (a[1] == b[1] == c[1]):
                simplified.pop(-2)
            else:
                break
    return simplified


def _candidate_coordinates(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    obstacles: List[Tuple[int, int, int, int]],
    existing_segments: List[Tuple[int, int, int, int]],
    padding: int
) -> Tuple[List[int], List[int]]:
    lane_gap = max(8, padding)
    clearance = padding + 1
    xs = {start[0], goal[0]}
    ys = {start[1], goal[1]}

    if obstacles:
        min_x = min(rx for rx, _, _, _ in obstacles)
        max_x = max(rx + rw for rx, _, rw, _ in obstacles)
        min_y = min(ry for _, ry, _, _ in obstacles)
        max_y = max(ry + rh for _, ry, _, rh in obstacles)
    else:
        min_x = min(start[0], goal[0])
        max_x = max(start[0], goal[0])
        min_y = min(start[1], goal[1])
        max_y = max(start[1], goal[1])

    outer = max(40, padding * 4)
    xs.update([min(min_x, start[0], goal[0]) - outer, max(max_x, start[0], goal[0]) + outer])
    ys.update([min(min_y, start[1], goal[1]) - outer, max(max_y, start[1], goal[1]) + outer])

    for rx, ry, rw, rh in obstacles:
        xs.update([rx - clearance, rx + rw + clearance])
        ys.update([ry - clearance, ry + rh + clearance])

    for x1, y1, x2, y2 in existing_segments:
        xs.update([x1, x2])
        ys.update([y1, y2])
        if y1 == y2:
            ys.update([y1 - lane_gap, y1 + lane_gap])
        if x1 == x2:
            xs.update([x1 - lane_gap, x1 + lane_gap])

    return sorted(xs), sorted(ys)


def _find_grid_path(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    obstacles: List[Tuple[int, int, int, int]],
    existing_segments: List[Tuple[int, int, int, int]],
    padding: int
) -> Optional[List[Tuple[int, int]]]:
    """障害物外周と既存線周辺の候補座標上で直交A*探索を行う。"""
    xs, ys = _candidate_coordinates(start, goal, obstacles, existing_segments, padding)
    blocked = set()
    points = set()
    for x in xs:
        for y in ys:
            point = (x, y)
            if point not in (start, goal) and any(_point_in_rect(point, obs, padding) for obs in obstacles):
                blocked.add(point)
            else:
                points.add(point)

    if start not in points or goal not in points:
        return None

    points_by_x: Dict[int, List[int]] = defaultdict(list)
    points_by_y: Dict[int, List[int]] = defaultdict(list)
    for x, y in points:
        points_by_x[x].append(y)
        points_by_y[y].append(x)
    for x in points_by_x:
        points_by_x[x].sort()
    for y in points_by_y:
        points_by_y[y].sort()

    def neighbors(point: Tuple[int, int]) -> List[Tuple[Tuple[int, int], str]]:
        x, y = point
        result = []
        x_row = points_by_y[y]
        y_col = points_by_x[x]
        x_index = x_row.index(x)
        y_index = y_col.index(y)
        for next_x in (x_row[x_index - 1] if x_index > 0 else None,
                       x_row[x_index + 1] if x_index + 1 < len(x_row) else None):
            if next_x is not None:
                next_point = (next_x, y)
                if next_point not in blocked and _path_clear([point, next_point], obstacles, padding):
                    result.append((next_point, 'h'))
        for next_y in (y_col[y_index - 1] if y_index > 0 else None,
                       y_col[y_index + 1] if y_index + 1 < len(y_col) else None):
            if next_y is not None:
                next_point = (x, next_y)
                if next_point not in blocked and _path_clear([point, next_point], obstacles, padding):
                    result.append((next_point, 'v'))
        return result

    def heuristic(point: Tuple[int, int]) -> int:
        return abs(point[0] - goal[0]) + abs(point[1] - goal[1])

    start_state = (start, None)
    counter = 0
    queue = [(heuristic(start), 0.0, counter, start, None)]
    best: Dict[Tuple[Tuple[int, int], Optional[str]], float] = {start_state: 0.0}
    previous: Dict[
        Tuple[Tuple[int, int], Optional[str]],
        Tuple[Tuple[int, int], Optional[str]]
    ] = {}
    goal_state = None

    while queue:
        _, current_cost, _, point, prev_dir = heapq.heappop(queue)
        state = (point, prev_dir)
        if current_cost != best.get(state):
            continue
        if point == goal:
            goal_state = state
            break

        for next_point, direction in neighbors(point):
            x1, y1 = point
            x2, y2 = next_point
            segment = (x1, y1, x2, y2)
            length = abs(x2 - x1) + abs(y2 - y1)
            bend_cost = 0 if prev_dir in (None, direction) else 30
            next_cost = (
                current_cost
                + length
                + bend_cost
                + _soft_segment_cost(segment, existing_segments)
            )
            next_state = (next_point, direction)
            if next_cost < best.get(next_state, float('inf')):
                best[next_state] = next_cost
                previous[next_state] = state
                counter += 1
                heapq.heappush(queue, (next_cost + heuristic(next_point), next_cost, counter, next_point, direction))

    if goal_state is None:
        return None

    path = []
    state = goal_state
    while True:
        path.append(state[0])
        if state == start_state:
            break
        state = previous[state]
    path.reverse()
    return _simplify_path(path)


def _choose_path(
    src_port: Tuple[int, int],
    dst_port: Tuple[int, int],
    src_side: str,
    dst_side: str,
    obstacles: List[Tuple[int, int, int, int]],
    padding: int,
    existing_segments: List[Tuple[int, int, int, int]]
) -> Optional[List[Tuple[int, int]]]:
    """障害物外周候補と既存線コストを使って直交経路を探索する。"""
    offset = padding + 1
    src_exit = _outside_point(src_port, src_side, offset)
    dst_entry = _outside_point(dst_port, dst_side, offset)
    routed = _find_grid_path(src_exit, dst_entry, obstacles, existing_segments, padding)
    if routed is None:
        return None

    path = _simplify_path([src_port, src_exit, *routed, dst_entry, dst_port])
    if not _path_clear(path, obstacles, padding):
        return None
    return path[1:-1]


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
        used_segments: List[Tuple[int, int, int, int]] = []
        result: List[RouteResult] = []
        for idx, info in enumerate(edge_info):
            if info is None:
                # 不正なエッジ: ダミーの結果を返す(呼び出し側で扱う)
                result.append(RouteResult(
                    from_point=(0, 0), to_point=(0, 0),
                    from_side='right', to_side='left', waypoints=[],
                    route_status="failed",
                    route_reason="missing-node"
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
                obstacles, padding, used_segments
            )
            route_status = "ok" if waypoints is not None else "failed"
            route_reason = "" if waypoints is not None else "no-orthogonal-path"
            if waypoints is None:
                waypoints = []
            else:
                used_segments.extend(_segments_from_points([src_port, *waypoints, dst_port]))

            result.append(RouteResult(
                from_point=src_port,
                to_point=dst_port,
                from_side=info['src_side'],
                to_side=info['dst_side'],
                waypoints=waypoints,
                route_status=route_status,
                route_reason=route_reason
            ))
        return result
