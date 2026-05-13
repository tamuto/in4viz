from dataclasses import dataclass

from in4viz.backends.drawio.generator import DrawioGenerator
from in4viz.backends.svg.rendering import Edge
from in4viz.core.models import LineType
from in4viz.core.routing import EdgeRouter, _find_grid_path, _segments_from_points


@dataclass
class RouteTestNode:
    node_id: str
    x: int
    y: int
    width: int
    height: int


@dataclass
class RouteTestEdge:
    from_node_id: str
    to_node_id: str


def test_edge_router_routes_around_blocking_node_with_visibility_grid():
    nodes = [
        RouteTestNode("source", 0, 0, 50, 50),
        RouteTestNode("target", 200, 0, 50, 50),
        RouteTestNode("blocker", 75, -100, 100, 300),
    ]
    edges = [RouteTestEdge("source", "target")]

    route = EdgeRouter.route(nodes, edges)[0]

    assert route.route_status == "ok"
    assert route.route_reason == ""
    assert route.waypoints
    assert any(y < -100 for _, y in route.waypoints) or any(y > 200 for _, y in route.waypoints)


def test_edge_router_marks_missing_node_as_failed_route():
    nodes = [RouteTestNode("source", 0, 0, 50, 50)]
    edges = [RouteTestEdge("source", "missing")]

    route = EdgeRouter.route(nodes, edges)[0]

    assert route.waypoints == []
    assert route.route_status == "failed"
    assert route.route_reason == "missing-node"


def test_grid_router_treats_existing_segments_as_soft_obstacles():
    existing_path = [(0, 0), (100, 0)]
    path = _find_grid_path(
        (0, 0),
        (100, 0),
        obstacles=[],
        existing_segments=_segments_from_points(existing_path),
        padding=12,
    )

    assert path is not None
    assert path != existing_path
    assert path[0] == (0, 0)
    assert path[-1] == (100, 0)


def test_svg_failed_route_metadata_does_not_change_styling():
    edge = Edge(
        "source",
        "target",
        LineType.ORTHOGONAL,
        waypoints=[],
        route_status="failed",
        route_reason="no-orthogonal-path",
    )

    svg = edge.render(50, 25, 200, 25, LineType.ORTHOGONAL, "right", "left")

    assert 'data-route-status="failed"' in svg
    assert 'data-route-reason="no-orthogonal-path"' in svg
    assert 'stroke="black"' in svg
    assert 'stroke-width="1"' in svg


def test_drawio_failed_route_metadata_is_written_to_edge_cell():
    cell = DrawioGenerator.create_edge_cell(
        "edge-1",
        "source-cell",
        "target-cell",
        "edgeStyle=none;html=1;",
        route_status="failed",
        route_reason="no-orthogonal-path",
    )

    assert cell["routeStatus"] == "failed"
    assert cell["routeReason"] == "no-orthogonal-path"
    assert cell["style"] == "edgeStyle=none;html=1;"
