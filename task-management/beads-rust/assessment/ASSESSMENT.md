# beads_rust: local issue authority with guarded handoff and configurable workflow

Source: https://github.com/Dicklesworthstone/beads_rust

Reviewed commit: `117f81de0d5dae007d972a9ff7f1d73c392d8822`.
Assessment date: November 9, 2026.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Evidence ledger: [review.json](review.json).

## Fit decision

beads_rust is a substantial task-record component for agents that cooperate through one local workspace. It has persistent issues, hierarchy, dependency-aware selection, conditional claims, explicit stale-owner handoff, workflow gates, capacity admission and machine-readable interfaces. It can retain the work graph after a conversation ends. Its scheduler recommends work; it does not launch or supervise workers.

The important boundary is authority. A guarded claim protects one assignment operation. Ordinary updates can still edit another actor's issue or replace its assignee. Actor names, reviewer provider names and harness attribution are supplied by callers. There is no required execution-attempt credential on later progress or completion. The system therefore suits a trusted local team with an external execution coordinator. It does not supply the baseline's complete organization, authenticated review authority or shared online ownership across separate Mac and Linux stores.

This revision also has a restricted license. [LICENSE](../repo/LICENSE), lines 1–73, contains an MIT grant with an OpenAI/Anthropic rider that restricts parties and activities. Describe it as source available with restrictions, rather than unqualified MIT open source. This is a recorded adoption constraint, separate from the technical findings.

## Review scope and evidence level

The full tracked checkout contains 4,288 files. This is a targeted static source review, not an every-line audit. It follows the issue model, command inventory, create/update/claim/reclaim paths, workflow and capacity transaction admission, close and epic callers, optional MCP writes, selected JSONL publication/import boundaries, local lock authority, inherited context, audit lookup and reopen. Selected test assertion bodies were read. No candidate executable, dependency installation, build or test suite was run.

The largest modules require care: `storage/sqlite.rs` has 47,264 lines, `sync/mod.rs` has 37,368 and `storage/schema.rs` has 11,597. The ledger records inspected ranges, not whole-file body coverage for those modules. The storage engine, full migration/repair system, every merge policy, operating-system lock primitive, installer and terminal rendering remain outside certification. Product documentation and instruction files describe intent; source bodies support the findings below.

## Architecture and data authority

The package builds the `br` command and a WAL recovery utility. [Cargo.toml](../repo/Cargo.toml), lines 1–145, identifies version 0.7.6, edition 2024, a declared Rust minimum of 1.89, the FrankenSQLite family and optional FastMCP dependency. [rust-toolchain.toml](../repo/rust-toolchain.toml) selects `nightly-2026-08-31`. The checkout's build configuration takes precedence over a generic stable-Rust assumption.

The executable owns startup and dispatch. The library's `run()` is a no-op placeholder, not the CLI implementation. See [lib.rs](../repo/src/lib.rs), lines 29–78. A tool embedding the crate must call the actual storage or command surfaces rather than assume `run()` processes work. The [command enum](../repo/src/cli/mod.rs), lines 748–1004, exposes task, graph, policy, diagnostics, synchronization, scheduler and optional stdio MCP operations. Its `Agents` command manages instruction files; that name does not establish a persistent agent roster.

[Issue](../repo/src/model/mod.rs), lines 462–678, holds stable IDs, descriptions, design, acceptance text, prerequisites, notes, owner, assignee, status, priority, effort, dates, source repository, inherited agent context and closure attribution. Dependencies, labels and comments are related records. Session data at close and self-reported agent metadata improve attribution. They are not an execution-attempt state machine. The schema's table inventory covers issues, relations, events, dirty/export metadata, close metadata, gate history and capacity state; it does not introduce authenticated accounts or worker process records. See [schema declarations](../repo/src/storage/schema.rs), with the declaration inventory distinguished in the ledger from the small schema body read.

One FrankenSQLite database is the immediate mutation authority. JSONL is the repository exchange and recovery representation. These are separate persistence steps. Normal writes use database-family locks and transactions; synchronization publishes a file afterward. The instruction document's recommended Agent Mail and beads-viewer workflow adds other products, not hidden native messaging or a browser board.

## Requirement assessment

Verdicts describe fit to this baseline. They are not reliability scores. The sections after the table explain the implementation boundaries and evidence.

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Repository workspaces, source fields and prefix-to-path routing separate task stores. There is no complete leadership/project registry or portfolio authority. |
| T02 | Similar | Rich durable issue records, stable IDs, comments and close outcomes. The result remains task data, with no distinct accepted execution result object. |
| T03 | Similar | Parent-child edges, hierarchical IDs, epics and linked issues support decomposition. Runtime parent/child delegation relationships remain external. |
| T04 | Similar | Ready queries, dependency blockers and transactional edge-cycle checks exist. Start and close deliberately use different hierarchy rollups; direct storage updates do not universally enforce CLI start checks. |
| T05 | Resembles | Owner/assignee, actor, session and harness fields distinguish some attribution. There is no native agent/session/attempt registry with enforced attempt ownership. |
| T06 | Similar | CLI JSON/robot/TOON interfaces, schemas and optional seven-tool stdio MCP surface. Some contracts and output envelopes require version pinning. |
| T07 | Similar | Conditional claims and guarded reclaim compare ownership state in a write transaction. Ordinary assignment edits and MCP field updates do not require those claim guards. |
| T08 | Similar | Configurable status/group/scoped capacity admission and atomic batch checks; ranked scheduler output. It does not dispatch workers or prove their actual process capacity. |
| T09 | Similar | Shared child records, epic eligibility and child/blocker close checks support coordination. No child worker launch, join, cancellation or parent execution supervision. |
| T10 | Similar | Design/notes/references and opt-in inherited ancestor context. References are supplied data, not immutable artifact storage or complete content-bound review evidence. |
| T11 | Similar | Durable notes, comments, transition comments, audit and closure reason. A structured handoff/result protocol must be imposed by the coordinator. |
| T12 | Resembles | Shared comments and audit queries permit polling. No native recipient inbox, delivery acknowledgement or bounded loss-recoverable event cursor was found in the inspected model and interfaces. |
| T13 | Similar | Blocked/question records, dependency-only provenance and explicit stale-owner advice. Human escalation and answer routing are conventions and external communication. |
| T14 | Similar | Stale-work classification and guarded handoff use issue time plus supplied agent/reservation snapshots. These are not expiring task leases or a native heartbeat service. |
| T15 | Similar | Optional updated-at preconditions, claim tuple checks, status-scoped gate history and replay refusal on old reclaim evidence. No mandatory stale-worker token or general request-idempotency ledger. |
| T16 | Similar | Reopen, explicit requeue/edit, retained task history, import/export and recovery controls. Task-state repair does not resume or cancel an agent process or undo its external effects. |
| T17 | Resembles | JSONL exchange and routed local databases connect work across repositories. Separate cloned stores can independently assign the same task before exchanging changes. |
| T18 | Similar | Transactional mutation events and durable close attribution, plus workflow gate history. Some policy metadata is best effort after close; actor strings are not verified identities. |
| T19 | Similar | Terminal list/detail/search/graph/stats, ready selection, coordination diagnosis and structured views. No native browser portfolio was found in the inspected command/module inventory. |
| T20 | Similar | Priorities, labels, epics, estimates, due/defer dates and custom workflows support backlog management. Native sprint and milestone entities are absent from the inspected issue/schema model. |
| T21 | Similar | Opt-in checklist, close-reason, self-close and transition gates; review-cycle scoping. Providers are caller asserted and content edits do not necessarily invalidate a status-revision pass. |
| T22 | Resembles | Local file authority checks, explicit force/bypass surfaces and policy audit. No authenticated per-agent/project roles; local writers can change policy and actor labels. |
| T23 | Similar | Custom statuses/types, transition rules, required fields, typed references, capacity scopes and structured integration. Role authorization and execution adapters still need external implementation. |
| T24 | Similar | Single CLI, portable exchange, diagnostics and optional MCP keep deployment compact. Engine-specific recovery and lock/namespace machinery add material operational complexity. Runtime portability was not tested. |

## Work lifecycle and alternate mutations

### Create, decompose and select

The CLI prepares the issue and populates requested relations before calling storage. The storage create body validates the issue, checks ID/external-reference collisions, validates initial workflow admission and capacity, and inserts the issue, labels, dependencies, comments and events in the mutation transaction. Dependency targets and cycles are checked before committing the new record. See [create preparation](../repo/src/cli/commands/create.rs), lines 612–669, and [storage create](../repo/src/storage/sqlite.rs), lines 7503–7738. Do not generalize this single-issue atomicity to every bulk-import or cross-project operation.

The edge writer also checks endpoints, parent rules, existing edges and cycle creation inside `mutate()`. It marks affected state dirty and defers blocked-cache repair. See [add dependency](../repo/src/storage/sqlite.rs), lines 13845–14002. Readiness can compute blocked state in memory when the cache is stale. That avoids declaring all stale-cache tasks ready or silently rewriting cache state during that query. See [ready query](../repo/src/storage/sqlite.rs), lines 11335–11406.

Starting and closing intentionally interpret hierarchy differently. A parent's open children can prevent closing the parent without preventing work on it. A propagated blocked-parent marker should not prevent an otherwise actionable child from starting. `get_start_blockers()` strips both rollup markers; `get_close_blockers()` retains open-child constraints while stripping the parent marker. See [blocker views](../repo/src/storage/sqlite.rs), lines 12100–12172. These distinctions are useful, but a consumer must use the appropriate operation rather than equate every blocked marker with a prerequisite.

The scheduler builds a ready candidate set, resolves external dependency statuses, scores candidates, preserves fallback order on ties and returns recommendations with evidence. It does not claim, spawn or monitor them. Its candidate cap is applied before ranking; a bounded recommendation is not necessarily the global best choice across all tasks. See [scheduler](../repo/src/cli/commands/scheduler.rs), lines 205–313. Cross-project [routing](../repo/src/config/routing.rs), lines 1–150, maps prefixes to local paths, not remote service credentials or a common distributed transaction.

### Claim and reassign

CLI `--claim` sets status to `in_progress`, assignee to the resolved actor and `expect_unassigned` to true. Ordinary `--assignee` edits leave that guard false. See [update construction](../repo/src/cli/commands/update.rs), lines 1914–2002. The command checks start blockers before mutation; `--force` bypasses that advisory start check, but not the claim's terminal/deferred-state rejection. See [start validation](../repo/src/cli/commands/update.rs), lines 1350–1403.

Inside storage, a claim rejects closed, tombstone and deferred work. It checks current ownership and then includes the observed assignee, status, deferral and updated-at tuple in its SQL update predicate. A zero-row conditional write returns a claim conflict. Same-actor claims are allowed unless exclusive mode is configured. They still use the ordinary update machinery; this is eligibility idempotence, not a guaranteed no-write or cached-response contract. See [claim eligibility and transfer](../repo/src/storage/sqlite.rs), lines 8270–8517, and [conditional SQL](../repo/src/storage/sqlite.rs), lines 8888–8950.

The ownership contract is narrower than the full mutation API. A non-claim edit can change another actor's task. MCP `update_issue` parses ordinary assignee/status fields and an optional `if_unchanged`; it does not manufacture the CLI claim predicate. Its start-blocker check does not turn an assignment replacement into an exclusive claim. See [MCP field parser](../repo/src/mcp/tools.rs), lines 850–984, and [MCP update body](../repo/src/mcp/tools.rs), lines 2150–2267. Serializing two unconditional replacements still permits the later replacement.

The storage claim eligibility body checks state and assignment, not the CLI's start-blocker query. Normal CLI and MCP writers retain workspace authority across their preparation and mutation, which reduces races between cooperating commands. Direct library writers must not assume that calling `update_issue()` imports every CLI guard. This review does not certify behavior when other tools bypass the shared lock protocol.

### Progress, context and escalation

Scalar fields and labels can update in one storage batch. `expect_updated_at` is checked in that transaction when supplied. It is optional, so an unconditional stale whole-field rewrite can still replace newer text. The timestamp identifies issue state, not a worker incarnation. The issue update type exposes both guarded and unguarded operations. See [IssueUpdate](../repo/src/storage/sqlite.rs), lines 20543–20630, and [update guards](../repo/src/storage/sqlite.rs), lines 8428–8454.

MCP field/label changes precede a separately persisted optional comment. A comment failure can therefore follow a committed field update. The MCP wrapper detects changed dirty metadata, attempts export even after a late error and marks committed/unknown outcomes. It does not make the whole tool call a single transaction. See [MCP update](../repo/src/mcp/tools.rs), lines 2214–2267, and [mutation wrapper](../repo/src/mcp/mod.rs), lines 486–650.

Inherited context is opt-in. The inspected collector emits the immediate parent and selected root ancestor's nonempty `agent_context`, deduplicated. It does not emit every intermediate layer or pin a content revision for later acceptance. See [inheritance](../repo/src/inheritance.rs), lines 1–246. This helps cold-start task context, but does not prove an agent read or followed it.

Dependency-only blocked status can have explicit provenance. Storage rejects invalid combinations, ownership overrides, pinned/ephemeral/template exclusions and blocker-free attestations before recording the proof. See [dependency block proof](../repo/src/storage/dependency_repair.rs), lines 750–845. This is more precise than treating every blocked task as waiting on a graph edge. Human questions still need someone to monitor and answer them; no native recipient delivery service appears in the inspected domain and operation inventory.

### Review and finish

Policy defaults are permissive. Close policy can require a reason, satisfied acceptance checklist, different closer from the last in-progress actor, attribution or typed references. Workflow policy adds permitted statuses/transitions, prospective required fields and per-transition gates. See [policy model](../repo/src/close_policy.rs), lines 51–115 and 157–350.

Storage rechecks workflow transitions, required fields and scoped gate results before the atomic batch. Capacity is evaluated against the batch's prospective state. This supports a drain/admit swap without incorrectly rejecting the admission solely because it appears first. See [workflow preflight](../repo/src/storage/sqlite.rs), lines 7857–8050, and [batch admission](../repo/src/storage/sqlite.rs), lines 8053–8235. This is shared task-state policy, not a worker process scheduler.

Gate history is scoped to issue, from-status, target-status and the latest status-change event ID. A return to review after rework requires fresh reports. But changing description or acceptance text while remaining in the same status does not itself change that status revision. A prior pass can therefore remain eligible after content changes; this is a source-derived limitation, not a reproduced exploit. See [gate recording and status revision](../repo/src/storage/sqlite.rs), lines 4803–4952.

Minimum reviewers counts distinct lowercased provider strings with recognized reviewer prefixes. Named gates accept reported passes. There is no identity proof in that count, and a syntactically typed commit or PR reference does not verify the referenced artifact. See [gate satisfaction](../repo/src/close_policy.rs), lines 1478–1507, and [close evaluation/reference parsing](../repo/src/close_policy.rs), lines 2532–2658. Add authenticated evidence producers and content/version binding before using these gates as organizational approval authority.

The CLI refuses `update --status closed` and routes completion through `close`. MCP similarly redirects closing to its close tool. CLI close checks open children and blockers, evaluates close policy, prepares updates and commits a batch. `--force` waives graph/child checks; policy bypass is a separate flag with a reason, and `allow_bypass: false` can reject it. See [terminal-status refusal](../repo/src/cli/commands/update.rs), lines 1865–1895, and [close path](../repo/src/cli/commands/close.rs), lines 974–1405.

These are caller-layer close controls. The generic public storage update still accepts `Status::Closed` subject to its shared workflow checks; it does not call the CLI-specific close-reason/self-close/blocker evaluator. MCP close does call that evaluator and its blocker checks before updating. See [MCP close](../repo/src/mcp/tools.rs), lines 2533–2711. An embedding must choose the checked completion interface or explicitly implement the missing policy.

Close attribution is stored with the close event. Additional policy metadata is enriched afterward; failure logs a warning and does not undo the close. Epic close-eligible applies policy and then shares atomic storage mutation for the selected epics. See [epic close](../repo/src/cli/commands/epic.rs), lines 121–218 and 369–400. No inspected path waits for an external child process or verifies its output merely because a child issue is closed.

## Concurrency, failure and recovery

Database mutation uses `BEGIN IMMEDIATE`, bounded retries with jitter and rollback before replaying transient body/commit errors. Rollback failure stops retry with transaction state unknown. Authority is verified before the transaction and after commit. A post-commit authority error is not evidence that data rolled back. See [transaction wrapper](../repo/src/storage/sqlite.rs), lines 4002–4148. The mutation layer groups issue writes, events and dirty markers, then can perform cache maintenance after the primary commit. See [mutate](../repo/src/storage/sqlite.rs), lines 7245–7502.

Local write authority combines workspace lock, canonical database-family lock and database inode identity. It rejects routing or inode changes observed while authority is held. MCP reacquires this authority per mutation, refuses incomplete merge state, acquires the sync lock before writing and reloads policy under that authority. See [lock acquisition](../repo/src/sync/mod.rs), lines 1830–1915, [identity checks](../repo/src/sync/mod.rs), lines 649–715, and the MCP wrapper. These are valuable filesystem defenses. They neither authenticate an actor nor coordinate two independently cloned databases over a network.

Stale work uses evidence-based classification rather than task TTL expiry. Swarm thresholds are two quiet hours for stale-candidate and eight for likely abandonment. Human/unknown thresholds are 24 and 72 elapsed hours; the source constants do not implement a business-day calendar. Activity uses the newer issue update or supplied owner heartbeat. Active reservations, absent snapshots and invalid snapshots alter the advice. See [coordination assessment](../repo/src/coordination.rs), lines 15–45 and 482–602.

Reclaim requires an explicit new actor, observed previous assignee, issue updated-at and snapshot evidence. It reloads snapshots, examines comments, rechecks eligibility and uses the normal update route. Inside the transaction it validates the old tuple and policy evidence, inserts the audit comment and changes ownership together. Replaying the old handoff conflicts. See [reclaim command](../repo/src/cli/commands/coordination.rs), lines 36–208, and storage claim ranges above. Empty snapshot files are rejected; explicit `[]` can represent a verified empty export. See [snapshot loading](../repo/src/cli/commands/coordination.rs), lines 593–626.

The external evidence is still a file snapshot. Reloading it is not an atomic read of Agent Mail's current authority, nor proof that a worker cannot start immediately afterward. Returning old workers can make ordinary unguarded edits. Reclaim protects the handoff itself; it does not revoke process capabilities or fence every later write.

JSONL export captures previous-source authority, rejects stale replacement evidence, guards against losing existing IDs, stages output, flushes and syncs it, verifies staged content and calls conditional publication. See [export](../repo/src/sync/mod.rs), lines 11763–12165. Import scans conflicts, validates records, plans collisions and applies streamed actions plus witness metadata in a database transaction; foreign-key restoration/verification follows. See [import boundary](../repo/src/sync/mod.rs), lines 17004–17187. This review did not certify every merge/collision decision or publication primitive.

The database write and JSONL publication are not one atomic commit. CLI export failure can be a warning after a successful mutation. MCP returns structured committed/sync-pending information, retains request output and says not to retry the mutation. The test source explicitly retains a committed dirty issue when conflict-marked JSONL prevents export. A coordinator must repair and flush, then publish repository changes. It must not blindly repeat create/comment calls after a transport error.

Reopen clears close/deferral fields and uses the shared atomic update path. See [reopen](../repo/src/cli/commands/reopen.rs), lines 197–315. It repairs record state rather than resuming a process. Similarly, deleting or deferring work does not stop a worker already performing external actions.

## Usability, operating costs and implementation quality

The terminal and machine interfaces are well aligned with repository agents: list/detail/search, concise selection, schema discovery, explainable recommendation and actionable conflicts. Optional MCP avoids shell parsing, but requires a build with that feature and uses stdio, not a LAN endpoint. A central host wrapper or separate service is still needed for remote workers to share one authoritative store.

Audit queries expose durable facts but are not a bounded delivery queue. `get_all_events()` fetches all rows, then sorts and truncates in Rust. The CLI since-query asks for all events and filters inclusively by time. This can support external deduplicating polling, but scales with accumulated history and has no per-recipient acknowledgement or truncation recovery contract in that path. See [event lookup](../repo/src/storage/events.rs), lines 457–481, and [audit since](../repo/src/cli/commands/audit.rs), lines 241–291.

The code contains real policy and recovery depth, not just prompts describing a workflow. Shared transaction admission is a strong design choice. The main maintenance concern is how many guarantees remain distributed between startup, commands, storage, MCP, export and recovery. The large storage/sync modules and engine-specific workarounds increase the cost of checking equivalent behavior across interfaces.

[ENGINE_OPERATING_MODEL.md](../repo/docs/reliability/ENGINE_OPERATING_MODEL.md), lines 1–130, records historical engine incidents and containment. Its opening version description differs from the current Cargo pins; use the manifest for the pinned dependency family, and treat historical test receipts as their recorded evidence. The inspected `admit_checkpoint()` and full-checkpoint caller require sole-opener admission when an opener lease exists and refuse a full checkpoint when peers are present. See [checkpoint admission](../repo/src/storage/sqlite.rs), lines 4452–4528. The engine itself was not audited or executed here, so neither universal corruption claims nor broad engine-safety guarantees follow from this review.

## Test-source review and remaining uncertainty

The following assertions were read, not run:

- [Claim test](../repo/tests/e2e_claim_atomic.rs), lines 305–356: one of two contenders succeeds, but the fixture serializes storage access with an explicit Rust mutex. This does not independently demonstrate unsynchronized multi-process engine safety. Lines 421–435 explicitly permit a non-claim edit by another actor.
- [Reclaim assertions](../repo/src/storage/sqlite.rs), lines 31669–31754: one audit and transfer, old-evidence replay refusal, rollback on later invalid field and recent-heartbeat rejection. These are selected in-memory storage cases.
- [Queued reclaim processes](../repo/tests/e2e_coordination.rs), lines 2167–2228: two child CLI processes wait behind workspace authority, then one wins and the loser appends no handoff audit. The selected body is stronger process-path coverage than the mutex claim fixture, but was not executed in this assessment.
- [Gate cycle assertions](../repo/src/storage/sqlite.rs), lines 26423–26538: returning through rework invalidates prior status-scoped passes, preserves history and rejects an old-scope report. It does not test all content-edit invalidation cases.
- [Capacity batch assertions](../repo/src/storage/sqlite.rs), lines 26883–26978: excess prospective occupancy rejects both tasks and field changes; a matching drain permits admission. This is policy atomicity coverage, not worker capacity measurement.
- [MCP export failure](../repo/src/mcp/mod.rs), lines 1607–1647: export refusal leaves the created task committed and dirty. The inspected assertions do not prove exactly-once request behavior.

Unverified areas include real terminal usability, cross-platform locks, host failure during publication, engine behavior under contention, complete migration/doctor/merge semantics, installer safety and integration with external agent runtime or mail services. Source completeness is not product acceptance.

## Adoption work and useful components

For the full baseline, add a shared authenticated authority or keep all mutations on one designated host. Introduce persistent agent and attempt identities, mandatory attempt fences for controlled writes, request-idempotency records and a reconciler for committed-but-unpublished outcomes. Make assignment, CLI, MCP and library completion use the same declared ownership and acceptance contract.

Add authenticated reviewers, artifact/content revisions, durable recipient communication and a coordinator that owns dispatch, process cancellation, child result integration and human decisions. Preserve the useful existing primitives: transactional graph edits, guarded ownership transfer, explicit dependency-block provenance, configurable workflow admission, capacity checks, inherited context and structured recovery outcomes. Confirm license suitability independently before adoption.
