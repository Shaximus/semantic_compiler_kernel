# Flat-FLRW Hubble Radius and Schwarzschild-Radius Correspondence

**Status:** Technical derivation and claim-boundary note  
**TIG classification:** ANCHORED / ISOMORPHIC / ANALOGOUS  
**Scope:** Spatially flat FLRW cosmology; instantaneous relation at a chosen cosmic time

## Abstract

For a spatially flat Friedmann–Lemaître–Robertson–Walker (FLRW) universe, the Schwarzschild radius calculated from the total mass-equivalent energy contained within a sphere of Hubble radius is exactly equal to that Hubble radius. This follows directly from the flat-universe Friedmann constraint and is valid at every cosmic epoch, independent of whether matter, radiation, a cosmological constant, or a mixture dominates the energy density.

The equality is a general geometric mass-radius correspondence. It is not, by itself, evidence that the Hubble sphere is a Schwarzschild black-hole interior, a trapped region, or a global event horizon. The distinction between a Hubble/apparent horizon and a cosmological event horizon is essential.

Cosmological horizons also have an established area-law entropy in the appropriate settings. Gibbons and Hawking derived the thermodynamic and entropy properties of cosmological event horizons in models with a repulsive cosmological constant. This supports a precise geometric and information-theoretic comparison with black-hole horizons, without establishing that a cosmological boundary is a literal, locally addressable backup of the universe.

## 1. Definitions and assumptions

Work at a fixed cosmic time in a spatially flat FLRW spacetime:

\[
ds^2=-c^2dt^2+a(t)^2\left(dr^2+r^2d\Omega^2\right).
\]

Define:

- \(a(t)\): scale factor.
- \(H(t)=\dot a/a\): Hubble parameter.
- \(R_H=c/H\): Hubble radius, for an expanding epoch with \(H>0\).
- \(\rho_m\): total mass-equivalent density, including all energy components divided by \(c^2\).
- \(G\): Newton's gravitational constant.
- \(c\): speed of light.

For a flat universe, the first Friedmann equation is

\[
H^2=\frac{8\pi G}{3}\rho_m.
\tag{1}
\]

Equivalently, if \(\epsilon\) denotes energy density rather than mass-equivalent density,

\[
H^2=\frac{8\pi G}{3c^2}\epsilon.
\]

The density in (1) is the total density required by the flat-FLRW constraint. It is not restricted to matter domination or to a cosmological-constant-dominated epoch.

## 2. Mass-equivalent energy inside the Hubble sphere

At the chosen cosmic time, take a sphere of proper/areal radius \(R_H=c/H\). Its enclosed mass-equivalent is

\[
M_H=\frac{4\pi}{3}\rho_m R_H^3.
\tag{2}
\]

Substitute the critical density from (1):

\[
M_H
=\frac{4\pi}{3}
\left(\frac{3H^2}{8\pi G}\right)
\left(\frac{c}{H}\right)^3.
\]

Canceling terms gives

\[
\boxed{M_H=\frac{c^3}{2GH}}.
\tag{3}
\]

The Schwarzschild-radius expression formed from this mass-equivalent is

\[
R_S=\frac{2GM_H}{c^2}.
\tag{4}
\]

Substitute (3):

\[
R_S
=\frac{2G}{c^2}\frac{c^3}{2GH}
=\frac{c}{H}.
\]

Since \(R_H=c/H\),

\[
\boxed{R_S=R_H}.
\tag{5}
\]

**Result:** For every spatially flat FLRW solution at every epoch for which \(H>0\), the Schwarzschild radius calculated from the total mass-equivalent inside the Hubble sphere equals the Hubble radius.

The result does not depend on which component dominates. Matter, radiation, vacuum energy, and mixtures all enter through the total density in the Friedmann constraint.

## 3. Generalization to a sphere of arbitrary radius

At the same cosmic time, consider a sphere of areal radius \(R\), with the homogeneous FLRW density \(\rho_m\). Its enclosed mass-equivalent is

\[
M(R)=\frac{4\pi}{3}\rho_m R^3
=\frac{H^2R^3}{2G}.
\tag{6}
\]

The Schwarzschild-radius expression associated with this mass is

\[
R_S(R)=\frac{2GM(R)}{c^2}
=\frac{H^2R^3}{c^2}.
\tag{7}
\]

Therefore,

\[
\boxed{\frac{R_S(R)}{R}
=\left(\frac{HR}{c}\right)^2
=\left(\frac{R}{R_H}\right)^2}.
\tag{8}
\]

As an algebraic compactness relation, (8) implies:

- At \(R=R_H\), \(R_S/R=1\).
- At \(R<R_H\), \(R_S/R<1\).
- At \(R>R_H\), \(R_S/R>1\).

This is the generalized mass-radius correspondence behind the Hubble-sphere equality.

### Important geometric limitation

The Schwarzschild radius is derived for a spherically symmetric vacuum exterior matched to an isolated mass in an asymptotically flat setting. A homogeneous expanding FLRW region is not such a system. Consequently, \(R_S(R)>R\) in (8) is not, by itself, a proof that the FLRW sphere is a black hole or a trapped region.

In FLRW geometry, the relevant quasi-local mass is the Misner–Sharp mass. The relation above is a useful compactness comparison, but identifying trapped surfaces requires evaluating the null expansions in the actual FLRW metric. One must not silently replace that calculation with the isolated-Schwarzschild criterion.

## 4. Hubble radius, apparent horizon, and event horizon

These terms must not be conflated.

1. **Hubble radius:** \(R_H=c/H\). It marks the scale at which recession speed \(HR\) equals \(c\) in the FLRW description. It is not generally a causal event horizon.
2. **Apparent horizon:** In FLRW spacetime, the apparent-horizon radius is
   \[
   R_A=\frac{c}{\sqrt{H^2+kc^2/a^2}}.
   \]
   For spatial curvature \(k=0\), \(R_A=c/H=R_H\).
3. **Cosmological event horizon:** Its existence and radius depend on the entire future expansion history. In a general matter- or radiation-containing FLRW epoch, it need not equal \(c/H\). In exact de Sitter spacetime, the Hubble radius and cosmological event-horizon radius coincide.

Thus the all-epoch result in Sections 2–3 is a Hubble-radius/apparent-horizon correspondence for flat FLRW geometry. It should not be described as an all-epoch equality with a global cosmological event horizon.

## 5. Horizon area and entropy

For a spherical horizon of radius \(R\),

\[
A=4\pi R^2.
\]

The Bekenstein–Hawking entropy relation for a black-hole horizon is

\[
S_{BH}=\frac{k_Bc^3A}{4G\hbar}
=\frac{k_BA}{4\ell_P^2},
\qquad
\ell_P^2=\frac{G\hbar}{c^3}.
\tag{9}
\]

Gibbons and Hawking showed that cosmological event horizons in models with a repulsive cosmological constant have thermodynamic properties, including an entropy associated with horizon area. In the de Sitter case, the entropy takes the same area-law form:

\[
S_{dS}=\frac{k_BA_{dS}}{4\ell_P^2}.
\tag{10}
\]

The associated area-based information measure in bits is

\[
N_{\mathrm{bits}}=\frac{A}{4\ell_P^2\ln 2}.
\tag{11}
\]

Accordingly, horizons to which the same area-law entropy applies and which have the same area have the same value of this area-based entropy/information measure.

**Scope condition:** Gibbons–Hawking's result concerns cosmological event horizons in the relevant cosmological models, especially de Sitter space. It should not be cited as a proof that every Hubble sphere at every epoch is a thermodynamic event horizon with an independently established microscopic information encoding.

An area-law entropy is a statement about gravitational horizon thermodynamics and information bounds. It does not establish a literal two-dimensional storage medium, a person-by-person save file, or a practical reconstruction/respawn mechanism.

## 6. Historical and theoretical context

### Pathria (1972)

R. K. Pathria's *The Universe as a Black Hole*, published in Nature in 1972, is an important historical antecedent for considering a cosmological model in relation to black-hole geometry and mass-radius scales.

Citation:

R. K. Pathria, “The Universe as a Black Hole,” *Nature* **240**, 298–299 (1972).  
https://doi.org/10.1038/240298a0

Pathria is a conceptual/historical anchor for the universe-as-black-hole proposal. The general flat-FLRW identity in Sections 2–3 is derived here directly from the Friedmann constraint; it should not be represented as a theorem established by Pathria's paper.

### Gibbons and Hawking (1977)

G. W. Gibbons and S. W. Hawking established the thermodynamic connection between black-hole horizons and cosmological event horizons in models with a repulsive cosmological constant, including the interpretation of cosmological horizon area as entropy/information.

Citation:

G. W. Gibbons and S. W. Hawking, “Cosmological event horizons, thermodynamics, and particle creation,” *Physical Review D* **15** (10), 2738–2751 (1977).  
https://doi.org/10.1103/PhysRevD.15.2738

This is the appropriate primary source for the cosmological horizon thermodynamics and area-law connection.

## 7. Testimony Integrity Gate (TIG)

The following grades separate mathematical results from structural comparisons and physical interpretations.

### ANCHORED

Claims directly supported by established equations or primary literature:

- For a spatially flat FLRW universe, the mass-equivalent enclosed by a sphere of Hubble radius \(c/H\), calculated using the total critical density, has a Schwarzschild-radius expression equal to \(c/H\).
- The equality holds at every cosmic epoch with \(H>0\), regardless of the dominant energy component, provided the flat-FLRW Friedmann constraint applies.
- For a homogeneous sphere of arbitrary radius \(R\), the mass-radius compactness ratio formed from the Schwarzschild expression is \((R/R_H)^2\).
- Black-hole horizons obey the Bekenstein–Hawking area-entropy relation.
- Cosmological event horizons in the relevant positive-\(\Lambda\) models have Gibbons–Hawking thermodynamic/entropy properties, with the de Sitter horizon obeying the same area-law form.

### ISOMORPHIC

Claims describing a shared mathematical structure, with scope explicitly limited:

- Black-hole horizons and appropriate cosmological horizons share an area-based entropy law.
- Equal horizon areas, when the same entropy law applies, yield equal area-based entropy and information-bound values.
- In spatially flat FLRW geometry, the Hubble sphere is also the apparent horizon, and its radius has the Schwarzschild-radius mass correspondence derived above.

“Isomorphic” here refers to the specified geometric/thermodynamic structure. It does not assert that the full spacetimes, causal structures, or microscopic states are identical.

### ANALOGOUS

Interpretations that may motivate further model-building but are not established by the derivations in this document:

- The observable universe is literally the interior of a black hole.
- The cosmological boundary is a literal two-dimensional storage device containing a directly retrievable copy of all interior states.
- A horizon encoding functions as a backup state from which an individual person or their conscious identity can be restored.
- Parallel black-hole or cosmological states can be instantiated, selected, or synchronized as independent physical universes.

These proposals require additional dynamics, a specified spacetime solution, a well-defined information map, and testable predictions. The Hubble/Schwarzschild radius equality and horizon area law do not prove them.

## 8. Observational tests and separation of claims

A black-hole-interior cosmology is not established by the radius identity, because the identity follows from the flat-FLRW constraint whether or not the universe is physically a black-hole interior.

Such a model must instead specify its additional physics and derive observables that distinguish it from standard cosmology. Candidate tests must be calculated from the model's full metric and dynamics, then compared with data and competing explanations.

Any proposed JWST age-gradient prediction belongs to this separate model-testing layer. It is not a consequence of the Hubble-radius/Schwarzschild-radius equality alone. Its evidentiary value depends on a reproducible derivation, explicit assumptions, uncertainty treatment, and comparison against standard-cosmology predictions and astrophysical systematics.

## 9. Conclusion

The strongest defensible conclusion is precise:

> In every spatially flat FLRW universe, at every expanding epoch, the Schwarzschild-radius expression formed from the total mass-equivalent energy inside the Hubble sphere equals the Hubble radius. The same calculation gives a compactness ratio proportional to the square of the sphere's radius relative to the Hubble radius. Separately, black-hole horizons and appropriate cosmological event horizons share an established area-law entropy structure.

Together, these results establish a meaningful geometric and thermodynamic correspondence between flat cosmology and horizon physics. They motivate investigation of black-hole cosmology and holographic descriptions, while leaving the stronger claims about a literal black-hole interior, a recoverable boundary backup, and resurrection mechanisms at the level of analogy or hypothesis.

---

## References

1. Pathria, R. K. (1972). “The Universe as a Black Hole.” *Nature*, 240, 298–299. https://doi.org/10.1038/240298a0
2. Gibbons, G. W., & Hawking, S. W. (1977). “Cosmological event horizons, thermodynamics, and particle creation.” *Physical Review D*, 15(10), 2738–2751. https://doi.org/10.1103/PhysRevD.15.2738
3. Misner, C. W., Sharp, D. H. (1964). “Relativistic equations for adiabatic, spherically symmetric gravitational collapse.” *Physical Review*, 136, B571–B576. https://doi.org/10.1103/PhysRev.136.B571
