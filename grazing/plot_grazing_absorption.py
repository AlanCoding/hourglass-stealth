#!/usr/bin/env python3
"""
Plot grazing-incidence mirror absorption over the solar half-angle.

This is intended for the hourglass stealth spacecraft / mirrored-cylinder
discussion. The assumed small-grazing-angle relation is:

    A(alpha) = A_beta * alpha / beta

where:
    alpha  = grazing angle above the mirror surface
    beta   = solar angular radius, default 0.26 degrees
    A_beta = absorption fraction at alpha = beta

The default central value is A_beta = 1e-3, i.e. 0.1% absorption at
the solar limb grazing angle.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


# ----------------------------
# User-adjustable parameters
# ----------------------------

beta_deg = 90.0

# Plausible range used in the blog derivation:
# 5e-4  = 0.05% absorption at alpha = 0.26 deg
# 1e-3  = 0.10% absorption at alpha = 0.26 deg
# 2e-3  = 0.20% absorption at alpha = 0.26 deg
A_beta_values = [5e-4, 1e-3, 2e-3]

output_dir = Path(".")
png_name = "grazing_absorption_vs_angle.png"
svg_name = "grazing_absorption_vs_angle.svg"


# ----------------------------
# Calculation
# ----------------------------

alpha_deg = np.linspace(0.0, beta_deg, 400)

def absorption_fraction(alpha_deg, A_beta, beta_deg=0.26):
    """Linear grazing absorption relation."""
    return A_beta * alpha_deg / beta_deg


# ----------------------------
# Plot
# ----------------------------

fig, ax = plt.subplots(figsize=(8, 5))

for A_beta in A_beta_values:
    A = absorption_fraction(alpha_deg, A_beta, beta_deg)
    label = f"$A_\\beta = {A_beta:.0e}$ at $\\alpha = {beta_deg}^\\circ$"
    ax.plot(alpha_deg, A, label=label)

ax.set_title("Mirror Absorption at Extreme Grazing Incidence")
ax.set_xlabel("Grazing angle above mirror surface, $\\alpha$ (degrees)")
ax.set_ylabel("Absorbed fraction per reflection, $A(\\alpha)$")

ax.set_xlim(0, beta_deg)
ax.set_ylim(0, max(A_beta_values) * 1.08)

ax.grid(True, alpha=0.35)
ax.legend()

# Add a secondary y-axis showing percent absorption.
def fraction_to_percent(y):
    return 100 * y

def percent_to_fraction(y):
    return y / 100

secax = ax.secondary_yaxis("right", functions=(fraction_to_percent, percent_to_fraction))
secax.set_ylabel("Absorption per reflection (%)")

fig.tight_layout()

fig.savefig(output_dir / png_name, dpi=200)
fig.savefig(output_dir / svg_name)

print(f"Wrote {output_dir / png_name}")
print(f"Wrote {output_dir / svg_name}")
