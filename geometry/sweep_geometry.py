#!/usr/bin/env python3
"""Sweep candidate hourglass geometries and report ray-trace metrics."""

from __future__ import annotations

import argparse

from hourglass_stealth.geometry_core import (
    classify_skirt,
    GeometryConfig,
    compute_sawtooth_facet_angles,
    compute_sawtooth_wall_hit_range,
    compute_vertical_throat_hit_range,
    resolved_front_span_z,
    sample_input_rays,
    summarize_failed_families,
)
from hourglass_stealth.raytrace import TraceMetrics, trace_rays


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beta-deg", type=float, default=3.0)
    parser.add_argument("--q-min", type=float, default=0.05)
    parser.add_argument("--q-max", type=float, default=0.45)
    parser.add_argument("--q-count", type=int, default=80)
    parser.add_argument("--rear-offset-min", type=float, default=0.01)
    parser.add_argument("--rear-offset-max", type=float, default=2.0)
    parser.add_argument("--rear-offset-count", type=int, default=100)
    parser.add_argument("--front-span-z", type=float, default=0.5)
    parser.add_argument("--alpha-deg", type=float, default=22.5)
    parser.add_argument("--aperture-width", type=float, default=1.0)
    parser.add_argument("--throat-band-min-min", type=float, default=0.02)
    parser.add_argument("--throat-band-min-max", type=float, default=0.10)
    parser.add_argument("--throat-band-min-count", type=int, default=5)
    parser.add_argument("--throat-band-max-min", type=float, default=0.12)
    parser.add_argument("--throat-band-max-max", type=float, default=0.40)
    parser.add_argument("--throat-band-max-count", type=int, default=6)
    parser.add_argument("--rear-top-target-min-min", type=float, default=0.72)
    parser.add_argument("--rear-top-target-min-max", type=float, default=0.90)
    parser.add_argument("--rear-top-target-min-count", type=int, default=6)
    parser.add_argument("--rear-top-target-max-min", type=float, default=0.88)
    parser.add_argument("--rear-top-target-max-max", type=float, default=1.00)
    parser.add_argument("--rear-top-target-max-count", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    best_entry: tuple[GeometryConfig, TraceMetrics] | None = None
    best_score: tuple[int, float, float] | None = None
    best_results = []

    front_span = args.front_span_z
    for q in linspace(args.q_min, args.q_max, args.q_count):
        for rear_offset in linspace(args.rear_offset_min, args.rear_offset_max, args.rear_offset_count):
            for throat_band_min in linspace(
                args.throat_band_min_min,
                args.throat_band_min_max,
                args.throat_band_min_count,
            ):
                for throat_band_max in linspace(
                    max(throat_band_min, args.throat_band_max_min),
                    args.throat_band_max_max,
                    args.throat_band_max_count,
                ):
                    for rear_top_target_min in linspace(
                        args.rear_top_target_min_min,
                        args.rear_top_target_min_max,
                        args.rear_top_target_min_count,
                    ):
                        for rear_top_target_max in linspace(
                            max(rear_top_target_min, args.rear_top_target_max_min),
                            args.rear_top_target_max_max,
                            args.rear_top_target_max_count,
                        ):
                            config = GeometryConfig(
                                aperture_width=args.aperture_width,
                                alpha_deg=args.alpha_deg,
                                beta_deg=args.beta_deg,
                                front_span_z=front_span,
                                throat_half_width=q,
                                rear_start_z=front_span + rear_offset,
                                include_bottom_throat_mirror=True,
                                include_top_sawtooth=True,
                                throat_return_band_min_fraction=throat_band_min,
                                throat_return_band_max_fraction=throat_band_max,
                                rear_top_target_min_fraction=rear_top_target_min,
                                rear_top_target_max_fraction=rear_top_target_max,
                            )
                            rays = sample_input_rays(config, mode="grid", num_rays=24, seed=0)
                            results, metrics = trace_rays(config, rays, max_bounces=8)
                            score = score_candidate(config, results, metrics)
                            if best_score is None or score < best_score:
                                best_score = score
                                best_entry = (config, metrics)
                                best_results = results

    if best_entry is None:
        raise RuntimeError("No candidate geometries were evaluated.")

    config, metrics = best_entry
    throat_range = compute_vertical_throat_hit_range(config)
    wall_range = compute_sawtooth_wall_hit_range(config)
    facets = compute_sawtooth_facet_angles(config)
    worst = max(
        best_results,
        key=lambda result: (
            0 if result.within_solar_cone else 1,
            abs(result.final_angle_deg) - config.beta_deg,
            len(result.hits),
        ),
    )

    print("best candidate")
    print(f"  beta_deg = {config.beta_deg:.6f}")
    print(f"  alpha_deg = {config.alpha_deg:.6f}")
    print(f"  front_span_z = {resolved_front_span_z(config):.6f}")
    print(f"  throat_half_width = {config.throat_half_width:.6f}")
    print(f"  rear_start_z = {config.rear_start_z:.6f}")
    print(f"  throat_return_band_min_fraction = {config.throat_return_band_min_fraction:.6f}")
    print(f"  throat_return_band_max_fraction = {config.throat_return_band_max_fraction:.6f}")
    print(f"  rear_top_target_min_fraction = {config.rear_top_target_min_fraction:.6f}")
    print(f"  rear_top_target_max_fraction = {config.rear_top_target_max_fraction:.6f}")
    print("metrics")
    print(f"  failed rays = {len(metrics.failed_rays)}")
    print(f"  rays forward = {metrics.rays_forward}/{metrics.total_rays}")
    print(f"  rays within cone = {metrics.rays_within_cone}/{metrics.total_rays}")
    print(f"  max cone excess deg = {metrics.max_cone_excess_deg:.6f}")
    print(f"  mean bounces = {metrics.mean_bounces:.6f}")
    print(f"  maximum bounces = {metrics.max_bounces}")
    print(f"  used throat mirror z-range = {fmt_range(throat_range)}")
    print(f"  used sawtooth wall z-range = {fmt_range(wall_range)}")
    if facets:
        print(
            "  sawtooth facet angle range = "
            f"{min(spec.facet_angle_deg for spec in facets):.6f} to "
            f"{max(spec.facet_angle_deg for spec in facets):.6f}"
        )
    else:
        print("  sawtooth facet angle range = none")
    print("worst ray")
    print(f"  label = {worst.ray.label}")
    print(f"  final angle deg = {worst.final_angle_deg:.6f}")
    print(f"  exits forward = {worst.exits_forward}")
    print(f"  within cone = {worst.within_solar_cone}")
    print(f"  notes = {', '.join(worst.notes) if worst.notes else 'none'}")
    families = summarize_failed_families(best_results)
    if families:
        print("failed ray families")
        for family in families:
            print(f"  {family}")


def linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + (index * step) for index in range(count)]


def fmt_range(value: tuple[float | None, float | None]) -> str:
    lower, upper = value
    if lower is None or upper is None:
        return "none"
    return f"{lower:.6f} to {upper:.6f}"


def score_candidate(config: GeometryConfig, results: list, metrics: TraceMetrics) -> tuple[int, int, int, float, float]:
    top_path_failures = 0
    bottom_path_failures = 0
    for result in results:
        skirt_info = classify_skirt(result.ray, config)
        if skirt_info is None:
            continue
        skirt_kind = skirt_info[0]
        segments = [hit.segment_name for hit in result.hits]
        if skirt_kind == "top" and not has_ordered_hits(segments, ("wall_", "throat_", "rear_")):
            top_path_failures += 1
        if skirt_kind == "bottom" and not has_ordered_hits(segments, ("throat_", "rear_")):
            bottom_path_failures += 1
    return (
        len(metrics.failed_rays),
        top_path_failures,
        bottom_path_failures,
        round(metrics.max_cone_excess_deg, 9),
        round(metrics.mean_bounces, 9),
    )


def has_ordered_hits(segments: list[str], prefixes: tuple[str, ...]) -> bool:
    cursor = 0
    for prefix in prefixes:
        while cursor < len(segments) and not segments[cursor].startswith(prefix):
            cursor += 1
        if cursor >= len(segments):
            return False
        cursor += 1
    return True


if __name__ == "__main__":
    main()
