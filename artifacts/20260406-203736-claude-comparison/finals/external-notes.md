# Master Figure — Notes

## Figure concept

A three-panel horizontal flow diagram summarizing the full research program at a glance:
**Imaging Data → Information Field Theory → Outputs & Impact**, with a bottom strip showing the four Specific Aims and their key tasks.

The layout follows the natural narrative arc of the proposal: the *challenge* (noisy, incomplete multi-modal cardiac imaging), the *innovation* (IFT as a Bayesian framework that encodes physics directly in prior measures without a PDE solver), and the *payoff* (uncertainty-quantified hemodynamic reconstructions and clinical decision support).

## Main content elements

| Region | Content |
|---|---|
| **Left panel – Imaging Data** | Three input modalities: PC-MRI, 4D Flow MRI, Color Doppler Echocardiography. Each box names the modality and briefly describes its measurement type. An annotation notes the shared limitations: noisy, low resolution, ill-posed inverse problem. |
| **Center panel – IFT Framework** | The methodological engine. Two sub-boxes describe (a) *Physics-Informed Priors* (Navier–Stokes, Eikonal equation, level-set dynamics) and (b) *Measurement Operators* (modality-specific signal models). These feed into a *Scalable Joint Posterior Inference* box showing the posterior Hamiltonian equation and three inference strategies (Stochastic Gradient Langevin Dynamics, Amortized Variational Inference, GPU-parallel data parallelism). A highlighted innovation strip emphasizes three key novelties. |
| **Right panel – Outputs & Impact** | Three output categories: Hemodynamic Fields (velocity, pressure, geometry), Uncertainty Maps (posteriors, credible intervals, model-form error), and Clinical Decision Support (risk assessment, protocol optimization, open-source tools). A validation pathway annotation shows the progression Synthetic → In Vitro → Clinical. |
| **Bottom strip – Specific Aims** | Four color-coded boxes for SA 1 (Theoretical Formulation), SA 2 (Field Parameterization), SA 3 (Scalable Algorithms), and SA 4 (V&V & Demonstration), each listing three key tasks. |

## What is new / innovative (highlighted in the figure)

- **No PDE solver required**: Physics is encoded directly in the prior information Hamiltonian, avoiding the computational bottleneck of repeated CFD solves.
- **Multi-modal data fusion**: IFT naturally combines PC-MRI, 4D Flow MRI, and Echo through additive data Hamiltonians.
- **Joint uncertainty quantification**: The framework characterizes the full joint posterior over hemodynamic fields *and* physical parameters.
- **Model-form error detection**: The β parameter in the information Hamiltonian enables automatic quantification of model-form uncertainty.

These innovations are called out with purple star (★) markers inside the center panel boxes and in the innovation strip banner.

## Important omissions and simplifications

- **Mathematical detail**: The information Hamiltonian formalism (Eq. 1–3 in the proposal) is reduced to a single equation line. The partition function discussion and renormalization are omitted.
- **Co-registration problem**: Task 1.3's hierarchical Bayesian co-registration approach is listed in SA 1 but not diagrammed in detail.
- **Field parameterization specifics**: SA 2 lists the concept but omits the specific parameterization options (Fourier, wavelet, DNN, etc.) discussed in the proposal.
- **Broader impacts**: Training activities, open-source software dissemination, and conference organization are mentioned only as "open-source software & data" in the outputs panel.
- **Prior NSF support and team composition**: Not shown; outside the scope of a methods-overview figure.

## Caption draft

**Figure 1.** Overview of the proposed research program for uncertainty-quantified reconstruction of cardiovascular hemodynamic fields from advanced medical imaging. *Left*: Three complementary but individually incomplete imaging modalities — Phase-Contrast MRI (PC-MRI), 4D Flow MRI, and Color Doppler Echocardiography — provide noisy, low-resolution velocity measurements. *Center*: The Information Field Theory (IFT) framework formulates the reconstruction as Bayesian inference over function spaces. Physics-informed prior probability measures encode the governing equations (Navier–Stokes, Eikonal, level-set dynamics) directly — without requiring a PDE solver — while modality-specific measurement operators connect the fields to observed data. The joint posterior over hemodynamic fields and physical parameters is characterized via scalable stochastic gradient Langevin dynamics and amortized variational inference, exploiting GPU-parallel data parallelism. *Right*: The methodology produces full posterior distributions over velocity, pressure, and vessel geometry fields, enabling uncertainty-quantified clinical decision support. Validation proceeds from synthetic benchmarks through in vitro phantom experiments to clinical datasets. *Bottom*: The four Specific Aims span theoretical formulation (SA 1), spatiotemporal field parameterization (SA 2), scalable posterior inference algorithms (SA 3), and systematic verification, validation, and clinical demonstration (SA 4). Key innovations — solver-free physics encoding, multi-modal data fusion, and automatic model-form error detection — are highlighted with star markers (★).

# Review History

## 0001-review.md

STATUS: Approved.

JUSTIFICATION:
The figure faithfully represents the proposal's structure and scientific story. The three-column layout (Imaging Data → Information Field Theory → Outputs & Impact) clearly conveys the central inverse-problem pipeline. All three imaging modalities (PC-MRI, 4D Flow MRI, Color Doppler Echo) are listed as inputs. The IFT engine is well-represented with physics-informed priors (Navier-Stokes, Eikonal, level-set), measurement operators for each modality, and the scalable posterior inference block covering both SGLD and amortized VI with GPU parallelism. Key distinguishing features ("No PDE solver required," "Multi-modal data fusion," "Model-form error detection," "Joint uncertainty quantification") are highlighted. The outputs column covers reconstructed hemodynamic fields, uncertainty maps, and clinical decision support, matching the proposal's stated goals. The bottom strip cleanly enumerates all four Specific Aims with their sub-tasks, matching the proposal text. The co-registration problem (Task 1.3) is listed under SA 1. The validation pipeline (Synthetic → In Vitro → Clinical) is called out. Visual hierarchy is strong: gradient-filled headers, consistent color coding per column, readable font sizes, and the wide-shallow aspect ratio is appropriate for an NSF proposal figure. Clutter is well managed. Minor quibbles exist (e.g., the β parameter's role in model-form error could be more explicit, and the co-registration hierarchical structure could be visually richer), but these are not significant enough to warrant revision for a proposal overview figure.

CHANGES:
- None.
