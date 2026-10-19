# Academic source discovery register

Inspected 19 October 2026. Requirements supported: FR-CNT-005, FR-DIAG-003 and
NFR-MNT-001. Status: reference discovery only; no academic or rights approval.

The [production-pilot decision](../specifications/16_Production_Pilot_Decisions.md)
freezes six product clusters and requires academic reviewers to establish exact
current NCDC outcomes and syllabus references before item approval. This register
makes the located source editions reproducible for that review. It does not change
scope, select curriculum mappings or certify that these files remain the applicable
curriculum for the intended cohort.

## Official references inspected

The [NCDC resource directory](https://ncdc.go.ug/resource/) distinguishes revised
O-Level resources from accelerated and A-Level programmes. The inspected PDF covers
identify the Lower Secondary Curriculum and the National Curriculum Development
Centre. The [Physics resource page](https://ncdc.go.ug/books/physics-syllabus/)
embeds the Physics PDF below. No corresponding Mathematics landing page is asserted.

| Local discovery key | Official PDF | Observed pages / bytes | Visually checked locator |
| --- | --- | --- | --- |
| NCDC-LSC-MATH-20261019 | [Mathematics syllabus](https://ncdc.go.ug/wp-content/uploads/2024/02/Mathematics_Syllabus_compressed.pdf) | 70 / 1,869,423 | Cover: PDF page 1. First Senior 4 detail: PDF page 58, printed page 56. |
| NCDC-LSC-PHYSICS-20261019 | [Physics syllabus](https://ncdc.go.ug/wp-content/uploads/2024/02/PHYSICS_Syllabus_compressed.pdf) | 62 / 1,714,512 | Cover: PDF page 1. First Senior 4 detail: PDF page 47, printed page 45. |

Discovery keys are document-review labels, not NCDC identifiers or learning-outcome
codes. PDF page locators are one-based and include the cover; printed numbering is
recorded separately. These starting locators do not constitute a full syllabus audit.
No outcome text, question, diagram, answer key or rubric is reproduced here.

SHA-256 of the actual inspected bytes:

- Mathematics: `83e3739a34ebe5cb52b25b500971265e3e90d48179e7aefa5cf75b4c0c41911e`.
- Physics: `3de33277b9b1112428ee0b1765770d19ae2504742d11dfe9102d2e1266a7e507`.

The upload path's 2024 date and PDF creation/modification metadata are not evidence
of an academic edition, effective date or current-cohort applicability. An owner must
record those facts from authoritative academic confirmation, including superseding
circulars or amendments if applicable. Changed bytes require a new review entry;
a matching filename alone does not establish the same source.

## Rights and use boundary

Both entries remain `UNKNOWN_BLOCKED` pending a documented rights decision under
[content operations section 5](../specifications/07_Content_Operations_and_Academic_QA.md).
Public download availability does not establish publication or embedding permission.
The NCDC website retains a copyright notice. No licence, permission, public-domain
classification or reference-only clearance has been inferred.

Local inspection copies, extracted text and rendered images stay in ignored
`.local/curriculum-review/`; none are committed, uploaded to application storage,
imported as drafts, embedded, sent to a model or served to learners. The downloads
used verified TLS and an existing certificate bundle; no trust bypass, dependency
change, cloud SDK or application provider call was introduced.

The present register contains links, hashes and factual inspection metadata only.
A later reference-only rights decision would still prohibit reproducing source text
or media. Only an authorized publishable rights state and its recorded conditions,
plus independent academic approval, can make actual item content eligible.

## Academic review handoff

Academic/content owners have not been named or supplied approval evidence. Required
work before the academic inventory gate can close:

1. Confirm normal Lower Secondary programme, effective edition, amendments and
   intended Senior 4 cohort. Do not substitute accelerated, primary or A-Level
   materials because a newer download date appears in search.
2. Confirm each item's exact outcome and source locator, including original teaching
   year where Senior 4 revision draws on prior learning. The approved product clusters
   span accumulated O-Level learning; do not limit the bank to the Senior 4 heading
   or treat those product labels as official NCDC taxonomy.
3. Record the rights owner, permitted uses, evidence reference and restrictions.
   Determine rights independently for each authored item and any included media.
4. Approve the concept/competency/prerequisite map and balanced coverage cells for the
   existing six clusters. Assign independent authors/reviewers and preserve versions.
5. Supply at least 250 independently approved items with adequate coverage and unseen
   equivalent pairs. Freeze expert-scored benchmark truth separately; a source link
   or synthetic fixture does not establish scoring accuracy or calibration.

No reviewer signatures, permissions, learning-outcome IDs, coverage counts or
benchmark scores are invented. The [release gates](RELEASE_GATES.md) remain open;
normal synthetic fixtures and disabled short-text release controls remain in force.

## Verification scope

`pdfinfo` confirmed page/byte counts; SHA-256 identifies both inspected files.
`pdftotext -layout` located candidate headings; `pdftoppm` rendered both covers and
both stated Senior 4 detail pages, which were visually inspected to distinguish
printed numbering from PDF offsets. This is limited source inspection, not academic
validation, accessibility certification or reproduction clearance. Repository checks
for this Markdown-only change are `make check-docs` and `git diff --check`; no API,
application, dependency, migration, test data or architecture change is made.
