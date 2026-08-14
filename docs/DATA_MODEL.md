# Synthetic data model

All v0.1 inputs live in `data/synthetic/`. They are deterministic JSON so the complete inference can be audited without a database.

## Files

| File | Purpose |
|---|---|
| `scenario.json` | Fixed simulation clock, seed, and synthetic flag |
| `people.json` | Fictional subject identifiers and harmless baseline attributes |
| `events.json` | Candidate events, future times, stylized map coordinates, and type priors |
| `observations.json` | Fictional messages, trips, purchases, access events, and other evidence |
| `zones.json` | Stylized Manhattan display polygons and background scenario terms |
| `ground_truth.json` | Hidden synthetic involvement/role labels used only for evaluation |

## Observation contract

```json
{
  "id": "MSG-104",
  "person_id": "P-017",
  "event_id": "EV-042",
  "timestamp": "2026-08-13T19:18:00-04:00",
  "source": "message",
  "summary": "Short human-readable description",
  "detail": "Fictional record body",
  "tags": ["targeted", "vulnerability"],
  "reliability": 0.84,
  "related_person_id": null
}
```

`related_person_id` creates an explicit person-person graph edge when present. It never appears because the engine searched for a hidden real-world relationship.

## Output contract

`engine/run_pipeline.py` produces the same artifact in two locations:

- `app/data/machine-output.json` is statically imported by the React application;
- `public/data/machine-output.json` is available to external educational visualizations.

The top-level keys are:

| Key | Content |
|---|---|
| `meta` | Version, simulation time, threshold, and disclaimer |
| `people` | Best event per person, scores, posteriors, explanations, and evidence |
| `events` | Event risk, participants, type mix, signal count, and time window |
| `zones` | Spatial scenario-risk index and contributing events |
| `timeline` | Most recent synthetic observations |
| `metrics` | Checks against the synthetic labels |

## Why JSON before a database?

The first project milestone is a fixed, inspectable time slice. JSON has three advantages here:

1. every input and output can be reviewed in a pull request;
2. regenerating results requires no service credentials or schema migration;
3. the boundary between Python inference and TypeScript visualization stays explicit.

A later simulation clock can place the same logical entities in SQLite/PostgreSQL without changing the scoring interface.

## Adding a fictional scenario

Edit the constants in `engine/generate_synthetic_data.py`, then run:

```bash
python engine/generate_synthetic_data.py
python engine/run_pipeline.py
python -m unittest discover -s tests -p "test_*.py"
```

Every observation timestamp must be no later than the scenario clock. Probabilities must be in $[0,1]$, IDs must be unique, and references must point to existing people/events.
