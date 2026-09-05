from backend.intelligence.extraction.models import Point
from backend.intelligence.topology.geometry import (
    IntersectionKind,
    closest_segment_endpoint,
    distance,
    intersect_segments,
    point_on_segment,
    point_to_segment_distance,
    points_close,
    segments_collinear,
)


def test_distance_and_tolerance_aware_point_comparison():
    assert distance(Point(0, 0), Point(3, 4)) == 5.0
    assert points_close(Point(1, 2), Point(1, 2), tolerance=0.001)
    assert points_close(Point(10.0, 20.0), Point(10.0005, 20.0003), tolerance=0.001)
    assert not points_close(Point(10.0, 20.0), Point(10.0005, 20.0003), tolerance=0.0005)


def test_point_to_finite_segment_distance_handles_projection_and_endpoints():
    assert point_to_segment_distance(Point(5, 3), Point(0, 0), Point(10, 0)) == 3.0
    assert point_to_segment_distance(Point(15, 0), Point(0, 0), Point(10, 0)) == 5.0
    assert point_to_segment_distance(Point(0, 0), Point(0, 0), Point(0, 0)) == 0.0


def test_point_on_segment_supports_horizontal_vertical_diagonal_and_degenerate_cases():
    assert point_on_segment(Point(5, 0), Point(0, 0), Point(10, 0), 1e-6)
    assert point_on_segment(Point(0, 5), Point(0, 0), Point(0, 10), 1e-6)
    assert point_on_segment(Point(2.5, 2.5), Point(0, 0), Point(5, 5), 1e-6)
    assert point_on_segment(Point(10.0005, 0), Point(0, 0), Point(10, 0), 0.001)
    assert not point_on_segment(Point(10.01, 0), Point(0, 0), Point(10, 0), 0.001)
    assert point_on_segment(Point(1e-7, -1e-7), Point(0, 0), Point(0, 0), 1e-6)


def test_closest_segment_endpoint_returns_name_and_distance():
    assert closest_segment_endpoint(Point(1, 1), Point(0, 0), Point(10, 0)) == (
        "start",
        2**0.5,
    )
    assert closest_segment_endpoint(Point(9, 1), Point(0, 0), Point(10, 0))[0] == "end"


def test_segment_intersection_handles_crossing_endpoint_and_t_intersections():
    crossing = intersect_segments(Point(0, 0), Point(10, 10), Point(0, 10), Point(10, 0))
    assert crossing.kind is IntersectionKind.POINT
    assert points_close(crossing.point, Point(5, 5), 1e-9)

    endpoint = intersect_segments(Point(0, 0), Point(5, 0), Point(5, 0), Point(5, 5))
    assert endpoint.kind is IntersectionKind.POINT
    assert endpoint.point == Point(5, 0)

    t_intersection = intersect_segments(Point(0, 0), Point(10, 0), Point(5, -5), Point(5, 5))
    assert t_intersection.kind is IntersectionKind.POINT
    assert t_intersection.point == Point(5, 0)


def test_segment_intersection_handles_parallel_nonintersecting_and_collinear_overlap():
    parallel = intersect_segments(Point(0, 0), Point(10, 0), Point(0, 1), Point(10, 1))
    assert parallel.kind is IntersectionKind.NONE

    non_intersecting = intersect_segments(Point(0, 0), Point(2, 0), Point(3, 0), Point(5, 0))
    assert non_intersecting.kind is IntersectionKind.NONE

    overlap = intersect_segments(Point(0, 0), Point(10, 0), Point(5, 0), Point(15, 0))
    assert overlap.kind is IntersectionKind.OVERLAP
    assert overlap.overlap_start == Point(5, 0)
    assert overlap.overlap_end == Point(10, 0)

    touching = intersect_segments(Point(0, 0), Point(5, 0), Point(5, 0), Point(10, 0))
    assert touching.kind is IntersectionKind.POINT
    assert touching.point == Point(5, 0)


def test_segment_intersection_handles_degenerate_segments_and_small_coordinate_noise():
    point_hit = intersect_segments(Point(2, 2), Point(2, 2), Point(0, 2), Point(5, 2))
    assert point_hit.kind is IntersectionKind.POINT
    assert point_hit.point == Point(2, 2)

    point_miss = intersect_segments(Point(2, 2.01), Point(2, 2.01), Point(0, 2), Point(5, 2), 0.001)
    assert point_miss.kind is IntersectionKind.NONE

    noisy = intersect_segments(
        Point(0, 0),
        Point(10, 0),
        Point(5, -1e-8),
        Point(5, 10),
        tolerance=1e-6,
    )
    assert noisy.kind is IntersectionKind.POINT
    assert points_close(noisy.point, Point(5, 0), 1e-6)


def test_segments_collinear_distinguishes_line_alignment_from_overlap():
    assert segments_collinear(Point(0, 0), Point(2, 0), Point(5, 0), Point(8, 0))
    assert not segments_collinear(Point(0, 0), Point(2, 0), Point(0, 1), Point(2, 1))