#!/usr/bin/env python3
"""Generate a small representative set of hourglass SVGs."""

from __future__ import annotations

from pathlib import Path

from hourglass_stealth.geometry_core import GeometryConfig, sample_input_rays
from hourglass_stealth.raytrace import trace_rays
from hourglass_stealth.svg import write_svg


def main() -> None:
    output_dir = Path("geometry/out")
    output_dir.mkdir(parents=True, exist_ok=True)
    for beta_deg in (0.26, 1.0, 3.0, 5.0):
        config = GeometryConfig(beta_deg=beta_deg, front_span_z=0.5)
        rays = sample_input_rays(config, mode="extremal", num_rays=24, seed=0)
        results, metrics = trace_rays(config, rays, max_bounces=8)
        name = f"hourglass_beta_{str(beta_deg).replace('.', 'p')}_extremal.svg"
        output_path = output_dir / name
        write_svg(output_path, config, results, metrics, title=f"Hourglass beta={beta_deg:g} deg extremal")
        print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
