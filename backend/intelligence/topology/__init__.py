from .interfaces import TopologyProvider
from .junctions import JunctionMatchingConfig, reconstruct_junctions
from .crossings import (
    CrossingClassification,
    CrossingClassificationConfig,
    CrossingKind,
    classify_crossings,
    reconstruct_with_crossing_classification,
)
from .reconstruction import (
    DeterministicTopologyReconstructor,
    TopologyReconstructionConfig,
    reconstruct_topology,
)
from .connectivity import (
    EndpointMatch,
    EndpointMatchingConfig,
    reconstruct_endpoint_connectivity,
)
from .geometry import (
    DEFAULT_GEOMETRY_TOLERANCE,
    IntersectionKind,
    SegmentIntersection,
    closest_segment_endpoint,
    distance,
    intersect_segments,
    point_on_segment,
    point_to_segment_distance,
    points_close,
    segments_collinear,
)
from .models import TopologyEdge, TopologyNode, TopologyResult

__all__ = [
    "DEFAULT_GEOMETRY_TOLERANCE",
    "EndpointMatch",
    "EndpointMatchingConfig",
    "CrossingClassification",
    "CrossingClassificationConfig",
    "CrossingKind",
    "DeterministicTopologyReconstructor",
    "IntersectionKind",
    "JunctionMatchingConfig",
    "SegmentIntersection",
    "TopologyEdge",
    "TopologyNode",
    "TopologyProvider",
    "TopologyResult",
    "TopologyReconstructionConfig",
    "closest_segment_endpoint",
    "classify_crossings",
    "distance",
    "intersect_segments",
    "point_on_segment",
    "point_to_segment_distance",
    "points_close",
    "reconstruct_endpoint_connectivity",
    "reconstruct_junctions",
    "reconstruct_with_crossing_classification",
    "reconstruct_topology",
    "segments_collinear",
]
