# Kasoma Adaptive Mastery Engine v1

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Algorithm family | Interpretable weighted evidence |
| Status | MVP baseline; configuration values require calibration |

## 1. Purpose

The engine estimates a learner's mastery and evidence confidence, finds prerequisite gaps, selects the next approved activity and explains the choice. It is not a certified grade or psychological profile.

## 2. Skill unit

Primary estimate key:

```text
(learner_id, concept_id, competency_id)
```

Topic and subject values are derived aggregates, not independently updated truth. When an item maps to several skills, academic metadata supplies normalized contribution weights summing to 1.

## 3. Evidence normalization

For each graded attempt and mapped skill:

```text
observed_score s = points_awarded / points_possible       # 0..1
difficulty_weight d = {FOUNDATIONAL:0.85, CORE:1.00, STRETCH:1.15}
independence i = max(0.50, 1 - 0.15*hint_count - 0.25*solution_seen_before_grade)
grade_confidence g = deterministic ? 1.0 : grade_confidence
mapping_weight m = academic mapping contribution          # 0..1
recency_weight r(t) = 0.5^(age_days / half_life_days)
base_weight w = d * i * g * m
```

`solution_seen_before_grade` should normally be zero because MVP rules block it. Half-life starts at 30 days and is configuration-versioned.

Low-confidence or review-required grades do not create mastery evidence until resolved.

## 4. Estimate calculation

Use a neutral prior:

```text
prior_score = 0.50
prior_weight = 2.0

mastery = (prior_score*prior_weight + Σ(s_j*w_j*r_j)) /
          (prior_weight + Σ(w_j*r_j))

raw_confidence = 1 - exp(-Σ(w_j*r_j)/5)
coverage_factor = min(1, distinct_item_count/3) * min(1, distinct_format_count/2)
confidence = raw_confidence * (0.6 + 0.4*coverage_factor)
```

Configuration values are initial hypotheses. They must be stored with algorithm version and tuned only through an approved evaluation.

Display states:

| Condition | State |
|---|---|
| confidence < 0.25 | `NOT_ENOUGH_EVIDENCE` |
| confidence 0.25–0.49 | `DEVELOPING_ESTIMATE` |
| confidence ≥0.50 and mastery <0.50 | `NEEDS_ATTENTION` |
| confidence ≥0.50 and mastery 0.50–0.74 | `DEVELOPING` |
| confidence ≥0.50 and mastery ≥0.75 | `STRONG` |

Avoid red/green judgment without accessible text.

## 5. Diagnostic selection

Constraints:

- 10–15 items;
- all selected topic clusters receive initial coverage where inventory permits;
- first item per topic is `CORE` difficulty;
- after strong response, sample a harder application/interpretation item;
- after weak response, sample prerequisite or foundational item;
- stop when maximum reached or topic evidence reaches configured sufficiency;
- no hints, solutions or immediate corrective teaching during diagnostic.

Deterministic policy pseudocode:

```text
initialize uncovered topics
while item_count < 15:
  if uncovered topic exists: choose core representative item
  else choose skill with lowest confidence and highest curriculum importance
  adjust difficulty by latest score for that skill
  enforce content, repetition, format and channel constraints
  stop after >=10 when every topic covered and marginal information need is low
```

## 6. Recommendation ranking

For each eligible skill target:

```text
gap = 1 - mastery
importance = academic configuration 0.5..1.5
uncertainty = 0.75 + 0.5*(1-confidence)
spacing_due = 0.8..1.3 based on time since evidence and review schedule
prerequisite_readiness = 0.4..1.0
recent_repetition_penalty = 0.3..1.0
available_content_factor = 0 or 1

priority = gap * importance * uncertainty * spacing_due *
           prerequisite_readiness * recent_repetition_penalty *
           available_content_factor
```

If a prerequisite is below `0.45` with confidence ≥`0.35`, recommend the prerequisite instead of the dependent target. If confidence is low, prefer diagnostic evidence rather than assert a weakness.

Tie-breakers, in order:

1. prerequisite impact;
2. curriculum importance;
3. oldest evidence;
4. lower recent exposure;
5. stable ID for deterministic replay.

## 7. Item selection within a target

Filter:

- approved/current;
- correct level/subject/topic;
- mapped to target skill;
- supported by channel and response type;
- not recently seen, unless retry/reassessment;
- difficulty appropriate to current mastery;
- rights and media available.

Rank by target mapping strength, desired difficulty, format diversity, scenario diversity and historical exposure. Randomness, if used, must be seeded and recorded so selection is reproducible.

## 8. Reassessment

After feedback/remediation:

- prefer an explicitly reviewed `EQUIVALENT` item;
- otherwise choose same primary concept/competency and difficulty band;
- exclude textual/structural near-duplicates;
- do not reveal that the same answer pattern is expected;
- record relationship basis and elapsed time.

Misconception resolution requires a failed/partial original response and a subsequent independent reassessment meeting the criterion threshold. A hint-heavy retry alone does not count.

## 9. Explainability

The engine emits a structured reason code and safe text template, for example:

```json
{
  "reason_code": "WEAK_SKILL_WITH_PREREQUISITE_READY",
  "target": "Interpreting wave diagrams",
  "evidence_summary": {"recent_attempts": 3, "mastery": 0.42, "confidence": 0.58},
  "learner_text": "Recommended because recent answers show difficulty interpreting wave diagrams."
}
```

Do not expose internal probability as certainty or mention sensitive comparisons with other learners.

## 10. Versioning and replay

Every evidence record, estimate and recommendation stores:

- algorithm version;
- configuration version;
- input evidence IDs or immutable input hash;
- calculated timestamp;
- reason code.

An offline replay command shall rebuild estimates from evidence and compare results before an algorithm rollout.

## 11. Evaluation

Required before MVP release:

- monotonic unit tests for every weighting factor;
- deterministic replay tests;
- synthetic learner trajectories;
- calibration plot by mastery band;
- predicted mastery versus unseen equivalent performance;
- recommendation sanity review by subject teachers;
- subgroup error review where sample size permits;
- comparison against simple percent-correct baseline.

The rules engine remains the production baseline until a later approach improves calibration or learning outcomes without unacceptable complexity or fairness cost.
