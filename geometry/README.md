# Geometry Module For Finite Solar Angle Hourglass Correction

This folder contains a specialized geometry, ray-transport, and SVG workflow for the mirror-based hourglass concept. It is not a generic optics renderer. The model is intentionally limited to the 2-D cross-section needed to study finite solar angular spread and the two displaced radiance skirts it creates.

## Problem Statement

The hourglass mirror uses front and rear conical or frustum mirror sections at nominal angle `alpha = 22.5 deg` from the `+z` axis, with an open central throat. Parallel sunlight is the easy case. Finite solar half-angle `beta` broadens the reflected family and shifts the rear footprint so that some rays land below the nominal rear mirror span and some land above it.

Those two overflow regions are the key object of study:

- Bottom skirt: rays displaced below the nominal rear mirror footprint.
- Top skirt: rays displaced above the nominal rear mirror footprint.

These skirts are not extra flux. They are displaced radiance, so the correction strategy is to return them to the regions whose shine they depleted.

## Parallel-Ray Baseline

Let:

- `a = aperture_width / 2`
- `alpha = mirror angle from vertical`
- `t = tan(alpha)`
- `h = front mirror vertical span`

For the right front mirror:

`P_f(s) = (a - s tan alpha, s)`, for `0 <= s <= h`

At the 22.5 degree baseline:

- `alpha = 22.5 deg`
- `2 alpha = 45 deg`

A parallel incoming ray reflects inward at `2 alpha`, so for the baseline geometry the rear active mirror span equals the front active span:

`Delta z_rear = Delta z_front = h`

That equality is preserved explicitly in the package geometry builder.

## Finite Angular Spread And Skirts

Let the incoming solar deviation be:

`phi in [-beta, +beta]`

For the right front mirror the post-front-reflection slope family is:

`k(phi) = tan(2 alpha + phi)`

For `alpha = 22.5 deg` this becomes:

`k(phi) = tan(45 deg + phi)`

A reflected ray launched from front coordinate `s` follows:

`x(z; s, phi) = a - s tan alpha - k(phi)(z - s)`

Numerically, the family intersects the nominal rear line over a shifted interval rather than the exact parallel-ray interval. One angular edge reaches below the rear span and the opposite edge reaches above it, which creates the bottom and top skirts.

## Why Rear-Mirror Translation Alone Fails

Changing only the rear mirror offset can move where the nominal rear span sits, but it does not remove the fact that the finite-angle family has two opposite overflow directions. Solving one skirt by translation alone tends to worsen the other. This package therefore treats the finite-angle problem as a phase-space restoration problem rather than a single-parameter alignment problem.

## Bottom-Skirt Restoration

The bottom skirt is corrected with a vertical throat mirror placed in the open throat region. In the SVGs this region is drawn in blue. The implementation computes the actually used hit interval numerically rather than assuming the full vertical connector is active. A dead region is therefore allowed naturally by the traced hit set.

## Top-Skirt Restoration

The top skirt requires a different correction because the displaced rays overflow above the rear mirror span. The package models a macroscopic wall at `x = +-a` and assigns local sawtooth or microfacet angles along that wall so that the top-skirt rays are redirected first into an unused return band at the lower part of the opposite throat, then reflected back into the upper edge of the corresponding rear mirror.

The local facet-angle rule is:

`theta_facet = (gamma + delta) / 2`

where `gamma` and `delta` are the incoming and desired outgoing direction angles in the same signed convention. The code uses a conservative two-step target map unless a more exact analytic mapping is supplied:

- Lower part of the top-skirt wall hit interval maps to the lower throat return band.
- Upper part of the wall hit interval maps slightly higher in that return band.
- That throat return band then maps into the upper portion of the rear mirror span, near the top edge, to complete the pass-through.

This preserves the macroscopic wall boundary while allowing local facet angles to vary.

## Success Criterion

The model does not optimize for exact ray identity. It accepts angular rearrangement within the solar disk. The relaxed requirement used by the sweep and SVG tools is:

`The outgoing ray must remain inside the original solar angular cone and exit forward.`

So `phi_out` does not need to equal `phi_in`. Texture scrambling, sign reversal, and within-cone rearrangement are acceptable at this stage.

## Scripts

Generate one SVG:

```bash
python geometry/make_geometry_svg.py --beta-deg 3 --mode extremal --output geometry/out/test.svg
```

Generate representative cases:

```bash
python geometry/make_representative_svgs.py
```

Run a parameter sweep:

```bash
python geometry/sweep_geometry.py --beta-deg 3
```

## Known Limitations / TODO

- Current wall-to-throat and throat-to-rear target mapping is conservative and heuristic unless a fuller closed-form solution is derived.
- Diffraction and finite facet pitch are ignored.
- Only a 2-D cross-section is modeled; full 3-D annular geometry remains future work.
- Scattering, absorption, manufacturability, and thermal loading are not modeled here.
- Solar texture scrambling is accepted in this stage.
