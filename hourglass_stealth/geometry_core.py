"""Specialized geometry helpers for the mirror-hourglass finite-angle model."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hourglass_stealth.raytrace import Ray, RayTraceResult


EPSILON = 1e-9


@dataclass(frozen=True)
class Point:
    x: float
    z: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.z + other.z)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.z - other.z)

    def scale(self, factor: float) -> "Point":
        return Point(self.x * factor, self.z * factor)

    def norm(self) -> float:
        return math.hypot(self.x, self.z)


@dataclass(frozen=True)
class Segment:
    name: str
    a: Point
    b: Point
    mirror_type: str


@dataclass(frozen=True)
class GeometryConfig:
    aperture_width: float = 1.0
    alpha_deg: float = 22.5
    beta_deg: float = 0.26
    front_span_z: float | None = None
    throat_half_width: float | None = None
    rear_start_z: float | None = None
    include_bottom_throat_mirror: bool = True
    include_top_sawtooth: bool = True
    wall_extension_z: float = 0.35
    wall_facet_angle_offset_deg: float = 0.0
    throat_return_angle_offset_deg: float = 0.0
    throat_return_band_min_fraction: float = 0.03
    throat_return_band_max_fraction: float = 0.28
    rear_top_target_min_fraction: float = 0.82
    rear_top_target_max_fraction: float = 0.98


@dataclass(frozen=True)
class FacetSpec:
    wall_side: str
    z: float
    incoming_angle_deg: float
    target_x: float
    target_z: float
    outgoing_angle_deg: float
    facet_angle_deg: float


@dataclass(frozen=True)
class HourglassGeometry:
    config: GeometryConfig
    segments: list[Segment]
    front_left: Segment
    front_right: Segment
    rear_left: Segment
    rear_right: Segment
    throat_left: Segment
    throat_right: Segment
    wall_left: Segment
    wall_right: Segment
    wall_top_z: float


def deg_to_rad(angle_deg: float) -> float:
    return math.radians(angle_deg)


def rad_to_deg(angle_rad: float) -> float:
    return math.degrees(angle_rad)


def tan_deg(angle_deg: float) -> float:
    return math.tan(deg_to_rad(angle_deg))


def normalize_angle_deg(angle_deg: float) -> float:
    value = angle_deg
    while value > 180.0:
        value -= 360.0
    while value < -180.0:
        value += 360.0
    return value


def mirror_reflect(direction: Point, mirror_angle: float) -> Point:
    incoming = angle_from_vertical(direction)
    outgoing = 2.0 * mirror_angle - incoming
    return direction_from_vertical_angle(outgoing)


def line_intersection(p: Point, p2: Point, q: Point, q2: Point) -> Point | None:
    r = p2 - p
    s = q2 - q
    denom = cross(r, s)
    if abs(denom) < EPSILON:
        return None
    t = cross(q - p, s) / denom
    return p + r.scale(t)


def ray_segment_intersection(ray_start: Point, direction: Point, segment: Segment) -> tuple[Point, float, float] | None:
    edge = segment.b - segment.a
    denom = cross(direction, edge)
    if abs(denom) < EPSILON:
        return None
    delta = segment.a - ray_start
    t = cross(delta, edge) / denom
    u = cross(delta, direction) / denom
    if t <= EPSILON:
        return None
    if u < -EPSILON or u > 1.0 + EPSILON:
        return None
    return ray_start + direction.scale(t), t, u


def angle_from_vertical(direction: Point) -> float:
    return rad_to_deg(math.atan2(direction.x, direction.z))


def direction_from_vertical_angle(angle_deg: float) -> Point:
    angle_rad = deg_to_rad(angle_deg)
    return Point(math.sin(angle_rad), math.cos(angle_rad))


def cross(a: Point, b: Point) -> float:
    return a.x * b.z - a.z * b.x


def midpoint(a: Point, b: Point) -> Point:
    return Point((a.x + b.x) / 2.0, (a.z + b.z) / 2.0)


def segment_tangent_angle_deg(segment: Segment) -> float:
    return angle_from_vertical(segment.b - segment.a)


def side_sign(side: str) -> float:
    if side == "left":
        return -1.0
    if side == "right":
        return 1.0
    raise ValueError(f"Unsupported side: {side}")


def resolved_front_span_z(config: GeometryConfig) -> float:
    return 0.5 if config.front_span_z is None else config.front_span_z


def resolved_throat_half_width(config: GeometryConfig) -> float:
    if config.throat_half_width is not None:
        return config.throat_half_width
    a = config.aperture_width / 2.0
    q = a - tan_deg(config.alpha_deg) * resolved_front_span_z(config)
    return max(0.02, q)


def resolved_rear_start_z(config: GeometryConfig) -> float:
    if config.rear_start_z is not None:
        return config.rear_start_z
    a = config.aperture_width / 2.0
    q = resolved_throat_half_width(config)
    return a + q


def front_point(config: GeometryConfig, side: str, s: float) -> Point:
    a = config.aperture_width / 2.0
    sign = side_sign(side)
    x = sign * (a - tan_deg(config.alpha_deg) * s)
    return Point(x, s)


def rear_point(config: GeometryConfig, side: str, s: float) -> Point:
    q = resolved_throat_half_width(config)
    z0 = resolved_rear_start_z(config)
    h = resolved_front_span_z(config)
    sign = side_sign(side)
    z = z0 + s
    x = sign * (q + tan_deg(config.alpha_deg) * s)
    if s < -EPSILON or s > h + EPSILON:
        raise ValueError("Rear coordinate outside active rear span.")
    return Point(x, z)


def build_hourglass_geometry(config: GeometryConfig, wall_extra_z: float | None = None) -> HourglassGeometry:
    a = config.aperture_width / 2.0
    h = resolved_front_span_z(config)
    q = resolved_throat_half_width(config)
    zr = resolved_rear_start_z(config)
    zb = zr + h
    if wall_extra_z is None:
        wall_extra_z = config.wall_extension_z
    wall_top_z = zb + wall_extra_z

    front_left = Segment("front_left", Point(-a, 0.0), Point(-q, h), "front")
    front_right = Segment("front_right", Point(a, 0.0), Point(q, h), "front")
    rear_left = Segment("rear_left", Point(-q, zr), Point(-a, zb), "rear")
    rear_right = Segment("rear_right", Point(q, zr), Point(a, zb), "rear")
    throat_left_type = "throat_vertical" if config.include_bottom_throat_mirror else "guide"
    throat_right_type = "throat_vertical" if config.include_bottom_throat_mirror else "guide"
    throat_left = Segment("throat_left", Point(-q, h), Point(-q, zr), throat_left_type)
    throat_right = Segment("throat_right", Point(q, h), Point(q, zr), throat_right_type)
    wall_type = "wall_sawtooth" if config.include_top_sawtooth else "wall_vertical"
    wall_left = Segment("wall_left", Point(-a, zb), Point(-a, wall_top_z), wall_type)
    wall_right = Segment("wall_right", Point(a, zb), Point(a, wall_top_z), wall_type)
    segments = [
        front_left,
        front_right,
        throat_left,
        throat_right,
        rear_left,
        rear_right,
        wall_left,
        wall_right,
    ]
    return HourglassGeometry(
        config=config,
        segments=segments,
        front_left=front_left,
        front_right=front_right,
        rear_left=rear_left,
        rear_right=rear_right,
        throat_left=throat_left,
        throat_right=throat_right,
        wall_left=wall_left,
        wall_right=wall_right,
        wall_top_z=wall_top_z,
    )


def nominal_rear_segment_for_front(segment_name: str, geometry: HourglassGeometry) -> Segment:
    if segment_name == geometry.front_right.name:
        return geometry.rear_left
    if segment_name == geometry.front_left.name:
        return geometry.rear_right
    raise ValueError(f"Unsupported front segment: {segment_name}")


def throat_segment_for_front(segment_name: str, geometry: HourglassGeometry) -> Segment:
    if segment_name == geometry.front_right.name:
        return geometry.throat_left
    if segment_name == geometry.front_left.name:
        return geometry.throat_right
    raise ValueError(f"Unsupported front segment: {segment_name}")


def wall_segment_for_front(segment_name: str, geometry: HourglassGeometry) -> Segment:
    if segment_name == geometry.front_right.name:
        return geometry.wall_left
    if segment_name == geometry.front_left.name:
        return geometry.wall_right
    raise ValueError(f"Unsupported front segment: {segment_name}")


def build_source_ray(front_segment: Segment, hit_point: Point, phi_deg: float, tail_length: float = 0.35) -> "Ray":
    from hourglass_stealth.raytrace import Ray

    direction = direction_from_vertical_angle(phi_deg)
    start = hit_point - direction.scale(tail_length)
    return Ray(start=start, direction_angle_deg=phi_deg, label=f"{front_segment.name}@z={hit_point.z:.3f},phi={phi_deg:.3f}")


def sample_input_rays(
    config: GeometryConfig,
    mode: str = "extremal",
    num_rays: int = 24,
    seed: int = 0,
) -> list["Ray"]:
    geometry = build_hourglass_geometry(config)
    h = resolved_front_span_z(config)
    beta = config.beta_deg

    def add_samples(side_segment: Segment, s_values: list[float], phi_values: list[float], rays: list["Ray"]) -> None:
        for s in s_values:
            point = interpolate_segment(side_segment, s / h if h > EPSILON else 0.0)
            for phi in phi_values:
                rays.append(build_source_ray(side_segment, point, phi))

    rays: list["Ray"] = []
    if mode == "extremal":
        s_values = [0.0, h]
        phi_values = [-beta, beta]
        add_samples(geometry.front_left, s_values, phi_values, rays)
        add_samples(geometry.front_right, s_values, phi_values, rays)
        return rays

    if mode == "grid":
        levels = max(2, num_rays // 4)
        s_values = [h * index / (levels - 1) for index in range(levels)]
        phi_values = [-beta + (2.0 * beta * index / (levels - 1)) for index in range(levels)]
        add_samples(geometry.front_left, s_values, phi_values, rays)
        add_samples(geometry.front_right, s_values, phi_values, rays)
        return rays

    if mode == "random":
        generator = random.Random(seed)
        per_side = max(1, num_rays // 2)
        for segment in (geometry.front_left, geometry.front_right):
            for _ in range(per_side):
                s = generator.uniform(0.0, h)
                phi = generator.uniform(-beta, beta)
                point = interpolate_segment(segment, s / h if h > EPSILON else 0.0)
                rays.append(build_source_ray(segment, point, phi))
        return rays

    raise ValueError(f"Unsupported mode: {mode}")


def interpolate_segment(segment: Segment, u: float) -> Point:
    return Point(
        segment.a.x + (segment.b.x - segment.a.x) * u,
        segment.a.z + (segment.b.z - segment.a.z) * u,
    )


def classify_skirt(ray: "Ray", config: GeometryConfig) -> tuple[str, Segment, Point] | None:
    geometry = build_hourglass_geometry(config)
    first_front = geometry.front_right if ray.label.startswith("front_right") else geometry.front_left
    hit = ray_segment_intersection(ray.start, direction_from_vertical_angle(ray.direction_angle_deg), first_front)
    if hit is None:
        return None
    hit_point = hit[0]
    outgoing = direction_from_vertical_angle(2.0 * segment_tangent_angle_deg(first_front) - ray.direction_angle_deg)
    rear = nominal_rear_segment_for_front(first_front.name, geometry)
    rear_line_hit = line_intersection(hit_point, hit_point + outgoing, rear.a, rear.b)
    if rear_line_hit is None:
        return None
    rear_min_z = min(rear.a.z, rear.b.z)
    rear_max_z = max(rear.a.z, rear.b.z)
    if rear_line_hit.z < rear_min_z - EPSILON:
        return "bottom", first_front, rear_line_hit
    if rear_line_hit.z > rear_max_z + EPSILON:
        return "top", first_front, rear_line_hit
    return None


def compute_bottom_skirt_rays(config: GeometryConfig) -> list["Ray"]:
    rays = sample_input_rays(config, mode="grid", num_rays=36, seed=0)
    return [ray for ray in rays if (classify_skirt(ray, config) or (None,))[0] == "bottom"]


def compute_top_skirt_rays(config: GeometryConfig) -> list["Ray"]:
    rays = sample_input_rays(config, mode="grid", num_rays=36, seed=0)
    return [ray for ray in rays if (classify_skirt(ray, config) or (None,))[0] == "top"]


def compute_vertical_throat_hit_range(config: GeometryConfig) -> tuple[float | None, float | None]:
    from hourglass_stealth.raytrace import trace_rays

    rays = compute_bottom_skirt_rays(config) + compute_top_skirt_rays(config)
    if not rays:
        return None, None
    results, _ = trace_rays(config, rays, max_bounces=8)
    z_values = [
        hit.point.z
        for result in results
        for hit in result.hits
        if hit.segment_name.startswith("throat_")
    ]
    if not z_values:
        return None, None
    return min(z_values), max(z_values)


def compute_sawtooth_wall_hit_range(config: GeometryConfig) -> tuple[float | None, float | None]:
    from hourglass_stealth.raytrace import trace_rays

    rays = compute_top_skirt_rays(config)
    if not rays:
        return None, None
    probe_config = GeometryConfig(
        aperture_width=config.aperture_width,
        alpha_deg=config.alpha_deg,
        beta_deg=config.beta_deg,
        front_span_z=config.front_span_z,
        throat_half_width=config.throat_half_width,
        rear_start_z=config.rear_start_z,
        include_bottom_throat_mirror=config.include_bottom_throat_mirror,
        include_top_sawtooth=False,
    )
    results, _ = trace_rays(probe_config, rays, max_bounces=8)
    z_values = [
        hit.point.z
        for result in results
        for hit in result.hits
        if hit.segment_name.startswith("wall_")
    ]
    if not z_values:
        return None, None
    return min(z_values), max(z_values)


def sawtooth_target_point(config: GeometryConfig, wall_side: str, wall_z: float, wall_range: tuple[float | None, float | None]) -> Point:
    throat_target, _ = sawtooth_path_targets(config, wall_side, wall_z, wall_range)
    return throat_target


def sawtooth_path_targets(
    config: GeometryConfig,
    wall_side: str,
    wall_z: float,
    wall_range: tuple[float | None, float | None],
) -> tuple[Point, Point]:
    """Return the throat return point and the final rear-edge target for top-skirt recovery."""
    z_min, z_max = wall_range
    h = resolved_front_span_z(config)
    if z_min is None or z_max is None or abs(z_max - z_min) < EPSILON:
        fraction = 0.0
    else:
        fraction = (wall_z - z_min) / (z_max - z_min)
    fraction = max(0.0, min(1.0, fraction))

    geometry = build_hourglass_geometry(config)
    throat_segment = geometry.throat_right if wall_side == "left" else geometry.throat_left
    throat_z_low, throat_z_high = throat_return_band(config)
    rear_target_s = h * (0.82 + 0.16 * fraction)
    rear_target = rear_point(config, wall_side, min(h, rear_target_s))
    throat_target_z = throat_z_low + (fraction * (throat_z_high - throat_z_low))

    throat_target = Point(throat_segment.a.x, throat_target_z)
    return throat_target, rear_target


def throat_return_band(config: GeometryConfig) -> tuple[float, float]:
    geometry = build_hourglass_geometry(config)
    throat_z_low = geometry.throat_left.a.z
    throat_z_high = geometry.throat_left.b.z
    h = resolved_front_span_z(config)
    bottom_used_min, bottom_used_max = compute_bottom_throat_hit_range(config)
    band_high = throat_z_low + config.throat_return_band_max_fraction * (throat_z_high - throat_z_low)
    if bottom_used_min is not None:
        band_high = min(band_high, max(throat_z_low + 0.06 * h, bottom_used_min - 0.02 * h))
    if bottom_used_max is not None:
        band_high = min(band_high, max(throat_z_low + 0.06 * h, bottom_used_max - 0.04 * h))
    band_low = throat_z_low + config.throat_return_band_min_fraction * h
    if band_high < band_low:
        band_high = band_low
    return band_low, band_high


def throat_return_target_point(config: GeometryConfig, throat_side: str, throat_z: float) -> Point:
    h = resolved_front_span_z(config)
    band_low, band_high = throat_return_band(config)
    if abs(band_high - band_low) < EPSILON:
        fraction = 0.0
    else:
        fraction = (throat_z - band_low) / (band_high - band_low)
    fraction = max(0.0, min(1.0, fraction))
    rear_side = "right" if throat_side == "left" else "left"
    rear_target_s = h * (
        config.rear_top_target_min_fraction
        + ((config.rear_top_target_max_fraction - config.rear_top_target_min_fraction) * fraction)
    )
    return rear_point(config, rear_side, min(h, rear_target_s))


def compute_bottom_throat_hit_range(config: GeometryConfig) -> tuple[float | None, float | None]:
    from hourglass_stealth.raytrace import trace_rays

    rays = compute_bottom_skirt_rays(config)
    if not rays:
        return None, None
    probe_config = GeometryConfig(
        aperture_width=config.aperture_width,
        alpha_deg=config.alpha_deg,
        beta_deg=config.beta_deg,
        front_span_z=config.front_span_z,
        throat_half_width=config.throat_half_width,
        rear_start_z=config.rear_start_z,
        include_bottom_throat_mirror=config.include_bottom_throat_mirror,
        include_top_sawtooth=False,
    )
    results, _ = trace_rays(probe_config, rays, max_bounces=8)
    z_values = [
        hit.point.z
        for result in results
        for hit in result.hits
        if hit.segment_name.startswith("throat_")
    ]
    if not z_values:
        return None, None
    return min(z_values), max(z_values)


def compute_sawtooth_facet_angles(config: GeometryConfig) -> list[FacetSpec]:
    from hourglass_stealth.raytrace import trace_rays

    rays = compute_top_skirt_rays(config)
    if not rays:
        return []
    probe_config = GeometryConfig(
        aperture_width=config.aperture_width,
        alpha_deg=config.alpha_deg,
        beta_deg=config.beta_deg,
        front_span_z=config.front_span_z,
        throat_half_width=config.throat_half_width,
        rear_start_z=config.rear_start_z,
        include_bottom_throat_mirror=config.include_bottom_throat_mirror,
        include_top_sawtooth=False,
    )
    results, _ = trace_rays(probe_config, rays, max_bounces=8)
    wall_range = compute_sawtooth_wall_hit_range(config)
    facets: list[FacetSpec] = []
    for result in results:
        for hit in result.hits:
            if not hit.segment_name.startswith("wall_"):
                continue
            side = "left" if hit.segment_name.endswith("left") else "right"
            throat_target, _ = sawtooth_path_targets(config, side, hit.point.z, wall_range)
            delta = throat_target - hit.point
            outgoing_angle = angle_from_vertical(delta)
            facet_angle = normalize_angle_deg((hit.incoming_angle_deg + outgoing_angle) / 2.0)
            facets.append(
                FacetSpec(
                    wall_side=side,
                    z=hit.point.z,
                    incoming_angle_deg=hit.incoming_angle_deg,
                    target_x=throat_target.x,
                    target_z=throat_target.z,
                    outgoing_angle_deg=outgoing_angle,
                    facet_angle_deg=facet_angle,
                )
            )
    facets.sort(key=lambda facet: (facet.wall_side, facet.z, facet.incoming_angle_deg))
    return facets


def summarize_failed_families(results: list["RayTraceResult"]) -> list[str]:
    failed = [result for result in results if not result.within_solar_cone or not result.exits_forward]
    families: list[str] = []
    for result in failed[:6]:
        families.append(result.ray.label)
    return families
