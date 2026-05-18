"""Deterministic SVG rendering for hourglass geometry and traced rays."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import os
from pathlib import Path

from hourglass_stealth.geometry_core import (
    GeometryConfig,
    build_hourglass_geometry,
    compute_sawtooth_facet_angles,
    compute_sawtooth_wall_hit_range,
    compute_vertical_throat_hit_range,
    resolved_front_span_z,
    resolved_rear_start_z,
)
from hourglass_stealth.raytrace import RayTraceResult, TraceMetrics, ray_path


@dataclass(frozen=True)
class SvgViewport:
    xmin: float
    xmax: float
    zmin: float
    zmax: float
    width: int = 1200
    height: int = 1500
    margin: int = 90

    def x(self, value: float) -> float:
        span = self.xmax - self.xmin
        return self.margin + ((value - self.xmin) / span) * (self.width - (2 * self.margin))

    def y(self, value: float) -> float:
        span = self.zmax - self.zmin
        return self.height - self.margin - ((value - self.zmin) / span) * (self.height - (2 * self.margin))


def write_svg(
    output_path: str | Path,
    config: GeometryConfig,
    traced_results: list[RayTraceResult],
    metrics: TraceMetrics,
    title: str = "Mirror Hourglass Geometry",
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    svg_text = build_svg_document(config=config, traced_results=traced_results, metrics=metrics, title=title)
    output.write_text(svg_text, encoding="utf-8")
    return output


def write_png(
    output_path: str | Path,
    config: GeometryConfig,
    traced_results: list[RayTraceResult],
    metrics: TraceMetrics,
    title: str = "Mirror Hourglass Geometry",
) -> Path:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    geometry = build_hourglass_geometry(config)
    wall_range = compute_sawtooth_wall_hit_range(config)
    throat_range = compute_vertical_throat_hit_range(config)
    facets = compute_sawtooth_facet_angles(config)

    viewport = SvgViewport(
        xmin=-(config.aperture_width * 0.9),
        xmax=(config.aperture_width * 0.9),
        zmin=-0.32,
        zmax=geometry.wall_top_z + 0.25,
    )

    fig, ax = plt.subplots(figsize=(10, 12), dpi=160)
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    for segment in geometry.segments:
        stroke, width, dash = _segment_style(segment.mirror_type)
        line, = ax.plot(
            [segment.a.x, segment.b.x],
            [segment.a.z, segment.b.z],
            color=stroke,
            linewidth=width / 1.5,
            solid_capstyle="round",
        )
        if dash:
            line.set_dashes([float(item) for item in dash.split()])

    ax.plot(
        [-config.aperture_width / 2.0, config.aperture_width / 2.0],
        [0.0, 0.0],
        color="#94a3b8",
        linewidth=1.2,
        dashes=(6, 5),
    )

    for result in traced_results:
        path = ray_path(result, tail_length=0.28)
        if result.within_solar_cone:
            stroke = "#2563eb"
        elif result.exits_forward:
            stroke = "#f97316"
        else:
            stroke = "#991b1b"
        ax.plot(
            [point.x for point in path],
            [point.z for point in path],
            color=stroke,
            linewidth=1.5,
            alpha=0.9,
        )

    for hit_range, color, x in (
        (throat_range, "#2563eb", 0.0),
        (wall_range, "#0891b2", config.aperture_width / 2.0),
    ):
        z_min, z_max = hit_range
        if z_min is None or z_max is None:
            continue
        ax.plot([x, x], [z_min, z_max], color=color, linewidth=3.0, dashes=(4, 4))

    ax.text(
        viewport.xmin,
        geometry.wall_top_z + 0.18,
        title,
        fontsize=16,
        color="#0f172a",
        ha="left",
        va="bottom",
    )
    ax.text(
        viewport.xmin,
        geometry.wall_top_z + 0.08,
        "incoming sunlight (+z)",
        fontsize=10,
        color="#334155",
        ha="left",
        va="bottom",
    )
    ax.text(0.0, resolved_front_span_z(config) + 0.04, "open throat", fontsize=9, color="#0f172a", ha="center")
    ax.text(0.0, resolved_rear_start_z(config) + resolved_front_span_z(config) + 0.04, "rear mirror span", fontsize=9, color="#0f172a", ha="center")

    metric_lines = [
        f"beta = {config.beta_deg:.3f} deg",
        f"alpha = {config.alpha_deg:.3f} deg",
        f"front span h = {resolved_front_span_z(config):.3f}",
        f"throat half-width q = {build_hourglass_geometry(config).throat_left.a.x * -1.0:.3f}",
        f"rear start z = {resolved_rear_start_z(config):.3f}",
        f"rays forward = {metrics.rays_forward}/{metrics.total_rays}",
        f"rays within cone = {metrics.rays_within_cone}/{metrics.total_rays}",
        f"max cone excess = {metrics.max_cone_excess_deg:.4f} deg",
        f"mean bounces = {metrics.mean_bounces:.2f}",
        f"max bounces = {metrics.max_bounces}",
        f"throat use = {_fmt_range(throat_range)}",
        f"wall use = {_fmt_range(wall_range)}",
        f"facet specs = {len(facets)}",
    ]
    if facets:
        metric_lines.append(
            f"facet angle range = {min(spec.facet_angle_deg for spec in facets):.2f} to {max(spec.facet_angle_deg for spec in facets):.2f} deg"
        )

    box = FancyBboxPatch(
        (0.72, 0.74),
        0.25,
        0.23,
        transform=ax.transAxes,
        boxstyle="round,pad=0.012",
        linewidth=1.0,
        edgecolor="#cbd5e1",
        facecolor="#ffffff",
    )
    ax.add_patch(box)
    ax.text(
        0.735,
        0.955,
        "\n".join(metric_lines),
        transform=ax.transAxes,
        fontsize=8.5,
        color="#0f172a",
        ha="left",
        va="top",
        linespacing=1.35,
    )

    ax.set_xlim(viewport.xmin, viewport.xmax)
    ax.set_ylim(viewport.zmin, viewport.zmax)
    ax.axis("off")
    fig.tight_layout(pad=0.6)
    fig.savefig(output, dpi=160, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return output


def build_svg_document(
    config: GeometryConfig,
    traced_results: list[RayTraceResult],
    metrics: TraceMetrics,
    title: str,
) -> str:
    geometry = build_hourglass_geometry(config)
    wall_range = compute_sawtooth_wall_hit_range(config)
    throat_range = compute_vertical_throat_hit_range(config)
    facets = compute_sawtooth_facet_angles(config)

    h = resolved_front_span_z(config)
    z0 = resolved_rear_start_z(config)
    viewport = SvgViewport(
        xmin=-(config.aperture_width * 0.9),
        xmax=(config.aperture_width * 0.9),
        zmin=-0.32,
        zmax=geometry.wall_top_z + 0.25,
    )

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{viewport.width}" height="{viewport.height}" viewBox="0 0 {viewport.width} {viewport.height}">',
        "<defs>",
        '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">',
        '<path d="M 0 0 L 8 4 L 0 8 z" fill="#1f2937" />',
        "</marker>",
        "</defs>",
        f'<rect x="0" y="0" width="{viewport.width}" height="{viewport.height}" fill="#f8fafc" />',
        _screen_text(title, 90, 50, size=28, fill="#0f172a"),
    ]

    for segment in geometry.segments:
        stroke, width, dash = _segment_style(segment.mirror_type)
        lines.append(_line(viewport, segment.a.x, segment.a.z, segment.b.x, segment.b.z, stroke, width, dash))

    lines.append(_line(viewport, -config.aperture_width / 2.0, 0.0, config.aperture_width / 2.0, 0.0, "#94a3b8", 1.5, "6 5"))
    lines.append(_screen_text("incoming sunlight (+z)", 90, 82, size=16, fill="#334155"))
    lines.append(_label(viewport, 0.0, h + 0.04, "open throat", anchor="middle"))
    lines.append(_label(viewport, 0.0, z0 + h + 0.04, "rear mirror span", anchor="middle"))

    for result in traced_results:
        path = ray_path(result, tail_length=0.28)
        stroke = "#dc2626" if "phi=" in result.ray.label and ("front" in result.ray.label) else "#2563eb"
        if result.within_solar_cone:
            stroke = "#2563eb"
        elif result.exits_forward:
            stroke = "#f97316"
        else:
            stroke = "#991b1b"
        lines.append(_polyline(viewport, [(point.x, point.z) for point in path], stroke, 2.1))

    for hit_range, color, label in (
        (throat_range, "#2563eb", "used throat hit interval"),
        (wall_range, "#0891b2", "used wall hit interval"),
    ):
        z_min, z_max = hit_range
        if z_min is None or z_max is None:
            continue
        x = 0.0 if label.startswith("used throat") else (config.aperture_width / 2.0)
        lines.append(_line(viewport, x, z_min, x, z_max, color, 5.0, "4 4"))
        lines.append(_label(viewport, x, z_max + 0.03, label, anchor="middle", fill=color))

    if facets:
        min_angle = min(spec.facet_angle_deg for spec in facets)
        max_angle = max(spec.facet_angle_deg for spec in facets)
        lines.append(_screen_text(f"facet angle range: {min_angle:.2f}° to {max_angle:.2f}°", 90, 126, size=14, fill="#0f172a"))

    lines.append(_metrics_box(config, metrics, throat_range, wall_range, len(facets), viewport))
    lines.append("</svg>")
    return "\n".join(lines)


def _metrics_box(
    config: GeometryConfig,
    metrics: TraceMetrics,
    throat_range: tuple[float | None, float | None],
    wall_range: tuple[float | None, float | None],
    facet_count: int,
    viewport: SvgViewport,
) -> str:
    lines = [
        f"beta = {config.beta_deg:.3f} deg",
        f"alpha = {config.alpha_deg:.3f} deg",
        f"front span h = {resolved_front_span_z(config):.3f}",
        f"throat half-width q = {build_hourglass_geometry(config).throat_left.a.x * -1.0:.3f}",
        f"rear start z = {resolved_rear_start_z(config):.3f}",
        f"rays forward = {metrics.rays_forward}/{metrics.total_rays}",
        f"rays within cone = {metrics.rays_within_cone}/{metrics.total_rays}",
        f"max cone excess = {metrics.max_cone_excess_deg:.4f} deg",
        f"mean bounces = {metrics.mean_bounces:.2f}",
        f"max bounces = {metrics.max_bounces}",
        f"throat use = {_fmt_range(throat_range)}",
        f"wall use = {_fmt_range(wall_range)}",
        f"facet specs = {facet_count}",
    ]
    x = viewport.width - 370
    y = 90
    width = 285
    height = 24 + (18 * len(lines))
    text_lines = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="12" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2" />'
    ]
    for index, line in enumerate(lines):
        text_lines.append(_screen_text(line, x + 14, y + 26 + (index * 18), size=13, fill="#0f172a"))
    return "\n".join(text_lines)


def _fmt_range(value: tuple[float | None, float | None]) -> str:
    lower, upper = value
    if lower is None or upper is None:
        return "none"
    return f"{lower:.3f} to {upper:.3f}"


def _segment_style(mirror_type: str) -> tuple[str, float, str | None]:
    if mirror_type == "front":
        return "#111827", 4.0, None
    if mirror_type == "rear":
        return "#374151", 4.0, None
    if mirror_type == "throat_vertical":
        return "#2563eb", 3.0, None
    if mirror_type == "wall_sawtooth":
        return "#0f766e", 3.0, None
    if mirror_type == "wall_vertical":
        return "#0891b2", 2.6, "8 4"
    return "#94a3b8", 1.8, "6 4"


def _line(viewport: SvgViewport, x1: float, z1: float, x2: float, z2: float, stroke: str, width: float, dash: str | None) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{viewport.x(x1):.2f}" y1="{viewport.y(z1):.2f}" '
        f'x2="{viewport.x(x2):.2f}" y2="{viewport.y(z2):.2f}" '
        f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="round"{dash_attr} />'
    )


def _polyline(viewport: SvgViewport, points: list[tuple[float, float]], stroke: str, width: float) -> str:
    pts = " ".join(f"{viewport.x(x):.2f},{viewport.y(z):.2f}" for x, z in points)
    return (
        f'<polyline points="{pts}" fill="none" stroke="{stroke}" '
        f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arrow)" />'
    )


def _label(viewport: SvgViewport, x: float, z: float, text: str, anchor: str = "start", fill: str = "#0f172a") -> str:
    return (
        f'<text x="{viewport.x(x):.2f}" y="{viewport.y(z):.2f}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="14" text-anchor="{anchor}" fill="{fill}">{escape(text)}</text>'
    )


def _screen_text(text: str, x: float, y: float, size: int, fill: str) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{size}" fill="{fill}">{escape(text)}</text>'
    )
