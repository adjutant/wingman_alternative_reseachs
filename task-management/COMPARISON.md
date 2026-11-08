# Agent task management: findings across 25 codebases

This study assesses shared project and task records for an organization of agents, subagents, leaders, reviewers and a human owner. The [baseline](../AGENT_TASK_MANAGEMENT.md) defines T01–T24. All 25 codebases have complete tracked worktrees at recorded commits and a targeted source assessment against every requirement. The collection includes systems, an adapter, communication companions and a frontend. These are not 25 interchangeable products.

The conclusions below synthesize the individual reports. Their source links, inspected ranges, hashes and lifecycle limits remain authoritative. No candidate application or test suite was run. Feature presence, a test assertion and an observed working deployment are different evidence levels. The original 75-project Wingman study and the earlier task-coordination screening retain their separate scope.

## Main finding

The central choice is the shared authority and its execution contract. A board can retain plans without reserving work. A runtime can launch several sessions without governing task ownership. A mailbox can deliver a result without accepting it. The useful components are distributed across these categories; adding MCP does not combine their guarantees automatically.

No reviewed implementation establishes the entire baseline, without qualification, across every inspected writer and deployment mode. Several have substantial native mechanisms. Their boundaries concern current-attempt authority, readiness consistency, child-result acceptance, alternate mutations and recovery across hosts. Read the boundary beside each mechanism rather than ranking products by verdict counts.

## Fit routes at the assessed revisions

| Need | Relevant source studies | Decision that remains |
|---|---|---|
| Organization records and agent execution in one control plane | [Paperclip](paperclip/assessment/ASSESSMENT.md), [Agent Swarm](agent-swarm/assessment/ASSESSMENT.md) | Select and validate one execution profile and transition policy. Native workflow guarantees do not automatically govern legacy or ordinary task paths. |
| Local task authority with explicit ownership/review invariants | [Rhizome MCP](rhizome-mcp/assessment/ASSESSMENT.md), [agent-kanban-rs](agent-kanban-rs/assessment/ASSESSMENT.md), [Beads](beads/assessment/ASSESSMENT.md), [beads_rust](beads-rust/assessment/ASSESSMENT.md) | Choose the identity, attempt and trust model. Local stores do not create exclusive ownership across independent host replicas. Licensing differs. |
| Shared browser planning with a separate execution coordinator | [OpenProject](openproject/assessment/ASSESSMENT.md), [GitLab](gitlab/assessment/ASSESSMENT.md), [Plane](plane/assessment/ASSESSMENT.md), [Taiga backend](taiga/assessment/ASSESSMENT.md), [Kanboard](kanboard/assessment/ASSESSMENT.md), [Vikunja](vikunja/assessment/ASSESSMENT.md), [Planka](planka/assessment/ASSESSMENT.md) | Add atomic execution admission, attempts, recovery and accepted-result policy. Normal assignment and workflow permissions solve a different problem. |
| Integrated operator workspace and dispatch references | [Gemba](gemba/assessment/ASSESSMENT.md), [Muster](muster/assessment/ASSESSMENT.md), [Vibe Kanban](vibe-kanban/assessment/ASSESSMENT.md) | Confirm durable ownership and routed human functionality. Gemba's session-map guard, Muster's later writes and Vibe Kanban's retired project routes have distinct limits. |
| Repository-local planning and task context | [Backlog.md](backlog-md/assessment/ASSESSMENT.md), [Task Master](task-master/assessment/ASSESSMENT.md) | Supply the execution supervisor and reconcile concurrent writers. File replacement and edit locks are not worker reservations. |
| Communication, resource coordination and inspection alongside a tracker | [Python Agent Mail](agent-mail-python/assessment/ASSESSMENT.md), [Rust Agent Mail](agent-mail-rust/assessment/ASSESSMENT.md), [beads-viewer](beads-viewer/assessment/ASSESSMENT.md) | Keep task ownership and acceptance in the tracker. Acknowledgements, resource leases and graph recommendations do not finish tasks. |

[Agent HQ](agent-hq/assessment/ASSESSMENT.md) is a compact board/API reference with conditional claims, but general updates bypass its claim/readiness contract and its HTTP actor is not authenticated. [DevBoard](devboard/assessment/ASSESSMENT.md) has read-check-write allocation and file durability defects at its pin. These are different findings from merely lacking optional project-management features.

[Plane MCP](plane-mcp/assessment/ASSESSMENT.md) exposes extensive upstream operations but does not add an independent task authority. Its retrieve/replace assignment helper is not atomic allocation. [Taiga frontend](taiga-front/assessment/ASSESSMENT.md) provides the browser half of the backend; reconnect, board reconciliation and build-chain findings belong to that separate codebase. The matrix retains both companions so their implementation limits stay visible.

## Ownership and readiness must agree

[Rhizome](rhizome-mcp/assessment/ASSESSMENT.md) has attempt-specific lease credentials, checkpoints, version checks and transactional completion gates. Its HTTP boundary is deliberately literal loopback, without authenticated project users. This is useful local execution authority, not an already available shared LAN service.

[agent-kanban-rs](agent-kanban-rs/assessment/ASSESSMENT.md) enforces conditional claim, dependencies and reviewer completion. It lacks project organization and an execution-attempt identity: two sessions using the same agent name remain indistinguishable. Strong local state transitions do not prove strong remote identity.

[Beads](beads/assessment/ASSESSMENT.md) has conditional claims, durable claim leases, ready selection and revision support. Named claim and claim-next differ: named claim does not use the same readiness query. Close verbs and generic status patches also differ. Actor attribution and optional row-version guards do not become mandatory authenticated attempt capabilities.

[beads_rust](beads-rust/assessment/ASSESSMENT.md) has conditional claims, owner/revision-guarded handoff and workflow/capacity mechanisms. Ordinary assignment/update paths do not all require the claim guard. These are useful primitives for a trusted local team, with a restricted license and an external execution coordinator still required.

[Agent Swarm](agent-swarm/assessment/ASSESSMENT.md) implements transactional manual claims, worker capacity and recovery. Its automatic pool selection does not apply the same dependency check as manual acquisition. MCP and fresh HTTP completion also apply different output validation. A coordinator must consolidate these paths before relying on one readiness or completion rule.

[Muster](muster/assessment/ASSESSMENT.md) transactionally claims a card and renews claims through agent heartbeat. Later lane edits and completion do not require that lease or an attempt credential. [Paperclip](paperclip/assessment/ASSESSMENT.md) binds native tool mutations to the current running native execution and stores replay receipts transactionally. Its general route and legacy guards have different authority branches. Both studies show why a working claim endpoint is only part of the ownership lifecycle.

## Completion has several meanings

Three common meanings must remain distinct: a worker stopped, a task changed to a terminal state, and a particular result passed required review. Parent acceptance adds another decision.

[Paperclip](paperclip/assessment/ASSESSMENT.md) supplies revisioned completion contracts, durable evidence assessment and an optional human quality gate bound to current output revision or attachment hash. Its lightweight agent-claim policy can accept claimed criteria without every independent verification passing. Native child creation leaves automatic parent blocking off, and pending-child wake delivery is not acceptance of all children.

[Agent Swarm](agent-swarm/assessment/ASSESSMENT.md) has stronger fenced workflow execution and validation/approval nodes than its ordinary task completion path. [GitLab](gitlab/assessment/ASSESSMENT.md) separates issue closure, session finish, plan writing and merge approval. New-session restart prevents reuse of old session identity, while normal issue writers still lack a universal task-attempt lease. These are implemented distinctions, not reasons to merge all terminal labels into one success signal.

Conventional planning products also differ. [Taiga](taiga/assessment/ASSESSMENT.md) calculates story completion from closed child tasks when children exist; that is status aggregation. [Kanboard](kanboard/assessment/ASSESSMENT.md) closes subtasks when the parent closes. [Planka](planka/assessment/ASSESSMENT.md) transactionally synchronizes selected linked checklist state on closure. [OpenProject](openproject/assessment/ASSESSMENT.md) aggregates progress and governs workflow transitions. None of those mechanisms alone is a reviewer accepting the versioned outputs of independent child executions.

[Vikunja's](vikunja/assessment/ASSESSMENT.md) agent CLI asks workers to leave closure to a human, but direct done writes remain available. [Gemba's](gemba/assessment/ASSESSMENT.md) definition of done is informational and its runtime done signal checks worktree cleanliness rather than accepted results. [Task Master's](task-master/assessment/ASSESSMENT.md) Git/workflow/task/log effects can diverge during finalization. Prompt conventions and clean Git state are useful context, not enforced acceptance.

## Communication and recovery are separate contracts

The two Agent Mail implementations must not be treated as equivalent. [Python Agent Mail](agent-mail-python/assessment/ASSESSMENT.md) reports reservation conflicts and still grants requested reservations. [Rust Agent Mail](agent-mail-rust/assessment/ASSESSMENT.md) excludes conflicting file paths and rechecks grants transactionally; its build slots remain advisory. Rust also has retained delivery cursors and keyed mutation replay. Neither mailbox owns the task graph or accepted task outcome. Both pins have explicit license restrictions.

[beads-viewer](beads-viewer/assessment/ASSESSMENT.md) produces planning tracks and routed tracker commands. A recommendation does not reserve the suggested work. Its mutation authority comes from the installed tracker, and source snapshots can become stale between analysis and execution.

Recovery needs more than a timestamp or reconnecting socket. [Rhizome](rhizome-mcp/assessment/ASSESSMENT.md) persists checkpoints and expires attempts. [Paperclip](paperclip/assessment/ASSESSMENT.md) checks checkpoint identity and holds ambiguous/live-owned execution rather than always restarting it. [Agent Swarm](agent-swarm/assessment/ASSESSMENT.md) has stale classification and generation-aware workflow recovery, while ordinary task writes have weaker fencing. [GitLab](gitlab/assessment/ASSESSMENT.md) cleans up stale created/running sessions and restarts failed/stopped execution as a new session. These mechanisms act on different records and cannot be substituted without a defined task contract.

Human views also have recovery boundaries. [Planka](planka/assessment/ASSESSMENT.md) fetches new snapshots after reconnect, while [Taiga frontend](taiga-front/assessment/ASSESSMENT.md) and [Gemba](gemba/assessment/ASSESSMENT.md) have gaps in the inspected universal reconnect/replay path. [Vibe Kanban](vibe-kanban/assessment/ASSESSMENT.md) retains useful local execution tools, but the routed project page is retired at its pin. Existing board components and historical screenshots do not prove an active project experience.

## Deployment and licensing boundaries

One local SQLite or file authority is different from independent replicated stores. A Mac and Linux worker can coordinate through a shared service, but two offline stores cannot promise exclusive ownership merely because they synchronize later. Adding a network listener to a local tool also requires an authenticated authority model; it does not create one by itself.

Shared web planners provide project membership, history and inspection but bring a larger operating boundary. Their database, assets, repository or object storage, secrets, queues and workers must be restored coherently. Embedded or single-process configurations can simplify setup while limiting the available concurrency guarantees. A process-local start lock is not a multi-server capacity lock, as the Paperclip review makes explicit.

Licensing and availability must be evaluated separately from technical fit. GitLab has CE/EE boundaries. OpenProject's inspected native MCP endpoint requires an Enterprise entitlement and configuration. Plane MCP's MIT license does not establish every upstream resource's availability. Planka's Community terms, Task Master's Commons Clause and the riders in the two Agent Mail projects, beads_rust and beads-viewer impose distinct use restrictions. The reports link the pinned declarations. None is reclassified as unrestricted open source merely because its code is public.

## What the matrix means

The matrix contains all 600 requirement verdicts from the 25 source-review ledgers. Exact, Similar, Resembles, Absent and Unclear retain each report's stated boundary. They are not points, maturity scores, installation results or a reliability ranking. Read the relevant row's detailed report before carrying a feature into a design.

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
