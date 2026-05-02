# Development Plan

## Purpose

This project is the technical calculation sheet behind a future blog post about a passive, low-emission "hourglass stealth spacecraft" concept.

It is not the blog post itself. Its job is to make assumptions explicit, run reusable calculations, and generate tables that can later feed the blog post.

## Primary Outputs

1. Passive sealed dwell time, in years.
2. Detection distance, primarily in Earth-Moon distances.

## Scope

The first implementation pass should model:

- Solar absorption through an inverse-hourglass optical path.
- Mirror and lens architecture variants.
- Sealed heat storage under volume constraints.
- Thermal emission as a function of emissivity, temperature, and area.
- A simplified detector-distance model.
- Earth and Moon heating penalties in cislunar space.
- Scenario grids and exported blog-ready tables.

## Out Of Scope

- Active cooling.
- Coolant ejection.
- Vented boiloff.
- Tactical maneuvering.
- High-fidelity detector engineering.
- Literal JWST instrument modeling.

## Modeling Stance

This repository is exploratory. Placeholder values are acceptable in the first pass if they are labeled clearly. The aim is a coherent, reusable pipeline, not a final authoritative answer.

## Locked Assumptions

These assumptions are now fixed for the first coding pass unless the concept changes later:

- Thermal emission is treated as homogeneous over the spacecraft surface.
- This is a deliberate simplification and a conservative one in favor of defense.
- The real detectability problem is angle-dependent, especially if mirrors or lenses become directly exposed to an observer.
- That angular dependence is an important strategic limitation and must be called out in the notebook and README.
- All scenarios assume perfect sun-axis alignment.
- Off-axis penalties are intentionally excluded from v1 because the model is meant to explore harder constraints first.

## Known Limitations To State Explicitly

- The emission model does not yet separate hull, baffles, mirrors, lenses, or throat-region surfaces.
- The model does not yet represent view-angle dependence or glint exposure.
- The model does not yet include pointing error, slewing, or transient thermal excursions.
- Survey detectability remains a simplified penalty-factor model rather than an instrument-specific end-to-end treatment.

## Package Plan

The library should provide reusable functions in these modules:

- `constants.py`: physical constants and rough default planetary placeholders.
- `optics.py`: optical absorption and absorbed solar power.
- `heat_store.py`: sealed-volume heat storage calculations and dwell-time helpers.
- `emission.py`: thermal luminosity, Wien peak, Planck spectrum, and band power.
- `detector.py`: collecting area, photon energy, flux, and distance formulas.
- `environment.py`: Earth/Moon IR and albedo heating approximations.
- `tables.py`: assumption tables as pandas DataFrames.
- `scenarios.py`: scenario evaluation wrapper over the lower-level functions.

## Notebook Plan

`notebooks/01_blog_calcs_sheet.ipynb` should eventually contain these sections:

1. Purpose and governing assumptions.
2. Design rating tables.
3. Architecture comparison: mirror vs lens absorption.
4. Heat-store candidates under sealed-volume constraints.
5. Emissivity and thermal luminosity.
6. Detector model and a JWST-scale benchmark.
7. Single baseline scenario.
8. Scenario grid for design grades.
9. Search for viable regions.
10. Optimized candidate cases.
11. Cislunar Earth/Moon heating penalties.
12. Operational envelope in cislunar space.
13. Blog-ready table exports.

## Baseline Scenario To Start With

- Architecture: `mirror`
- Optical grade: `B`
- Emissivity grade: `B`
- Solar aperture area: `10 m^2`
- Emitting area: `10 m^2`
- Heat-store volume: `10 m^3`
- Heat-store density placeholder: `1000 kg/m^3`
- Heat-store usable energy placeholder: `100_000 J/kg`
- Spacecraft temperature: `20 K`
- Detector diameter: `6.5 m`
- Detector throughput: `0.3`
- Integration time: `1000 s`
- Required signal photons: `25`
- Survey penalty factor: `1000`

## Default Heat-Store Classes By Temperature Range

For the first implementation pass, use non-exotic, liquid-dominated placeholder classes that fit the sealed-volume, liquid-to-liquid modeling stance as closely as practical.

These are defaults for modeling convenience, not final recommendations:

| Temperature band | Default class | Why it is the default | Notes |
| --- | --- | --- | --- |
| `4-25 K` | liquid hydrogen | Common cryogenic reference fluid with strong gravimetric heat capacity and plausible use in deep cryogenic storage models | Operationally difficult, low density, and not "easy", but still a standard industrial cryogen rather than an exotic material |
| `25-90 K` | liquid nitrogen | Simple, familiar cryogenic baseline around the `77 K` region | Best fit when the storage range stays near nitrogen temperatures; not suitable for `20 K` scenarios |
| `90-140 K` | liquid methane | Ordinary industrial cryogen with useful density and a natural fit near the `100 K` band | Better fit than nitrogen once the target temperature range is above nitrogen's liquid regime |
| `140-260 K` | liquid ammonia or light hydrocarbon placeholder | Keeps the model in a condensed, non-metallic, non-exotic regime through mid-cryogenic temperatures | Use as a class placeholder first; actual property selection can be refined later |
| `260-330 K` | water or water-glycol style liquid | Simple high-density baseline for warm cases | Strong volumetric baseline, easy to reason about, not relevant for the coldest stealth cases but useful for comparison |

### First-Pass Rule For The Notebook

When generating scenario tables, start with one default fluid class per temperature band:

- `4 K` and `10 K`: use `liquid hydrogen` placeholder values.
- `20 K`: still use `liquid hydrogen` placeholder values.
- `50 K`: use `liquid nitrogen` placeholder values.
- If later tables extend above `90 K`, switch to `liquid methane` until a more specific fluid is chosen.

### Parameterization Guidance

The code should not hardcode real property tables yet. Instead, it should let each candidate provide:

- `temperature_band`
- `material_class`
- `rho_initial_kg_m3`
- `rho_final_kg_m3`
- `usable_energy_j_kg`
- `pressure_flag`
- `notes`

That keeps the calculations reusable while leaving room to replace placeholders with sourced properties later.

## First Implementation Milestones

1. Implement tested core functions in the package.
2. Make the notebook import the local package and render the key assumption tables.
3. Run a baseline scenario end-to-end with clearly labeled placeholder assumptions where needed.
4. Export selected tables to `outputs/`.
5. Expand into scenario grids and cislunar heating sweeps.
