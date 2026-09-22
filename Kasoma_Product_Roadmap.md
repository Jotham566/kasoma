# Kasoma Product Roadmap

## Three-Month MVP and Staged Development Plan

| Document field | Value |
|---|---|
| Product | Kasoma |
| Document | Product Roadmap |
| Version | 1.1 |
| Status | Working baseline |
| Date | 22 September 2026 |
| MVP deadline | 12 weeks from kickoff |
| Initial market | Ugandan O-Level learners under the competency-based curriculum |
| Initial academic scope | Senior 4 Mathematics and Physics |
| Product promise | Know what you do not know. Master it before the exam. |

> This roadmap governs delivery. The companion **Kasoma Product Whitepaper** defines the mature product vision and should be used as the north star when scope decisions are made.

---

## 1. Executive decision

Kasoma will launch as an **adaptive revision and mastery platform**, not a general AI tutor or digital past-paper archive. Its core job is to answer:

> **What should this learner revise next, why, and did the intervention improve mastery?**

The MVP must be fully delivered within 12 weeks. It will prove one complete learning loop:

> Diagnose → Recommend → Practice → Explain → Reassess → Update mastery

The MVP succeeds when a Senior 4 learner can use web or WhatsApp to identify specific weaknesses, complete an adaptive revision session, receive trustworthy feedback, and demonstrate improvement on an unseen equivalent question.

---

## 2. Scope decisions required by the 12-week deadline

### 2.1 Keep the academic surface narrow

Launch with:

- Senior 4 only;
- Mathematics and Physics only;
- three frozen topic clusters per subject: Mathematics—Algebra and Functions; Geometry, Trigonometry and Measurement; Statistics and Probability; Physics—Mechanics and Energy; Waves, Light and Sound; Electricity and Magnetism;
- 250–400 fully reviewed assessment items across both subjects; and
- objective, numerical and tightly bounded short-answer formats.

Topic selection must be completed in Week 1 using curriculum importance, prerequisite value, learner difficulty and availability of valid assessment material.

### 2.2 Make web the complete experience

The responsive web application will contain onboarding, diagnostics, adaptive practice, explanations and progress. WhatsApp will provide account linking, short quizzes, concise feedback and continuation of the same learner state. Feature parity is not required.

### 2.3 Use interpretable adaptation first

The first mastery engine will be rules-based and auditable. It will use correctness, partial score, difficulty, hints, recency, consistency and prerequisite relationships. Advanced knowledge tracing and recommendation ML come only after Kasoma has enough clean learner data to test them against this baseline.

### 2.4 Constrain generative AI

AI may explain approved content, rephrase within controlled templates, classify responses and support rubric-based feedback. It may not independently publish new questions, set curriculum alignment or act as the sole judge of high-stakes answers.

### 2.5 Treat content production as a delivery stream

Content work begins on Day 1 and runs in parallel with engineering. Each released item must have curriculum mapping, competency tags, difficulty, rubric or answer key, explanation, misconception tags, source/rights status, reviewer and version history.

---

## 3. MVP product scope

### 3.1 Learner account and onboarding

- Mobile-number or email registration;
- age-appropriate consent and guardian pathway;
- class and subject selection;
- learner profile shared across web and WhatsApp;
- low-bandwidth, mobile-first interface.

### 3.2 Diagnostic assessment

- 10–15 curated questions per subject;
- lightweight adaptive branching;
- coverage across selected topics and competencies;
- initial strengths, weaknesses and confidence levels;
- a recommended first revision activity.

### 3.3 Adaptive revision

- recommended sessions of 5–10 questions;
- selection based on weakness, prerequisites, recency and difficulty;
- learner may manually select a topic;
- visible recommendation rationale;
- continuation across sessions and channels.

### 3.4 Grading and remediation

- deterministic grading for multiple-choice, numeric and structured answers;
- constrained rubric-assisted grading for supported short responses;
- partial credit where the approved rubric permits it;
- misconception-specific feedback and hints;
- worked solution after an attempt;
- one reassessment item testing the same competency in a different scenario;
- safe fallback when grading confidence is low.

### 3.5 Learner progress

- mastery by subject, topic and competency;
- areas improving and areas needing attention;
- recent revision history;
- clear language that mastery is an estimate;
- simple streak or consistency indicator without public ranking.

### 3.6 WhatsApp revision

- link a Kasoma account;
- start or continue a five-question session;
- answer supported text, numeric and multiple-choice items;
- receive concise marking and explanations;
- synchronize results with the web profile;
- link to web when richer diagrams or workings are required.

### 3.7 Academic content system

- subject → topic → concept → competency hierarchy;
- prerequisite relationships;
- structured question bank with source and rights metadata;
- answer keys, rubrics, explanations and misconception tags;
- workflow: draft → academic review → approved → retired;
- bulk import and editing;
- student preview and audit history.

### 3.8 Mastery engine v1

- update mastery after each graded response;
- factor in difficulty, hints, recency and repeated evidence;
- flag prerequisite gaps;
- choose the next best approved item;
- schedule reassessment;
- explain recommendations;
- log the evidence behind every update.

### 3.9 Platform and operations

- role-based access for learners, authors, reviewers and administrators;
- monitoring, error tracking, backups and audit logs;
- analytics events for the full learning loop;
- content flagging and learner support flow;
- AI usage limits, caching and cost monitoring;
- personal-data export/deletion workflow;
- incident and safeguarding process.

---

## 4. Explicitly outside the MVP

The following must not delay the 12-week release:

- full historic-paper library and full-paper Exam Mode;
- Chemistry, Biology, other O-Level subjects and A-Level;
- interactive simulations;
- Snap & Learn, handwriting or photo solving;
- voice interaction;
- teacher, school and parent portals;
- assignments and school-based assessment workflows;
- advanced flashcard system;
- public leaderboards, multiplayer features and virtual economies;
- native Android/iOS applications;
- advanced offline mode;
- Item Response Theory, Bayesian/Deep Knowledge Tracing or bandits;
- model fine-tuning;
- automatic publication of AI-generated questions.

---

## 5. Twelve-week delivery plan

Four workstreams run concurrently:

1. **Product and engineering** — learner experience, platform and WhatsApp;
2. **Academic content** — curriculum graph, questions, rubrics and review;
3. **AI and data** — grading, explanations, mastery and analytics;
4. **Pilot and operations** — research, safeguarding, support and launch.

### Phase 1 — Scope and foundation: Weeks 1–2

| Workstream | Deliverables |
|---|---|
| Product and engineering | Architecture; repositories/environments; product flows; design system; authentication skeleton; analytics schema |
| Academic content | Six topic clusters selected; item schema; competency/prerequisite graph v0.1; rights register; first 60 approved items |
| AI and data | Grading benchmark set; mastery formula v0.1; prompt and model policy; event model |
| Pilot and operations | 3–5 teacher reviewers; at least one pilot partner; safeguarding/data map; pilot protocol and success metrics |

**Week 2 exit gate**

- scope frozen and owners assigned;
- technical architecture approved;
- all intended sources classified for permitted use;
- at least 60 reviewed items available;
- benchmark grading set approved;
- pilot recruitment underway.

### Phase 2 — Working vertical slice: Weeks 3–5

| Workstream | Deliverables |
|---|---|
| Product and engineering | Onboarding; learner profile; question player; diagnostic flow; content administration; initial progress view |
| Academic content | Competency graph v1; 150 cumulative approved items; rubrics, worked solutions and misconception taxonomy |
| AI and data | Deterministic graders; constrained short-answer grader; mastery updates; recommendation service v0.1 |
| Pilot and operations | Test scripts; support process; device/connectivity testing; teacher review sessions |

**Week 5 exit gate**

- one learner can complete the full loop on web;
- every released item is traceable to curriculum and review evidence;
- objective/numeric benchmark grading accuracy is at least 95%;
- short-answer agreement with expert markers is at least 85% on supported formats;
- no unresolved critical privacy or safeguarding defect.

### Phase 3 — Feature completion and closed alpha: Weeks 6–8

| Workstream | Deliverables |
|---|---|
| Product and engineering | Responsive web experience; recommendation explanations; history; low-bandwidth tuning; WhatsApp account linking and quiz flow |
| Academic content | 250 cumulative approved items; balanced coverage; item-quality review; equivalent reassessment pairs |
| AI and data | Misconception feedback; low-confidence fallback; cross-channel learner state; evaluation dashboards and cost telemetry |
| Pilot and operations | Closed alpha with 30–50 learners; observed usability sessions; defect triage; support rehearsal |

**Week 8 exit gate**

- all MVP capabilities are feature-complete;
- at least 70% of alpha learners complete the diagnostic without assistance;
- web and WhatsApp update the same learner record correctly;
- no critical academic-content defect remains open;
- projected serving cost is inside the agreed MVP budget.

### Phase 4 — Hardening, pilot and release: Weeks 9–12

| Week | Primary outcome | Deliverables |
|---:|---|---|
| 9 | Beta-ready | 300+ approved items where feasible; accessibility and performance fixes; security review; grading regression suite |
| 10 | Real-world beta | 100–200 learners; baseline assessment; production monitoring; feedback and defect resolution |
| 11 | Release candidate | Delayed/unseen reassessment; calibration review; content freeze; support and incident-response rehearsal |
| 12 | MVP launch | Production release; launch reporting; known-limitations register; post-MVP backlog; go/no-go review |

**MVP release gate**

- complete learning loop works on supported mobile browsers;
- WhatsApp short practice synchronizes reliably;
- 250–400 reviewed items cover the six chosen topic clusters adequately;
- ≥95% objective/numeric benchmark grading accuracy;
- ≥85% expert agreement for supported short-answer scoring;
- no unresolved severity-1 security, privacy, safeguarding or academic defect;
- median feedback time and availability meet agreed service targets;
- pilot shows a positive learning signal on unseen equivalent items;
- operational cost per completed session is known and acceptable for the next pilot stage.

The 12-week date is fixed. If a gate is threatened, reduce topic breadth or supported response types—not review quality, safeguarding or grading integrity.

---

## 6. Build order and dependencies

| Priority | Capability | Depends on | Why it comes here |
|---:|---|---|---|
| 1 | Curriculum and competency schema | Topic selection | Everything else needs stable academic identifiers |
| 2 | Rights and content workflow | Source inventory | Prevents unusable or untraceable content |
| 3 | Question player and deterministic grading | Approved item schema | Creates the smallest testable learning interaction |
| 4 | Diagnostic and learner profile | Question player | Establishes initial learner evidence |
| 5 | Mastery update and recommendation | Diagnostic/event logging | Makes the platform adaptive |
| 6 | Feedback and reassessment | Rubrics/misconceptions | Tests whether an intervention worked |
| 7 | Progress view | Mastery evidence | Converts data into learner action |
| 8 | WhatsApp flow | Stable learner and assessment APIs | Avoids duplicating unstable logic |
| 9 | Hardening and pilot | End-to-end instrumentation | Validates quality, learning and economics |

---

## 7. Definition of MVP done

The MVP is complete when a Senior 4 learner can:

1. create or link an account on a low-cost smartphone;
2. complete a short Mathematics or Physics diagnostic;
3. see specific strengths and weaknesses;
4. understand why Kasoma recommends a revision activity;
5. complete that activity and receive accurate feedback;
6. retry after misconception-specific remediation;
7. answer an unseen equivalent reassessment item;
8. see the mastery estimate update; and
9. continue short practice through WhatsApp without losing progress.

The operating team must also be able to:

1. trace every item to its curriculum mapping, rights status and reviewers;
2. reproduce why an answer was graded and why an activity was recommended;
3. publish, correct or retire content safely;
4. monitor reliability, academic errors, safety events and AI cost;
5. support users without engineers manually intervening in routine sessions.

---

## 8. MVP measures

### Learning

- improvement between baseline and unseen equivalent reassessment;
- misconception resolution rate;
- mastery calibration against actual performance;
- performance across recall, interpretation, application and problem-solving.

### Product

- diagnostic completion;
- first recommended session completion;
- weekly returning learners;
- median questions completed per active learner;
- percentage of learners who understand the recommendation rationale;
- successful web/WhatsApp continuity.

### Quality and safety

- grading accuracy and expert-marker agreement;
- content flags per 1,000 attempts;
- low-confidence responses correctly withheld or escalated;
- critical incident count;
- percentage of active items with complete approval metadata.

### Economics and operations

- cost per completed revision session;
- support cases per 100 learners;
- median support resolution time;
- infrastructure and model cost by interaction type;
- willingness to continue and willingness to pay.

No broad acquisition campaign begins until Kasoma has credible learning improvement, acceptable grading quality and a viable serving cost.

---

## 9. Post-MVP roadmap

Timing is conditional on evidence, not merely calendar completion.

| Release | Target timing | Focus | Candidate capabilities | Entry gate |
|---|---:|---|---|---|
| 1.1 Retention and exam readiness | Months 4–5 | Make mastery stick | Adaptive flashcards; spaced retrieval; topic tests; timed mini-mocks; revision plans | MVP quality stable; sufficient approved content |
| 1.2 Subject expansion | Months 5–6 | Broaden usefulness | Chemistry or Biology; additional Mathematics/Physics topics | New subject has reviewers, rights clearance and ≥250 approved items |
| 1.3 Visual learning | Months 7–8 | Improve difficult conceptual learning | 3–5 simulations; diagram interactions; transfer assessments | Clear learning hypothesis and evaluation design |
| 1.4 Exam Mode | Months 8–9 | Build examination readiness | Timed papers; rubric-aligned scoring; competency breakdown; post-exam plan | Coverage supports valid full-paper assembly |
| 1.5 School intelligence | Months 9–12 | Serve teachers and institutions | Teacher dashboard; class heatmaps; assignments; intervention groups; school administration | Individual learner model is reliable at classroom scale |
| 1.6 Guided capture | Months 10–12 | Connect offline work | Guarded Snap & Learn; question/concept recognition; scaffolded solving | Safety and accuracy thresholds met |
| 2.0 Scale | Year 2 | Expand reach and defensibility | More subjects/levels; parent summaries; offline options; institutional APIs; regional adaptation | Uganda unit economics and academic outcomes validated |
| Intelligence upgrades | Year 2+ | Improve personalization | IRT/BKT trials; recommender experiments; justified fine-tuning | New method beats the rules baseline in controlled evaluation |

### Post-MVP sequencing principles

- Add subjects only when content quality can match the MVP standard.
- Add simulations only when they are paired with transfer assessment.
- Add school dashboards only when recommendations are credible enough to guide teaching.
- Fine-tune only for a defined deficiency with proprietary training/evaluation data.
- Preserve one learner identity and one mastery model across every channel and feature.

---

## 10. Team and operating model

Minimum effective team for the 12-week plan:

- product lead/founder;
- technical lead;
- two software engineers with frontend/backend capacity;
- one AI/data engineer;
- product designer/researcher, full-time or strongly allocated;
- academic/content lead;
- at least two Mathematics and two Physics reviewers;
- content operations contributors;
- QA engineer with academic-test responsibility;
- fractional safeguarding/privacy adviser;
- pilot/support coordinator by Week 6.

To meet the deadline, the team should run:

- one prioritized backlog;
- weekly release demonstrations;
- twice-weekly academic/engineering dependency reviews;
- a content throughput dashboard;
- a written decision log;
- a scope-change rule requiring removal of equivalent effort.

---

## 11. Key risks and controls

| Risk | Control |
|---|---|
| Content production misses schedule | Freeze topics in Week 1; daily throughput targets; reviewer service levels; reduce breadth before quality |
| Incorrect grading | Deterministic checks first; benchmark set; regression tests; confidence threshold and fallback |
| Curriculum mapping is weak | Teacher-reviewed graph; syllabus references; sampled audits |
| Past-paper rights are unclear | Rights register; permissions; separate source content from original Kasoma items |
| LLM hallucination | Approved retrieval sources; structured output; constrained explanations; monitoring and safe refusal |
| Mastery scores overclaim certainty | Minimum evidence thresholds; confidence display; calibration testing |
| WhatsApp integration delays core release | Stable shared APIs first; restrict WhatsApp to short supported flows |
| Connectivity excludes learners | Mobile-first PWA; compressed assets; resumable sessions; WhatsApp continuation |
| Child privacy or safety failure | Data minimization; consent pathway; moderation; retention rules; incident process |
| Team expands scope | Fixed 12-week deadline; explicit exclusions; trade one capability for another |
| AI costs undermine pricing | Cached approved explanations; rules for simple tasks; routing and budget caps |

---

## 12. Immediate actions

1. Confirm kickoff date and name one owner for each workstream.
2. Select the six initial topic clusters within five working days.
3. Confirm the content rights position for every proposed source.
4. Recruit teacher reviewers and agree weekly review capacity.
5. Recruit at least one pilot partner and define the learner cohort.
6. Approve the item, rubric, misconception and event schemas.
7. Create the fixed benchmark grading set before AI grading implementation.
8. Convert this roadmap into a named-owner sprint board and capacity plan.
9. Review the companion whitepaper at kickoff and record any changes as a new version.

---

## 13. Roadmap change control

This is a living document.

- Patch changes (1.0.x): wording, owners, dates and clarifications that do not change scope.
- Minor changes (1.x): scope, sequencing or release-gate changes.
- Major changes (x.0): material change to product strategy, target market or core learning model.
- Every revision must record the date, author, reason and decisions affected.
- The current approved version must remain accessible; do not overwrite history without a changelog.

### Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 22 Sep 2026 | Renamed product to Kasoma; replaced the 24-week MVP with a fixed 12-week delivery plan; added parallel workstreams, weekly gates and post-MVP sequencing |
| 1.1 | 22 Sep 2026 | Froze the six MVP academic topic clusters and aligned the roadmap with the production-pilot decision baseline |
