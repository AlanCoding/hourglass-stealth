from pathlib import Path

from hourglass_stealth.geometry_core import (
    FacetSpec,
    GeometryConfig,
    Point,
    compute_bottom_skirt_rays,
    compute_top_skirt_rays,
    compute_sawtooth_facet_angles,
    direction_from_vertical_angle,
    mirror_reflect,
)
from hourglass_stealth.raytrace import Ray, trace_rays
from hourglass_stealth.svg import write_png, write_svg


def test_vertical_mirror_reflection_flips_horizontal_component() -> None:
    incoming = direction_from_vertical_angle(12.0)
    outgoing = mirror_reflect(incoming, 0.0)
    assert round(outgoing.x, 10) == round(-incoming.x, 10)
    assert round(outgoing.z, 10) == round(incoming.z, 10)


def test_bottom_skirt_rays_are_detected() -> None:
    rays = compute_bottom_skirt_rays(GeometryConfig(beta_deg=3.0, front_span_z=0.5))
    assert rays


def test_trace_rays_returns_metrics() -> None:
    config = GeometryConfig(beta_deg=1.0, front_span_z=0.5)
    rays = [
        Ray(start=Point(0.5, -0.25), direction_angle_deg=0.0, label="manual"),
    ]
    results, metrics = trace_rays(config, rays, max_bounces=6)
    assert len(results) == 1
    assert metrics.total_rays == 1
    assert metrics.max_bounces >= 0


def test_svg_writer_emits_svg(tmp_path: Path) -> None:
    config = GeometryConfig(beta_deg=0.26, front_span_z=0.5)
    rays = [
        Ray(start=Point(0.5, -0.25), direction_angle_deg=0.0, label="manual"),
    ]
    results, metrics = trace_rays(config, rays, max_bounces=6)
    output = tmp_path / "hourglass.svg"
    write_svg(output, config, results, metrics)
    text = output.read_text(encoding="utf-8")
    assert "<svg" in text
    assert "max cone excess" in text


def test_png_writer_emits_png(tmp_path: Path) -> None:
    config = GeometryConfig(beta_deg=0.26, front_span_z=0.5)
    rays = [
        Ray(start=Point(0.5, -0.25), direction_angle_deg=0.0, label="manual"),
    ]
    results, metrics = trace_rays(config, rays, max_bounces=6)
    output = tmp_path / "hourglass.png"
    write_png(output, config, results, metrics)
    assert output.exists()
    assert output.stat().st_size > 0


def test_sawtooth_facets_have_consistent_midpoint_rule() -> None:
    config = GeometryConfig(beta_deg=3.0, front_span_z=0.5)
    specs = compute_sawtooth_facet_angles(config)
    if not specs:
        return
    spec = specs[0]
    expected = (spec.incoming_angle_deg + spec.outgoing_angle_deg) / 2.0
    assert abs(spec.facet_angle_deg - expected) < 1e-9


def test_top_skirt_hits_wall() -> None:
    config = GeometryConfig(beta_deg=3.0, front_span_z=0.5)
    rays = compute_top_skirt_rays(config)
    assert rays
    results, _ = trace_rays(config, [rays[0]], max_bounces=8)
    segments = [hit.segment_name for hit in results[0].hits]
    assert any(name.startswith("wall_") for name in segments)


def test_wall_remains_angled_for_upward_top_skirt_capture() -> None:
    config = GeometryConfig(beta_deg=3.0, front_span_z=0.5)
    rays = compute_top_skirt_rays(config)
    results, _ = trace_rays(config, [rays[0]], max_bounces=8)
    wall_hits = [hit for hit in results[0].hits if hit.segment_name.startswith("wall_")]
    assert wall_hits
    assert abs(wall_hits[0].outgoing_angle_deg + wall_hits[0].incoming_angle_deg) > 1.0


def test_rays_do_not_hit_wall_after_rear() -> None:
    config = GeometryConfig(beta_deg=3.0, front_span_z=0.5)
    rays = compute_top_skirt_rays(config)[:12]
    results, _ = trace_rays(config, rays, max_bounces=8)
    for result in results:
        segments = [hit.segment_name for hit in result.hits]
        for index, name in enumerate(segments[:-1]):
            assert not (name.startswith("rear_") and segments[index + 1].startswith("wall_"))
