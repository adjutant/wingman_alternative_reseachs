# Research instructions

## Scope

This folder contains Wingman research. Do not read `../main/` or `../newman/` for this task.
Keep each source checkout unchanged. Do not install or start a candidate product to update a report.
Read a checkout's own instructions before you operate inside that checkout.

## Structure

- `index.html` contains the portfolio overview and comparison table.
- `WINGMAN_PURPOSE.md` defines the assessment baseline.
- `<project>/repo/` contains one independent Git checkout.
- `<project>/assessment/ASSESSMENT.md` contains the technical assessment.
- `<project>/assessment/` also holds supporting chapters and retained experiment evidence.
- `<project>/index.html` contains the project report.
- `generic/assessments/` contains shared methods, comparisons, and audit records.
- `generic/index.html` contains the shared architecture report.
- `generic/method.html` explains evidence and assessment limits.
- `generic/purpose.html` presents the Wingman purpose.
- `assets/` contains shared CSS, JavaScript, fonts, and navigation icons.
- `tools/` contains the report builder and validators.
- `tools/serve_reports.py` serves reports on the LAN. Source checkout access requires `--include-source`.
- `checkouts.json`, `coverage.json`, and `migration.json` record source provenance.

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
Inspect representative desktop and mobile renders. Check search, filters, and return navigation.
Keep a completion audit that states unresolved work. Do not treat a structural check as a semantic review.
