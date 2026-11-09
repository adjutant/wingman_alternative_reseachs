# Agent task management: findings across 9 codebases

This study assesses shared project and task records for an organization of agents, subagents, leaders, reviewers and a human owner. The [baseline](../AGENT_TASK_MANAGEMENT.md) defines T01–T24. All 9 codebases have complete tracked worktrees at recorded commits and a targeted source assessment against every requirement. The collection includes task systems, execution workspaces and companions.

The conclusions below synthesize the individual reports. Their source links, inspected ranges, hashes and lifecycle limits remain authoritative. No candidate application or test suite was run. Feature presence, a test assertion and an observed working deployment are different evidence levels. The orchestration study uses a separate baseline. The earlier task-coordination screening records its historical scope.

## Main finding

The central choice is the shared authority and its execution contract. A board can retain plans without reserving work. A runtime can launch several sessions without governing task ownership. A mailbox can deliver a result without accepting it. The useful components are distributed across these categories; adding MCP does not combine their guarantees automatically.

No reviewed implementation establishes the entire baseline, without qualification, across every inspected writer and deployment mode. Several have substantial native mechanisms. Their boundaries concern current-attempt authority, readiness consistency, child-result acceptance, alternate mutations and recovery across hosts. Read the boundary beside each mechanism rather than ranking products by verdict counts.

## Design and implementation review

The shortlist evaluates each project against its own role. A local tracker, browser board, execution workspace and mail companion each have different responsibilities. Early projects can qualify when their design is coherent and the source implements a substantial part of that role.

- **DevBoard** (`cbe017a445fd4f9dee2de73f729c65b7fe0f9b9b`). In `src/devboard/__init__.py`, competing processes can both claim a task or generate the same ID because the checks and file writes run separately. A rename deletes the old file before writing its replacement. A failed write can lose the task. Source repository https://github.com/RapidWebs-Enterprise/DevBoard
- **Agent HQ** (`785cd8c9a55b2b517eb8eb8f680cd65985992282`). In `src/services.js`, ordinary updates can overwrite a claimed assignee, release can clear a claim without an actor, and direct claims skip the readiness checks used by next-task selection. The HTTP interface accepts caller-supplied identities without authentication.
- **Task Master** (`c0c98d367c55296bfe69e65680625b6db437af02`). The file storage adapter can replace a whole task group with a snapshot read before locking, losing concurrent edits. The legacy and current writers use incompatible lock types at the same path. Workflow finalization can delete workflow state after the task status save fails.

Vibe Kanban stays for local execution, worktrees and session inspection. Its project board route is retired.

## Fit routes at the assessed revisions

| Need | Relevant source studies | Decision that remains |
|---|---|---|
| Organization records and agent execution in one control plane | [Paperclip](paperclip/assessment/ASSESSMENT.md), [Agent Swarm](agent-swarm/assessment/ASSESSMENT.md) | Select and validate one execution profile and transition policy. Native workflow guarantees do not automatically govern legacy or ordinary task paths. |
| Local task authority with explicit ownership/review invariants | [Beads](beads/assessment/ASSESSMENT.md), [beads_rust](beads-rust/assessment/ASSESSMENT.md) | Choose the identity, attempt and trust model. Local stores do not create exclusive ownership across independent host replicas. Licensing differs. |
| Local execution workspaces | [Vibe Kanban](vibe-kanban/assessment/ASSESSMENT.md) | Supply durable task ownership and a project board above the local execution layer. |
| Repository-local planning and task context | [Backlog.md](backlog-md/assessment/ASSESSMENT.md) | Supply the execution supervisor and reconcile concurrent writers. File replacement and edit locks are not worker reservations. |
| Communication, resource coordination and inspection alongside a tracker | [Python Agent Mail](agent-mail-python/assessment/ASSESSMENT.md), [Rust Agent Mail](agent-mail-rust/assessment/ASSESSMENT.md), [beads-viewer](beads-viewer/assessment/ASSESSMENT.md) | Keep task ownership and acceptance in the tracker. Acknowledgements, resource leases and graph recommendations do not finish tasks. |

## Human interfaces

| Interface | Assessed codebases |
|---|---|
| Browser UI for projects and tasks | Paperclip |
| Task UI scoped to a project or workspace | Backlog.md has a browser board and TUI. |
| Browser task dashboard with limited project views | Agent Swarm has a task board, table and execution details. |
| Interactive TUI and cross-repository overview | beads-viewer supplies terminal Kanban, search and graph views, plus static browser reports. It reads an external tracker. |
| Terminal commands and summaries | Beads and beads_rust. |
| Other interface or no task board | Python Agent Mail and Rust Agent Mail show mail and reservations. Vibe Kanban shows execution sessions, while its project board route is export-only at the assessed revision. |

## Ownership and readiness must agree

[Beads](beads/assessment/ASSESSMENT.md) has conditional claims, durable claim leases, ready selection and revision support. Named claim and claim-next differ: named claim does not use the same readiness query. Close verbs and generic status patches also differ. Actor attribution and optional row-version guards do not become mandatory authenticated attempt capabilities.

[beads_rust](beads-rust/assessment/ASSESSMENT.md) has conditional claims, owner/revision-guarded handoff and workflow/capacity mechanisms. Ordinary assignment/update paths do not all require the claim guard. These are useful primitives for a trusted local team, with a restricted license and an external execution coordinator still required.

[Agent Swarm](agent-swarm/assessment/ASSESSMENT.md) implements transactional manual claims, worker capacity and recovery. Its automatic pool selection does not apply the same dependency check as manual acquisition. MCP and fresh HTTP completion also apply different output validation. A coordinator must consolidate these paths before relying on one readiness or completion rule.

[Paperclip](paperclip/assessment/ASSESSMENT.md) binds native tool mutations to the current running native execution and stores replay receipts transactionally. Its general route and legacy guards have different authority branches.

## Completion has several meanings

Three common meanings must remain distinct: a worker stopped, a task changed to a terminal state, and a particular result passed required review. Parent acceptance adds another decision.

[Paperclip](paperclip/assessment/ASSESSMENT.md) supplies revisioned completion contracts, durable evidence assessment and an optional human quality gate bound to current output revision or attachment hash. Its lightweight agent-claim policy can accept claimed criteria without every independent verification passing. Native child creation leaves automatic parent blocking off, and pending-child wake delivery is not acceptance of all children.

[Agent Swarm](agent-swarm/assessment/ASSESSMENT.md) has stronger fenced workflow execution and validation/approval nodes than its ordinary task completion path.

## Communication and recovery are separate contracts

The two Agent Mail implementations must not be treated as equivalent. [Python Agent Mail](agent-mail-python/assessment/ASSESSMENT.md) reports reservation conflicts and still grants requested reservations. [Rust Agent Mail](agent-mail-rust/assessment/ASSESSMENT.md) excludes conflicting file paths and rechecks grants transactionally; its build slots remain advisory. Rust also has retained delivery cursors and keyed mutation replay. Neither mailbox owns the task graph or accepted task outcome. Both pins have explicit license restrictions.

[beads-viewer](beads-viewer/assessment/ASSESSMENT.md) produces planning tracks and routed tracker commands. A recommendation does not reserve the suggested work. Its mutation authority comes from the installed tracker, and source snapshots can become stale between analysis and execution.

Recovery needs more than a timestamp or reconnecting socket. [Paperclip](paperclip/assessment/ASSESSMENT.md) checks checkpoint identity and holds ambiguous/live-owned execution rather than always restarting it. [Agent Swarm](agent-swarm/assessment/ASSESSMENT.md) has stale classification and generation-aware workflow recovery, while ordinary task writes have weaker fencing. These mechanisms act on different records and cannot be substituted without a defined task contract.

[Vibe Kanban](vibe-kanban/assessment/ASSESSMENT.md) retains useful local execution tools, but the routed project page is retired at its pin. Existing board components and historical screenshots do not prove an active project experience.

## Deployment and licensing boundaries

One local SQLite or file authority is different from independent replicated stores. A Mac and Linux worker can coordinate through a shared service, but two offline stores cannot promise exclusive ownership merely because they synchronize later. Adding a network listener to a local tool also requires an authenticated authority model; it does not create one by itself.

Shared web planners provide project membership, history and inspection but bring a larger operating boundary. Their database, assets, repository or object storage, secrets, queues and workers must be restored coherently. Embedded or single-process configurations can simplify setup while limiting the available concurrency guarantees. A process-local start lock is not a multi-server capacity lock, as the Paperclip review makes explicit.

Licensing and availability must be evaluated separately from technical fit. The two Agent Mail projects, beads_rust and beads-viewer have license riders that restrict use. The reports link the pinned declarations. None is reclassified as unrestricted open source merely because its code is public.

## What the matrix means

The matrix contains all 216 requirement verdicts from the 9 source-review ledgers. Exact, Similar, Resembles, Absent and Unclear retain each report's stated boundary. They are not points, maturity scores, installation results or a reliability ranking. Read the relevant row's detailed report before carrying a feature into a design.

The [full Markdown matrix](REQUIREMENT_MATRIX.md) and the browser matrix use the same recorded verdicts. The [checkout manifest](checkouts.json) records revisions and materialization. The [progress record](progress.json) records integrity checks, and the [completion audit](COMPLETION_AUDIT.md) separates source review from publication and presentation verification.

## Validation needed before adoption

Use the final integration's real writers and credentials for these experiments:

1. Race two independent workers for the same ready task and for the last capacity slot. Repeat through direct, automatic, bulk and board interfaces.
2. Expire or cancel an attempt, start its replacement, then let the old worker submit progress, results and external side effects.
3. Finish a parent while a required child is active, failed, cancelled or awaiting review. Confirm the intended accepted-child rule.
4. Approve one artifact revision, modify it, and attempt completion. Check the exact version/hash binding.
5. Interrupt between primary persistence, audit, notification, result receipt and downstream wake. Reconcile committed and uncommitted work without duplicating effects.
6. Restore the database with corresponding artifacts, secrets and execution ownership state. Recover live, ambiguous and stopped workers across both execution hosts.
7. Disconnect a human client, change work elsewhere, then reconnect. Verify backlog, ownership, pending decisions and stale status converge.

These experiments were not run in this study. They define the remaining acceptance work for a chosen implementation and integration, rather than implying that source inspection certified production operation.
