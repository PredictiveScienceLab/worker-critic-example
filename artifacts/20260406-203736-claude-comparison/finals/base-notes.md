# Master Figure Notes

## Figure concept

A **three-column schematic flow diagram** (Input → Method → Output) showing how noisy multi-modal cardiovascular imaging data enter the Information Field Theory (IFT) framework and yield hemodynamic field reconstructions with full uncertainty quantification. The center column — the methodological engine — is the visual focal point, anchored by the posterior Hamiltonian equation. A bottom strip maps the four Specific Aims to the main flow. An innovation callout bar highlights what is new.

## Main content elements

| Element | Description |
|---|---|
| **Left column – Imaging Data** | Three imaging modalities: 4D Flow MRI, PC-MRI, and Color Doppler Echocardiography. Brief annotation of their inherent limitations (noisy, low-resolution, no native UQ). Key knowledge gaps listed. |
| **Center column – IFT Framework** | (1) **Posterior equation** H(φ\|d) = H(d\|Rφ) + H(φ) displayed prominently — the mathematical heart of the proposal. (2) Three concept panels: **Physics-Informed Prior** (encodes Navier–Stokes, Eikonal & continuity PDEs without a solver; model-form error via β; parametric BCs), **Measurement Model & Data Fusion** (modality-specific operators Rᵢ; additive data Hamiltonian; Bayesian co-registration), **Scalable Posterior Inference** (preconditioned SGLD; amortized variational inference; GPU data parallelism). (3) **Innovation bar** summarizing the four key novelties. |
| **Right column – Outputs & Impact** | Five output cards: hemodynamic fields with uncertainty, posterior over parameters, model-form error detection, clinical decision support, and open-source code with V&V benchmark datasets. |
| **Bottom strip – Specific Aims** | SA 1 (Theoretical Formulation), SA 2 (Field Parameterization), SA 3 (Scalable Algorithms), SA 4 (V&V & Demonstration). Each includes a brief task summary. Dotted lines link each aim to the relevant region of the main flow. |

## Omissions and simplifications

- **Mathematical detail**: The figure shows the posterior Hamiltonian symbolically but does not reproduce the full partition-function discussion or the detailed variational/sampling update rules.
- **Specific PDE forms**: Navier–Stokes, Eikonal, and continuity equations are named but not written out; the energy-based and ISR Hamiltonian forms are omitted for space.
- **Co-registration geometry**: The hierarchical Bayesian formulation with translations τᵢ(t) and rotations Uᵢ(t) ∈ SO(3) is mentioned only as "Bayesian co-registration."
- **Time-evolution treatment**: The Neural ODE-inspired parameterization of dynamics (θ̇ = f(θ,t)) appears only in the SA 2 description.
- **Validation pipeline detail**: The synthetic → in vitro → clinical progression is noted in SA 4 but the specific datasets (mouse LV, human RV, aortic flow), phantoms, and metrics (Bland–Altman, AIC/BIC) are omitted from the figure.
- **Broader impacts**: Training, open-source software, and conference activities are captured only through the "Open-source code & V&V benchmarks" output card.
- **Personnel**: PI roles (Bilionis, Vlachos) and institutional partners are not shown.

## Caption draft

**Figure 1.** Schematic overview of the proposed research plan. Multi-modal cardiovascular imaging data — 4D Flow MRI, phase-contrast MRI, and Color Doppler echocardiography — enter the Information Field Theory (IFT) framework (center), which combines a physics-informed prior probability measure H(φ) encoding Navier–Stokes, Eikonal, and continuity equations (without a PDE solver) with modality-specific measurement operators Rᵢ to form the joint posterior Hamiltonian H(φ|d) = H(d|Rφ) + H(φ). Scalable posterior inference is achieved via preconditioned stochastic gradient Langevin dynamics and amortized variational inference on GPU clusters. The framework produces reconstructed hemodynamic fields (velocity, pressure, vessel geometry) with full uncertainty quantification, enables automatic model-form error detection through the precision parameter β, and supports clinical decision-making (right). Four Specific Aims (bottom) span the theoretical formulation (SA 1), causality-respecting field parameterization (SA 2), scalable inference algorithms (SA 3), and a verification–validation–demonstration pipeline from synthetic data through in vitro phantoms to clinical datasets (SA 4). The key innovation is the first application of IFT to cardiovascular hemodynamics, offering physics-informed Bayesian inference on function spaces, multi-modal data fusion with co-registration, and scalable GPU-parallel posterior characterization — all without requiring a numerical PDE solver.
