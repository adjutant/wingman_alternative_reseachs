# Assessment method and evidence

## Scope

The active orchestration study contains 49 source assessments. Each assessment uses one pinned local checkout.
The common baseline is [Wingman's purpose](../../WINGMAN_PURPOSE.md).
The original source review date is November 5, 2026.
The report reorganization started on November 6, 2026.

The reports assess source behavior. They do not certify a current upstream release or a production deployment.
No candidate repository was updated during reorganization.
The Wingman application folders `main/` and `newman/` remain outside this review.

## Review path

1. Record the repository URL, full commit, and Git status.
2. Read applicable checkout instructions.
3. Locate the executable entry point and state owner.
4. Trace agent creation, identity, tools, permissions, and execution.
5. Trace one request through routing, persistence, worker activity, and completion.
6. Inspect concurrency, interruption, retries, recovery, and cleanup.
7. Compare all 24 Wingman features with cited implementation evidence.
8. Describe substantial extra capabilities and their integration cost.
9. State tests inspected, tests run, missing source, and unverified runtime behavior.

Use targeted searches for an absent feature. State the code areas searched.
A missing README section is insufficient evidence for an Absent verdict.
An externally hosted implementation can require an Unclear verdict.

## Verdicts

| Verdict | Meaning |
|---|---|
| Exact | The inspected behavior meets the stated feature within the report's boundary. |
| Similar | A substantial equivalent exists. Its workflow, scope, or persistence differs. |
| Resembles | A related mechanism exists. It does not supply the complete feature. |
| Absent | Targeted source searches found no corresponding implementation. |
| Unclear | Missing source or an external dependency prevents a reliable finding. |

Do not sum these labels into a maturity score.
A workflow compiler, a workbench, and an organization service solve different problems.
Read the evidence beside each label before using it for a design decision.

## Evidence levels

| Level | What it supports | Limit |
|---|---|---|
| Source traced | A concrete implementation path at the pinned commit | Deployment configuration can change observed behavior. |
| Test inspected | The assertion and its intended contract | The test was not necessarily executed. |
| Isolated test executed | The named contract in the recorded environment | It does not establish a complete deployed agent organization. |
| Documentation inspected | The documented interface or hosted behavior at the recorded date | It can differ from the local implementation or later releases. |
| Proposed design | A possible Wingman contract or experiment | It is not an observed candidate capability. |

The 25 historical audit records are in [the audit folder](_audits/).
They record independent source checks from the original assessment work.
Their document hashes are historical. Use current validation records for current file hashes.

## Retained older evidence

The older collection used an earlier Wingman definition.
The reorganization removed its duplicated landscape tables, workspace operations, and old Wingman assessment.
Current project assessments govern the fit verdicts.
Selected focused experiment evidence remains with the relevant project.

| Project | Retained historical result | Evidence limit |
|---|---|---|
| [Orca](../../orca/index.html) | Six initial checks and 15 communication checks; a later combined log records 21 passes. | Source-derived bundles and isolated SQLite state. No full desktop team was exercised. |
| [Agent Swarm](../../agent-swarm/index.html) | 363 tests across 14 files; five additional in-memory probes. | The probes expose specific cursor, notification, steering, and async-result behavior. They do not establish all integration behavior. |
| [CAR](../../codex-autorunner/index.html) | The old narrative reports 237 focused passes. | No raw run log was retained. Treat the count as a historical narrative claim. |
| [gstack](../../gstack/index.html) | Initial run: 180 passes and five failures. A two-file rerun: 84 passes and zero failures. | The rerun overlaps the first run. It does not erase the failures or add 84 distinct tests. |

Each project has a [legacy evidence note](../../orca/assessment/LEGACY_EVIDENCE.md) with its own links and limits.
Do not run retained scripts blindly. Some imports name historical paths or temporary dependencies.
Keep raw logs unchanged. An edited log cannot serve as the original observation.

## Writing review

Use ASD-STE100 principles for authored assessments and reports.
Use short sentences, active voice, one topic per sentence, and consistent terminology.
Preserve API names, state names, code paths, and necessary technical terms.
Explain a technical term at its first use when the reader needs that definition.
Avoid a formal compliance claim without a controlled-vocabulary review.

A sentence-length check can locate difficult prose. It cannot establish active voice or technical accuracy.
Source excerpts and raw experiment evidence retain their original wording.
The report review must distinguish those records from authored explanations.

## Report design

The reports share one stylesheet and one script.
They use the supplied Manrope fonts, navy navigation, pale surfaces, red accents, and compact tables.
Project detail uses readable technical prose and evidence links.
The overview uses high-impact findings and a filterable comparison table.
All report content remains available without network access or JavaScript.
