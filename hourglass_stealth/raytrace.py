"""Purpose-built 2-D ray tracing for the mirror-hourglass geometry."""

from __future__ import annotations

from dataclasses import dataclass
import math

from hourglass_stealth.geometry_core import (
    GeometryConfig,
    HourglassGeometry,
    Point,
    Segment,
    angle_from_vertical,
    build_hourglass_geometry,
    direction_from_vertical_angle,
    mirror_reflect,
    normalize_angle_deg,
    ray_segment_intersection,
    sawtooth_target_point,
    segment_tangent_angle_deg,
    throat_return_target_point,
)


@dataclass(frozen=True)
class Ray:
    start: Point
    direction_angle_deg: float
    label: str = ""


@dataclass(frozen=True)
class RayHit:
    segment_name: str
    point: Point
    incoming_angle_deg: float
    outgoing_angle_deg: float


@dataclass(frozen=True)
class RayTraceResult:
    ray: Ray
    hits: list[RayHit]
    final_angle_deg: float
    exits_forward: bool
    within_solar_cone: bool
    notes: list[str]


@dataclass(frozen=True)
class TraceMetrics:
    total_rays: int
    rays_forward: int
    rays_within_cone: int
    max_cone_excess_deg: float
    max_bounces: int
    mean_bounces: float
    failed_rays: list[RayTraceResult]


def trace_rays(
    config: GeometryConfig,
    rays: list[Ray],
    max_bounces: int = 8,
) -> tuple[list[RayTraceResult], TraceMetrics]:
    geometry = build_hourglass_geometry(config)
    wall_range = _wall_range(geometry)

    results = [
        trace_single_ray(
            ray=ray,
            config=config,
            geometry=geometry,
            wall_range=wall_range,
            max_bounces=max_bounces,
        )
        for ray in rays
    ]
    metrics = compute_trace_metrics(config, results)
    return results, metrics


def trace_single_ray(
    ray: Ray,
    config: GeometryConfig,
    geometry: HourglassGeometry,
    wall_range: tuple[float | None, float | None],
    max_bounces: int,
) -> RayTraceResult:
    position = ray.start
    direction = direction_from_vertical_angle(ray.direction_angle_deg)
    previous_segment: str | None = None
    hits: list[RayHit] = []
    notes: list[str] = []

    for bounce_index in range(max_bounces):
        candidates: list[tuple[Segment, Point, float, float]] = []
        for segment in geometry.segments:
            if segment.name == previous_segment:
                continue
            if segment.mirror_type == "guide":
                continue
            hit = ray_segment_intersection(position, direction, segment)
            if hit is None:
                continue
            candidates.append((segment, hit[0], hit[1], hit[2]))

        if not candidates:
            break

        segment, hit_point, _, _ = _choose_candidate(candidates, geometry)
        incoming_angle = angle_from_vertical(direction)
        outgoing_direction = _reflect_on_segment(
            direction=direction,
            segment=segment,
            hit_point=hit_point,
            config=config,
            wall_range=wall_range,
            previous_segment=previous_segment,
        )
        outgoing_angle = angle_from_vertical(outgoing_direction)
        hits.append(
            RayHit(
                segment_name=segment.name,
                point=hit_point,
                incoming_angle_deg=incoming_angle,
                outgoing_angle_deg=outgoing_angle,
            )
        )
        direction = outgoing_direction
        position = hit_point + direction.scale(1e-7)
        previous_segment = segment.name

        if bounce_index == max_bounces - 1:
            notes.append("max_bounces_reached")

    final_angle = angle_from_vertical(direction)
    exits_forward = direction.z > 0.0
    within_solar_cone = exits_forward and abs(final_angle) <= config.beta_deg + 1e-6
    if not exits_forward:
        notes.append("ray_exits_backward")
    if not within_solar_cone:
        notes.append("ray_outside_solar_cone")
    return RayTraceResult(
        ray=ray,
        hits=hits,
        final_angle_deg=final_angle,
        exits_forward=exits_forward,
        within_solar_cone=within_solar_cone,
        notes=notes,
    )


def compute_trace_metrics(config: GeometryConfig, results: list[RayTraceResult]) -> TraceMetrics:
    total = len(results)
    rays_forward = sum(1 for result in results if result.exits_forward)
    rays_within_cone = sum(1 for result in results if result.within_solar_cone)
    max_cone_excess = 0.0
    max_bounces = 0
    total_bounces = 0
    failed: list[RayTraceResult] = []
    for result in results:
        max_bounces = max(max_bounces, len(result.hits))
        total_bounces += len(result.hits)
        if result.exits_forward:
            max_cone_excess = max(max_cone_excess, max(0.0, abs(result.final_angle_deg) - config.beta_deg))
        else:
            max_cone_excess = max(max_cone_excess, abs(result.final_angle_deg))
        if not result.within_solar_cone:
            failed.append(result)
    mean_bounces = total_bounces / total if total else 0.0
    return TraceMetrics(
        total_rays=total,
        rays_forward=rays_forward,
        rays_within_cone=rays_within_cone,
        max_cone_excess_deg=max_cone_excess,
        max_bounces=max_bounces,
        mean_bounces=mean_bounces,
        failed_rays=failed,
    )


def ray_path(result: RayTraceResult, tail_length: float = 0.35) -> list[Point]:
    points = [result.ray.start]
    points.extend(hit.point for hit in result.hits)
    direction = direction_from_vertical_angle(result.final_angle_deg)
    points.append(points[-1] + direction.scale(tail_length))
    return points


def _reflect_on_segment(
    direction: Point,
    segment: Segment,
    hit_point: Point,
    config: GeometryConfig,
    wall_range: tuple[float | None, float | None],
    previous_segment: str | None,
) -> Point:
    if segment.mirror_type in {"front", "rear", "wall_vertical"}:
        tangent_angle = segment_tangent_angle_deg(segment)
        return mirror_reflect(direction, tangent_angle)

    if segment.mirror_type == "throat_vertical":
        if previous_segment is not None and previous_segment.startswith("wall_"):
            throat_side = "left" if segment.name.endswith("left") else "right"
            target = throat_return_target_point(config, throat_side, hit_point.z)
            desired = target - hit_point
            desired_angle = angle_from_vertical(desired)
            tangent_angle = normalize_angle_deg((angle_from_vertical(direction) + desired_angle) / 2.0)
            return mirror_reflect(direction, tangent_angle)
        tangent_angle = segment_tangent_angle_deg(segment)
        return mirror_reflect(direction, tangent_angle)

    if segment.mirror_type == "wall_sawtooth":
        wall_side = "left" if segment.name.endswith("left") else "right"
        target = sawtooth_target_point(config, wall_side, hit_point.z, wall_range)
        desired = target - hit_point
        desired_angle = angle_from_vertical(desired)
        tangent_angle = normalize_angle_deg((angle_from_vertical(direction) + desired_angle) / 2.0)
        return mirror_reflect(direction, tangent_angle)

    raise ValueError(f"Unsupported mirror type: {segment.mirror_type}")


def _choose_candidate(
    candidates: list[tuple[Segment, Point, float, float]],
    geometry: HourglassGeometry,
) -> tuple[Segment, Point, float, float]:
    ordered = sorted(candidates, key=lambda item: item[2])
    t0 = ordered[0][2]
    same = [item for item in ordered if abs(item[2] - t0) < 1e-8]
    if len(same) == 1:
        return same[0]

    hit = same[0][1]
    priorities = [
        ((geometry.rear_left.name, geometry.throat_left.name), geometry.rear_left.a),
        ((geometry.rear_right.name, geometry.throat_right.name), geometry.rear_right.a),
        ((geometry.rear_left.name, geometry.wall_left.name), geometry.rear_left.b),
        ((geometry.rear_right.name, geometry.wall_right.name), geometry.rear_right.b),
    ]
    for pair, point in priorities:
        if _points_close(hit, point):
            for preferred in pair:
                for candidate in same:
                    if candidate[0].name == preferred:
                        return candidate
    return same[0]


def _points_close(a: Point, b: Point) -> bool:
    return math.hypot(a.x - b.x, a.z - b.z) < 1e-8


def _wall_range(geometry: HourglassGeometry) -> tuple[float | None, float | None]:
    z_values = [geometry.wall_left.a.z, geometry.wall_left.b.z, geometry.wall_right.a.z, geometry.wall_right.b.z]
    return min(z_values), max(z_values)
