# Kasoma Content Operations and Academic QA

| Field | Value |
|---|---|
| Version | 1.0.0 |
| MVP target | 250–400 approved items across six topic clusters |

## 1. Content is production code

An academically incorrect question, rubric or explanation is a production defect. Content therefore uses schemas, reviews, versions, tests, release states and audit trails comparable to software.

## 2. Item schema

Required fields before review:

- stable item ID and version;
- level, subject, topic and primary concept;
- one or more competency mappings with weights;
- syllabus/learning-outcome reference;
- difficulty band and expected time;
- response type and channel suitability;
- prompt blocks and accessible media alternatives;
- answer specification or rubric;
- maximum points and partial-credit rules;
- worked solution;
- at least one feedback/remediation path;
- common misconception mappings where relevant;
- prerequisite concepts;
- source/provenance and rights status;
- author and change reason.

## 3. Status workflow

```text
DRAFT -> IN_REVIEW -> APPROVED -> RETIRED
   ^          |
   |----------| RETURNED
```

- Draft: editable and never learner-visible.
- In review: frozen for the review decision.
- Returned: author must create corrections/change record.
- Approved: immutable learner-eligible version.
- Retired: remains for history but cannot be newly served.

Emergency withdrawal may make an approved version immediately ineligible while the audit record remains.

## 4. Review checklist

Reviewer confirms:

1. curriculum and learning-outcome alignment;
2. competency and difficulty tagging;
3. scenario relevance and factual correctness;
4. one clear interpretation unless ambiguity is intentional and rubriced;
5. answer/rubric completeness;
6. numerical values, units and significant figures;
7. partial-credit logic;
8. worked solution accuracy;
9. misconception/feedback validity;
10. equivalent-item relationship where claimed;
11. English clarity and age appropriateness;
12. accessibility of diagrams/media;
13. rights/provenance classification;
14. channel suitability;
15. absence of hidden sensitive, discriminatory or unsafe content.

Authors may not approve their own content. High-risk or disputed items require a second reviewer.

## 5. Rights states

Allowed controlled values:

- `ORIGINAL_KASOMA`
- `LICENSED`
- `PUBLIC_DOMAIN_CONFIRMED`
- `PERMISSION_CONFIRMED`
- `REFERENCE_ONLY_NO_REPRODUCTION`
- `UNKNOWN_BLOCKED`

Only the first four may be published, subject to recorded conditions. `REFERENCE_ONLY_NO_REPRODUCTION` may guide taxonomy/manual authoring but its text/media cannot be reproduced. `UNKNOWN_BLOCKED` cannot enter learner-facing pipelines or embeddings.

## 6. Import pipeline

1. register source and rights state;
2. scan/sanitize file;
3. extract candidate items to staging;
4. detect duplicates and preserve page/source locator;
5. map candidate fields;
6. human author corrects and completes;
7. validate schema;
8. submit for independent review;
9. publish only approved version;
10. index approved explanation/context if permitted.

Extraction output is always a candidate, never approved content.

## 7. Coverage controls

Maintain a matrix by:

```text
Subject × Topic × Concept × Competency × Difficulty × Response type
```

Release coverage must avoid large cells with no items and prevent one concept or response form dominating. The content lead defines minimum cells after the six topic clusters are frozen. A raw total of 250 does not satisfy release if coverage is unusably imbalanced.

## 8. Equivalent and reassessment items

An equivalent pair should assess the same primary concept/competency at comparable difficulty while changing surface context or values sufficiently to test transfer. Reviewers must reject pairs solvable by remembering the prior wording/answer.

## 9. Content quality metrics

- metadata completeness;
- author-to-approval cycle time;
- reviewer agreement;
- defect and flag rate per 1,000 attempts;
- grade override rate;
- unusually high/low item success after controlling for expected difficulty;
- distractor effectiveness;
- reassessment transfer performance;
- retirement reasons.

Metrics trigger review; they do not automatically rewrite or retire content.

## 10. Production correction

For a critical item defect:

1. make the version ineligible immediately;
2. identify affected attempts/grades/mastery evidence;
3. determine whether results must be invalidated and replayed;
4. publish a corrected new version after review;
5. record incident, impact and decision;
6. notify affected learners only when useful and age-appropriate.

Historical evidence is never silently changed.

## 11. Seed and fixture content

Development and CI use clearly labelled synthetic questions. Production exports or copyrighted materials must not enter the repository. Fixture items must exercise every response type and edge case without being mistaken for approved learner content.

## Reviewed hint metadata (ADR-022 implementation)

Versioned choice/numeric documents may contain zero to three ordered `hints`, each
1–1000 characters after trimming. Existing approved versions remain unchanged;
author a successor version to add hints. The independent feedback/hints review must
confirm progressive scaffolding without disclosing the answer or worked solution.
The editor and reviewer display all authored levels; learner routes disclose only
requested levels. Synthetic fixture text and automated tests do not replace academic
review of production hints. See [ADR-022](../decisions/ADR/022-reviewed-hints.md).

## Versioned equivalence claims (ADR-023 implementation)

Authors may include up to ten `equivalents` entries with `version_id` and `confidence`
(0–1). The referenced version must be approved synthetic content in the same subject,
primary concept/competency and difficulty band. Primary competency is greatest mapping
weight with stable-ID tie breaking. Reject duplicate IDs and textual/structural clones.

The staff editor accepts one version ID/confidence pair per line; reviewers can inspect
the referenced version and return to the claim-bearing item through the item list.
An approving reviewer cannot author either side. Existing independent-review and
high-risk second-review controls apply. The review must establish transfer validity;
automated text checks and synthetic confidence values do not certify equivalence.
Published claims are immutable; changes require a successor version and new review.

## Learner flag operations (ADR-025)

The reviewer/admin queue supports audited inspection, self-assignment, priority,
resolution, dismissal and reopening. Authors cannot triage flags on their own content.
Comments are confidential plain text; no private learner messaging or general learner
record access is granted. Non-dismissed QUESTION_ERROR, GRADE_DISPUTE and UNSAFE_CONTENT
reports make the stable item disputed for successor creation and review. Existing
published versions are immutable; successor approval requires two independent reviewers,
including when a report arrives after the successor draft was created. A triage decision
does not change grades/mastery, publish corrections or automatically retire content.
Use existing explicit retirement and independently reviewed successor procedures.
