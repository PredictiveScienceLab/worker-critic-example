# Master Figure Notes

## Figure concept

A single wide overview figure that reads left to right:

1. incomplete cardiovascular imaging inputs;
2. the central methodological contribution, Information Field Theory (IFT);
3. posterior outputs and intended impact.

The design goal was a proposal-style graphical abstract rather than a dense infographic.

## Main content elements included

- Central objective: reconstruct patient-specific cardiovascular hemodynamic fields and cardiac structure from multimodal imaging with quantified uncertainty.
- Input modalities: `2D PC-MRI`, `4D Flow MRI`, and `Color Doppler Echo`.
- Main methodological engine: `Information Field Theory (IFT)` framed as Bayesian inference over continuous fields.
- Key methodological ingredients: physics-informed priors and multimodal measurement operators with co-registration.
- Main novelty statement: joint posterior inference from multimodal imaging without repeated CFD solves.
- Main outputs: posterior velocity/pressure/wall-shear quantities, cardiac structure/geometry, and uncertainty/model-form-error awareness.
- Main impact: better image analysis and more reliable cardiovascular decision support.

## Important omissions and simplifications

- The specific aims were gradually compressed and then removed from the on-figure layout to preserve print-scale readability; their role is now implied by the left-to-right progression and should be reinforced in the caption/body text.
- Algorithm-specific details such as persistent SGLD and amortized VI were deemphasized to keep the center panel focused on the conceptual contribution.
- The earlier bottleneck and proof-path boxes were removed to reduce density and strengthen one-glance reading.

## Caption draft

Overview of the proposed research to reconstruct patient-specific cardiovascular hemodynamic fields and cardiac structure from complementary but incomplete imaging modalities. The project fuses `2D PC-MRI`, `4D Flow MRI`, and `Color Doppler Echo` using `Information Field Theory (IFT)`, a Bayesian inference framework over continuous fields that combines physics-informed priors with modality-specific measurement operators. The central innovation is joint posterior inference from multimodal imaging without repeated CFD solves, enabling recovery of hemodynamic quantities and structure/geometry together with uncertainty and model-form-error awareness. The intended payoff is improved cardiovascular image analysis and more reliable decision support.

## External review record

- External reviewer model: `gpt-5.4-pro` via the OpenAI Responses API.
- Completed review rounds: `14`.
- Reviewer status: `Revise.` in every completed round.
- Main repeated reviewer themes: reduce on-figure density, enlarge small text for proposal print scale, clarify the center claim in plain language, and simplify the right-hand deliverables/impact section.
- Final applied changes after the last completed review: fixed right-panel containment, made cardiac structure/geometry explicit in outputs, and simplified the right-hand deliverables into a single outcomes block.
- Result: strongest available draft produced, but the external reviewer did not explicitly return `Approved.` before run completion.
