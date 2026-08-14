# Roadmap

The project is structured as progressive experiments rather than one jump from a hand-authored demo to “AI surveillance.” Every stage should remain fictional or consent-based.

## v0.1 — fixed inference prototype (complete)

- create a deterministic synthetic scenario and transparent Python baseline;
- compute involvement, role, crime type, event, and area-risk outputs;
- separate the red-frame involvement decision from victim/perpetrator inference;
- introduce Machine and Analyst views;
- add City Grid, Evidence Graph, and Model Core visualizations;
- provide an adjustable relevance threshold and reproducible tests.

## v0.2 — offline edition and expanded Manhattan scenario (complete)

- add a dependency-free, self-contained HTML edition that runs directly from a local file;
- expand the scenario to 30 fictional people, 10 candidate events, and 3,400 heterogeneous observations;
- move person-specific map offsets into `people.json` so identities and positions remain data-driven;
- replace schematic areas with all 38 Manhattan 2020 Neighborhood Tabulation Areas derived from NYC Department of City Planning boundaries;
- keep geographic boundaries realistic while ensuring that every incident, risk value, identity, and record remains synthetic;
- add beginner-oriented documentation, data contracts, responsible-use boundaries, and GitHub-ready project structure.

## v0.3 — interactive map and interface refinement (complete)

- enlarge typography and spacing to improve readability without increasing information density;
- make the threshold control continuously draggable and update the Relevant List and map in real time;
- render district selection with the actual neighborhood outline and update Area Aggregate details on selection;
- add click-to-enable, pointer-centered map zoom and smooth drag-to-pan controls;
- preserve the current map position after leaving map-control mode while restoring normal page scrolling;
- add day and night display modes with explicit controls and theme-aware contrast;
- refine map selection and drag behavior so district clicks, persistent outlines, and panning coexist correctly.

## v0.4 — simulation clock

- move records into SQLite;
- replay a 24-hour scenario in chronological order;
- add pause, scrub, speed, and event-arrival controls;
- recompute temporal decay and alerts at each tick;
- compare the same model before and after each new observation.

## v0.5 — learned tabular baseline

- generate many fictional days with controllable causal templates;
- use rolling time splits rather than random train/test splits;
- train logistic regression and LightGBM involvement/role heads;
- calibrate with isotonic regression or Platt scaling;
- plot precision-recall, calibration, lead-time recall, and false alarms per simulated day.

## v0.6 — temporal graph model

- encode person, event, place, and observation node types;
- compare R-GCN, HGT, and TGN variants with the transparent baseline;
- preserve per-edge provenance and add explanation-stability tests;
- run ablations for graph propagation, text signals, mobility, and temporal decay.

## v0.7 — uncertainty and counterfactual lab

- distinguish aleatoric and epistemic uncertainty;
- display conformal prediction sets for role and crime type;
- let viewers remove a record and observe the score change;
- detect duplicated or correlated evidence;
- add abstention when evidence is insufficient or contradictory.

## v1.0 — narrative sandbox

- author multiple fictional borough-scale stories;
- branch outcomes when an intervention changes the simulated future;
- expose a scenario editor and versioned model cards;
- keep all people and records generated, local, and clearly fictional.
