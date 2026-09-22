# Kasoma MVP UX Flows and Accessibility

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Primary device | Low-cost Android smartphone |
| Language | English MVP |

## 1. UX principles

- The next useful action is obvious.
- Show progress without false precision.
- Feedback is specific, respectful and short before it is detailed.
- Network failure never looks like learner failure.
- Learners can recover/resume without repeating completed work.
- Web is complete; WhatsApp is focused.
- Gamification supports consistency but never public ranking or shame.

## 2. Information architecture

Learner navigation:

- Home
- Revise
- Progress
- History
- Profile/Settings

Admin navigation:

- Content
- Review queue
- Imports
- Flags
- Operations
- Audit

Do not expose teacher, parent, simulation or Exam Mode navigation in MVP.

## 3. Learner flows

### 3.1 Registration and consent

```text
Welcome -> Email/phone -> OTP -> Basic profile -> Age/consent
-> Select subject(s) -> Diagnostic invitation -> Home
```

Requirements:

- Explain why contact verification is needed.
- Do not reveal whether an identifier already exists before verification.
- If guardian consent is required, clearly pause learning access and allow safe resume.
- Terms/privacy summaries use plain language with full versions linked.

### 3.2 Diagnostic

```text
Subject -> Purpose and time estimate -> Questions -> Completion
-> Strengths/needs -> First recommendation
```

- No hints, solution or backtracking that changes submitted answers.
- Autosave answer submission before advancing.
- Show item count, not a threatening score during diagnostic.
- Result uses evidence confidence and avoids `You are bad at...` language.

### 3.3 Recommended revision

Home card includes target, reason, estimated duration and start action.

Question state sequence:

```text
Prompt -> Answer -> Submit -> Feedback -> Hint/remediation if needed
-> Reassessment when appropriate -> Next item -> Session summary
```

After submission, the response is immutable. Network retries reuse the same idempotency key.

### 3.4 Progress

Show:

- subject summary;
- topic/competency states;
- confidence label;
- change based on recent evidence;
- recommended next action;
- history link.

Do not rank against peers. Do not equate estimate with UNEB grade. Colour is never the sole signal.

### 3.5 WhatsApp linking

```text
Web authenticated -> Generate code -> Send code to official Kasoma number
-> Confirmation on both channels -> START/CONTINUE
```

The web page displays expiry and warns not to share the code. WhatsApp supports simple numbered choices and explicit commands.

## 4. Required UI states

Every data-dependent view must define:

- initial loading;
- slow operation;
- empty state;
- recoverable error;
- offline/interrupted state;
- permission/consent block;
- success confirmation;
- stale/version-conflict state where relevant.

Skeletons may be used for layout, but never fabricate mastery values. AI grading pending state says feedback is being checked and preserves navigation/resume.

## 5. Low-bandwidth behaviour

- Server-render primary shell where useful.
- Split admin and learner bundles.
- Avoid automatic video/large animation.
- Compress responsive images and cache static curriculum assets.
- Prefetch at most the next authorized item without answers.
- Persist safe in-progress UI state locally, but server submission remains authoritative.
- Provide text alternative when nonessential media fails.
- On reconnect, reconcile using server attempt/session state.

## 6. Accessibility

Core journeys target WCAG 2.2 AA:

- full keyboard operation;
- visible focus;
- semantic headings, landmarks, labels and error associations;
- touch targets at least 44×44 CSS px where feasible;
- contrast-compliant text/status;
- alt text or textual description for every instructional diagram;
- math rendered accessibly with readable source alternative;
- no timed interaction except clearly necessary sessions, with accommodation path;
- screen-reader announcement for grade/feedback without stealing focus;
- reduced-motion preference respected;
- language declared.

## 7. Content tone

Use direct, supportive language:

- Good: `Your calculation is correct. Check the unit conversion.`
- Avoid: `Wrong! You failed to convert the units.`
- Good: `Kasoma needs more answers before estimating this skill.`
- Avoid: `Mastery: 0%.`

## 8. Analytics with purpose

Track flow events needed to answer product questions, not every gesture. Do not place raw answer text, phone, email or guardian data in analytics. Every event name/property is registered in the analytics schema.

## 9. UX acceptance journeys

At minimum, E2E tests cover:

1. first-time learner registration through first recommendation;
2. interrupted diagnostic resume;
3. deterministic answer and remediation;
4. pending short-text grade;
5. progress with sparse versus sufficient evidence;
6. WhatsApp link and five-question continuation;
7. learner flagging an item;
8. consent-required block;
9. offline/retry without duplicate attempt;
10. keyboard-only completion of a revision session.
