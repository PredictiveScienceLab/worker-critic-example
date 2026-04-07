## Figure concept

Single wide overview figure that reads left-to-right: multimodal cardiovascular imaging inputs -> proposed information field theory (IFT) reconstruction engine organized by the four specific aims -> recovered latent cardiovascular state and validation/impact outcomes. The top-right inset isolates the main scientific novelty so a reviewer can see immediately what is distinctive about the project.

## Main content elements included

- Proposal objective and central question.
- Key input modalities: PC-MRI, 4D Flow MRI, and Color Doppler Echo.
- The main methodological engine: Bayesian IFT with a joint posterior over geometry, velocity, pressure, motion, and hyperparameters.
- Explicit mapping to the four specific aims:
  - Aim 1: inverse problem formulation with physics-informed priors, forward models, and co-registration.
  - Aim 2: parameterization of time-evolving fields.
  - Aim 3: scalable posterior inference via SGLD and amortized variational inference.
  - Aim 4: verification, validation, and clinical demonstration.
- Expected outputs: anatomy/geometry, velocity/streamlines, pressure/wall shear, posterior uncertainty.
- Validation and impact path: synthetic -> in vitro -> clinical, plus decision support, protocol design, open-source software, and benchmark datasets.
- Distinctive advances: multimodal fusion, physics without repeated CFD solves, joint posterior over fields and parameters, and model-form error quantification.

## Important omissions or simplifications

- The detailed physics and measurement equations are intentionally compressed; the figure does not show the full Bloch-to-k-space MRI chain or the complete Echo imaging physics.
- The PDE set is summarized conceptually rather than listing Eikonal, continuity, and Navier-Stokes separately on the figure.
- Vessel strain/stress reconstruction was omitted because the proposal does not make it a primary deliverable.
- Clinical cohorts, benchmark metrics, and broader-impact activities are condensed into short labels rather than shown as separate panels.

## Caption draft

Overview of the proposed research program for uncertainty-aware cardiovascular hemodynamics reconstruction. Noisy, partial, and potentially misaligned PC-MRI, 4D Flow MRI, and Color Doppler Echo measurements are fused in a Bayesian information field theory (IFT) framework to reconstruct patient-specific cardiac geometry, velocity, pressure, and associated uncertainty. Specific Aim 1 formulates the inverse problem through physics-informed priors, modality-specific forward models, and Bayesian co-registration; Aim 2 develops parameterizations for spatially and temporally evolving fields with boundary and initial conditions built in; Aim 3 develops scalable stochastic-gradient Langevin dynamics and amortized variational inference for the joint posterior over fields and parameters; and Aim 4 verifies, validates, and demonstrates the method on synthetic, in vitro MRI/Echo versus PIV/PTV, and clinical datasets. The central innovation is that known cardiovascular physics is embedded directly in the probabilistic field model, enabling multimodal fusion, joint uncertainty quantification, and model-form error characterization without repeated patient-specific CFD solves. The intended impact is clinically relevant, uncertainty-aware hemodynamic reconstruction together with reusable open-source software and benchmark datasets for the broader research community.
