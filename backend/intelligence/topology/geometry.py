"""Numerically tolerant geometry primitives for topology reconstruction.

These functions describe geometric relationships only. They do not classify
intersections as process connectivity or create topology relationships.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from backend.intelligence.extraction.models import Point


# This is a coordinate-space numerical tolerance, not a drawing/pixel tolerance.
DEFAULT_GEOMETRY_TOLERANCE = 1e-9


class IntersectionKind(str, Enum):
    NONE = "none"
    POINT = "point"
    OVERLAP = "overlap"


@dataclass(frozen=True)
class SegmentIntersection:
    kind: IntersectionKind
    point: Point | None = None
    overlap_start: Point | None = None
    overlap_end: Point | None = None


def distance(first: Point, second: Point) -> float:
    """Return Euclidean distance between two points."""
    return math.hypot(second.x - first.x, second.y - first.y)


def points_close(
    first: Point,
    second: Point,
    tolerance: float = DEFAULT_GEOMETRY_TOLERANCE,
) -> bool:
    """Return whether two points are within the supplied distance tolerance."""
    _validate_tolerance(tolerance)
    return distance(first, second) <= tolerance


def point_to_segment_distance(point: Point, start: Point, end: Point) -> float:
    """Return the shortest distance from a point to a finite segment."""
    delta_x = end.x - start.x
    delta_y = end.y - start.y
    length_squared = delta_x * delta_x + delta_y * delta_y
    if length_squared == 0.0:
        return distance(point, start)

    projection = (
        (point.x - start.x) * delta_x + (point.y - start.y) * delta_y
    ) / length_squared
    projection = max(0.0, min(1.0, projection))
    closest = Point(
        start.x + projection * delta_x,
        start.y + projection * delta_y,
    )
    return distance(point, closest)


def point_on_segment(
    point: Point,
    start: Point,
    end: Point,
    tolerance: float = DEFAULT_GEOMETRY_TOLERANCE,
) -> bool:
    """Return whether a point lies on or within tolerance of a finite segment."""
    _validate_tolerance(tolerance)
    segment_length = distance(start, end)
    if segment_length == 0.0:
        return points_close(point, start, tolerance)

    if point_to_segment_distance(point, start, end) > tolerance:
        return False

    projection = (
        (point.x - start.x) * (end.x - start.x)
        + (point.y - start.y) * (end.y - start.y)
    ) / (segment_length * segment_length)
    extension = tolerance / segment_length
    return -extension <= projection <= 1.0 + extension


def closest_segment_endpoint(
    point: Point,
    start: Point,
    end: Point,
) -> tuple[str, float]:
    """Return the nearest endpoint name and its distance from a point."""
    start_distance = distance(point, start)
    end_distance = distance(point, end)
    if start_distance <= end_distance:
        return "start", start_distance
    return "end", end_distance


def segments_collinear(
    first_start: Point,
    first_end: Point,
    second_start: Point,
    second_end: Point,
    tolerance: float = DEFAULT_GEOMETRY_TOLERANCE,
) -> bool:
    """Return whether two finite segments lie on the same infinite line."""
    _validate_tolerance(tolerance)
    first_length = distance(first_start, first_end)
    second_length = distance(second_start, second_end)
    if first_length == 0.0 and second_length == 0.0:
        return points_close(first_start, second_start, tolerance)
    if first_length == 0.0:
        return point_on_segment(first_start, second_start, second_end, tolerance)
    if second_length == 0.0:
        return point_on_segment(second_start, first_start, first_end, tolerance)

    scale = max(first_length, second_length, 1.0)
    return (
        abs(_cross(first_start, first_end, second_start)) <= tolerance * scale
        and abs(_cross(first_start, first_end, second_end)) <= tolerance * scale
    )


def intersect_segments(
    first_start: Point,
    first_end: Point,
    second_start: Point,
    second_end: Point,
    tolerance: float = DEFAULT_GEOMETRY_TOLERANCE,
) -> SegmentIntersection:
    """Return the geometric intersection of two finite segments.

    Collinear overlap returns its inclusive endpoints. A collinear single-point
    touch returns ``POINT``. No result implies that the finite segments do not
    meet; no process-connectivity meaning is inferred.
    """
    _validate_tolerance(tolerance)
    first_length = distance(first_start, first_end)
    second_length = distance(second_start, second_end)

    if first_length == 0.0 and second_length == 0.0:
        if points_close(first_start, second_start, tolerance):
            return SegmentIntersection(IntersectionKind.POINT, point=first_start)
        return SegmentIntersection(IntersectionKind.NONE)
    if first_length == 0.0:
        if point_on_segment(first_start, second_start, second_end, tolerance):
            return SegmentIntersection(IntersectionKind.POINT, point=first_start)
        return SegmentIntersection(IntersectionKind.NONE)
    if second_length == 0.0:
        if point_on_segment(second_start, first_start, first_end, tolerance):
            return SegmentIntersection(IntersectionKind.POINT, point=second_start)
        return SegmentIntersection(IntersectionKind.NONE)

    first_delta = Point(first_end.x - first_start.x, first_end.y - first_start.y)
    second_delta = Point(second_end.x - second_start.x, second_end.y - second_start.y)
    denominator = _cross_vectors(first_delta, second_delta)
    cross_tolerance = tolerance * max(first_length, second_length, 1.0)

    if abs(denominator) <= cross_tolerance:
        if not segments_collinear(
            first_start, first_end, second_start, second_end, tolerance
        ):
            return SegmentIntersection(IntersectionKind.NONE)
        return _collinear_intersection(
            first_start, first_end, second_start, second_end, tolerance
        )

    offset = Point(second_start.x - first_start.x, second_start.y - first_start.y)
    first_parameter = _cross_vectors(offset, second_delta) / denominator
    second_parameter = _cross_vectors(offset, first_delta) / denominator
    first_extension = tolerance / first_length
    second_extension = tolerance / second_length
    if not (
        -first_extension <= first_parameter <= 1.0 + first_extension
        and -second_extension <= second_parameter <= 1.0 + second_extension
    ):
        return SegmentIntersection(IntersectionKind.NONE)

    bounded_parameter = max(0.0, min(1.0, first_parameter))
    return SegmentIntersection(
        IntersectionKind.POINT,
        point=Point(
            first_start.x + bounded_parameter * first_delta.x,
            first_start.y + bounded_parameter * first_delta.y,
        ),
    )


def _collinear_intersection(
    first_start: Point,
    first_end: Point,
    second_start: Point,
    second_end: Point,
    tolerance: float,
) -> SegmentIntersection:
    delta = Point(first_end.x - first_start.x, first_end.y - first_start.y)
    denominator = delta.x * delta.x + delta.y * delta.y
    second_start_parameter = (
        (second_start.x - first_start.x) * delta.x
        + (second_start.y - first_start.y) * delta.y
    ) / denominator
    second_end_parameter = (
        (second_end.x - first_start.x) * delta.x
        + (second_end.y - first_start.y) * delta.y
    ) / denominator
    overlap_start_parameter = max(0.0, min(second_start_parameter, second_end_parameter))
    overlap_end_parameter = min(1.0, max(second_start_parameter, second_end_parameter))
    parameter_tolerance = tolerance / math.sqrt(denominator)

    if overlap_start_parameter > overlap_end_parameter + parameter_tolerance:
        return SegmentIntersection(IntersectionKind.NONE)

    overlap_start = _point_at(first_start, delta, overlap_start_parameter)
    overlap_end = _point_at(first_start, delta, overlap_end_parameter)
    if overlap_end_parameter - overlap_start_parameter <= parameter_tolerance:
        return SegmentIntersection(
            IntersectionKind.POINT,
            point=_point_at(
                first_start,
                delta,
                (overlap_start_parameter + overlap_end_parameter) / 2.0,
            ),
        )
    return SegmentIntersection(
        IntersectionKind.OVERLAP,
        overlap_start=overlap_start,
        overlap_end=overlap_end,
    )


def _point_at(origin: Point, delta: Point, parameter: float) -> Point:
    return Point(
        origin.x + parameter * delta.x,
        origin.y + parameter * delta.y,
    )


def _cross(first: Point, second: Point, third: Point) -> float:
    return _cross_vectors(
        Point(second.x - first.x, second.y - first.y),
        Point(third.x - first.x, third.y - first.y),
    )


def _cross_vectors(first: Point, second: Point) -> float:
    return first.x * second.y - first.y * second.x


def _validate_tolerance(tolerance: float) -> None:
    if tolerance < 0.0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative")