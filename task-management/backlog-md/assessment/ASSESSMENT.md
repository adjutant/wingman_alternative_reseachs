# Backlog.md task management assessment

Repository: https://github.com/MrLesk/Backlog.md

Commit: `3a296c0f6f949b31e458b849b9617702c56c1023`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 9, 2026. Full local checkout; targeted static implementation and test-source review.
Candidate dependencies, applications and tests were not installed or run.

## Fit decision and assessment boundary

Backlog.md is a substantial local task workspace for a human and coding agents working through repository files.
It provides durable Markdown tasks, parent links, dependencies, readiness, acceptance checklists, implementation notes, milestones, search, a terminal interface and a browser board.
The CLI, MCP adapter and browser API share a central task implementation.
This is a useful foundation for planning and recording work close to its source code.

It does not provide the execution authority required by the baseline.
Assignees are editable strings, rather than authenticated workers with exclusive claims.
There are no execution attempts, worker heartbeats, ownership leases, stale-attempt fences or supervised delegation.
A short lock around a file edit does not reserve the work until an agent finishes it.

The best fit is a trusted local workspace with agents coordinated by a separate supervisor.
Using several Git clones as independent task authorities would require conflict resolution and an ownership service above the files.
Completion also needs additional policy: a valid status change does not require completed children, satisfied dependencies, checked criteria or independent approval.

The package is MIT licensed.
This review covers the task lifecycle, storage and locking, dependency reads and writes, worktree boundaries, browser mutations and refresh, MCP task operations and selected test assertions.
It is not an every-line audit of all 1,533 tracked files.
It does not establish installation success, race reproduction, live usability, performance or accessibility conformance.
See [license](../repo/LICENSE), [package metadata](../repo/package.json) and the [review ledger](review.json).

## Architecture and source scope

The central `Core` coordinates a filesystem abstraction, Git operations, content indexing and search.
Tasks have a Markdown body plus structured metadata.
The model includes status, assignees, reporter, dates, labels, milestone, dependency IDs, parent identity, priority, type, project label, references, documentation, modified files, plans, notes, comments, final summary and two checklists.
A task record is distinct from its derived readiness and dependency graph.
Neither the model nor the MCP task catalogue introduces an execution-attempt entity.
See [task model](../repo/src/types/index.ts), lines 1–118, and [task tools](../repo/src/mcp/tools/tasks/index.ts), lines 1–110.

The content store maintains in-process maps, versions, filesystem watchers and publication state.
Search uses Fuse over tasks, documents and decisions, with task filters applied to the results.
These are derived local views; the Markdown files remain the durable work records.
A store version is not a conditional write version supplied by the caller.
See [content store](../repo/src/core/content-store.ts), lines 1–170, and [search service](../repo/src/core/search-service.ts), lines 1–115.

The browser server binds to `127.0.0.1` and defaults to port 6420.
It serves both the React application and task APIs.
MCP startup supports stdio and resolves a workspace root from command options, environment or the client workspace.
These interfaces are designed around a trusted local process and filesystem, rather than a remotely authenticated organization service.
See [browser startup](../repo/src/server/index.ts), lines 391–438, and [MCP startup](../repo/src/commands/mcp.ts), lines 1–85.

The source agreement identifies the CLI and shared model as public product contracts and treats internal TypeScript exports differently.
This assessment therefore traces actual HTTP and MCP callers before treating an internal mutation as an exposed behavior.
Candidate instructions to operate its workflow or architecture tooling were not executed: this is static assessment work outside the candidate, under the research repository's no-runtime rule.
See [candidate instructions](../repo/AGENTS.md) and [manifesto](../repo/MANIFESTO.md).

## Requirement verdicts

The verdicts describe fit to the baseline, not product reliability scores.
A useful file-based planning feature can receive Similar while the stronger organizational execution requirement remains unmet.

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Workspace roots and configuration separate repositories. A task's configured `project` field also labels monorepo components. It is not an organizational project registry with independent access, ownership and service authority. [Model](../repo/src/types/index.ts), lines 1–118; [MCP root](../repo/src/commands/mcp.ts), lines 1–85. |
| T02 | Similar | Markdown records retain stable IDs, outcomes, metadata, plans and summaries. Creation checks occupied identities across configured sources. Permanent deletion can release an ID, so identity is not an irreversible historical key. [Model](../repo/src/types/index.ts), lines 1–118; [allocation](../repo/src/core/backlog.ts), lines 1978–2095; [deletion](../repo/src/core/backlog.ts), lines 3866–3926. |
| T03 | Similar | Parent resolution and hierarchical IDs support decomposition, while dependencies and references link related work. There is no separate typed follow-up or delegation contract. [Parent creation](../repo/src/core/backlog.ts), lines 2360–2377; [model](../repo/src/types/index.ts), lines 1–118. |
| T04 | Similar | Shared readiness resolves the full corpus, fails closed for missing or ambiguous dependencies, and uses the final configured status as completion. Proposed edges reject reachable cycles. These are advisory reads and per-edit checks, not an atomic start gate or globally serialized graph constraint. [Readiness](../repo/src/utils/readiness.ts); [validation](../repo/src/utils/task-builders.ts), lines 63–170. |
| T05 | Absent | Assignee and reporter strings do not identify an authenticated agent separately from a session or execution attempt. No such entities appear in the task model or task operation catalogue. [Model](../repo/src/types/index.ts), lines 1–118; [catalogue](../repo/src/mcp/tools/tasks/index.ts), lines 1–110. |
| T06 | Similar | CLI-oriented Core methods, validated MCP task tools and HTTP endpoints support structured agent access. Mutation errors are surfaced, including HTTP 409 for edit contention. There is no durable execution-operation or claim protocol. [MCP tools](../repo/src/mcp/tools/tasks/index.ts); [edit response](../repo/src/server/index.ts), lines 1200–1237. |
| T07 | Absent | Edit locks serialize cooperating writers for a short mutation, but assignees can be replaced without an owner condition. No exclusive work reservation survives the edit. Board snapshots also have a different locking boundary. [Assignees](../repo/src/core/backlog.ts), lines 2540–2575; [patch lock](../repo/src/core/backlog.ts), lines 3053–3097; [bulk writes](../repo/src/core/backlog.ts), lines 3386–3410. |
| T08 | Resembles | Status columns, priority, ordinal ordering, ready filters and assignee filters help a leader choose work. They do not enforce worker capacity, WIP limits, fairness or dispatch. [Read projection](../repo/src/core/task-detail.ts), lines 72–138; [board movement](../repo/src/core/backlog.ts), lines 3505–3579; [board controls](../repo/src/web/components/BoardPage.tsx), lines 1–130. |
| T09 | Resembles | Parents and subtasks record decomposition and parallel work. Creation resolves a real local parent. No supervisor launches children, waits for their results or prevents parent completion while children remain unfinished. [Parent resolution](../repo/src/core/backlog.ts), lines 2360–2377; [status edit](../repo/src/core/backlog.ts), lines 2480–2520. |
| T10 | Similar | References, documentation, modified-file paths, plans and repository-local documents support context. Git can version files. These fields do not pin an immutable execution input or verify that an artifact still matches its recorded revision. [Task model](../repo/src/types/index.ts), lines 1–118; [search](../repo/src/core/search-service.ts), lines 1–115. |
| T11 | Similar | Notes, comments and final summaries preserve progress and handoff content in the task. They are editable record content, without acknowledged transfer of ownership or an immutable result tied to an attempt. [Model](../repo/src/types/index.ts), lines 1–118; [MCP edit surface](../repo/src/mcp/tools/tasks/index.ts), lines 56–69. |
| T12 | Resembles | Filesystem-derived updates notify browser clients; a health connection triggers full reload after reconnect. There is no durable agent inbox, recipient acknowledgement or replayable communication log. The data subscription itself has no reconnect loop in the inspected effect. [Data subscription](../repo/src/web/App.tsx), lines 803–849; [reconnect refresh](../repo/src/web/App.tsx), lines 470–482; [health hook](../repo/src/web/hooks/useHealthCheck.tsx). |
| T13 | Resembles | Readiness explains unfinished and unresolved predecessors; comments and configurable statuses can record questions or blockers. There is no structured escalation recipient, decision request, timeout or manager response lifecycle. [Blocker projection](../repo/src/utils/readiness.ts); [model](../repo/src/types/index.ts), lines 1–118. |
| T14 | Absent | `proper-lockfile` stale handling concerns abandoned edit locks. It is not an execution heartbeat or stale-worker detector. Task ownership has no expiry or lease renewal. [Lock implementation](../repo/src/file-system/operations.ts), lines 700–881; [model](../repo/src/types/index.ts), lines 1–118. |
| T15 | Absent | No worker generation, attempt token or expected task revision is required to mutate progress or completion. An old agent with workspace access can write again. Exclusive file creation prevents one filename collision, not duplicate logical requests after a retry. [Writes](../repo/src/file-system/operations.ts), lines 909–997; [patch entry](../repo/src/core/backlog.ts), lines 3053–3097. |
| T16 | Resembles | Durable files, archive/restore and explicit moved-but-not-committed errors aid manual recovery. There is no running-worker cancellation, resumable attempt or failure scheduler. Several filesystem changes and the Git commit remain separate steps. [Archive](../repo/src/core/backlog.ts), lines 3813–3855; [delete/restore](../repo/src/core/backlog.ts), lines 3866–3948. |
| T17 | Resembles | Git branches and sibling worktrees contribute visibility and occupied IDs. The local create lock uses Git's common directory. Task edits use each worktree's own lock directory; independent clones do not share a claim authority. [Create/task locks](../repo/src/file-system/operations.ts), lines 700–760; [worktree scan](../repo/src/core/backlog.ts), lines 1978–2095; [branch reader](../repo/src/core/cross-branch-tasks.ts), lines 1–100. |
| T18 | Resembles | Reporter, comment author, timestamps and optional Git commits provide useful history. Local strings and Git identity do not authenticate an individual agent, and uncommitted edits have no append-only audit stream. [Model](../repo/src/types/index.ts), lines 1–118; [write/commit order](../repo/src/core/backlog.ts), lines 2413–2443. |
| T19 | Similar | Browser board, milestones, task detail, fuzzy search, filters and a terminal interface provide broad inspection. Modal code handles keyboard trapping, Escape and focus restoration. No live interaction, screen-reader or small-screen acceptance test was performed. [Board](../repo/src/web/components/BoardPage.tsx), lines 1–130; [search](../repo/src/core/search-service.ts), lines 1–115; [modal](../repo/src/web/components/Modal.tsx), lines 1–145. |
| T20 | Similar | Drafts, priorities, types, milestones, dates and ordinal board ordering support backlog planning. Milestone lanes and filters are explicit. No capacity-aware iteration or autonomous dispatch policy appears in the reviewed model and movement paths. [Model](../repo/src/types/index.ts), lines 1–118; [board controls](../repo/src/web/components/BoardPage.tsx), lines 1–130; [move endpoint](../repo/src/server/index.ts), lines 1870–1908. |
| T21 | Resembles | Acceptance criteria and Definition of Done are structured checklists. A status edit or board move does not require their completion, a qualified reviewer, a delivered revision or a result-bound approval. [Checklist validation/status edit](../repo/src/core/backlog.ts), lines 2445–2520; [board status write](../repo/src/core/backlog.ts), lines 3505–3579. |
| T22 | Resembles | Workspace selection, filesystem access, loopback binding and read-only treatment of cross-branch cards establish local boundaries. There is no authenticated per-agent role or project permission system in these paths. Configured status callbacks run with the process environment and local shell authority. [Server](../repo/src/server/index.ts), lines 391–438; [cross-branch write filter](../repo/src/core/backlog.ts), lines 3778–3792; [callback](../repo/src/utils/status-callback.ts). |
| T23 | Similar | Configurable labels, types, projects, statuses and DoD defaults plus post-status shell callbacks support adaptation. There is no role schema, policy workflow or transactional plugin gate. Callback failure does not undo the saved transition. [Create configuration](../repo/src/core/backlog.ts), lines 2202–2295; [callback dispatch](../repo/src/core/backlog.ts), lines 3344–3374. |
| T24 | Similar | Plain files and optional Git avoid a mandatory database service. npm distributes platform-specific binaries through a Node launcher; source development uses Bun. The launcher includes architecture diagnostics and signal forwarding. Installation and platform behavior were not exercised. [Metadata](../repo/package.json), lines 1–75; [launcher](../repo/scripts/cli.cjs), lines 1–125. |

## Lifecycle and alternate mutation paths

### Create and decompose

Creation validates title, status, priority, type, project, dates and structured sections.
It applies default assignees and DoD items, resolves an optional parent and acquires the allocator lock before generating the new ID and validating dependencies.
The occupied-ID scan includes active and archived records, filename-reserved IDs and sibling worktree files; configured branch scanning adds further visibility.
This is more deliberate than selecting the next number from only the current active folder.
See [creation](../repo/src/core/backlog.ts), lines 2202–2379, and [allocation](../repo/src/core/backlog.ts), lines 1978–2095.

The allocator lock uses Git's common directory where available.
This lets sibling worktrees in the same local repository serialize creation.
An environment option can disable that lock.
This mechanism does not synchronize independent remote clones or reserve work execution.
A selected test pauses one worktree at save, starts a second create and asserts only one save has entered until release, followed by distinct IDs.
That test source was read; it was not run.
See [lock target](../repo/src/file-system/operations.ts), lines 700–737, and [worktree test](../repo/src/test/worktree-task-id-allocation.test.ts), lines 124–163.

Creation and optional Git finalization are separate stages.
Its failure path avoids deleting a file or staged entry it no longer owns and reports when manual Git review is required.
This is useful defensive recovery, but it does not give creation a durable idempotency key.
After an uncertain response, the agent must inspect existing records before creating the same logical work again.
See [create rollback](../repo/src/core/backlog.ts), lines 2295–2360.

### Select and assign

Readiness is derived from a shared corpus rather than from only the displayed rows.
A list filtered to one assignee still sees dependencies hidden by that filter.
Missing and ambiguous identities fail closed, with a separate explanation for unresolved dependencies.
Archived dependencies count as satisfied only if their status is terminal.
The terminal status is the last configured status, so a workflow configuration change can change readiness without editing tasks.
See [corpus and projections](../repo/src/core/task-detail.ts), lines 1–138, [readiness](../repo/src/utils/readiness.ts) and [terminal rule](../repo/src/utils/terminal-status.ts).

A ready task can be assigned by replacing its assignee list and changing status.
Neither operation checks an authenticated current owner or issues a reservation token.
Two agents can therefore agree on the same readiness view and both begin work, even when their metadata edits serialize correctly.
The execution race lies outside the file-lock mechanism.
See [assignment update](../repo/src/core/backlog.ts), lines 2540–2575, and [patch entry](../repo/src/core/backlog.ts), lines 3053–3097.

### Progress, review and completion

Agents can edit plans, notes, checklists and summaries through shared Core paths.
The MCP edit handler delegates to `editTaskOrDraft`; the HTTP update path delegates to the corresponding Core update method.
Normal task patches acquire a per-task lock, reload the current record inside it and apply the requested changes before saving.
This protects cooperating incremental editors from applying a patch to an old pre-lock copy.
See [MCP handler](../repo/src/mcp/tools/tasks/handlers.ts), lines 492–507, [HTTP update](../repo/src/server/index.ts), lines 1200–1237, and [patch implementation](../repo/src/core/backlog.ts), lines 3053–3097.

Completing work is still an ordinary canonical status change.
Checklist syntax checks protect structured content; they do not require every item to be checked before status changes.
The status branch does not inspect dependency readiness, child completion or review evidence.
The browser reorder path also directly constructs a task with its target status.
A team's completion instructions can require more, but those instructions are not application-enforced acceptance.
See [status edit](../repo/src/core/backlog.ts), lines 2445–2520, and [board write](../repo/src/core/backlog.ts), lines 3505–3579.

### Archive, delete and recover

Archive moves a task off the board while retaining identity, status and links.
Restore returns that file without rewriting its identity or status.
Neither action stops an agent process that may still be working.
Permanent deletion requires an archived task and refuses a parent with remaining direct children, including drafts.
It cleans related references before unlinking the archived file.
See [archive](../repo/src/core/backlog.ts), lines 3813–3855, and [delete/restore](../repo/src/core/backlog.ts), lines 3866–3948.

The cleanup path repeatedly widens its locked set and rescans under the allocator lock.
This reduces stale-snapshot damage during deletion.
The implementation also documents a remaining boundary: a relationship edit outside that set can add a reference after the final scan.
That reference can survive as unknown and later refer to a reused number.
This is especially relevant when interpreting IDs as permanent organizational history.
See [cleanup locking](../repo/src/core/backlog.ts), lines 1254–1317.

Deletion records whether unlink already happened and distinguishes a later commit failure from a refusal before deletion.
However, reference rewrites, unlink and Git commit are not one database transaction.
An interruption between them needs file and Git inspection.
Durable Markdown makes the state inspectable; it does not supply a resumable execution state machine.
See [delete ordering](../repo/src/core/backlog.ts), lines 3866–3926.

## Concurrency and consistency findings

### Mutation locks and execution ownership have different lifetimes

The file layer uses `proper-lockfile`, sorted multi-record acquisition and short fail-fast task locks.
Create locks have retry and stale-lock handling.
These mechanisms protect cooperating local edits.
They do not represent an agent's exclusive right to execute or renew ownership, and direct file edits need not honor them.
The same task in separate worktrees has separate per-task lock paths, even though creation shares an allocator lock.
See [lock implementation](../repo/src/file-system/operations.ts), lines 700–881.

### Public board writes can use snapshots taken before their locks

Board resolution refreshes the content store and selects task objects before acquiring bulk write locks.
Reorder and multi-move construct whole-task snapshots from those objects.
`updateTasksBulk` then locks the selected tasks and passes those snapshots to a sequential writer; it does not reload and merge only status, ordinal and milestone under the locks.
`updateTask` reads a stored task for timestamp and status-callback purposes, but saves the supplied task object.
See [resolution and bulk writer](../repo/src/core/backlog.ts), lines 3386–3462, [reorder](../repo/src/core/backlog.ts), lines 3505–3579, and [save path](../repo/src/core/backlog.ts), lines 2413–2443.

The public reorder and move endpoints call these methods directly.
If another edit completes between snapshot preparation and lock acquisition, a later board write can replace that edit with older fields.
This is a source-derived interleaving, not a reproduced race.
Fail-fast locks prevent overlap while held; they do not detect that a prepared object became stale before acquisition.
See [public callers](../repo/src/server/index.ts), lines 1826–1908.

Acquiring every lock before a bulk operation avoids writing when lock acquisition itself fails.
Once writes begin, however, they occur one by one.
A later filesystem or callback failure can leave earlier files changed without the final Git commit.
Batching store notifications does not make the disk sequence transactional.
See [bulk sequence](../repo/src/core/backlog.ts), lines 3386–3410.

### Cycle checks do not serialize the whole dependency graph

Dependency validation loads local tasks, drafts and archives, rejects missing or self references and checks the proposed graph for a path back to the edited task.
This correctly rejects a cycle visible to that edit's snapshot.
The edit holds only its task lock, rather than a common graph lock spanning validation and write.
As a result, concurrent edits adding A-to-B and B-to-A edges can each validate against the old graph before either writes.
That is an inferred concurrency gap, not a test result.
See [validator](../repo/src/utils/task-builders.ts), lines 63–170, and [per-task scope](../repo/src/core/backlog.ts), lines 3053–3097.

The read graph and readiness index handle ambiguous and unresolved identities explicitly.
That protects inspection from falsely declaring missing work satisfied, but it does not prevent every concurrent graph mutation.
See [record index](../repo/src/utils/task-record-index.ts), lines 1–92, and [dependency graph](../repo/src/utils/dependency-graph.ts), lines 1–165.

### A saved Markdown rewrite is not a crash-atomic transaction

New files use exclusive `writeFile` creation.
Existing records are rewritten with `Bun.write` after any path rename; this path does not stage a temporary complete file and atomically replace the old contents.
The reviewed code therefore does not establish crash-atomic replacement or transactional consistency across files and Git.
An editor lock alone cannot establish those properties.
See [save/write implementation](../repo/src/file-system/operations.ts), lines 909–997.

### Notifications recover a snapshot, but not a durable stream

The application subscribes to task, milestone and configuration change messages.
A separate health WebSocket reconnects after a delay, and a restored connection triggers a full data load.
This helps recover the current snapshot after a disconnection.
The inspected data-message effect has no reconnect timer of its own, while the health connection does not consume task messages.
It therefore does not establish reliable resubscription of incremental data events after a broken socket.
A future manual refresh or reload may be needed for subsequent changes.
See [health hook](../repo/src/web/hooks/useHealthCheck.tsx), [restored connection](../repo/src/web/App.tsx), lines 470–482, and [data effect](../repo/src/web/App.tsx), lines 803–849.

There are no persistent recipient cursors or task-event acknowledgement records in these paths.
Browser freshness is separate from a dependable agent handoff or management notification channel.

## Design quality, usability and operation

Shared Core methods and derived task-detail projections reduce semantic drift between interfaces.
Canonical identity, ambiguous-record refusals, archived dependency handling, sorted locks and explicit post-mutation errors show attention to difficult repository workflows.
The main architectural cost is a large Core combining planning rules, Git staging, file transactions, archive transitions and publication coordination.
The board snapshot path demonstrates how a second mutation abstraction can weaken invariants provided by the canonical patch path.

Human inspection is broad for a local tool.
The board preserves filters in URL parameters and milestone lane preference in local storage.
Search covers tasks, documents and decisions.
The shared modal implements focus capture, Tab wrapping, Escape handling, body scroll control and focus restoration.
These are concrete usability mechanisms, not proof of a complete accessibility review.
No candidate UI was launched or rendered during this study.
See [board controls](../repo/src/web/components/BoardPage.tsx), lines 1–130, [search](../repo/src/core/search-service.ts), lines 1–115, and [modal](../repo/src/web/components/Modal.tsx), lines 1–145.

The operating model is lightweight: files and optionally Git replace a required hosted database.
The npm package launches a separately distributed binary for the host architecture.
The launcher diagnoses missing or incompatible binaries and forwards termination signals on non-Windows systems.
The source build and tests use Bun.
Published artifact availability and OS compatibility were not checked by running an install.
See [package](../repo/package.json), lines 1–75, and [launcher](../repo/scripts/cli.cjs), lines 1–125.

Status callbacks are an integration mechanism with full local process authority.
They run `sh -c` in the project directory with inherited environment and task fields passed as environment variables.
They are post-save effects, not acceptance hooks; failures are logged without reversing the status change.
The callback path has no explicit timeout in the inspected executor.
A long-running command can delay the caller, and when called within the patch path it also extends that edit's lock span.
Treating task/configuration content as trusted executable configuration is part of this operating boundary.
See [executor](../repo/src/utils/status-callback.ts), lines 1–69, [dispatch](../repo/src/core/backlog.ts), lines 3344–3374, and [update ordering](../repo/src/core/backlog.ts), lines 2413–2443.

## Test-source evidence and implementation limits

The inspected atomic-edit tests assert that concurrent successful label patches survive, while contending operations return actionable lock errors.
Separate CLI processes are exercised in the test source, and the HTTP edit test expects 409 while another process holds the task lock.
These assertions target the canonical patch path, not execution ownership or the pre-lock board snapshot interleaving.
See [edit tests](../repo/src/test/atomic-task-edit.test.ts), lines 1–130 and 221–356.

Atomic-create tests pause saves, overlap creators and assert distinct IDs.
The worktree test additionally verifies use of one common creation lock across sibling worktrees.
Readiness tests explicitly assert blocked, unresolved, ambiguous and archived dependency behavior, including terminal-status configuration changes.
See [creation tests](../repo/src/test/atomic-task-create.test.ts), lines 1–185, [worktree test](../repo/src/test/worktree-task-id-allocation.test.ts), lines 124–163, and [readiness tests](../repo/src/test/readiness.test.tsx), lines 1–180.

Sequential dependency tests assert rejection of two-node and longer cycles without writing the rejected edge.
The reorder publication test asserts returned changed ordinals, one browser notification and refusal of an ambiguous target without file changes.
It does not test a second writer between snapshot preparation and bulk lock acquisition.
See [cycle tests](../repo/src/test/dependency.test.ts), lines 448–490, and [reorder test](../repo/src/test/server-reorder-publication.test.ts), lines 1–126.

These are meaningful assertion bodies, but none was executed here.
Their presence does not certify the pinned package, distributed binaries, browser session, crash durability or every concurrency condition.
The full checkout is preserved for further review; unrelated feature implementations and the complete watcher reconciliation machinery were not audited line by line.

## Adoption gaps and useful components

Backlog.md can provide the repository-local planning and reporting layer for this use case.
Its useful components are the Markdown task schema, shared detail/readiness projection, dependency diagnostics, local creation locking and human board/search interfaces.
They reduce the work needed to make planned and completed activity inspectable.

A system built on it still needs a durable agent registry and separate execution-attempt model; authenticated, conditional claims; capacity and dispatch policy; heartbeat expiry; stale-attempt rejection; supervised child completion; and result-bound review.
Shared hosts need one authoritative write service rather than an assumption that Git copies coordinate live work.
The service should also serialize graph invariants and apply board field patches under a fresh read or expected revision.

Recovery should distinguish task-record edits, running worker state and external side effects.
It needs durable operation IDs, an event or handoff channel with replay, and a defined response to partial multi-file changes.
For this baseline, Backlog.md is a capable local work record and interface layer, with a substantial coordination authority still to build above it.
