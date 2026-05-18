#!/usr/bin/env python3
"""Generate one deterministic SVG for the mirror-hourglass geometry."""

from __future__ import annotations

import argparse

from hourglass_stealth.geometry_core import GeometryConfig, sample_input_rays
from hourglass_stealth.raytrace import trace_rays
from hourglass_stealth.svg import write_png, write_svg


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beta-deg", type=float, default=0.26)
    parser.add_argument("--alpha-deg", type=float, default=22.5)
    parser.add_argument("--aperture-width", type=float, default=1.0)
    parser.add_argument("--front-span-z", type=float, default=0.5)
    parser.add_argument("--throat-half-width", type=float, default=None)
    parser.add_argument("--rear-start-z", type=float, default=None)
    parser.add_argument("--mode", choices=["extremal", "random", "grid"], default="extremal")
    parser.add_argument("--num-rays", type=int, default=24)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--include-bottom-throat-mirror", dest="include_bottom_throat_mirror", action="store_true")
    parser.add_argument("--no-include-bottom-throat-mirror", dest="include_bottom_throat_mirror", action="store_false")
    parser.set_defaults(include_bottom_throat_mirror=True)
    parser.add_argument("--include-top-sawtooth", dest="include_top_sawtooth", action="store_true")
    parser.add_argument("--no-include-top-sawtooth", dest="include_top_sawtooth", action="store_false")
    parser.set_defaults(include_top_sawtooth=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = GeometryConfig(
        aperture_width=args.aperture_width,
        alpha_deg=args.alpha_deg,
        beta_deg=args.beta_deg,
        front_span_z=args.front_span_z,
        throat_half_width=args.throat_half_width,
        rear_start_z=args.rear_start_z,
        include_bottom_throat_mirror=args.include_bottom_throat_mirror,
        include_top_sawtooth=args.include_top_sawtooth,
    )
    rays = sample_input_rays(config, mode=args.mode, num_rays=args.num_rays, seed=args.seed)
    results, metrics = trace_rays(config, rays, max_bounces=8)
    if args.output.lower().endswith(".png"):
        path = write_png(args.output, config, results, metrics, title=f"Hourglass beta={args.beta_deg:g} deg mode={args.mode}")
    else:
        path = write_svg(args.output, config, results, metrics, title=f"Hourglass beta={args.beta_deg:g} deg mode={args.mode}")
    print(f"wrote {path}")
    print(f"rays within cone: {metrics.rays_within_cone}/{metrics.total_rays}")
    print(f"max cone excess deg: {metrics.max_cone_excess_deg:.6f}")


if __name__ == "__main__":
    main()
