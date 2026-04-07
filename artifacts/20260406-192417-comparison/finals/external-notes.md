# Master Figure Notes

## Figure concept

Wide conceptual overview figure for the proposal opening: multimodal cardiovascular imaging on the left, the new information field theory (IFT) reconstruction engine in the center, and validation / impact on the right.

## Main content elements included

- The central objective: reconstruct patient-specific cardiovascular geometry, flow, and pressure from noisy multimodal imaging with quantified uncertainty.
- The key measurement modalities: PC-MRI, 4D Flow MRI, and Color Doppler Echo.
- The main methodological engine: IFT with physics-informed priors, modality-specific measurement operators, Bayesian co-registration, and scalable joint-posterior inference.
- The four specific aims:
  1. Priors, measurement operators, and co-registration.
  2. Boundary-aware spatial fields, initial conditions, and causal / Markovian dynamics.
  3. Persistent SGLD plus amortized variational inference for scalable joint inference.
  4. Synthetic verification, in vitro validation, and clinical demonstration.
- Expected outputs and impact: posterior uncertainty over geometry, velocity, pressure, motion, and uncertainty-aware cardiovascular image analysis.
- Compact broader-impact cues: open-source GPU software, benchmark datasets with reproducible code, and student / course / clinical outreach.

## Important omissions or simplifications

- The figure compresses the proposal's mathematical detail into short labels such as Eikonal geometry, continuity, Navier-Stokes, and model-form error via beta.
- It shows the reconstructed fields conceptually rather than depicting a specific anatomy, dataset, or patient cohort.
- It does not explicitly show strain / stress tensor reconstruction because the proposal says the team will not attempt explicit vessel strain and stress reconstruction.
- It compresses the broader impacts section into a short footer rather than showing all six broader-impact tasks individually.
- It abstracts the verification / validation metrics and cohort counts to keep the figure readable at proposal scale.

## Caption draft

Overview of the proposed framework for multimodal Bayesian reconstruction of cardiovascular hemodynamics. Noisy, partial observations from PC-MRI, 4D Flow MRI, and Color Doppler echocardiography are co-registered and fused within an information field theory formulation that combines physics-informed priors with modality-specific measurement operators and scalable Bayesian inference. The project develops priors and measurement operators with unified co-registration (Aim 1), boundary-aware and causal space-time parameterizations (Aim 2), persistent SGLD and amortized variational inference for the joint posterior (Aim 3), and a verification-to-validation-to-clinical demonstration pathway (Aim 4). The key innovation is solver-free physics-informed Bayesian field inference that quantifies uncertainty over geometry, flow, pressure, and related parameters, enabling improved cardiovascular image analysis, open tools and benchmarks, and more reliable future decision support.

## External review record

1. Round 1: `Revise.` The reviewer asked for stronger proposal fidelity: correct the pressure symbol, replace the overly specific "analytical truth" wording with known / simulated truth, and explicitly add unknown geometry, initial conditions, modality misalignment, and causal / Markovian dynamics.
2. Round 2: `Approved.` The reviewer said the revised figure now faithfully captured the proposal arc and was clear, readable, and polished enough for a wide NSF overview figure.
