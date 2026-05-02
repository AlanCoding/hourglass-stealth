"""Physical constants and first-pass placeholder defaults."""

SOLAR_FLUX_1_AU_W_M2 = 1361.0
EARTH_MOON_DISTANCE_M = 384_400_000.0
SIGMA_SB = 5.670374419e-8
K_B = 1.380649e-23
H = 6.62607015e-34
C = 299_792_458.0

EARTH_RADIUS_M = 6_371_000.0
MOON_RADIUS_M = 1_737_400.0

# These planetary flux and albedo values are first-pass placeholders.
EARTH_EFFECTIVE_IR_FLUX_W_M2 = 239.0
MOON_EFFECTIVE_IR_FLUX_W_M2 = 240.0
EARTH_BOND_ALBEDO = 0.30
MOON_BOND_ALBEDO = 0.12

OPTICAL_ABSORPTION_GRADES = {
    "A": {
        "mirror_absorption_per_pass": 1e-5,
        "lens_absorption_per_pass": 1e-4,
        "interpretation": "heroic / speculative",
    },
    "B": {
        "mirror_absorption_per_pass": 1e-4,
        "lens_absorption_per_pass": 1e-3,
        "interpretation": "aggressive advanced engineering",
    },
    "C": {
        "mirror_absorption_per_pass": 1e-3,
        "lens_absorption_per_pass": 1e-2,
        "interpretation": "plausible-good but costly for stealth",
    },
    "D": {
        "mirror_absorption_per_pass": 1e-2,
        "lens_absorption_per_pass": 1e-1,
        "interpretation": "poor for stealth",
    },
}

EMISSIVITY_GRADES = {
    "A": {"emissivity": 1e-4, "interpretation": "heroic low-emissivity surface"},
    "B": {"emissivity": 1e-3, "interpretation": "aggressive engineered surface"},
    "C": {"emissivity": 1e-2, "interpretation": "good reflective surface"},
    "D": {"emissivity": 1e-1, "interpretation": "poor for stealth"},
}

HEAT_STORE_DEFAULTS = (
    {
        "temperature_min_k": 4.0,
        "temperature_max_k": 25.0,
        "material_class": "liquid hydrogen",
        "rho_initial_kg_m3": 71.0,
        "rho_final_kg_m3": 65.0,
        "usable_energy_j_kg": 220_000.0,
        "pressure_flag": "medium",
        "notes": "Placeholder liquid-to-liquid deep-cryogenic baseline.",
    },
    {
        "temperature_min_k": 25.0,
        "temperature_max_k": 90.0,
        "material_class": "liquid nitrogen",
        "rho_initial_kg_m3": 810.0,
        "rho_final_kg_m3": 760.0,
        "usable_energy_j_kg": 120_000.0,
        "pressure_flag": "low",
        "notes": "Placeholder baseline around the 77 K regime.",
    },
    {
        "temperature_min_k": 90.0,
        "temperature_max_k": 140.0,
        "material_class": "liquid methane",
        "rho_initial_kg_m3": 420.0,
        "rho_final_kg_m3": 370.0,
        "usable_energy_j_kg": 150_000.0,
        "pressure_flag": "medium",
        "notes": "Placeholder condensed-fluid baseline above nitrogen temperatures.",
    },
    {
        "temperature_min_k": 140.0,
        "temperature_max_k": 260.0,
        "material_class": "liquid ammonia",
        "rho_initial_kg_m3": 680.0,
        "rho_final_kg_m3": 610.0,
        "usable_energy_j_kg": 180_000.0,
        "pressure_flag": "medium",
        "notes": "Placeholder mid-cryogenic condensed-fluid baseline.",
    },
    {
        "temperature_min_k": 260.0,
        "temperature_max_k": 330.0,
        "material_class": "water",
        "rho_initial_kg_m3": 998.0,
        "rho_final_kg_m3": 983.0,
        "usable_energy_j_kg": 200_000.0,
        "pressure_flag": "low",
        "notes": "Warm-case volumetric comparison baseline.",
    },
)
