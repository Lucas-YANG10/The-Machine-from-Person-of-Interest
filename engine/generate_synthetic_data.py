"""Generate the deterministic, entirely fictional Manhattan scenario.

The records in this module are invented for an educational simulation.  They
do not describe real people, businesses, incidents, or surveillance feeds.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "synthetic"
SCENARIO_TIME = "2026-08-13T21:40:00-04:00"


PEOPLE = [
    {"id": "P-017", "name": "Lena Ortiz", "code": "ORTIZ, L.", "occupation": "Night pharmacist", "home_zone": "Chelsea", "baseline_mobility": 0.34},
    {"id": "P-024", "name": "Darius Cole", "code": "COLE, D.", "occupation": "Independent courier", "home_zone": "Lower East Side", "baseline_mobility": 0.71},
    {"id": "P-031", "name": "Evelyn Park", "code": "PARK, E.", "occupation": "Archive researcher", "home_zone": "Upper West Side", "baseline_mobility": 0.29},
    {"id": "P-044", "name": "Noah Vale", "code": "VALE, N.", "occupation": "Building technician", "home_zone": "Harlem", "baseline_mobility": 0.58},
    {"id": "P-052", "name": "Mika Rowe", "code": "ROWE, M.", "occupation": "Nonprofit bookkeeper", "home_zone": "Greenwich Village", "baseline_mobility": 0.22},
    {"id": "P-063", "name": "Julian Sayer", "code": "SAYER, J.", "occupation": "Financial analyst", "home_zone": "Midtown", "baseline_mobility": 0.48},
    {"id": "P-078", "name": "Tasha Bell", "code": "BELL, T.", "occupation": "Restaurant manager", "home_zone": "SoHo", "baseline_mobility": 0.55},
    {"id": "P-086", "name": "Isaac Reed", "code": "REED, I.", "occupation": "Paramedic", "home_zone": "Upper East Side", "baseline_mobility": 0.76},
    {"id": "P-099", "name": "Elias North", "code": "NORTH, E.", "occupation": "Graduate student", "home_zone": "Inwood", "baseline_mobility": 0.41},
]


ZONES = [
    {"id": "inwood", "name": "Inwood", "centroid": [214, 66], "polygon": [[184, 34], [252, 48], [254, 95], [178, 103]], "background": 0.08},
    {"id": "harlem", "name": "Harlem", "centroid": [211, 137], "polygon": [[178, 103], [254, 95], [271, 166], [162, 174]], "background": 0.11},
    {"id": "upper-west", "name": "Upper West Side", "centroid": [181, 231], "polygon": [[162, 174], [214, 170], [218, 293], [145, 303]], "background": 0.07},
    {"id": "upper-east", "name": "Upper East Side", "centroid": [246, 229], "polygon": [[214, 170], [271, 166], [286, 282], [218, 293]], "background": 0.06},
    {"id": "midtown", "name": "Midtown", "centroid": [215, 344], "polygon": [[145, 303], [286, 282], [277, 399], [151, 411]], "background": 0.13},
    {"id": "chelsea", "name": "Chelsea", "centroid": [174, 451], "polygon": [[151, 411], [215, 405], [214, 493], [137, 502]], "background": 0.10},
    {"id": "greenwich", "name": "Greenwich Village", "centroid": [210, 522], "polygon": [[214, 493], [268, 488], [274, 548], [160, 558], [137, 502]], "background": 0.09},
    {"id": "soho", "name": "SoHo", "centroid": [200, 580], "polygon": [[160, 558], [274, 548], [262, 606], [151, 615]], "background": 0.12},
    {"id": "lower-east", "name": "Lower East Side", "centroid": [246, 625], "polygon": [[210, 609], [262, 606], [273, 659], [218, 665]], "background": 0.14},
    {"id": "financial", "name": "Financial District", "centroid": [195, 680], "polygon": [[151, 615], [210, 609], [218, 665], [202, 724], [158, 694]], "background": 0.09},
]


EVENTS = [
    {
        "id": "EV-042",
        "title": "23rd Street handoff",
        "zone": "Chelsea",
        "location": "W 23rd St / 10th Ave",
        "coordinates": [166, 458],
        "starts_at": "2026-08-13T22:25:00-04:00",
        "type_prior": {"robbery": 0.48, "assault": 0.29, "abduction": 0.13, "fraud": 0.10},
    },
    {
        "id": "EV-113",
        "title": "Canal service corridor",
        "zone": "SoHo",
        "location": "Canal St / Greene St",
        "coordinates": [196, 579],
        "starts_at": "2026-08-13T23:10:00-04:00",
        "type_prior": {"robbery": 0.16, "assault": 0.24, "abduction": 0.52, "fraud": 0.08},
    },
    {
        "id": "EV-208",
        "title": "Ledger extraction",
        "zone": "Financial District",
        "location": "Nassau St / Cedar St",
        "coordinates": [194, 682],
        "starts_at": "2026-08-14T00:05:00-04:00",
        "type_prior": {"robbery": 0.11, "assault": 0.08, "abduction": 0.04, "fraud": 0.77},
    },
    {
        "id": "EV-305",
        "title": "Columbus Circle intercept",
        "zone": "Midtown",
        "location": "W 59th St / 8th Ave",
        "coordinates": [178, 318],
        "starts_at": "2026-08-14T01:20:00-04:00",
        "type_prior": {"robbery": 0.33, "assault": 0.43, "abduction": 0.15, "fraud": 0.09},
    },
]


def record(
    record_id: str,
    person_id: str,
    event_id: str,
    timestamp: str,
    source: str,
    summary: str,
    detail: str,
    tags: list[str],
    *,
    reliability: float,
    related_person_id: str | None = None,
) -> dict:
    return {
        "id": record_id,
        "person_id": person_id,
        "event_id": event_id,
        "timestamp": timestamp,
        "source": source,
        "summary": summary,
        "detail": detail,
        "tags": tags,
        "reliability": reliability,
        "related_person_id": related_person_id,
    }


OBSERVATIONS = [
    record("MSG-104", "P-017", "EV-042", "2026-08-13T19:18:00-04:00", "message", "Unrecognized sender asks whether she closes alone", 'Message: "Still closing by yourself tonight?"', ["targeted", "vulnerability", "threat_language"], reliability=0.84),
    record("TRN-221", "P-017", "EV-042", "2026-08-13T20:55:00-04:00", "transit", "Usual train replaced by a late westbound bus", "Route diverges 2.8 km from twelve-week baseline", ["route_change", "proximity", "anomaly"], reliability=0.96),
    record("CAM-881", "P-017", "EV-042", "2026-08-13T21:31:00-04:00", "camera", "Subject enters the projected event radius", "Synthetic camera hit at W 22nd Street", ["proximity", "vulnerability"], reliability=0.72),
    record("CAL-310", "P-017", "EV-042", "2026-08-13T17:04:00-04:00", "calendar", "Closing shift extended by forty minutes", "Staffing schedule edit places subject near event window", ["schedule_match", "proximity"], reliability=0.91),

    record("PUR-401", "P-024", "EV-042", "2026-08-13T15:42:00-04:00", "purchase", "Cash purchase of a prepaid handset", "Corner electronics receipt; device activated 16:03", ["burner_device", "capability", "anomaly"], reliability=0.81),
    record("MSG-119", "P-024", "EV-042", "2026-08-13T20:07:00-04:00", "message", "Coordinates and exit timing exchanged", 'Message: "West door. 22:25. Two minutes, then gone."', ["coordination", "timing", "intent", "proximity"], reliability=0.89, related_person_id="P-044"),
    record("LOC-902", "P-024", "EV-042", "2026-08-13T21:26:00-04:00", "location", "Three short stops around the same block", "Synthetic device pings form a surveillance loop", ["casing", "proximity", "mobility_anomaly"], reliability=0.77),
    record("FIN-507", "P-024", "EV-042", "2026-08-12T23:16:00-04:00", "finance", "Courier account receives an unusual cash-equivalent transfer", "$640 equivalent from a dormant sender", ["financial_motive", "anomaly", "coordination"], reliability=0.86, related_person_id="P-044"),

    record("MSG-133", "P-031", "EV-113", "2026-08-13T18:03:00-04:00", "message", "Anonymous warning references a private archive visit", 'Message: "The Canal files were never yours to read."', ["targeted", "vulnerability", "threat_language"], reliability=0.83),
    record("TRN-240", "P-031", "EV-113", "2026-08-13T20:48:00-04:00", "transit", "Ride-share destination changed to Canal Street", "Destination entered after a cancelled subway trip", ["route_change", "proximity", "anomaly"], reliability=0.93),
    record("CAL-328", "P-031", "EV-113", "2026-08-13T14:11:00-04:00", "calendar", "Meeting added by an unknown external address", "Invitation title: ARCHIVE RETURN / 23:00", ["schedule_match", "targeted", "proximity"], reliability=0.74),
    record("CAM-894", "P-031", "EV-113", "2026-08-13T21:34:00-04:00", "camera", "Same dark vehicle appears in two nonadjacent locations", "Synthetic plate token repeats behind subject", ["followed", "vulnerability", "threat_language"], reliability=0.68),

    record("ACS-601", "P-044", "EV-113", "2026-08-13T16:52:00-04:00", "access", "Service-corridor badge cloned outside shift", "Two denied entries followed by a successful entry", ["capability", "casing", "anomaly"], reliability=0.92),
    record("PUR-417", "P-044", "EV-113", "2026-08-13T12:37:00-04:00", "purchase", "Work order includes cable ties and opaque sheeting", "Items inconsistent with assigned maintenance call", ["restraint_access", "capability", "anomaly"], reliability=0.78),
    record("MSG-148", "P-044", "EV-113", "2026-08-13T20:21:00-04:00", "message", "Instructions reference lower loading entrance", 'Message: "Keep the corridor clear. Van takes the lower ramp."', ["coordination", "intent", "timing", "proximity"], reliability=0.87, related_person_id="P-024"),
    record("LOC-919", "P-044", "EV-113", "2026-08-13T21:17:00-04:00", "location", "Vehicle idles near the service ramp", "Fourteen-minute dwell with engine running", ["proximity", "casing", "mobility_anomaly"], reliability=0.79),

    record("EML-710", "P-052", "EV-208", "2026-08-13T16:09:00-04:00", "email", "Reports a ledger discrepancy to a private address", "Attachment hash matches the altered grant ledger", ["financial_target", "vulnerability", "targeted"], reliability=0.88),
    record("ACS-622", "P-052", "EV-208", "2026-08-13T19:44:00-04:00", "access", "Credentials rejected after an unrequested password reset", "Synthetic audit log: five failed sign-ins", ["account_takeover", "vulnerability", "anomaly"], reliability=0.94),
    record("TRN-256", "P-052", "EV-208", "2026-08-13T21:02:00-04:00", "transit", "Heads downtown after being summoned by a supervisor alias", "Tap-in aligns with Nassau Street arrival window", ["route_change", "proximity", "targeted"], reliability=0.91),
    record("MSG-159", "P-052", "EV-208", "2026-08-13T21:11:00-04:00", "message", "Sender pressures subject to bring the only local copy", 'Message: "Bring the drive. Do not upload it."', ["financial_target", "threat_language", "vulnerability"], reliability=0.82),

    record("NET-802", "P-063", "EV-208", "2026-08-13T13:26:00-04:00", "network", "Encrypted archive staged for timed transfer", "Outbound bundle contains synthetic ledger fragments", ["account_takeover", "capability", "intent", "financial_motive"], reliability=0.95),
    record("FIN-529", "P-063", "EV-208", "2026-08-13T17:38:00-04:00", "finance", "New shell account receives test deposits", "Three transfers below internal review threshold", ["financial_motive", "coordination", "anomaly"], reliability=0.90),
    record("MSG-171", "P-063", "EV-208", "2026-08-13T20:46:00-04:00", "message", "Requests physical drive and confirms deadline", 'Message: "Midnight. Local copy first, then the account clears."', ["coordination", "timing", "intent", "financial_target"], reliability=0.91, related_person_id="P-052"),
    record("LOC-934", "P-063", "EV-208", "2026-08-13T21:24:00-04:00", "location", "Office device appears downtown outside normal hours", "Twenty-four week baseline has no comparable visit", ["proximity", "mobility_anomaly", "anomaly"], reliability=0.76),

    record("RES-901", "P-078", "EV-305", "2026-08-13T18:54:00-04:00", "reservation", "Last-minute table cancellation near Columbus Circle", "Manager handles a routine cancellation", ["schedule_match"], reliability=0.73),
    record("TRN-271", "P-078", "EV-305", "2026-08-13T20:38:00-04:00", "transit", "Bus route passes event radius", "Route is common for this subject", ["proximity"], reliability=0.92),
    record("MSG-182", "P-078", "EV-305", "2026-08-13T21:07:00-04:00", "message", "Asks coworker to cover the closing shift", 'Message: "Running late—can you lock up?"', ["route_change"], reliability=0.77),

    record("DSP-010", "P-086", "EV-305", "2026-08-13T21:14:00-04:00", "dispatch", "Anonymous medical call redirects ambulance unit", "Caller disconnects before triage completes", ["targeted", "schedule_match", "proximity", "anomaly"], reliability=0.89),
    record("MSG-196", "P-086", "EV-305", "2026-08-13T20:58:00-04:00", "message", "Unknown sender claims to know the unit route", 'Message: "Unit 14 will reach the circle first."', ["targeted", "threat_language", "vulnerability"], reliability=0.79),
    record("LOC-949", "P-086", "EV-305", "2026-08-13T21:29:00-04:00", "location", "Dispatch route converges on projected event point", "Synthetic AVL coordinate within 340 m", ["proximity", "mobility_anomaly"], reliability=0.97),
    record("CAL-344", "P-086", "EV-305", "2026-08-13T18:22:00-04:00", "calendar", "Shift swap places subject in Unit 14", "Change approved by a newly created account", ["targeted", "vulnerability", "anomaly"], reliability=0.85),

    record("LIB-011", "P-099", "EV-113", "2026-08-13T17:16:00-04:00", "library", "Returns an urban history book near closing", "Ordinary account activity", [], reliability=0.98),
    record("TRN-289", "P-099", "EV-113", "2026-08-13T20:14:00-04:00", "transit", "Normal commute remains in Upper Manhattan", "No spatial overlap with event radius", [], reliability=0.95),
    record("FIN-544", "P-099", "EV-208", "2026-08-13T18:31:00-04:00", "finance", "Routine grocery purchase", "$31.42 at a regular merchant", [], reliability=0.91),
]


GROUND_TRUTH = {
    "threshold": 0.62,
    "labels": [
        {"person_id": "P-017", "event_id": "EV-042", "involved": True, "role": "victim"},
        {"person_id": "P-024", "event_id": "EV-042", "involved": True, "role": "perpetrator"},
        {"person_id": "P-031", "event_id": "EV-113", "involved": True, "role": "victim"},
        {"person_id": "P-044", "event_id": "EV-113", "involved": True, "role": "perpetrator"},
        {"person_id": "P-052", "event_id": "EV-208", "involved": True, "role": "victim"},
        {"person_id": "P-063", "event_id": "EV-208", "involved": True, "role": "perpetrator"},
        {"person_id": "P-086", "event_id": "EV-305", "involved": True, "role": "victim"},
        {"person_id": "P-078", "event_id": "EV-305", "involved": False, "role": "bystander"},
    ],
}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    write_json(DATA_DIR / "people.json", PEOPLE)
    write_json(DATA_DIR / "zones.json", ZONES)
    write_json(DATA_DIR / "events.json", EVENTS)
    write_json(DATA_DIR / "observations.json", OBSERVATIONS)
    write_json(DATA_DIR / "ground_truth.json", GROUND_TRUTH)
    write_json(DATA_DIR / "scenario.json", {"scenario_time": SCENARIO_TIME, "synthetic": True, "seed": 1100101})
    print(f"Wrote {len(PEOPLE)} people, {len(EVENTS)} events, and {len(OBSERVATIONS)} observations to {DATA_DIR}")


if __name__ == "__main__":
    main()
