# Responsible-use boundary

The fiction is compelling because it imagines total visibility. A real implementation would combine severe privacy invasion with high-impact prediction under uncertainty. This repository therefore treats the ethical boundary as part of the architecture, not as a footer added later.

## Included

- entirely invented identities and records;
- a closed, reproducible scenario;
- explicit uncertainty and full probability distributions;
- a clear separation between involvement and perpetrator likelihood;
- evidence provenance and local score contributions;
- a threshold control that makes alert-volume tradeoffs visible;
- labels that describe outputs as synthetic scenario indices.

## Deliberately excluded

- real-person names, photos, contact details, or location histories;
- face recognition or biometric matching;
- covert collection, private-account access, or scraped surveillance feeds;
- automated police, employer, insurance, credit, immigration, or security actions;
- operational alerts about real people;
- claims that graph proximity establishes intent or guilt;
- neighborhood labels presented as real crime forecasts.

## Failure modes to study

Even with synthetic data, the project can teach why real systems fail:

- **base-rate error:** rare events create many false positives even for apparently accurate classifiers;
- **feedback loops:** enforcement changes the data that later trains enforcement models;
- **correlated evidence:** multiple databases can repeat one underlying claim;
- **proxy discrimination:** geography, mobility, purchases, and networks can encode protected traits;
- **role ambiguity:** the same observed pattern may describe a target, witness, helper, or offender;
- **calibration drift:** a numerical probability can look authoritative after its data-generating process changes;
- **automation bias:** polished interfaces can make weak inference feel certain;
- **contestability:** a person cannot rebut a score assembled from inaccessible sources.

## If the project evolves

Keep future work within a sandboxed fictional or consent-based simulation. Use counterfactual tests, subgroup error analysis on deliberately generated attributes, provenance, deletion controls, uncertainty visualization, and human review. Do not connect this code to real surveillance sources or use it to rank real individuals.
