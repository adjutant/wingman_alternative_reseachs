# Wingman research

Open [index.html](index.html) for the overview and comparison table.
All reports use local fonts, icons, CSS, and JavaScript.
Search and filters need JavaScript. The complete content does not.

## Structure

```text
research/
├── index.html
├── WINGMAN_PURPOSE.md
├── AGENTS.md
├── <project>/
│   ├── repo/
│   ├── assessment/
│   │   ├── ASSESSMENT.md
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
└── migration.json
```

`research/` is the real folder and Git repository root.
The original categories remain in `checkouts.json` as metadata.

## Reading paths

- [Wingman purpose](generic/purpose.html) defines the required product.
- [Architecture findings](generic/index.html) explain shared mechanisms and decisions.
- [Method and evidence](generic/method.html) define verdicts and verification limits.
- [Agent task coordination](generic/task-coordination.html) compares shared trackers, boards, claims and handoffs for agents and subagents.
- [Source index](generic/assessments/CHECKOUT_INDEX.md) lists all checkouts and commits.
- [Feature matrix](generic/assessments/FEATURE_MATRIX.md) provides the complete Markdown comparison.

Project reports start with a decision summary.
Their technical sections cover architecture, 24 features, lifecycle, coordination, extra capabilities, and adoption gaps.
Code links refer to the pinned local checkout.

Focused studies can add new upstream source evidence without adding projects to the original 75-checkout comparison.
The task coordination study records 17 open-source systems and five restricted alternatives or companions.
Its revisions, licenses, file hashes and review scopes are in [the evidence index](generic/assessments/agent-task-coordination/EVIDENCE.md).

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
python3 tools/validate_research.py --write
```

Run these commands from this repository's root.
The builder does not install or start candidate products.
The validator checks repository preservation, coverage, links, anchors, and assets.
The full migration validation needs the original local checkouts and workspace layout.
It compares their directory inodes with the recorded pre-move state.
It does not certify source semantics or formal ASD-STE100 compliance.

Read [the completion audit](generic/assessments/COMPLETION_AUDIT.md) for the current review state.
