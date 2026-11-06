# Reorganization and report audit

Status: complete. Final verification date: November 7, 2026.

## Requirement review

| Requested result | Delivered result | Evidence |
|---|---|---|
| Reorganize the research | `research/` is the real folder. It contains all source snapshots, assessments and shared documents. | `migration.json`, `checkouts.json` |
| Preserve each source checkout | All 75 checkouts retain their original commit, Git status and directory inode. | `validation.json` |
| Keep project evidence together | Each project has `repo/`, `assessment/` and `index.html`. Supporting chapters remain with the project. | `coverage.json` |
| Document structure and method | The purpose is at the research root. `AGENTS.md` describes structure, evidence and maintenance. | `WINGMAN_PURPOSE.md`, `AGENTS.md` |
| Remove the old folders | `alternatives/`, `alt_researchs/` and `other-research/` no longer exist. | Structural validation |
| Select useful older research | Focused Orca, Agent Swarm and gstack records remain. CAR has a curated evidence note. Duplicate landscape and old deployment material was discarded. | Project `LEGACY_EVIDENCE.md` notes |
| Create comprehensive HTML | 75 project reports include decision briefs, full technical assessments and supporting chapters. | 75 project `index.html` files |
| Create overview and shared reports | The overview links all projects and compares 24 requirements. Three shared reports cover purpose, architecture and method. | `index.html`, `generic/` |
| Reuse the supplied design assets | Reports share Manrope, copied navigation icons, navy navigation, pale surfaces, red accents and compact tables. Branding is Wingman. | `assets/provenance.json`, shared CSS |
| Review writing and retain depth | The editorial pass covers 119 documents, including 75 assessments, supporting chapters and 25 historical audit notes. | `prose-review-progress.json` |
| Keep high-impact decisions visible | The overview states the purpose, four central findings, reading paths and adoption boundaries. | `index.html` |
| Respect excluded workspaces | The reorganization did not inspect or modify `main/` or `newman/`. | Task scope and research instructions |

## Final verification

The final structural check found no issues.
It checked all 75 checkouts, 24 feature verdicts per project, 79 HTML files, local links, anchors and shared assets.
The three original source folders are absent.
The canonical folder and instruction file use their standard names. No compatibility symlinks remain.
The November 7 cleanup updated current paths and rebuilt the reports. Historical source records retain their original paths.

All 79 pages passed browser checks at 1440px and 390px widths.
The 158 checks covered fonts, heading sizes, navigation, images, overflow, visible branding and keyboard access to code blocks.
Desktop and mobile renders were also inspected visually.
The design review used the supplied source styles and a rendered reference.

Search, source-group filters, combined empty results and all 24 comparison columns passed interaction checks.
The mobile menu opened and closed. Escape restored focus to its button.
Local-file filtering worked. Navigation opened Paperclip and returned to the overview.

Five representative automated accessibility checks found zero violations.
These covered the overview and gstack at desktop/mobile widths, plus the mobile architecture report.
A mobile check first found a code block without keyboard scroll access.
The builder now makes every code block focusable. The corrected reports passed the repeated checks.

All 14 retained raw evidence files match their original hashes.
The copied assets match their recorded hashes.
Historical commit and report hashes remain intact in all 25 audit notes.
Their original prose is preserved in `_audits/original-audit-prose.json`.

Verification records:

- `../../validation.json`
- `browser-validation.json`
- `accessibility-validation.json`
- `interaction-validation.json`
- `legacy-evidence-preservation.json`
- `prose-review-progress.json`
- `writing-review.json`

## Evidence and writing boundaries

The editorial pass applied short sentences, active voice, one topic per sentence and consistent terms.
It retained technical mechanisms, failure conditions, feature verdicts and source references.
The sentence queue remains an editorial aid. Some entries include citations or technical inventories.
The review does not claim formal ASD-STE100 certification.

Historical audits refer to the report versions reviewed on their stated dates.
Their hashes do not describe the current edited reports.
Current assessment hashes are in `coverage.json`.

Candidate products and their test suites were not started during this reorganization.
Retained experiment records establish only their named historical runs.
Structural checks and report browser tests do not establish candidate runtime reliability or product acceptance.
