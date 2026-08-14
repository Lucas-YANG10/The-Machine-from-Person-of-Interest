"use client";

import { useMemo, useState } from "react";
import machineJson from "./data/machine-output.json";

type ProbabilityMap = Record<string, number>;

type Evidence = {
  id: string;
  source: string;
  timestamp: string;
  summary: string;
  detail: string;
  reliability: number;
};

type Person = {
  id: string;
  name: string;
  code: string;
  occupation: string;
  event_id: string;
  event_title: string;
  zone: string;
  map_zone: string;
  location: string;
  coordinates: [number, number];
  involvement: number;
  status: string;
  roles: ProbabilityMap;
  crime_types: ProbabilityMap;
  confidence: number;
  role_uncertainty: number;
  imminence_minutes: number;
  features: ProbabilityMap;
  explanations: Array<{
    feature: string;
    label: string;
    value: number;
    record_ids: string[];
  }>;
  evidence: Evidence[];
};

type EventCandidate = {
  id: string;
  title: string;
  zone: string;
  location: string;
  coordinates: [number, number];
  starts_at: string;
  risk: number;
  imminence: number;
  imminence_minutes: number;
  participants: string[];
  signal_count: number;
  crime_types: ProbabilityMap;
};

type Zone = {
  id: string;
  name: string;
  label: string;
  centroid: [number, number];
  polygons: Array<Array<[number, number]>>;
  label_priority: boolean;
  risk: number;
  trend: string;
  contributors: string[];
};

type MachineData = {
  meta: {
    title: string;
    model_version: string;
    scenario_time: string;
    threshold: number;
    synthetic: boolean;
    disclaimer: string;
  };
  people: Person[];
  events: EventCandidate[];
  zones: Zone[];
  timeline: Array<{
    id: string;
    timestamp: string;
    source: string;
    person_id: string;
    event_id: string;
    summary: string;
  }>;
  metrics: {
    precision: number;
    recall: number;
    f1: number;
    brier: number;
    role_accuracy: number;
    evaluated_pairs: number;
    confusion: { tp: number; fp: number; fn: number; tn: number };
    note: string;
  };
};

const data = machineJson as unknown as MachineData;
type Surface = "city" | "network" | "model";
type Mode = "machine" | "analyst";

const percent = (value: number, digits = 0) => `${(value * 100).toFixed(digits)}%`;
const timeOnly = (value: string) =>
  new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "America/New_York",
  }).format(new Date(value));

const titleCase = (value: string) =>
  value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

function RiskBar({ value, danger = false }: { value: number; danger?: boolean }) {
  return (
    <div className="risk-track" aria-hidden="true">
      <span
        className={danger ? "danger" : ""}
        style={{ width: `${Math.max(2, value * 100)}%` }}
      />
    </div>
  );
}

function ManhattanMap({
  people,
  events,
  zones,
  threshold,
  selectedPerson,
  selectedZone,
  mode,
  onPerson,
  onZone,
}: {
  people: Person[];
  events: EventCandidate[];
  zones: Zone[];
  threshold: number;
  selectedPerson: Person;
  selectedZone: string;
  mode: Mode;
  onPerson: (id: string) => void;
  onZone: (id: string) => void;
}) {
  return (
    <div className="map-stage">
      <div className="map-coordinate north">40.8781° N</div>
      <div className="map-coordinate south">40.7003° N</div>
      <div className="scan-beam" />
      <svg
        className="manhattan-map"
        viewBox="0 0 420 760"
        role="img"
        aria-label="Synthetic risk map using official Manhattan NTA boundaries"
      >
        <defs>
          <pattern id="smallGrid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" className="map-grid-line" />
          </pattern>
          <filter id="redGlow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="2.4" result="glow" />
            <feMerge>
              <feMergeNode in="glow" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <rect width="420" height="760" fill="url(#smallGrid)" />

        <g className="zones">
          {zones.map((zone) => {
            const active = zone.id === selectedZone;
            const path = zone.polygons
              .map((ring) => `M ${ring.map((point) => point.join(" ")).join(" L ")} Z`)
              .join(" ");
            const showLabel = active || zone.label_priority || zone.contributors.length > 0;
            return (
              <g
                key={zone.id}
                className={`zone ${active ? "active" : ""}`}
                role="button"
                tabIndex={0}
                aria-label={`${zone.name}, risk index ${percent(zone.risk)}`}
                onClick={() => onZone(zone.id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") onZone(zone.id);
                }}
              >
                <path
                  className="zone-shape"
                  d={path}
                  style={{ fillOpacity: 0.12 + zone.risk * 0.42 }}
                />
                {active && <path className="zone-selection" d={path} />}
                {showLabel && (
                  <text x={zone.centroid[0]} y={zone.centroid[1]} className="zone-label">
                    {zone.label}
                  </text>
                )}
                {active && mode === "analyst" && (
                  <text x={zone.centroid[0]} y={zone.centroid[1] + 13} className="zone-risk-label">
                    RISK {percent(zone.risk)}
                  </text>
                )}
              </g>
            );
          })}
        </g>

        <g className="event-links" aria-hidden="true">
          {people
            .filter((person) => person.involvement >= threshold)
            .map((person) => {
              const event = events.find((candidate) => candidate.id === person.event_id);
              if (!event) return null;
              return (
                <line
                  key={`${person.id}-${event.id}`}
                  x1={person.coordinates[0]}
                  y1={person.coordinates[1]}
                  x2={event.coordinates[0]}
                  y2={event.coordinates[1]}
                />
              );
            })}
        </g>

        <g className="event-points">
          {events.map((event) => (
            <g key={event.id} transform={`translate(${event.coordinates[0]} ${event.coordinates[1]})`}>
              <circle r="5" />
              <circle r="11" className="event-ring" />
              <path d="M-14 0H14M0-14V14" />
              <text x="15" y="-9">{event.id}</text>
            </g>
          ))}
        </g>

        <g className="subjects">
          {people.map((person) => {
            const relevant = person.involvement >= threshold;
            const selected = person.id === selectedPerson.id;
            if (!relevant && mode === "machine") return null;
            return (
              <g
                key={person.id}
                transform={`translate(${person.coordinates[0]} ${person.coordinates[1]})`}
                className={`subject ${relevant ? "relevant" : "background"} ${selected ? "selected" : ""}`}
                onClick={() => onPerson(person.id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") onPerson(person.id);
                }}
                role="button"
                tabIndex={0}
                aria-label={`${person.code}, involvement ${percent(person.involvement)}`}
              >
                <circle r="3.5" />
                {relevant && <rect x="-13" y="-18" width="26" height="36" filter="url(#redGlow)" />}
                {selected && <rect x="-18" y="-23" width="36" height="46" className="selection-frame" />}
                <text x="17" y="-7">{person.code}</text>
                <text x="17" y="6" className="subject-score">
                  {mode === "analyst" ? `INV ${percent(person.involvement)}` : "RELEVANT"}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
      <div className="map-legend">
        <span><i className="legend-box" /> relevant subject</span>
        <span><i className="legend-cross">+</i> candidate event</span>
        <span><i className="legend-heat" /> scenario risk</span>
      </div>
    </div>
  );
}

function CitySurface(props: Parameters<typeof ManhattanMap>[0] & { activeZone: Zone }) {
  return (
    <div className="city-surface">
      <ManhattanMap {...props} />
      <aside className="zone-panel">
        <div className="panel-kicker">AREA AGGREGATE</div>
        <h3>{props.activeZone.name}</h3>
        <div className="zone-risk-number">{percent(props.activeZone.risk)}</div>
        <RiskBar value={props.activeZone.risk} danger={props.activeZone.risk > 0.55} />
        <dl className="micro-stats">
          <div><dt>STATE</dt><dd>{props.activeZone.trend.toUpperCase()}</dd></div>
          <div><dt>EVENT LINKS</dt><dd>{props.activeZone.contributors.length}</dd></div>
          <div><dt>MODEL</dt><dd>KDE / 92U</dd></div>
        </dl>
        <p className="micro-note">
          This is a synthetic scenario-risk index, not a historical Manhattan crime rate.
        </p>
        <div className="zone-ranking">
          {props.zones
            .slice()
            .sort((a, b) => b.risk - a.risk)
            .slice(0, 5)
            .map((zone, index) => (
              <button key={zone.id} onClick={() => props.onZone(zone.id)}>
                <span>0{index + 1}</span>
                <b>{zone.name}</b>
                <em>{percent(zone.risk)}</em>
              </button>
            ))}
        </div>
      </aside>
    </div>
  );
}

function NetworkSurface({ person, event }: { person: Person; event: EventCandidate }) {
  return (
    <div className="network-surface">
      <div className="network-header">
        <div>
          <div className="panel-kicker">TEMPORAL HETEROGENEOUS GRAPH</div>
          <h2>{person.code} / {event.id}</h2>
        </div>
        <div className="network-summary">
          {person.evidence.length} records · 1 person · 1 candidate event
        </div>
      </div>
      <div className="network-flow">
        <section className="record-nodes" aria-label="Evidence records">
          <div className="column-label">RAW RECORDS</div>
          {person.evidence.map((item) => (
            <article className="record-node" key={item.id}>
              <span>{item.source.toUpperCase()}</span>
              <b>{item.id}</b>
              <p>{item.summary}</p>
              <em>q={item.reliability.toFixed(2)}</em>
            </article>
          ))}
        </section>
        <div className="flow-arrow" aria-hidden="true">→</div>
        <section className="entity-column">
          <div className="column-label">ENTITY</div>
          <article className="entity-node">
            <span>{person.id}</span>
            <div className="avatar-token">{person.name.split(" ").map((part) => part[0]).join("")}</div>
            <h3>{person.code}</h3>
            <p>{person.occupation}</p>
            <b>{percent(person.involvement)} involved</b>
          </article>
        </section>
        <div className="flow-arrow" aria-hidden="true">→</div>
        <section className="inference-column">
          <div className="column-label">INFERENCE</div>
          <article className="event-node">
            <span>{event.id}</span>
            <h3>{event.title}</h3>
            <p>{event.location}</p>
            <b>T−{event.imminence_minutes} MIN</b>
          </article>
          <article className="role-node">
            <span>ROLE POSTERIOR</span>
            {Object.entries(person.roles).map(([role, value]) => (
              <div key={role}><b>{titleCase(role)}</b><em>{percent(value)}</em></div>
            ))}
          </article>
        </section>
      </div>
      <div className="network-footnote">
        Edges encode observed association, not causation. Direction is the flow of computation.
      </div>
    </div>
  );
}

const formulae = [
  {
    index: "01",
    name: "Temporal reliability",
    formula: "wₒ(t) = qₒ · exp(−ln 2 · Δt / hₛ)",
    note: "Source reliability q and source-specific half-life hₛ make a fresh location ping decay faster than a purchase record.",
  },
  {
    index: "02",
    name: "Evidence fusion",
    formula: "zₖ = 1 − ∏ₒ (1 − wₒ fₒₖ)",
    note: "Noisy-OR fuses independent clues without letting repeated weak records grow without bound.",
  },
  {
    index: "03",
    name: "Graph propagation",
    formula: "gᵢₑ = 1 − ∏ⱼ(1 − 0.58 aᵢⱼ mⱼₑ)",
    note: "One transparent network hop transfers bounded support through an observed person-person link.",
  },
  {
    index: "04",
    name: "Involvement",
    formula: "P(Iᵢₑ=1) = σ(−2.55 + βᵀzᵢₑ + 0.8gᵢₑ + 1.1τₑ)",
    note: "The red frame is a threshold on event involvement—not a verdict and not a perpetrator label.",
  },
  {
    index: "05",
    name: "Role posterior",
    formula: "P(role=c | I=1) = exp(s꜀) / Σᵣ exp(sᵣ)",
    note: "Victim, perpetrator, and ambiguous compete in a softmax; entropy is retained as uncertainty.",
  },
  {
    index: "06",
    name: "Spatial risk",
    formula: "R(a,t) = 1 − exp[−η(bₐ + Σₑ pₑτₑKₕ(dₐₑ))]",
    note: "A Gaussian kernel spreads imminent event risk to nearby zones while retaining a small background term.",
  },
];

function ModelSurface({ metrics }: { metrics: MachineData["metrics"] }) {
  const stages = ["RECORDS", "FEATURES", "GRAPH", "INVOLVEMENT", "ROLE + TYPE", "MAP + UI"];
  return (
    <div className="model-surface">
      <div className="model-title-row">
        <div>
          <div className="panel-kicker">AUDITABLE BASELINE / v0.1</div>
          <h2>From records to a red frame</h2>
        </div>
        <p>Every displayed score is reproducible from the fixed synthetic files and Python engine.</p>
      </div>
      <div className="pipeline-strip">
        {stages.map((stage, index) => (
          <div key={stage}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <b>{stage}</b>
            {index < stages.length - 1 && <i>→</i>}
          </div>
        ))}
      </div>
      <div className="formula-grid">
        {formulae.map((item) => (
          <article key={item.index}>
            <header><span>{item.index}</span><h3>{item.name}</h3></header>
            <code>{item.formula}</code>
            <p>{item.note}</p>
          </article>
        ))}
      </div>
      <section className="evaluation-strip">
        <div>
          <span>SYNTHETIC SANITY CHECK</span>
          <p>Designed to verify that the full pipeline is wired correctly. It is not an external benchmark.</p>
        </div>
        <dl>
          <div><dt>PRECISION</dt><dd>{percent(metrics.precision)}</dd></div>
          <div><dt>RECALL</dt><dd>{percent(metrics.recall)}</dd></div>
          <div><dt>F1</dt><dd>{percent(metrics.f1)}</dd></div>
          <div><dt>BRIER ↓</dt><dd>{metrics.brier.toFixed(3)}</dd></div>
          <div><dt>PAIRS</dt><dd>{metrics.evaluated_pairs}</dd></div>
        </dl>
      </section>
    </div>
  );
}

function Dossier({ person, mode }: { person: Person; mode: Mode }) {
  const dominantCrime = maxEntry(person.crime_types);
  return (
    <aside className="dossier">
      <header className="dossier-header">
        <div>
          <span>SUBJECT FILE / {person.id}</span>
          <h2>{person.code}</h2>
          <p>{person.occupation} · {person.zone}</p>
        </div>
        <div className="relevant-stamp">RELEVANT</div>
      </header>

      <section className="score-block">
        <div className="score-ring" style={{ "--score": `${person.involvement * 360}deg` } as React.CSSProperties}>
          <div><strong>{percent(person.involvement)}</strong><span>INVOLVEMENT</span></div>
        </div>
        <dl>
          <div><dt>EVENT</dt><dd>{person.event_id}</dd></div>
          <div><dt>WINDOW</dt><dd>T−{person.imminence_minutes} MIN</dd></div>
          <div><dt>CONFIDENCE</dt><dd>{percent(person.confidence)}</dd></div>
          <div><dt>TYPE</dt><dd>{dominantCrime[0].toUpperCase()}</dd></div>
        </dl>
      </section>

      {mode === "machine" ? (
        <section className="role-obscured">
          <div className="panel-kicker">ROLE CLASSIFICATION</div>
          <div className="redacted">VICTIM / PERPETRATOR</div>
          <p>WITHHELD IN MACHINE VIEW</p>
        </section>
      ) : (
        <section className="role-panel">
          <div className="section-heading"><span>ROLE POSTERIOR</span><em>H={person.role_uncertainty.toFixed(2)}</em></div>
          {Object.entries(person.roles).map(([role, value]) => (
            <div className="bar-row" key={role}>
              <label>{titleCase(role)}</label><RiskBar value={value} danger={role === "perpetrator"} /><b>{percent(value)}</b>
            </div>
          ))}
        </section>
      )}

      <section className="crime-panel">
        <div className="section-heading"><span>CRIME TYPE MIX</span><em>SOFTMAX</em></div>
        {Object.entries(person.crime_types)
          .sort((a, b) => b[1] - a[1])
          .map(([crime, value]) => (
            <div className="bar-row compact" key={crime}>
              <label>{titleCase(crime)}</label><RiskBar value={value} /><b>{percent(value)}</b>
            </div>
          ))}
      </section>

      <section className="explanation-panel">
        <div className="section-heading"><span>SCORE CONTRIBUTION</span><em>TOP 5</em></div>
        {person.explanations.map((item) => (
          <div className="explain-row" key={item.feature} title={item.record_ids.join(", ")}>
            <span>{item.label}</span><RiskBar value={item.value * 3.7} danger={item.feature === "threat"} /><b>+{(item.value * 100).toFixed(1)}</b>
          </div>
        ))}
      </section>

      <section className="evidence-panel">
        <div className="section-heading"><span>LATEST EVIDENCE</span><em>{person.evidence.length} ITEMS</em></div>
        {person.evidence.slice(0, 3).map((item) => (
          <article key={item.id}>
            <div><span>{item.id}</span><time>{timeOnly(item.timestamp)}</time></div>
            <p>{item.summary}</p>
            <small>{item.source.toUpperCase()} · q={item.reliability.toFixed(2)}</small>
          </article>
        ))}
      </section>
    </aside>
  );
}

function maxEntry(values: ProbabilityMap): [string, number] {
  return Object.entries(values).sort((a, b) => b[1] - a[1])[0];
}

export default function Home() {
  const [mode, setMode] = useState<Mode>("machine");
  const [surface, setSurface] = useState<Surface>("city");
  const [threshold, setThreshold] = useState(data.meta.threshold);
  const [selectedPersonId, setSelectedPersonId] = useState(data.people[0].id);
  const [selectedZoneId, setSelectedZoneId] = useState(
    data.zones.find((zone) => zone.name === (data.people[0].map_zone || data.people[0].zone))?.id ?? data.zones[0].id,
  );

  const selectedPerson = data.people.find((person) => person.id === selectedPersonId) ?? data.people[0];
  const selectedEvent = data.events.find((event) => event.id === selectedPerson.event_id) ?? data.events[0];
  const activeZone = data.zones.find((zone) => zone.id === selectedZoneId) ?? data.zones[0];
  const relevantPeople = useMemo(
    () => data.people.filter((person) => person.involvement >= threshold),
    [threshold],
  );

  function selectPerson(id: string) {
    const person = data.people.find((candidate) => candidate.id === id);
    if (!person) return;
    setSelectedPersonId(id);
    const zone = data.zones.find((candidate) => candidate.name === (person.map_zone || person.zone));
    if (zone) setSelectedZoneId(zone.id);
  }

  return (
    <main className="machine-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="machine-mark"><span /><span /><span /></div>
          <div><h1>THE MACHINE</h1><p>MANHATTAN // CLOSED SIMULATION</p></div>
        </div>
        <div className="system-state"><i /> SYSTEM ONLINE <span>07:40:00Z</span></div>
        <div className="scenario-clock">
          <span>SIMULATION TIME</span>
          <strong>21:40:00</strong>
          <em>13 AUG 2026 / NYC</em>
        </div>
      </header>

      <div className="modebar">
        <div className="mode-switch" role="group" aria-label="Analysis mode">
          <button className={mode === "machine" ? "active" : ""} onClick={() => setMode("machine")}>MACHINE VIEW</button>
          <button className={mode === "analyst" ? "active" : ""} onClick={() => setMode("analyst")}>ANALYST VIEW</button>
        </div>
        <nav aria-label="Visualization surface">
          {(["city", "network", "model"] as Surface[]).map((item) => (
            <button key={item} className={surface === item ? "active" : ""} onClick={() => setSurface(item)}>
              {item === "city" ? "01 / CITY GRID" : item === "network" ? "02 / EVIDENCE GRAPH" : "03 / MODEL CORE"}
            </button>
          ))}
        </nav>
        <div className="synthetic-badge">SYNTHETIC DATA ONLY</div>
      </div>

      <div className="workspace">
        <aside className="queue-panel">
          <div className="queue-heading">
            <div><span>RELEVANT LIST</span><strong>{String(relevantPeople.length).padStart(2, "0")}</strong></div>
            <i>UPDATED 21:40</i>
          </div>
          <div className="threshold-control">
            <label htmlFor="threshold">FRAME THRESHOLD <b>{threshold.toFixed(2)}</b></label>
            <input
              id="threshold"
              type="range"
              min="0.35"
              max="0.90"
              step="0.01"
              value={threshold}
              onChange={(event) => setThreshold(Number(event.target.value))}
            />
            <div><span>MORE SIGNALS</span><span>HIGH CERTAINTY</span></div>
          </div>
          <div className="subject-list">
            {data.people.map((person, index) => {
              const visible = person.involvement >= threshold;
              if (!visible && mode === "machine") return null;
              const role = maxEntry(person.roles)[0];
              return (
                <button
                  key={person.id}
                  className={`${selectedPerson.id === person.id ? "active" : ""} ${visible ? "flagged" : "quiet"}`}
                  onClick={() => selectPerson(person.id)}
                >
                  <span className="queue-index">{String(index + 1).padStart(2, "0")}</span>
                  <span className="queue-main"><b>{person.code}</b><em>{person.event_id} · T−{person.imminence_minutes}</em></span>
                  <span className="queue-score"><b>{percent(person.involvement)}</b><em>{mode === "analyst" ? role.toUpperCase() : visible ? "RELEVANT" : "BELOW"}</em></span>
                </button>
              );
            })}
          </div>
          <div className="event-queue">
            <div className="section-heading"><span>EVENT CANDIDATES</span><em>{data.events.length}</em></div>
            {data.events.map((event) => (
              <button key={event.id} onClick={() => {
                const first = data.people.find((person) => person.event_id === event.id && person.involvement >= threshold);
                if (first) selectPerson(first.id);
              }}>
                <span>{event.id}</span>
                <div><b>{event.title}</b><em>{event.zone} · {event.signal_count} signals</em></div>
                <strong>{percent(event.risk)}</strong>
              </button>
            ))}
          </div>
        </aside>

        <section className="primary-panel">
          <header className="panel-header">
            <div><span>{surface === "city" ? "BOROUGH / MANHATTAN" : surface === "network" ? "SUBGRAPH / ACTIVE SUBJECT" : "ENGINE / TRANSPARENT BASELINE"}</span><h2>{surface === "city" ? "CITY GRID" : surface === "network" ? "EVIDENCE GRAPH" : "MODEL CORE"}</h2></div>
            <div className="panel-readout"><span>MODEL</span><b>{data.meta.model_version}</b><em>STATIC FRAME</em></div>
          </header>
          {surface === "city" && (
            <CitySurface
              people={data.people}
              events={data.events}
              zones={data.zones}
              threshold={threshold}
              selectedPerson={selectedPerson}
              selectedZone={selectedZoneId}
              activeZone={activeZone}
              mode={mode}
              onPerson={selectPerson}
              onZone={setSelectedZoneId}
            />
          )}
          {surface === "network" && <NetworkSurface person={selectedPerson} event={selectedEvent} />}
          {surface === "model" && <ModelSurface metrics={data.metrics} />}
          <footer className="ticker" aria-label="Recent synthetic signals">
            <span>INGEST</span>
            <div>
              {data.timeline.slice(0, 4).map((item) => (
                <p key={item.id}><time>{timeOnly(item.timestamp)}</time><b>{item.id}</b>{item.summary}</p>
              ))}
            </div>
          </footer>
        </section>

        <Dossier person={selectedPerson} mode={mode} />
      </div>

      <footer className="global-footer">
        <p><span>FICTIONAL SYSTEM</span> {data.meta.disclaimer}</p>
        <p>NO REAL IDENTITIES · NO FACE RECOGNITION · NO OPERATIONAL USE</p>
      </footer>
    </main>
  );
}
