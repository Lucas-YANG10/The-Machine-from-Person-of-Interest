# Roadmap

The project is structured as progressive experiments rather than one jump from a hand-authored demo to “AI surveillance.” Every stage should remain fictional or consent-based.

## v0.1 — fixed time slice (complete)

- deterministic synthetic records;
- transparent Python baseline;
- involvement, role, type, event, and area outputs;
- Machine/Analyst modes;
- city, graph, and model visualizations;
- threshold interaction, tests, and deployment.

## v0.2 — simulation clock

- move records into SQLite;
- replay a 24-hour scenario in chronological order;
- add pause, scrub, speed, and event-arrival controls;
- recompute temporal decay and alerts at each tick;
- compare the same model before and after each new observation.

## v0.3 — learned tabular baseline

- generate many fictional days with controllable causal templates;
- use rolling time splits rather than random train/test splits;
- train logistic regression and LightGBM involvement/role heads;
- calibrate with isotonic regression or Platt scaling;
- plot precision-recall, calibration, lead-time recall, and false alarms per simulated day.

## v0.4 — temporal graph model

- encode person, event, place, and observation node types;
- compare R-GCN/HGT/TGN variants with the transparent baseline;
- preserve per-edge provenance and add explanation stability tests;
- run ablations for graph propagation, text signals, mobility, and temporal decay.

## v0.5 — uncertainty and counterfactual lab

- distinguish aleatoric and epistemic uncertainty;
- display conformal prediction sets for role/type;
- let viewers remove a record and observe the score change;
- detect duplicated/correlated evidence;
- add abstention when evidence is insufficient or contradictory.

## v1.0 — narrative sandbox

- author multiple fictional borough-scale stories;
- branch outcomes when an intervention changes the simulated future;
- expose a scenario editor and versioned model cards;
- keep all people and records generated, local, and clearly fictional.
