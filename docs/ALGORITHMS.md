# Algorithm design

This document specifies the v0.3 baseline from raw synthetic records to interactive output. The design goal is not maximum predictive power. It is an auditable end-to-end system in which every visual element can be traced back to a formula and a source record.

## 1. Problem definition

Let:

- $i\in\mathcal P$ denote a person;
- $e\in\mathcal E$ denote a candidate future event;
- $o\in\mathcal O_{ie}$ denote an observation associated with person-event pair $(i,e)$;
- $t_0$ denote the scenario time;
- $I_{ie}\in\{0,1\}$ denote whether person $i$ will participate in event $e$ in any role;
- $R_{ie}\in\{V,P,A\}$ denote victim, perpetrator, or ambiguous conditional on involvement;
- $C_e\in\{\text{robbery, assault, abduction, fraud}\}$ denote event type.

The system deliberately factorizes the problem:

$$
\text{records}
\rightarrow \text{evidence features}
\rightarrow P(I_{ie}=1)
\rightarrow \{ P(R_{ie}\mid I_{ie}=1),P(C_e) \}
\rightarrow \text{area risk and interface}.
$$

This matters conceptually. “Likely to be involved” is not synonymous with “likely to offend.” A target can have a high involvement score and a high victim posterior.

## 2. Record normalization

Each observation has a common envelope:

$$
o=(i,e,t_o,s_o,q_o,\mathbf{u}_o),
$$

where $s_o$ is the source type, $q_o\in[0,1]$ is its stated reliability, and $\mathbf{u}_o$ is a set of semantic tags such as `proximity`, `intent`, `targeted`, or `account_takeover`.

The raw record may be a message, purchase, transit tap, camera hit, access log, finance transaction, calendar edit, dispatch record, or network event. A tag-to-feature table turns the heterogeneous source into a common vector:

$$
f_{ok}\in[0,1],\qquad
k\in\mathcal K,
$$

with

$$
\mathcal K=\{\text{intent, capability, proximity, coordination, vulnerability, threat, financial, mobility, anomaly}\}.
$$

In v0.3 this semantic extraction is deterministic and explicit in `TAG_EFFECTS`. A learned text encoder or classifier can replace it later without changing downstream contracts. Records with no recognized model-bearing tag remain in the raw dataset as ordinary background activity, but contribute neither feature strength nor evidence confidence.

## 3. Temporal reliability

Evidence becomes stale at different rates. A location ping should matter strongly for a few hours, while a suspicious purchase can remain relevant longer. Each source therefore has half-life $h_s$:

$$
w_o(t_0)=q_o\exp\left(-\ln2\frac{t_0-t_o}{h_{s_o}}\right).
$$

Properties:

- $w_o(t_o)=q_o$;
- after one half-life, $w_o=q_o/2$;
- a lower-reliability record is down-weighted even when fresh;
- no evidence receives future information because $t_o\le t_0$.

## 4. Saturating evidence fusion

For each person-event-feature triple, observations are fused with a noisy-OR:

$$
z_{iek}=1-\prod_{o\in\mathcal O_{ie}}\left(1-w_o f_{ok}\right).
$$

This behaves like the probability that at least one independent clue activates feature $k$. It was selected instead of a raw sum because it is bounded in $[0,1]$ and has diminishing returns. Ten duplicated weak clues cannot make the feature arbitrarily large.

It is still an approximation: real records are often correlated. A future model should cluster duplicates or explicitly model source dependence.

## 5. Temporal heterogeneous graph

The system can be viewed as a graph

$$
G_{t_0}=(V,E_{t_0}),\qquad
V=V_P\cup V_E\cup V_O,
$$

with person, candidate-event, and observation nodes. Edges include:

- observation $\rightarrow$ person;
- observation $\rightarrow$ candidate event;
- person $\leftrightarrow$ person when a record explicitly connects them;
- candidate event $\rightarrow$ Manhattan zone.

For interpretability, v0.3 uses only one person-person propagation hop. Let $a_{ij}$ be the temporally weighted strength of an observed link and

$$
m_{je}=\max\{z_{je,\text{intent}},z_{je,\text{coordination}},z_{je,\text{vulnerability}}\}.
$$

The transferred graph signal is

$$
g_{ie}=1-\prod_{j\in\mathcal N(i)}\left(1-0.58a_{ij}m_{je}\right).
$$

The noisy-OR again bounds propagation. The graph never infers guilt by association: $g_{ie}$ is merely one modest feature, an edge must come from an explicit synthetic record, and the role model remains separate.

## 6. Event imminence

For event start $t_e>t_0$,

$$
\tau_e=\exp\left(-\frac{t_e-t_0}{6\text{ hours}}\right).
$$

An otherwise equal event receives more attention as it approaches. The demo's fixed time slice reports the same quantity in minutes as `T−N MIN`.

## 7. Involvement model

The main score is a transparent logistic model:

$$
p_{ie}=P(I_{ie}=1)=\sigma\left(
-2.55+\boldsymbol\beta^\top\mathbf z_{ie}+0.80g_{ie}+1.10\tau_e
\right),
$$

where $\sigma(x)=1/(1+e^{-x})$ and

| Feature | Weight |
|---|---:|
| Intent | 1.35 |
| Capability | 1.15 |
| Proximity | 1.20 |
| Coordination | 1.00 |
| Vulnerability | 1.25 |
| Threat | 0.90 |
| Financial motive/target | 0.55 |
| Mobility deviation | 0.50 |
| Baseline anomaly | 0.65 |

Vulnerability receives a positive involvement weight because a possible victim is still relevant. The red frame is applied when

$$
p_{ie}\ge\theta,
$$

with default $\theta=0.62$. The UI lets the viewer alter $\theta$ to see how alert volume changes.

For each person, the interface displays the candidate event with maximum $p_{ie}$:

$$
e_i^*=\arg\max_{e\in\mathcal E}p_{ie}.
$$

## 8. Role posterior

Role is evaluated only as a conditional second-stage problem. The three class logits are:

$$
\begin{aligned}
s_P={}&-0.40+1.50z_{\text{intent}}+1.25z_{\text{capability}}+0.80z_{\text{coordination}}\\
&+0.70z_{\text{threat}}+0.30z_{\text{financial}}-0.85z_{\text{vulnerability}},\\
s_V={}&-0.20+1.70z_{\text{vulnerability}}+0.70z_{\text{proximity}}+0.50z_{\text{threat}}\\
&-0.65z_{\text{intent}}-0.40z_{\text{capability}},\\
s_A={}&0.10+0.35z_{\text{anomaly}}+0.25z_{\text{proximity}}.
\end{aligned}
$$

They become probabilities through softmax:

$$
P(R_{ie}=c\mid I_{ie}=1)=\frac{e^{s_c}}{\sum_{r\in\{P,V,A\}}e^{s_r}}.
$$

Normalized entropy records uncertainty:

$$
H_R=-\frac{\sum_c p_c\log p_c}{\log 3}\in[0,1].
$$

Machine View withholds all three values. Analyst View exposes the complete distribution rather than only the winning label.

## 9. Crime-type posterior

Each candidate event begins with a fictional prior $\pi_{ec}$. Evidence modifies its log-probability:

$$
\ell_{iec}=\log\pi_{ec}+\boldsymbol\gamma_c^\top\mathbf z_{ie},
\qquad
P(C_e=c\mid i)=\mathrm{softmax}(\boldsymbol\ell_{ie})_c.
$$

For example, `financial` and `capability` add support to fraud, while `threat` adds support to assault. Event-level type mix is an involvement-weighted average across people:

$$
P(C_e=c)=\frac{\sum_i p_{ie}P(C_e=c\mid i)}{\sum_i p_{ie}}.
$$

## 10. Candidate-event and area risk

With a larger population, even the logistic no-evidence prior would accumulate if every pair score were multiplied directly. The demo therefore removes a fixed baseline floor before aggregating:

$$
u_{ie}=\frac{\max(0,p_{ie}-0.24)}{0.76},
\qquad
p_e=1-\prod_i(1-u_{ie}^2).
$$

The floor prevents event risk from rising merely because the synthetic population grows; squaring further reduces weak-pair influence. It is a scenario-ranking heuristic, not a calibrated real-world probability.

Let $a$ be a Manhattan zone with centroid $x_a$, background term $b_a$, and event coordinate $x_e$. A Gaussian spatial kernel is

$$
K_h(d_{ae})=\exp\left(-\frac{\lVert x_a-x_e\rVert^2}{2h^2}\right),\qquad h=92\text{ map units}.
$$

Zone risk is

$$
R(a,t_0)=1-\exp\left[-0.82\left(b_a+\sum_e p_e\tau_eK_h(d_{ae})\right)\right].
$$

The map correctly calls this a **synthetic scenario-risk index**. It is not a claim about historical or current crime in a real Manhattan neighborhood.

## 11. Explanation and confidence

Because the involvement logit is additive, its positive components can be normalized:

$$
\phi_k=\frac{\beta_kz_{iek}}{\sum_j\max(0,\beta_jz_{iej})+0.8g_{ie}+1.1\tau_e}.
$$

The interface displays the five largest $\phi$ values and preserves the record IDs that activated each feature. These are local score contributions, not causal explanations.

Evidence confidence combines weighted evidence mass $M_{ie}=\sum_ow_o$ with role certainty:

$$
Q_{ie}=0.72\left(1-e^{-M_{ie}/2.6}\right)+0.28(1-H_R).
$$

This is intentionally kept distinct from $p_{ie}$: the model can assign high involvement while admitting lower confidence about why or in what role.

## 12. Evaluation

The synthetic label file is evaluated over all $|\mathcal P||\mathcal E|$ person-event pairs. The pipeline reports precision, recall, F1, role accuracy, confusion counts, and the Brier score

$$
\mathrm{Brier}=\frac1N\sum_{i,e}(p_{ie}-y_{ie})^2.
$$

The scenario was authored so the baseline cleanly separates its cases. Therefore perfect precision/recall only proves that the generator, feature logic, scorer, output contract, and UI are joined correctly. It is not a research result.

## 13. How the algorithms are stitched together

For a single person-event pair, the complete composition is:

$$
\boxed{
\mathcal O_{ie}
\xrightarrow{\text{tag map}+w_o}
\mathbf z_{ie}
\xrightarrow{G_{t_0}}
g_{ie}
\xrightarrow{\sigma}
p_{ie}
\xrightarrow{\text{conditional softmax}}
(\mathbf r_{ie},\mathbf c_{ie})
}
$$

Across pairs, a second aggregation produces event and map outputs:

$$
\{p_{ie},\mathbf c_{ie}\}_i
\rightarrow p_e,P(C_e)
\xrightarrow{K_h,\tau_e}
R(a,t_0).
$$

Finally, `engine/run_pipeline.py` serializes a single artifact. The browser consumes that artifact but does not recompute the Python model. That separation is the key engineering seam: later versions can replace the baseline with LightGBM, a temporal GNN, or a probabilistic graphical model while preserving the UI contract.
