# Master Figure — Notes

## Figure Concept

A three-column horizontal flow diagram that communicates the complete proposal at a glance:

1. **Left column** — Multi-modal medical imaging inputs (PC-MRI, 4D Flow MRI, Color Doppler Echo) with annotations about data quality challenges (noise, low resolution, missing boundary conditions).
2. **Center column** — The Information Field Theory (IFT) framework, featuring the core Bayesian equation and four color-coded Specific Aims in a 2×2 grid.
3. **Right column** — Outputs and impact (hemodynamic fields with uncertainty, clinical decision support, open-source software and benchmarks).

Block arrows connect the three columns, labeled "data" (left→center) and "inference" (center→right), conveying the conceptual pipeline. An innovation highlight strip at the bottom of the center panel calls out the four key methodological advances.

The left column now opens with the clinical problem anchor ("CVD: leading U.S. killer") and includes a visually separated "Key Challenges" sub-section below the modality cards. The right column includes imaging protocol optimization as a distinct output.

## Main Content Elements

- **Central objective**: Scalable Bayesian reconstruction of cardiovascular hemodynamic fields from multi-modal imaging, with calibrated uncertainty quantification.
- **Imaging inputs**: PC-MRI (velocity-encoded phase images), 4D Flow MRI (~1 mm resolution), Color Doppler Echo (real-time 1D velocities).
- **Methodological engine**: Information Field Theory — Bayesian inference over fields using physics-informed prior measures and additive data Hamiltonians.
- **Core equation**: H(φ|d) = H(d|Rφ) + H(φ), decomposing the posterior into a data likelihood term and a physics-based prior.
- **Four Specific Aims**:
  - Aim 1 (blue): Theoretical formulation — physics-informed priors (Navier-Stokes, Eikonal), measurement operators, hierarchical co-registration.
  - Aim 2 (green): Spatiotemporal field parameterization — Fourier, wavelets, DNNs; causality-respecting time evolution via Neural ODEs.
  - Aim 3 (orange): Scalable algorithms — preconditioned SGLD, amortized variational inference, GPU-parallel distributed inference.
  - Aim 4 (purple): Verification, validation & demonstration — synthetic, in vitro (PIV/PTV), and clinical (mouse LV, human RV, aorta).
- **Innovation highlights**: No PDE solver required; multi-modal fusion; scalable to GPU clusters; model-form error detection.
- **Outputs**: Hemodynamic fields with posterior uncertainty bands; imaging protocol optimization via information gain; open-source software and V&V benchmarks.
- **Broader impacts**: Education, workforce training, and outreach (noted at bottom right).
- **Clinical context**: CVD as the leading cause of U.S. mortality, framing the clinical motivation at the top of the left column.

## Important Omissions and Simplifications

- The detailed mathematical formulation of the information Hamiltonian (energy-based vs. integrated squared residual) is omitted for visual clarity; only the posterior decomposition equation is shown.
- Individual tasks within each Aim (e.g., Task 1.1, 1.2, 1.3) are condensed into three summary bullets per Aim rather than listed exhaustively.
- The co-registration problem is mentioned but its hierarchical Bayesian structure (translation/rotation operators, modality-specific variations) is not detailed in the figure.
- Specific clinical partners (Indiana University, Children's National Hospital, Northwestern) and clinical conditions (Tetralogy of Fallot, single ventricle) are omitted for space.
- Broader impact tasks (6 total in the proposal) are collapsed into a single annotation.
- The partition function challenge and its resolution via Monte Carlo gradient estimates are not shown.
- The β parameter's role in controlling physics trust / model-form uncertainty is not explicitly diagrammed.

## Caption Draft

**Figure 1. Overview of the proposed methodology for Bayesian reconstruction of cardiovascular hemodynamics using Information Field Theory (IFT).** Cardiovascular disease is the leading cause of mortality in the United States, motivating the need for accurate, uncertainty-aware hemodynamic assessment. Multi-modal medical imaging data — phase-contrast MRI, 4D Flow MRI, and Color Doppler Echocardiography — provide noisy, incomplete velocity measurements (left), subject to key challenges including unknown patient geometry, variable boundary conditions, and high-dimensional fields. These data are assimilated through the IFT framework (center), which formulates a Bayesian posterior over hemodynamic fields by combining a physics-informed prior measure encoding the governing PDEs with modality-specific measurement operators, without requiring a PDE solver. The four Specific Aims address the theoretical formulation (Aim 1), spatiotemporal field parameterization (Aim 2), scalable posterior inference via SGLD and amortized variational inference on GPU clusters (Aim 3), and systematic verification, validation, and clinical demonstration (Aim 4). The methodology produces full posterior distributions over velocity and pressure with calibrated uncertainty (right), enables information-gain-driven imaging protocol optimization, and supports uncertainty-aware clinical decisions. Key innovations — solver-free physics encoding, multi-modal fusion, GPU scalability, and automatic model-form error detection — are highlighted at the bottom. Open-source software and V&V benchmark datasets will be released as community resources.

## Revision History

### Revision 2 (review round 1)
Changes made in response to critic feedback:
1. **Clinical problem context**: Added "CVD: leading U.S. killer" subtitle to left column header, anchoring the clinical motivation.
2. **Key Challenges sub-section**: Added horizontal divider and "Key Challenges" heading below the modality cards, grouping the four obstacles (noisy data, unknown geometry, variable BCs, high dimensionality) into a visually distinct block.
3. **Reduced aim text**: Removed all parenthetical examples (e.g., "(Fourier, wavelets, DNNs)", "(Navier-Stokes, Eikonal)") and secondary phrases from aim boxes; all items are now single-line.
4. **Print-legible fonts**: Switched from 19.5×9 in @100 DPI to 6.5×3 in @300 DPI canvas so font sizes map directly to print points. Minimum text is now 7 pt at print scale; body text 7–7.5 pt; headers 8–8.5 pt; equation 10 pt.
5. **NOVEL badge removed**: Replaced with a heavier border on the first output card (hemodynamic fields + UQ), letting the figure structure communicate novelty.
6. **Imaging protocol optimization**: Added a new output card "Imaging Optimization" describing information-gain-driven acquisition and UQ-aware clinical decisions, reflecting the proposal's emphasis on using uncertainty to optimize imaging protocols.

### Review round 2 — Approved
No further changes requested. All 10 evaluation criteria passed: fidelity, central objective, inputs, methodology, aims, outputs, story clarity, readability, NSF suitability, and polish.

# Review History

## 0001-review.md

I need to examine both the LaTeX source and the SVG source carefully to provide a thorough review.

Let me read through the SVG structure systematically to understand the figure layout and content.

STATUS: Revise.

JUSTIFICATION:
The figure has a strong three-column input → methodology → output structure and covers all four specific aims with task-level detail. The IFT equation banner and the key-advantages footer strip are effective. However, several issues prevent approval. First, the left column jumps directly to imaging modalities without framing the overarching clinical problem — cardiovascular disease as the leading cause of mortality — which the proposal opens with and which motivates the entire effort. A reader encountering this figure at the top of the proposal needs that anchor. Second, the figure is extremely text-heavy; at full-page width the smallest annotations (≈9.5 pt before figure scaling) will shrink to ≈5–6 pt, risking illegibility for reviewers reading printed copies. Third, the challenges block at the bottom of the left column ("Unknown patient geometry," "Variable boundary conditions") floats below the modality cards without a clear sub-heading or visual separation, making it read as an afterthought rather than the key obstacles the proposal addresses. Fourth, the "NOVEL" badge on the first output box has a marketing tone unusual for an NSF figure; the novelty is better communicated structurally.

CHANGES:
- Add a brief problem-context header or subtitle to the left column (e.g., "Cardiovascular Disease — #1 cause of mortality") above the imaging modality cards, so the clinical motivation is visible at first glance.
- Introduce a clear sub-heading (e.g., "Key Challenges") and a thin divider between the three modality cards and the challenges list in the left column to improve visual grouping.
- Reduce text volume inside the four Aim boxes by removing parenthetical examples (e.g., "(Fourier, wavelets, DNNs)", "(Navier-Stokes, Eikonal)") and secondary lines like "across modalities" and "space measures"; these belong in the proposal body, not the figure.
- Increase the minimum annotation font size so that no text falls below ~7 pt when the figure is rendered at \textwidth (~6.5 in); consolidate or remove the lowest-priority descriptors to make room.
- Replace the "NOVEL" badge with a more understated visual cue (e.g., a small star or bold border) or remove it entirely, letting the figure's structure convey novelty.
- In the right-column "Outputs & Impact" section, add an explicit mention of "optimized imaging protocols" or "information-gain–driven acquisition," since the proposal highlights that uncertainty can help optimize imaging protocols — a distinct output currently absent from the figure.

## 0002-review.md

**Review round 2 complete — Approved.**

The revised figure addresses all six round-1 issues and meets all ten evaluation criteria:

| Criterion | Verdict |
|---|---|
| Fidelity to proposal text | All key elements present and accurate |
| Central objective / problem | CVD context + IFT reconstruction objective clear |
| Inputs / modalities | PC-MRI, 4D Flow MRI, Color Doppler Echo with descriptors |
| Methodological engine | IFT equation, "physics is prior" insight, multi-modal fusion |
| Specific Aims | All 4 aims with task-level bullets matching proposal |
| Outputs / validation / impact | Hemodynamic fields, imaging optimization, software & V&V |
| Scientific story clarity | Clean left-to-right input → method → output flow |
| Visual hierarchy / readability | 7 pt min at print scale; center column dominant |
| NSF figure suitability | 6.5×3 in, 2.17:1 aspect ratio |
| Polish / clutter | Professional, no marketing language, well-organized |

The review files are saved at:
- `runs/20260406-203736-critic/reviews/0002-review.md`
- `runs/20260406-203736-critic/reviews/0002-review.json`

## 0003-review.md

STATUS: Approved.

JUSTIFICATION:
All six issues from round 1 have been fully resolved. The revised figure now anchors the left column with "CVD: leading U.S. killer" as clinical context, separates the modality cards from challenges with a "Key Challenges" heading and divider, strips parenthetical examples from all four Aim boxes, removes the "NOVEL" badge (replaced by a heavier border on the first output card), and adds a dedicated "Imaging Optimization" output card covering information-gain protocols and UQ-aware decisions. The 468×216 pt canvas (6.5×3 in, 2.17:1 aspect ratio) is well suited for a full-width NSF figure, and the font-size correction — minimum 7 pt at print scale — ensures legibility in printed review copies. Content fidelity is strong: all three imaging modalities with descriptors, the IFT posterior Hamiltonian equation with labeled terms, four Specific Aims with task-level bullets matching the proposal, the key-advantages strip (no PDE solver, multi-modal, GPU-scalable, model-form errors), three output categories, and broader-impacts text are present and accurate. The three-column input → methodology → output flow tells a clear scientific story with appropriate visual hierarchy, and the overall polish level is suitable for submission.

CHANGES:
- None.
