"""Core package for hourglass stealth calculation tooling."""

from hourglass_stealth.geometry_core import GeometryConfig
from hourglass_stealth.raytrace import trace_rays
from hourglass_stealth.scenarios import evaluate_scenario

__all__ = [
    "__version__",
    "GeometryConfig",
    "evaluate_scenario",
    "trace_rays",
]

__version__ = "0.1.0"
