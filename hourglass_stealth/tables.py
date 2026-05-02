"""Assumption table builders for notebook and export workflows."""

from hourglass_stealth.constants import EMISSIVITY_GRADES, HEAT_STORE_DEFAULTS, OPTICAL_ABSORPTION_GRADES


def _require_pandas():
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "pandas is required for table builders. Install the project dev dependencies first."
        ) from exc
    return pd


def optical_absorption_grade_table():
    pd = _require_pandas()
    rows = []
    for grade, values in OPTICAL_ABSORPTION_GRADES.items():
        rows.append(
            {
                "grade": grade,
                "mirror_absorption_per_pass": values["mirror_absorption_per_pass"],
                "lens_absorption_per_pass": values["lens_absorption_per_pass"],
                "interpretation": values["interpretation"],
            }
        )
    return pd.DataFrame(rows)


def emissivity_grade_table():
    pd = _require_pandas()
    rows = []
    for grade, values in EMISSIVITY_GRADES.items():
        rows.append(
            {
                "grade": grade,
                "emissivity": values["emissivity"],
                "interpretation": values["interpretation"],
            }
        )
    return pd.DataFrame(rows)


def heat_store_candidate_table():
    pd = _require_pandas()
    rows = []
    for candidate in HEAT_STORE_DEFAULTS:
        rows.append(
            {
                "temperature_band_k": f"{candidate['temperature_min_k']:.0f}-{candidate['temperature_max_k']:.0f}",
                "material_class": candidate["material_class"],
                "rho_initial_kg_m3": candidate["rho_initial_kg_m3"],
                "rho_final_kg_m3": candidate["rho_final_kg_m3"],
                "usable_energy_j_kg": candidate["usable_energy_j_kg"],
                "usable_energy_mj_kg": candidate["usable_energy_j_kg"] / 1_000_000.0,
                "pressure_flag": candidate["pressure_flag"],
                "notes": candidate["notes"],
            }
        )
    return pd.DataFrame(rows)
