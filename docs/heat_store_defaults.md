# Heat-Store Defaults

This document captures first-pass default heat-store classes for the sealed-volume model.

## Intent

The model needs plausible placeholder storage fluids before material-property sourcing is done. These defaults are chosen to be familiar, non-exotic classes and to preserve a liquid-to-liquid framing wherever possible.

They are scaffolding values, not recommendations.

## Defaults By Temperature Range

| Temperature band | Default class | Rationale | Caveats |
| --- | --- | --- | --- |
| `4-25 K` | liquid hydrogen | Standard deep-cryogenic industrial fluid; plausible reference for very cold storage | Low density and difficult handling; likely the most operationally demanding baseline |
| `25-90 K` | liquid nitrogen | Familiar and easy default near `77 K` | Does not cover `20 K` scenarios |
| `90-140 K` | liquid methane | Ordinary cryogenic fluid with better fit above nitrogen's liquid range | Flammability and storage details deferred |
| `140-260 K` | liquid ammonia or light-hydrocarbon placeholder | Keeps mid-cryogenic cases in a simple condensed-fluid category | Use as a class placeholder until better sourced data exists |
| `260-330 K` | water or water-glycol style liquid | Straightforward high-density warm-case baseline | Mainly useful as a comparison class, not a stealth-favored cold case |

## Notebook Mapping

Use these defaults when a scenario temperature is provided without a specific fluid:

- `4 K`: liquid hydrogen
- `10 K`: liquid hydrogen
- `20 K`: liquid hydrogen
- `50 K`: liquid nitrogen
- `>90 K`: liquid methane until a better fit is specified

## Data Shape For Code

Each row in the eventual table should support these fields:

- `temperature_band`
- `material_class`
- `rho_initial_kg_m3`
- `rho_final_kg_m3`
- `usable_energy_j_kg`
- `pressure_flag`
- `notes`
