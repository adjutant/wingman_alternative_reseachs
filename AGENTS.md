# Research instructions

## Scope

This folder contains Wingman research. Do not read the sibling main or newman projects for this task.
Keep retained source checkouts unchanged. Do not install or start a candidate product to update a report.
Read a checkout's own instructions before you operate inside that checkout.

## Structure

- `index.html` contains the portfolio overview and comparison table.
- `repositories.html` and `REPOSITORY_INVENTORY.md` are built from the active repository profiles. They list each upstream once and link both studies when applicable.
- `WINGMAN_PURPOSE.md` defines the assessment baseline.
- `AGENT_TASK_MANAGEMENT.md` defines the dedicated baseline for project and task coordination among agents.
- `task-management/` holds the full source study against its T01–T24 requirements. Its checkout and assessment progress are separate from the original 75-project comparison.
- `task-management/index.html` contains the 9-codebase comparison and searchable requirement matrix.
- `task-management/purpose.html` presents `AGENT_TASK_MANAGEMENT.md`; each `<codebase>/index.html` presents its complete task assessment.
- `<project>/repo/` contains one independent Git checkout.
- `<project>/assessment/ASSESSMENT.md` contains the technical assessment.
- `<project>/assessment/REPOSITORY_PROFILE.md` records the dated GitHub snapshot and concise findings for the corresponding assessment. Both studies use this filename.
- `<project>/assessment/` also holds supporting chapters and retained experiment evidence.
- `<project>/index.html` contains the project report.
- `generic/assessments/` contains shared methods, comparisons, and audit records.
- `generic/index.html` contains the shared architecture report.
- `generic/method.html` explains evidence and assessment limits.
- `generic/task-coordination.html` presents the focused study of shared agent tasks, boards, claims and handoffs.
- `generic/assessments/agent-task-coordination/` records focused candidate screening, immutable source references and verification evidence.
- `generic/purpose.html` presents the Wingman purpose.
- `assets/` contains shared CSS, JavaScript, fonts, and navigation icons.
- `tools/` contains the report builder and validators.
- `tools/serve_reports.py` serves reports on the LAN. Source checkout access requires `--include-source`.
- `checkouts.json` and `coverage.json` list active sources. `migration.json` records historical source provenance.
- `SHITLIST.md` records one repository URL per line for excluded sources.

`research/` is the physical folder and Git repository root.
Use `AGENTS.md` for these instructions. Do not create compatibility symlinks for misspelled names.

## Assessment method

The original assessment date is November 5, 2026. Reorganization started on November 6, 2026.
Assess each pinned commit against the 24 features in `generic/assessments/ASSESSMENT_GUIDE.md`.
Trace executable paths. Follow entry, identity, persistence, routing, execution, recovery, and completion.
Use a README to locate code. Do not use README claims as proof of runtime behavior.
Explain tools, permissions, concurrency, scheduling, cancellation, cleanup, and multi-host limits.
Separate role instructions from enforced application behavior.
Separate logical agent identity from a process, a session, a task, and an execution attempt.

Use the verdicts Exact, Similar, Resembles, Absent, and Unclear.
State the boundary of each verdict. Do not convert verdict counts into a product ranking.
Focused studies outside the original 75-project comparison can use topic-specific criteria.
For the full task-management study, use `task-management/checkouts.json`, each project's `assessment/ASSESSMENT.md` and `assessment/review.json`.
Run `tools/validate_task_management.py --write` for progress integrity and add `--require-complete` for its final source-assessment coverage gate.
State their review scope and evidence level. T01–T24 task requirements are distinct from the original F01–F24 Wingman features.
Preserve code links and line references. Keep the complete commit ID.
Use bare complete external URLs. Use relative links for local evidence.

## Evidence

The 25 files in `generic/assessments/_audits/` are historical independent source audits.
Their hashes refer to the documents at the time of each audit.
Migration changed relative paths. Later edits can also change prose.
Do not describe those historical hashes as current file hashes.
Retained tests and logs establish only the named experiment at the recorded revision.
A test read is not a test run. A successful turn is not product acceptance.
Do not rerun old probes without checking their imports and environment first.
Keep all assessment inputs, imports, links and scratch files within this repository.
Use repository-relative manifest paths. Do not record machine-specific paths or directory inodes.
Historical path normalization requires a notice and original/current hashes; it is not a new test run.
Runtime paths described as candidate behavior are reviewed separately in `generic/assessments/portability-runtime-paths.json`.
Run `python3 tools/validate_portability.py --write` before publishing.

## Writing and reports

Apply ASD-STE100 principles: short sentences, active voice, one topic per sentence, and consistent terms.
Keep the technical detail needed to explain a mechanism and its failure conditions.
Use the overview for high-impact decisions. Use project reports for implementation detail.
Do not claim formal ASD-STE100 certification from a sentence-length check.
Use Wingman branding. Reuse the supplied fonts, icons, colors, and layout patterns only.
All reports share `assets/report.css` and `assets/report.js`.
Keep reports usable from local files. Do not require a network request to read a report.
Support keyboard navigation, small screens, print, and reduced motion.

## Build and verification

Use `tools/build_reports.py` to generate HTML from the curated research and project assessments.
Use `tools/validate_research.py` to check repository preservation, coverage, links, assets, and report structure.
Use `tools/validate_task_publication.py --write` to check complete task-report prose, all matrix verdicts and their explanation links against the source artifacts.
Inspect representative desktop and mobile renders. Check search, filters, and return navigation.
Keep a completion audit that states unresolved work. Do not treat a structural check as a semantic review.
