# Master Figure Notes

## Figure concept

A left-to-right conceptual schematic that presents the proposal as a flow from noisy multimodal cardiovascular imaging to a physics-informed Information Field Theory inference engine and then to uncertainty-aware hemodynamic outputs, validation, and impact. The four specific aims are kept in a bottom ribbon so the reviewer can see both the scientific story and the planned work structure at a glance.

## Main content elements included

- The motivating clinical/imaging problem: cardiovascular flow is observed only indirectly and imperfectly.
- Key data modalities: PC-MRI, 4D Flow MRI, and Echo.
- Main methodological engine: physics-informed priors, modality-specific measurement operators, co-registration, and joint posterior inference in Information Field Theory.
- Distinctive innovation cue: multimodal Bayesian fusion without repeated CFD solves.
- The four specific aims: formulate the inverse problem, parameterize evolving fields, scale posterior inference, and verify/validate/demonstrate.
- Expected outputs and pathway to impact: posterior maps of geometry, flow, and pressure with credible uncertainty; synthetic, in vitro, and clinical evaluation; downstream diagnosis/image-analysis/tooling relevance.

## Important omissions or simplifications

- The figure suppresses detailed mathematical notation such as Hamiltonians, partition functions, and the full hierarchical co-registration formulation.
- It uses representative hemodynamic-field graphics rather than explicitly depicting every latent variable, hyperparameter, or imaging sub-step.
- Derived quantities such as wall shear stress are implied under reconstructed hemodynamics rather than called out individually to preserve one-glance readability.
- Broader impacts are condensed to open-source GPU tools and benchmark datasets rather than listing all training and dissemination activities.

## Caption draft

Overview of the proposed research: noisy and partially observed cardiovascular imaging data from PC-MRI, 4D Flow MRI, and Doppler echocardiography are fused in a single physics-informed Information Field Theory framework to reconstruct vessel geometry, flow, pressure, and related hemodynamic quantities with quantified uncertainty. The innovation is a multimodal Bayesian field-inference approach that encodes cardiovascular physics, measurement operators, and cross-modality co-registration directly in the probabilistic model, avoiding repeated CFD solves while supporting joint posterior inference over hidden fields and physical parameters. The project advances through four specific aims: formulate the inverse problem, parameterize evolving fields, develop scalable posterior algorithms, and verify, validate, and demonstrate the method on synthetic, in vitro, and clinical data. The intended impact is uncertainty-aware cardiovascular image analysis and decision support, supported by open-source computational tools and benchmark datasets.

## Critique rounds and changes

1. Round 1: `Revise.`
   Changes requested: shorten the left challenge text, enlarge or simplify the right impact panel, add more breathing room in the right column, and make the novelty cue more specific.
   Changes made: shortened the challenge text, rebalanced the right-column boxes, enlarged the impact area and reduced its copy, and updated the novelty pill to emphasize multimodal Bayesian fusion without repeated CFD solves.

2. Round 2: `Approved.`
