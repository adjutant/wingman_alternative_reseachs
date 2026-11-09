# Wingman research

Open [index.html](index.html) for the overview and comparison table.
Open the [repository inventory](repositories.html) or its [Markdown version](REPOSITORY_INVENTORY.md) for GitHub statistics, commit dates, and concise findings across both studies.
All reports use local fonts, icons, CSS, and JavaScript.
Search and filters need JavaScript. The complete content does not.

## Structure

```text
research/
├── index.html
├── repositories.html
├── REPOSITORY_INVENTORY.md
├── WINGMAN_PURPOSE.md
├── AGENT_TASK_MANAGEMENT.md
├── AGENTS.md
├── task-management/
│   ├── index.html
│   ├── purpose.html
│   ├── COMPARISON.md
│   ├── REQUIREMENT_MATRIX.md
│   ├── checkouts.json
│   └── <codebase>/...assessment, report and optional source checkout...
├── <project>/
│   ├── repo/
│   ├── assessment/
│   │   ├── ASSESSMENT.md
│   │   ├── REPOSITORY_PROFILE.md
│   │   └── ...supporting chapters and evidence...
│   └── index.html
├── generic/
│   ├── index.html
│   ├── purpose.html
│   ├── method.html
│   └── assessments/
├── assets/
├── tools/
├── checkouts.json
├── coverage.json
├── SHITLIST.md
└── migration.json
```

`research/` is the real folder and Git repository root.
The original categories remain in `checkouts.json` as metadata. The active studies cover 49 orchestration checkouts and 9 task assessments. Paperclip and Agent Swarm appear in both studies. Excluded repositories are recorded in `SHITLIST.md`.
The active inventory excludes repositories with fewer than 100 stars in the November 9, 2026 GitHub snapshot.

## Reading paths

- [Wingman purpose](generic/purpose.html) defines the required product.
- [Architecture findings](generic/index.html) explain shared mechanisms and decisions.
- [Method and evidence](generic/method.html) define verdicts and verification limits.
- [Agent task coordination](generic/task-coordination.html) compares shared trackers, boards, claims and handoffs for agents and subagents.
- [Agent task management baseline](AGENT_TASK_MANAGEMENT.md) defines the dedicated coordination requirements.
- [Agent task management](task-management/index.html) compares all 9 codebase assessments against T01–T24.
- [Task-study source guide](task-management/README.md) links Markdown reports, source ledgers and verification evidence.
- [Source index](generic/assessments/CHECKOUT_INDEX.md) lists all checkouts and commits.
- [Feature matrix](generic/assessments/FEATURE_MATRIX.md) provides the complete Markdown comparison.

Project reports start with a decision summary.
Their technical sections cover architecture, 24 features, lifecycle, coordination, extra capabilities, and adoption gaps.
Code links refer to the pinned local checkout.
Each study's Markdown profile records GitHub metadata as observed on November 9, 2026, alongside the findings from its pinned technical assessment. Update the profiles and rebuild both inventories together when collecting a new snapshot.

Focused studies can add new upstream source evidence without adding projects to the original 75-checkout comparison.
The earlier task coordination screening records 17 open-source systems and five restricted alternatives or companions.
Its revisions, licenses, file hashes and review scopes are in [the evidence index](generic/assessments/agent-task-coordination/EVIDENCE.md).
The deeper task-management study has 9 complete checkouts and reports, including the communication companions. The earlier screening also considered general-purpose project planners.

## Serve on your LAN

Start the server from this repository's root:

```sh
python3 tools/serve_reports.py
```

The server uses Python's standard library. No extra packages are required.
It listens on all IPv4 interfaces on port 8765.
Open the machine's LAN address on that port from another device.
Use `--host` to bind one address or `--port` to select another port.
Press Ctrl-C to stop the foreground server.

The server serves reports, assets, assessments and provenance files.
It blocks hidden paths, directory listings and files outside this report collection.
Source checkout links are disabled by default. Add `--include-source` to serve those code links on the LAN.
Git metadata stays blocked with either setting.

Run the server checks with:

```sh
python3 tools/test_serve_reports.py
```

## Git repository

This repository tracks assessments, HTML reports, shared assets, tools and provenance records.
Each `<project>/repo/` checkout is independent and excluded through `.gitignore`.
Source checkouts are not submodules and are not included in a clone of this repository.
`checkouts.json` records their upstream URLs. `coverage.json` records the assessed commits.
Reports can be read without the checkouts. Local code links need the corresponding checkout.

## Provenance

The original source assessment date is November 5, 2026.
Reorganization started on November 6, 2026.
`migration.json` records original document hashes and repository state.
`coverage.json` records current paths, hashes, feature verdicts, and audit paths.
`checkouts.json` records source paths and original clone history.

Historical source audits remain in `generic/assessments/_audits/`.
Their hashes refer to the documents at the time of each audit.
Selected older evidence remains with Orca, Agent Swarm, CAR, and gstack.
Each has a `LEGACY_EVIDENCE.md` note with evidence limits.
The reorganization removed duplicated older landscape tables and old workspace-operation records.

## Build and verify

Use the user's uv installation. The builder declares its dependencies.

```sh
uv run --script tools/build_reports.py
python3 tools/validate_portability.py --write
python3 tools/validate_research.py --write
python3 tools/validate_task_management.py --write --require-complete
uv run --script tools/validate_task_publication.py --write
python3 tools/test_serve_reports.py
```

Run these commands from this repository's root.
The builder does not install or start candidate products.
The validator checks repository preservation, coverage, links, anchors, and assets.
Source validation needs the pinned checkouts in their declared `repo/` directories.
It compares commits and Git state, not host paths or filesystem inodes.
The report collection builds and reads without source checkouts.
Run `python3 tools/validate_portability.py --reports-only` to check such a report-only clone.
The portability check covers every tracked file, including archived evidence and generated reports.
See [the portability audit](generic/assessments/PORTABILITY_AUDIT.md) for path normalization, evidence hashes and relocation checks.
It does not certify source semantics or formal ASD-STE100 compliance.

Read [the completion audit](generic/assessments/COMPLETION_AUDIT.md) for the current review state.
Read [the task-study completion audit](task-management/COMPLETION_AUDIT.md) for its separate source and publication evidence.
