"""Run the transparent baseline for the fictional Machine scenario.

The engine deliberately favors auditable math over model complexity.  It
turns heterogeneous records into a temporal person-event graph, aggregates
evidence with a noisy-OR, propagates one graph hop, and produces calibrated-ish
demo scores.  These scores are not claims about real-world criminality.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "synthetic"
APP_OUTPUT = ROOT / "app" / "data" / "machine-output.json"
PUBLIC_OUTPUT = ROOT / "public" / "data" / "machine-output.json"

FEATURES = (
    "intent",
    "capability",
    "proximity",
    "coordination",
    "vulnerability",
    "threat",
    "financial",
    "mobility",
    "anomaly",
)

TAG_EFFECTS: dict[str, dict[str, float]] = {
    "targeted": {"vulnerability": 0.62, "anomaly": 0.30},
    "vulnerability": {"vulnerability": 0.82},
    "threat_language": {"threat": 0.78, "vulnerability": 0.34},
    "route_change": {"mobility": 0.56, "anomaly": 0.48},
    "proximity": {"proximity": 0.84},
    "schedule_match": {"proximity": 0.58, "anomaly": 0.18},
    "burner_device": {"capability": 0.52, "coordination": 0.35, "anomaly": 0.64},
    "capability": {"capability": 0.80},
    "coordination": {"coordination": 0.82},
    "timing": {"intent": 0.62, "coordination": 0.44},
    "intent": {"intent": 0.86},
    "casing": {"intent": 0.54, "proximity": 0.48, "anomaly": 0.45},
    "mobility_anomaly": {"mobility": 0.72, "anomaly": 0.66},
    "financial_motive": {"financial": 0.78, "intent": 0.36},
    "followed": {"vulnerability": 0.80, "threat": 0.42},
    "restraint_access": {"capability": 0.86, "threat": 0.48},
    "financial_target": {"financial": 0.76, "vulnerability": 0.52},
    "account_takeover": {"capability": 0.68, "financial": 0.64, "anomaly": 0.58},
    "anomaly": {"anomaly": 0.72},
}

HALF_LIFE_HOURS = {
    "camera": 3.0,
    "location": 4.0,
    "dispatch": 5.0,
    "transit": 7.0,
    "message": 10.0,
    "access": 12.0,
    "network": 12.0,
    "finance": 24.0,
    "purchase": 30.0,
    "calendar": 18.0,
    "email": 18.0,
    "reservation": 12.0,
    "library": 24.0,
}

INVOLVEMENT_WEIGHTS = {
    "intent": 1.35,
    "capability": 1.15,
    "proximity": 1.20,
    "coordination": 1.00,
    "vulnerability": 1.25,
    "threat": 0.90,
    "financial": 0.55,
    "mobility": 0.50,
    "anomaly": 0.65,
}

FEATURE_LABELS = {
    "intent": "Intent signal",
    "capability": "Capability access",
    "proximity": "Spatiotemporal overlap",
    "coordination": "Coordination pattern",
    "vulnerability": "Target vulnerability",
    "threat": "Threat language",
    "financial": "Financial motive",
    "mobility": "Mobility deviation",
    "anomaly": "Baseline anomaly",
    "graph": "Network propagation",
    "imminence": "Event imminence",
}

CRIME_TYPES = ("robbery", "assault", "abduction", "fraud")


def load_json(name: str) -> Any:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def softmax(logits: dict[str, float]) -> dict[str, float]:
    maximum = max(logits.values())
    exps = {key: math.exp(value - maximum) for key, value in logits.items()}
    total = sum(exps.values())
    return {key: value / total for key, value in exps.items()}


def entropy(probabilities: dict[str, float]) -> float:
    values = [value for value in probabilities.values() if value > 0]
    raw = -sum(value * math.log(value) for value in values)
    return raw / math.log(len(probabilities))


def temporal_weight(observation: dict[str, Any], scenario_time: datetime) -> float:
    observed_at = datetime.fromisoformat(observation["timestamp"])
    age_hours = max(0.0, (scenario_time - observed_at).total_seconds() / 3600)
    half_life = HALF_LIFE_HOURS.get(observation["source"], 12.0)
    decay = math.exp(-math.log(2) * age_hours / half_life)
    return observation["reliability"] * decay


def is_model_signal(observation: dict[str, Any]) -> bool:
    """Return True only when at least one tag affects a model feature.

    The expanded dataset intentionally contains thousands of ordinary records.
    They remain available in the raw JSON, but should not inflate confidence or
    appear as incriminating evidence merely because the system observed them.
    """

    return any(tag in TAG_EFFECTS for tag in observation["tags"])


def aggregate_features(
    observations: list[dict[str, Any]], scenario_time: datetime
) -> tuple[dict[str, float], dict[str, list[str]], float]:
    complements = {feature: 1.0 for feature in FEATURES}
    provenance: dict[str, list[str]] = defaultdict(list)
    evidence_mass = 0.0

    for observation in observations:
        weight = temporal_weight(observation, scenario_time)
        strongest: dict[str, float] = defaultdict(float)
        for tag in observation["tags"]:
            for feature, strength in TAG_EFFECTS.get(tag, {}).items():
                strongest[feature] = max(strongest[feature], strength)
        for feature, strength in strongest.items():
            complements[feature] *= 1.0 - min(0.98, weight * strength)
            provenance[feature].append(observation["id"])
        if strongest:
            evidence_mass += weight

    features = {feature: 1.0 - complement for feature, complement in complements.items()}
    return features, dict(provenance), evidence_mass


def event_imminence(event: dict[str, Any], scenario_time: datetime) -> float:
    starts_at = datetime.fromisoformat(event["starts_at"])
    hours = max(0.0, (starts_at - scenario_time).total_seconds() / 3600)
    return math.exp(-hours / 6.0)


def role_probabilities(features: dict[str, float]) -> dict[str, float]:
    logits = {
        "perpetrator": (
            -0.40
            + 1.50 * features["intent"]
            + 1.25 * features["capability"]
            + 0.80 * features["coordination"]
            + 0.70 * features["threat"]
            + 0.30 * features["financial"]
            - 0.85 * features["vulnerability"]
        ),
        "victim": (
            -0.20
            + 1.70 * features["vulnerability"]
            + 0.70 * features["proximity"]
            + 0.50 * features["threat"]
            - 0.65 * features["intent"]
            - 0.40 * features["capability"]
        ),
        "ambiguous": 0.10 + 0.35 * features["anomaly"] + 0.25 * features["proximity"],
    }
    return softmax(logits)


def crime_probabilities(event: dict[str, Any], features: dict[str, float]) -> dict[str, float]:
    logits = {key: math.log(max(value, 1e-8)) for key, value in event["type_prior"].items()}
    logits["robbery"] += 0.80 * features["financial"] + 0.35 * features["capability"]
    logits["assault"] += 0.90 * features["threat"] + 0.30 * features["intent"]
    logits["abduction"] += 0.65 * features["capability"] + 0.45 * features["coordination"]
    logits["fraud"] += 1.00 * features["financial"] + 0.55 * features["capability"]
    return softmax(logits)


def involvement_score(
    features: dict[str, float], graph_signal: float, imminence: float
) -> tuple[float, dict[str, float]]:
    components = {feature: INVOLVEMENT_WEIGHTS[feature] * value for feature, value in features.items()}
    components["graph"] = 0.80 * graph_signal
    components["imminence"] = 1.10 * imminence
    logit = -2.55 + sum(components.values())
    return sigmoid(logit), components


def score_all_pairs(
    people: list[dict[str, Any]],
    events: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    scenario_time: datetime,
) -> dict[tuple[str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for observation in observations:
        grouped[(observation["person_id"], observation["event_id"])].append(observation)

    aggregate: dict[tuple[str, str], dict[str, Any]] = {}
    for person in people:
        for event in events:
            key = (person["id"], event["id"])
            features, provenance, mass = aggregate_features(grouped[key], scenario_time)
            aggregate[key] = {"features": features, "provenance": provenance, "mass": mass}

    neighbours: dict[tuple[str, str], list[tuple[str, float]]] = defaultdict(list)
    for observation in observations:
        related = observation.get("related_person_id")
        if related:
            edge_weight = temporal_weight(observation, scenario_time)
            neighbours[(observation["person_id"], observation["event_id"])].append((related, edge_weight))
            neighbours[(related, observation["event_id"])].append((observation["person_id"], edge_weight))

    scored: dict[tuple[str, str], dict[str, Any]] = {}
    events_by_id = {event["id"]: event for event in events}
    for key, bundle in aggregate.items():
        person_id, event_id = key
        graph_complement = 1.0
        for neighbour_id, edge_weight in neighbours[key]:
            neighbour_features = aggregate[(neighbour_id, event_id)]["features"]
            neighbour_signal = max(
                neighbour_features["intent"],
                neighbour_features["coordination"],
                neighbour_features["vulnerability"],
            )
            graph_complement *= 1.0 - min(0.85, 0.58 * edge_weight * neighbour_signal)
        graph_signal = 1.0 - graph_complement
        imminence = event_imminence(events_by_id[event_id], scenario_time)
        score, components = involvement_score(bundle["features"], graph_signal, imminence)
        roles = role_probabilities(bundle["features"])
        crimes = crime_probabilities(events_by_id[event_id], bundle["features"])
        scored[key] = {
            **bundle,
            "score": score,
            "graph": graph_signal,
            "imminence": imminence,
            "components": components,
            "roles": roles,
            "crime_types": crimes,
        }
    return scored


def evaluate(
    scored: dict[tuple[str, str], dict[str, Any]],
    people: list[dict[str, Any]],
    events: list[dict[str, Any]],
    ground_truth: dict[str, Any],
) -> dict[str, Any]:
    threshold = ground_truth["threshold"]
    truth_lookup = {
        (label["person_id"], label["event_id"]): label for label in ground_truth["labels"]
    }
    tp = fp = fn = tn = 0
    squared_error = 0.0
    role_correct = role_total = 0
    for person in people:
        for event in events:
            key = (person["id"], event["id"])
            truth = truth_lookup.get(key, {"involved": False})
            actual = bool(truth["involved"])
            predicted = scored[key]["score"] >= threshold
            if actual and predicted:
                tp += 1
            elif predicted:
                fp += 1
            elif actual:
                fn += 1
            else:
                tn += 1
            squared_error += (scored[key]["score"] - float(actual)) ** 2
            if actual and truth.get("role") in {"victim", "perpetrator"}:
                role_total += 1
                predicted_role = max(scored[key]["roles"], key=scored[key]["roles"].get)
                role_correct += int(predicted_role == truth["role"])

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "brier": squared_error / (len(people) * len(events)),
        "role_accuracy": role_correct / role_total if role_total else 0.0,
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "evaluated_pairs": len(people) * len(events),
        "note": "Metrics are measured only against the synthetic scenario ground truth.",
    }


def round_tree(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, dict):
        return {key: round_tree(child) for key, child in value.items()}
    if isinstance(value, list):
        return [round_tree(child) for child in value]
    return value


def build_output() -> dict[str, Any]:
    people = load_json("people.json")
    zones = load_json("zones.json")
    events = load_json("events.json")
    observations = load_json("observations.json")
    ground_truth = load_json("ground_truth.json")
    scenario = load_json("scenario.json")
    scenario_time = datetime.fromisoformat(scenario["scenario_time"])
    scored = score_all_pairs(people, events, observations, scenario_time)
    threshold = ground_truth["threshold"]
    events_by_id = {event["id"]: event for event in events}
    zones_by_name = {zone["name"]: zone for zone in zones}
    observations_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for observation in observations:
        observations_by_pair[(observation["person_id"], observation["event_id"])].append(observation)

    person_outputs = []
    for person in people:
        best_event_id = max(
            (event["id"] for event in events),
            key=lambda event_id: scored[(person["id"], event_id)]["score"],
        )
        best = scored[(person["id"], best_event_id)]
        event = events_by_id[best_event_id]
        evidence = sorted(
            (
                item
                for item in observations_by_pair[(person["id"], best_event_id)]
                if is_model_signal(item)
            ),
            key=lambda item: item["timestamp"],
            reverse=True,
        )
        positive_total = sum(max(value, 0.0) for value in best["components"].values()) or 1.0
        explanations = []
        for feature, value in sorted(best["components"].items(), key=lambda item: item[1], reverse=True)[:5]:
            explanations.append(
                {
                    "feature": feature,
                    "label": FEATURE_LABELS[feature],
                    "value": value / positive_total,
                    "record_ids": best["provenance"].get(feature, []),
                }
            )
        role_uncertainty = entropy(best["roles"])
        evidence_confidence = 1.0 - math.exp(-best["mass"] / 2.6)
        confidence = 0.72 * evidence_confidence + 0.28 * (1.0 - role_uncertainty)
        offset = person.get("display_offset", [0, 0])
        is_relevant = best["score"] >= threshold
        home_zone = zones_by_name.get(person.get("home_zone", ""))
        anchor = event["coordinates"] if is_relevant or home_zone is None else home_zone["centroid"]
        map_zone = event["zone"] if is_relevant or home_zone is None else home_zone["name"]
        person_outputs.append(
            {
                **person,
                "event_id": best_event_id,
                "event_title": event["title"],
                "zone": event["zone"],
                "location": event["location"],
                "map_zone": map_zone,
                "coordinates": [anchor[0] + offset[0], anchor[1] + offset[1]],
                "involvement": best["score"],
                "status": "relevant" if is_relevant else "background",
                "roles": best["roles"],
                "crime_types": best["crime_types"],
                "confidence": confidence,
                "role_uncertainty": role_uncertainty,
                "imminence_minutes": round(
                    (datetime.fromisoformat(event["starts_at"]) - scenario_time).total_seconds() / 60
                ),
                "features": best["features"],
                "explanations": explanations,
                "evidence": [
                    {
                        "id": item["id"],
                        "source": item["source"],
                        "timestamp": item["timestamp"],
                        "summary": item["summary"],
                        "detail": item["detail"],
                        "reliability": item["reliability"],
                    }
                    for item in evidence
                ],
            }
        )

    event_outputs = []
    for event in events:
        pair_scores = [(person["id"], scored[(person["id"], event["id"])]) for person in people]
        relevant = [person_id for person_id, bundle in pair_scores if bundle["score"] >= threshold]
        combined_risk = 1.0
        for _, bundle in pair_scores:
            # A no-evidence person still has a small logistic prior. Subtracting
            # that floor prevents event risk from rising merely because the
            # synthetic population grew from 9 to 30 people.
            evidence_adjusted = max(0.0, bundle["score"] - 0.24) / 0.76
            combined_risk *= 1.0 - evidence_adjusted**2
        crime_mix = {
            crime: sum(bundle["crime_types"][crime] * bundle["score"] for _, bundle in pair_scores)
            for crime in CRIME_TYPES
        }
        crime_total = sum(crime_mix.values()) or 1.0
        event_outputs.append(
            {
                **event,
                "risk": 1.0 - combined_risk,
                "imminence": event_imminence(event, scenario_time),
                "imminence_minutes": round(
                    (datetime.fromisoformat(event["starts_at"]) - scenario_time).total_seconds() / 60
                ),
                "participants": relevant,
                "signal_count": sum(
                    is_model_signal(observation)
                    for person in people
                    for observation in observations_by_pair[(person["id"], event["id"])]
                ),
                "crime_types": {crime: value / crime_total for crime, value in crime_mix.items()},
            }
        )

    zone_outputs = []
    for zone in zones:
        hazard = zone["background"]
        contributors = []
        for event in event_outputs:
            dx = zone["centroid"][0] - event["coordinates"][0]
            dy = zone["centroid"][1] - event["coordinates"][1]
            kernel = math.exp(-(dx * dx + dy * dy) / (2 * 92.0**2))
            contribution = event["risk"] * event["imminence"] * kernel
            hazard += contribution
            if contribution > 0.08:
                contributors.append(event["id"])
        risk = 1.0 - math.exp(-0.82 * hazard)
        zone_outputs.append(
            {
                **zone,
                "risk": risk,
                "trend": "rising" if risk > 0.42 else "stable" if risk > 0.20 else "quiet",
                "contributors": contributors,
            }
        )

    timeline = [
        {
            "id": item["id"],
            "timestamp": item["timestamp"],
            "source": item["source"],
            "person_id": item["person_id"],
            "event_id": item["event_id"],
            "summary": item["summary"],
        }
        for item in sorted(observations, key=lambda item: item["timestamp"], reverse=True)[:18]
    ]

    output = {
        "meta": {
            "title": "The Machine: Manhattan",
            "model_version": "transparent-baseline-v0.3",
            "scenario_time": scenario["scenario_time"],
            "threshold": threshold,
            "synthetic": True,
            "counts": scenario.get("counts", {}),
            "geography": scenario.get("geography", {}),
            "disclaimer": "All identities, records, incidents, and scores are fictional. Educational simulation only.",
        },
        "people": sorted(person_outputs, key=lambda item: item["involvement"], reverse=True),
        "events": sorted(event_outputs, key=lambda item: item["risk"], reverse=True),
        "zones": zone_outputs,
        "timeline": timeline,
        "metrics": evaluate(scored, people, events, ground_truth),
    }
    return round_tree(output)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(APP_OUTPUT, output)
    write_json(PUBLIC_OUTPUT, output)
    relevant = sum(person["status"] == "relevant" for person in output["people"])
    print(f"Scored {len(output['people'])} people; {relevant} crossed the relevance threshold")
    print(f"Wrote {APP_OUTPUT.relative_to(ROOT)} and {PUBLIC_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
