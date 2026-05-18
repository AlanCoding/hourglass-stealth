# Cylinder Grazing-Absorption Optimization

This note derives an approximate length-to-diameter optimization for a mirrored cylindrical spacecraft whose flat end points directly at the Sun.

The goal is to minimize absorbed solar heat for a fixed internal volume.

The motivating geometry is a long mirrored cylinder, like a Coke can, with:

- one flat circular end facing the Sun directly;
- a cylindrical side wall aligned nearly parallel to the incoming solar rays;
- all exterior surfaces treated as mirrors;
- direct sunlight on the side wall arising only from the finite angular radius of the Sun.

Because the Sun is not a point source, sunlight arrives over a small cone of angles. For a cylinder aligned with the Sun, rays from the edge of the solar disk strike the side wall at extremely grazing incidence. This creates a small but nonzero side-wall heating term.

The optimization balances two effects:

1. **Short, fat cylinder:** large front-facing area, therefore large normal-incidence absorption.
2. **Long, thin cylinder:** small front-facing area, but large side-wall area, so even tiny grazing-angle leakage accumulates.

This produces a finite optimum length-to-diameter ratio.

---

## 1. Definitions

Let:

\[
\beta = \text{solar angular radius}
\]

At Earth distance:

\[
\beta \approx 0.26^\circ
\]

In radians:

\[
\beta = 0.26^\circ \times \frac{\pi}{180}
\]

\[
\beta \approx 4.54\times 10^{-3}\ \mathrm{rad}
\]

For the cylinder:

- \(R\) = cylinder radius
- \(D = 2R\) = cylinder diameter
- \(L\) = cylinder length
- \(V\) = fixed volume
- \(S\) = solar irradiance at the spacecraft location
- \(A_f\) = absorbed fraction of the front mirror at normal incidence
- \(\alpha\) = grazing angle above the mirror surface
- \(A(\alpha)\) = absorbed fraction for a ray striking at grazing angle \(\alpha\)

Cylinder volume:

\[
V = \pi R^2 L
\]

---

## 2. Grazing-angle mirror absorption relation

For extreme grazing incidence, the absorbed fraction of a good metallic mirror can be approximated as proportional to the grazing angle:

\[
A(\alpha) = K\alpha
\]

where:

- \(\alpha\) is measured in radians;
- \(K\) is a coating/material constant.

A practical placeholder range for an excellent metallic mirror is:

\[
K \sim 0.1 \text{ to } 0.4
\]

Equivalently, define:

\[
A_\beta = A(\beta)
\]

where \(A_\beta\) is the absorbed fraction for a ray at the solar-limb grazing angle.

Since:

\[
A_\beta = K\beta
\]

we can write:

\[
K = \frac{A_\beta}{\beta}
\]

and therefore:

\[
A(\alpha) = A_\beta \left(\frac{\alpha}{\beta}\right)
\]

A useful first-pass value is:

\[
A_\beta \sim 10^{-3}
\]

so:

\[
A(\alpha) \approx 10^{-3}\left(\frac{\alpha}{0.26^\circ}\right)
\]

with \(\alpha\) interpreted as a grazing angle above the mirror surface.

---

## 3. Front-face absorbed power

The front face receives full solar irradiance at normal incidence.

The front area is:

\[
A_\text{front,geom} = \pi R^2
\]

The absorbed power on the front face is:

\[
P_\text{front} = S A_f \pi R^2
\]

---

## 4. Side-wall illumination from finite solar angular radius

The side wall is nearly parallel to the incoming solar rays. If the Sun were a point source exactly on the cylinder axis, the side wall would receive no direct sunlight.

But the Sun has angular radius \(\beta\). Rays from the solar disk arrive with small transverse components. These rays strike the cylindrical wall at grazing angles ranging from 0 to approximately \(\beta\).

For a uniformly bright solar disk, the side-wall absorbed heat flux, averaged over the cylinder circumference, is:

\[
q_\text{side} = S\frac{K\beta^2}{8}
\]

where \(q_\text{side}\) is absorbed power per unit side-wall area.

Using \(K = A_\beta/\beta\), this can also be written as:

\[
q_\text{side} = S\frac{A_\beta\beta}{8}
\]

This is a very small fraction of full sunlight.

For \(A_\beta = 10^{-3}\) and \(\beta = 4.54\times 10^{-3}\):

\[
\frac{q_\text{side}}{S}
= \frac{10^{-3}(4.54\times10^{-3})}{8}
\]

\[
\frac{q_\text{side}}{S}
\approx 5.7\times10^{-7}
\]

At 1 AU, using:

\[
S \approx 1361\ \mathrm{W/m^2}
\]

this gives:

\[
q_\text{side} \approx 7.7\times10^{-4}\ \mathrm{W/m^2}
\]

So the side wall absorbs less than a milliwatt per square meter under these assumptions.

---

## 5. Total side-wall absorbed power

The side-wall area is:

\[
A_\text{side,geom} = 2\pi R L
\]

Therefore:

\[
P_\text{side} = 2\pi R L \cdot S\frac{K\beta^2}{8}
\]

\[
P_\text{side} = S\frac{K\beta^2}{4}\pi R L
\]

Using \(K = A_\beta/\beta\):

\[
P_\text{side} = S\frac{A_\beta\beta}{4}\pi R L
\]

---

## 6. Total absorbed power

Total absorbed power is front absorption plus side absorption:

\[
P_\text{abs} = P_\text{front} + P_\text{side}
\]

\[
P_\text{abs}
=
S A_f \pi R^2
+
S\frac{K\beta^2}{4}\pi R L
\]

Now impose fixed volume:

\[
V = \pi R^2 L
\]

so:

\[
L = \frac{V}{\pi R^2}
\]

Substitute into the total absorbed power:

\[
P_\text{abs}
=
S A_f \pi R^2
+
S\frac{K\beta^2}{4}\pi R\left(\frac{V}{\pi R^2}\right)
\]

\[
P_\text{abs}
=
S A_f \pi R^2
+
S\frac{K\beta^2V}{4R}
\]

This has the expected form:

\[
P_\text{abs}(R)
=
\text{front term growing as }R^2
+
\text{side term growing as }\frac{1}{R}
\]

Therefore there is a finite optimum.

---

## 7. Optimized radius

Minimize:

\[
P(R) = S A_f \pi R^2 + S\frac{K\beta^2V}{4R}
\]

Take the derivative with respect to \(R\):

\[
\frac{dP}{dR}
=
2S A_f\pi R
-
S\frac{K\beta^2V}{4R^2}
\]

Set the derivative equal to zero:

\[
2S A_f\pi R
=
S\frac{K\beta^2V}{4R^2}
\]

Cancel \(S\):

\[
2A_f\pi R
=
\frac{K\beta^2V}{4R^2}
\]

Multiply by \(R^2\):

\[
2A_f\pi R^3
=
\frac{K\beta^2V}{4}
\]

Solve for \(R^3\):

\[
R^3
=
\frac{K\beta^2V}{8\pi A_f}
\]

So the optimized radius is:

\[
R_\star
=
\left(
\frac{K\beta^2V}{8\pi A_f}
\right)^{1/3}
\]

Using \(A_\beta = K\beta\):

\[
R_\star
=
\left(
\frac{A_\beta\beta V}{8\pi A_f}
\right)^{1/3}
\]

The optimized length is:

\[
L_\star = \frac{V}{\pi R_\star^2}
\]

---

## 8. Optimized length-to-diameter ratio

The length-to-diameter ratio is:

\[
\frac{L}{D}
=
\frac{L}{2R}
\]

Using fixed volume:

\[
L = \frac{V}{\pi R^2}
\]

so:

\[
\frac{L}{D}
=
\frac{V}{2\pi R^3}
\]

At the optimum:

\[
R_\star^3 = \frac{K\beta^2V}{8\pi A_f}
\]

Therefore:

\[
\left(\frac{L}{D}\right)_\star
=
\frac{V}{2\pi}
\frac{8\pi A_f}{K\beta^2V}
\]

Cancel \(V\) and \(\pi\):

\[
\left(\frac{L}{D}\right)_\star
=
\frac{4A_f}{K\beta^2}
\]

Using \(K = A_\beta/\beta\):

\[
\left(\frac{L}{D}\right)_\star
=
\frac{4A_f}{A_\beta\beta}
\]

This is the main result:

\[
\boxed{
\left(\frac{L}{D}\right)_\star
=
\frac{4A_f}{A_\beta\beta}
}
\]

For \(\beta = 4.54\times 10^{-3}\):

\[
\frac{4}{\beta} \approx 881
\]

so:

\[
\boxed{
\left(\frac{L}{D}\right)_\star
\approx
881\left(\frac{A_f}{A_\beta}\right)
}
\]

This ratio is independent of total volume.

Volume determines the absolute size of the optimized cylinder, but not the optimized shape.

---

## 9. Interpretation

The optimum is controlled mainly by the ratio:

\[
\frac{A_f}{A_\beta}
\]

where:

- \(A_f\) is the normal-incidence absorption of the front mirror;
- \(A_\beta\) is the grazing-incidence absorption of the side mirror at the solar-limb grazing angle.

If the front and side mirrors had equal absorption fractions:

\[
A_f = A_\beta
\]

then:

\[
\left(\frac{L}{D}\right)_\star \approx 881
\]

This is extremely long.

But if the front face can be made much better than the side-limb grazing absorption, the optimum becomes much shorter.

For example, if:

\[
A_f = 10^{-4}
\]

and:

\[
A_\beta = 10^{-3}
\]

then:

\[
\frac{A_f}{A_\beta} = 0.1
\]

and:

\[
\left(\frac{L}{D}\right)_\star \approx 88
\]

If:

\[
A_f = 10^{-5}
\]

and:

\[
A_\beta = 10^{-3}
\]

then:

\[
\left(\frac{L}{D}\right)_\star \approx 8.8
\]

This means that the practical shape is extremely sensitive to the relative performance of the front mirror and the grazing-incidence side mirror.

---

## 10. Example table

Using:

\[
\beta = 0.26^\circ = 4.54\times10^{-3}\ \mathrm{rad}
\]

| Front absorption \(A_f\) | Side limb absorption \(A_\beta\) | Optimal \(L/D\) |
|---:|---:|---:|
| \(10^{-3}\) | \(10^{-3}\) | 881 |
| \(3\times10^{-4}\) | \(10^{-3}\) | 264 |
| \(10^{-4}\) | \(10^{-3}\) | 88 |
| \(3\times10^{-5}\) | \(10^{-3}\) | 26 |
| \(10^{-5}\) | \(10^{-3}\) | 8.8 |
| \(10^{-4}\) | \(2\times10^{-3}\) | 44 |
| \(10^{-4}\) | \(5\times10^{-4}\) | 176 |

---

## 11. Heat-balance property at the optimum

At the optimum, the side absorption is twice the front absorption:

\[
P_\text{side} = 2P_\text{front}
\]

Therefore:

\[
P_\text{total} = 3P_\text{front}
\]

This is a useful sanity check.

The optimum is not where front and side heating are equal. Because the front term scales as \(R^2\), while the side term scales as \(1/R\), the minimum occurs when the side penalty is twice the front penalty.

---

## 12. Calculator-ready formula set

Use these as the minimal implementation formulas.

Solar angular radius:

\[
\beta = 0.26^\circ \times \frac{\pi}{180}
\]

\[
\beta \approx 4.54\times10^{-3}
\]

Grazing absorption law:

\[
A(\alpha) = A_\beta\left(\frac{\alpha}{\beta}\right)
\]

Side absorbed flux per unit side area:

\[
q_\text{side} = S\frac{A_\beta\beta}{8}
\]

Front absorbed power:

\[
P_\text{front} = S A_f \pi R^2
\]

Side absorbed power:

\[
P_\text{side} = S\frac{A_\beta\beta}{4}\pi R L
\]

Total absorbed power:

\[
P_\text{abs}
=
S A_f \pi R^2
+
S\frac{A_\beta\beta}{4}\pi R L
\]

Fixed-volume substitution:

\[
L=\frac{V}{\pi R^2}
\]

Optimized radius:

\[
R_\star
=
\left(
\frac{A_\beta\beta V}{8\pi A_f}
\right)^{1/3}
\]

Optimized length:

\[
L_\star = \frac{V}{\pi R_\star^2}
\]

Optimized length-to-diameter ratio:

\[
\left(\frac{L}{D}\right)_\star
=
\frac{4A_f}{A_\beta\beta}
\]

Numerically, at 1 AU solar angular radius:

\[
\left(\frac{L}{D}\right)_\star
\approx
881\left(\frac{A_f}{A_\beta}\right)
\]

---

## 13. Main design conclusion

For a mirrored cylinder pointed directly at the Sun, the optimal shape is long and thin, but not infinitely long.

The front face absorbs full-intensity sunlight over an area \(\pi R^2\). The side wall receives only finite-solar-disk leakage, and that leakage arrives at extreme grazing incidence. This makes side-wall absorption extraordinarily small per unit area, but the side area grows as the cylinder is elongated.

The resulting optimum is:

\[
\boxed{
\left(\frac{L}{D}\right)_\star
\approx
881\left(\frac{A_f}{A_\beta}\right)
}
\]

For a plausible stealth-mirror case:

\[
A_f \sim 10^{-4}
\]

\[
A_\beta \sim 10^{-3}
\]

then:

\[
\left(\frac{L}{D}\right)_\star \sim 90
\]

This is the first serious shape result to carry forward.

---

## 14. Caveats and next steps

This is a first-order model. It assumes:

1. The Sun is a uniformly bright disk.
2. The cylinder axis points exactly at the Sun.
3. The side-wall grazing absorption law is linear in grazing angle.
4. The side wall is smooth enough for extreme grazing reflection to behave ideally.
5. Diffraction, roughness, micrometeoroid damage, coating defects, thermal distortion, and contamination are ignored.
6. The front face and side wall are represented by scalar absorption fractions rather than wavelength-dependent coating models.

The next refinement should replace the scalar values \(A_f\) and \(A_\beta\) with wavelength-integrated solar-spectrum absorption:

\[
A_\text{solar}(\alpha)
=
\frac{
\int A(\lambda,\alpha) I_\odot(\lambda)\,d\lambda
}{
\int I_\odot(\lambda)\,d\lambda
}
\]

But for early geometry and sizing work, the closed-form result above is useful because it shows the key dependency clearly:

\[
\left(\frac{L}{D}\right)_\star
\propto
\frac{A_f}{A_\beta}
\]

The entire design question reduces to how good the front mirror can be compared with the side mirror at solar-limb grazing incidence.
