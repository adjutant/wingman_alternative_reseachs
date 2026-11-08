# Gemba: an operator board and agent dispatcher over a separate work authority

Source: https://github.com/GembaCore/gemba-core

Reviewed commit: `64c266f889c6d6a579904c5e336676fa1c49b216`.
Assessment date: November 9, 2026.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Evidence ledger: [review.json](review.json).

## Fit decision

Gemba is a substantial candidate for the human control surface and dispatch layer of an agent organization. Its implementation combines a hierarchical task board, agent sessions, workspace provisioning, context injection, automatic allocation, persona consultations and human escalation. This is more than a task viewer or an instruction template. The repository carries an ordinary [MIT license](../repo/LICENSE).

The inspected native path does not provide the baseline's durable, exclusive task ownership across coordinators. Its inline claim is a process-local session-map check after a pane has been spawned. It does not atomically claim the tracker task. General task updates also omit expected-revision and execution-attempt conditions. These gaps matter when multiple agents, operators or server processes share the same backlog.

Use Gemba as a reference for an integrated operator experience and configurable agent launch. Treat the authoritative claim, attempt fencing, recovery and acceptance protocol as additional engineering work. Rich role declarations and capability manifests do not close these gaps. The definition of done is deliberately informational, and a native `bead-done` signal checks worktree cleanliness rather than verifying accepted results.

## Scope and evidence level

The full checkout has 1,752 tracked files. This review traces selected executable bodies for the Beads CLI and direct Dolt work adapters, native orchestration, dispatch wiring, task writes and cascades, persona application, escalation, authentication, nonce handling, event delivery and board mutations. Selected unit-test assertion bodies were inspected. No candidate application, dependency install, build or test was executed.

This is not an every-line or live usability audit. Gas Town and other orchestration adapters, the full specification import/export engine, every persona executor, all container and virtual-machine backends, migrations and all frontend screens are outside certification. Findings about native ownership do not automatically describe every external orchestrator. Conversely, external tracker guarantees are not credited to Gemba's alternate SQL writer without tracing that writer.

The source instructions were read as contributor guidance. Their commands to claim work, run gates and push changes were not executed in this preserved checkout. The assessment distinguishes prompt instructions, interface contracts, implementation and actual runtime evidence.

## Architecture and authority

[go.mod](../repo/go.mod), lines 1–32, sets Go 1.25.0 despite older version comments above the directive. The server uses Cobra, Chi, the MySQL driver for Dolt, the MCP Go SDK and telemetry libraries. [web/package.json](../repo/web/package.json) identifies React 18, React Query, TypeScript and Vite. The work system and execution system are separate adapters.

The [work item model](../repo/core/types.go), lines 1–175, has namespaced IDs, repositories, branches, owner, assignee, labels, relationships, evidence, acceptance text, sprint and dispatch metadata. The [work-plane contract](../repo/core/workplane.go), lines 598–706, exposes list/get/create/update, evidence, sprints, budgets and subscriptions. Its patch has no expected revision, current owner or attempt token.

The server registers either the Beads CLI adapter or the direct Dolt adapter. It separately wires native orchestration with the selected work plane, repository root, agent registry and worktree directory. See [serve registration](../repo/internal/cli/serve.go), lines 1144–1228 and 1433–1482. A single bound work plane is not the same as an independently selected database for every project shown in the UI. [Project switching](../repo/internal/server/projects.go), lines 76–150, explicitly separates the active project label from rebinding the work host.

The [native adapter](../repo/internal/adapter/native/orchestration.go), lines 20–105 and 132–257, keeps sessions, pane membership, nonces and escalation indices in memory. It lists agent types from configuration. Pull-style `ClaimNextReady` and reservation release are unsupported. Its [manifest](../repo/internal/adapter/native/manifest.go) advertises push assignment and an inline claim model. The executable launch order defines the actual boundary of that claim.

Persistent [agent profiles](../repo/internal/agentprofile/types.go), lines 1–114, and [profile storage](../repo/internal/agentprofile/store.go), lines 1–118, distinguish logical agent history from a live session. The [planner schema](../repo/internal/planner/schema.sql), lines 1–120, also has session profiles. Persistent performance metadata is useful, but it does not reconstitute the native adapter's active ownership map or issue a fenced execution lease.

## Requirement assessment

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Projects, repositories, workspaces and task namespaces provide useful scope. UI project selection does not itself switch the bound task authority; the inspected router uses a single-user tenant resolver. |
| T02 | Similar | Rich tasks are persisted through Beads or Dolt and exposed through server CRUD. Commit, response, history and dispatch are separate steps. |
| T03 | Similar | Decisions, milestones, epics, parent relationships and follow-up creation support decomposition. Parent propagation is best effort rather than a transactional child-result barrier. |
| T04 | Similar | Automatic and cascade dispatch filter runnable states, dispatch readiness and direct open blockers. Named session start does not use the same readiness gate. Full graph invariants are not enforced by every writer. |
| T05 | Similar | Logical profiles, assignments and sessions are distinct types. Native agent identity is mainly configuration, while active sessions are local memory and no attempt token fences task writes. |
| T06 | Similar | HTTP, CLI-facing operations, adapter contracts and a real four-tool stdio MCP bridge serve agents. Some HTTP routes remain explicit stubs. |
| T07 | Resembles | A mutex prevents two active native session records for one bead within one process. It runs after spawn and does not conditionally claim the tracker row or coordinate other servers. |
| T08 | Similar | Ready readers, workspace conflict filtering, score floors, pool policy and pane parallel limits support allocation. Admission is local; the dispatch gate's completion wiring is incomplete in the inspected Go call inventory. |
| T09 | Similar | Wrapper cascades launch ready descendants and multiple logical sessions can share a pane. There is no atomic parent join over accepted child results. |
| T10 | Similar | Structured work context, DoD, project values, milestone context and workspace surface are injected. Default work adapters reject structured evidence attachment; no accepted-result version pin was established. |
| T11 | Similar | Task updates, runtime state signals, transcript peek and consultation output provide progress and handoff context. No mandatory durable result envelope binds task, attempt, artifact and review. |
| T12 | Similar | Bridge events, SSE and escalation views connect agents and the operator. They do not establish a durable peer inbox with acknowledgements and missed-event replay. |
| T13 | Similar | MCP questions/blockers, runtime escalation indices and operator replies are implemented. Caller role is not authenticated by the bridge, and failed reply delivery can discard the pending entry. |
| T14 | Resembles | Idle reaping and closed-task reconciliation expose stale runtime situations. They are not authenticated task heartbeats, renewable leases or fenced reclaim. |
| T15 | Resembles | Nonce caches and terminal session checks handle some sequential retries. Concurrent cache misses, restarts and unconditional task writes remain outside their protection. |
| T16 | Similar | End, pause/unpause where supported, recycle and background reconciliation provide recovery tools. Native restart rehydration and atomic compensation across task/process effects were not established. |
| T17 | Similar | A remote HTTP control surface and Docker host support can centralize operation. Independent native server instances still lack shared active-claim authority. |
| T18 | Similar | Dispatch records, retained event files and consultation logs aid investigation. They are separate writes, with mutable consult records and no complete authenticated task-attempt history. |
| T19 | Similar | Hierarchical board, state dragging, session inventory and escalation integration form a useful operator interface. Source inspection establishes interactions, not live usability or reconnect correctness. |
| T20 | Similar | Priorities, hierarchy, milestones, backlog states and pool planning support work organization. Default adapters report no native sprints or enforced token budgets. |
| T21 | Resembles | Acceptance text, clean-worktree checks and human consultations help review. DoD intentionally does not gate transitions; closure does not require qualified acceptance of pinned evidence. |
| T22 | Similar | Token authentication, non-loopback bind validation, read-only adapters and container controls are real safeguards. The inspected routing is single-user, with no general per-agent task authorization. |
| T23 | Similar | Work/orchestration adapters, agent configuration, personas and capability negotiation provide extension points. An advertised field or dormant two-phase contract is not an implemented native guarantee. |
| T24 | Similar | A Go service and web client offer a coherent deployment unit. Operation still depends on a compatible tracker/database, agent runtimes, launch backend, bridge and workspace configuration. No installation was trialed. |

## Creating and changing shared work

The [HTTP create handler](../repo/internal/server/work_items_write.go), lines 40–198, decodes a task, optionally generates a milestone prefix, calls the work adapter, appends history and then continues cascades and reconciles parents. A failure after the adapter succeeds can return an error for a committed task. The prefix is derived from a prior read; it is not an atomic sequence allocator.

The [Beads adapter](../repo/internal/adapter/bd/workplane.go), lines 471–546 and 579–736, builds `bd create` and `bd update` arguments. Milestones use an epic plus a label, and DoD is embedded in description text. General updates carry assignment and status fields without `--claim` or an expected revision. DoD updates first reread the description and then replace it, so concurrent edits can be overwritten. A successful subprocess is followed by a separate read and event publication.

The [Dolt writer](../repo/internal/adapter/dolt/workplane.go), lines 352–618, directly inserts or updates Beads-compatible tables. It transactionally groups the issue row, labels and parent relationship. That gives useful database atomicity within one mutation. However, `UPDATE issues ... WHERE id = ?` has no expected revision, previous assignee or attempt condition. Parent replacement has no graph-cycle check in this body. Read-modify-write preparation can occur before the transaction.

This alternate writer does not invoke the Beads CLI's claim, close or dependency-validation path. Installed database constraints can still reject SQL, and the complete deployed schema was not exercised. Therefore the finding is absence of those application guards in this writer, not a claim that every arbitrary status update will succeed. Commit precedes readback and event emission, leaving a committed-write/failed-response boundary.

The [Dolt manifest](../repo/internal/adapter/dolt/workplane.go), lines 196–248, reports no native sprint, enforced token budget or required evidence synthesis. [Beads evidence and sprint operations](../repo/internal/adapter/bd/workplane.go), lines 761–793, explicitly return capability denial. The [sprint handler](../repo/internal/server/sprints.go) converts unavailable native sprints into an empty result. A generic model field must not be mistaken for a complete default sprint service.

## Selecting, launching and owning work

The [pool ready reader](../repo/internal/server/autodispatch_wire.go), lines 181–260, lists unstarted work, excludes non-runnable wrapper kinds, checks dispatch status and looks up direct blockers. Lookup failure prevents that candidate from being dispatched. Persona resolution must also succeed. This is meaningful readiness logic, but it is a snapshot and has no assignee exclusion in the inspected body.

The [daemon](../repo/internal/planner/autodispatch/daemon.go), lines 278–418, 480–518 and 527–610, combines idle sessions, ready tasks and live workspace collisions. It applies score and dispatch gates and can try another candidate after a typed already-claimed result. [Pool wiring](../repo/internal/cli/pool_wiring.go), lines 165–200, constructs a gate per daemon and supplies empty optional profile/health readers. Do not infer that persistent profile types automatically influence this configured selection path.

The [dispatch gate](../repo/internal/planner/dispatch_policy.go), lines 78–190, separately checks admission, records dispatch and decrements completion. The non-test Go call inventory under `internal/` found dispatch increments but no caller of this gate's `RecordCompletion`; other same-named methods belong to profile stores. This suggests that a long-running pool can exhaust its local counter even after work finishes. It is a source-based integration concern, not an observed runtime failure. Separate allow/record operations also do not form a distributed reservation.

For a named task, [HTTP session start](../repo/internal/server/sessions.go), lines 112–258, calls the orchestration adapter directly. It does not first claim the task through the work plane or run the pool's full readiness filter. A reuse-capacity validation error can trigger a fresh-pane retry.

The decisive [native start path](../repo/internal/adapter/native/start.go), lines 1–416, validates configuration and checks an optional nonce cache. Fresh workspace and pane work occur before the final mutex-protected duplicate-bead check. A losing fresh launch is killed on a best-effort basis. The guard prevents duplicate active records in that adapter instance, but a process may already have run before it loses. Killing it cannot undo external effects. A second server has a different map and can launch the same task independently.

On success, session and nonce records are inserted under the lock. The task row is not atomically assigned or transitioned as part of that operation. Some bridge installation, context delivery and tail registration errors are tolerated. The manifest's description of pane spawn as an atomic claim therefore has a narrower meaning than the baseline's durable task ownership.

## Delegation, context and completion

[Cascade dispatch](../repo/internal/server/work_items_cascade.go), lines 125–217, gathers leaves, stages backlog work, checks direct blockers and limits launches. It sets a leaf to started before starting its session. If launch then fails, the response records an error but the prior state mutation is not rolled back in this body. A retry must reconcile task state with actual runtime state.

Multiple logical sessions can share a pane up to the agent's parallel limit. This enables intra-agent concurrency, but the pane remains a shared process context. It is not proof that independently delegated child results are integrated before a parent finishes.

[Preamble composition](../repo/internal/adapter/native/preamble/preamble.go), lines 80–152, combines project goals, values, guardrails, workspace context, interaction profile, work detail and milestone/surface context. It instructs the agent to signal working, commit, close the bead and then emit `bead-done`. These instructions improve continuity. They do not enforce the requested steps.

The [DoD model](../repo/core/dod.go) explicitly makes criteria informational. Its version is a free-form template tag. It is not the version of a submitted artifact accepted by a reviewer. The [native state handler](../repo/internal/adapter/native/state_events.go), lines 1–158, checks whether the worktree is clean before marking the session ready. It does not establish task closure, a remote push, successful tests or accepted output. An environment-controlled acceptance merge path is conditional and is not credited as the default production workflow.

[Ancestor reconciliation](../repo/internal/server/milestone_autoclose.go), lines 1–209, rereads descendants and updates wrappers separately. A wrapper with all leaves terminal becomes completed even when terminal leaves include cancellation. Failures are logged rather than made an atomic precondition of the original child write. This supports a helpful board rollup; it does not enforce a parent acceptance barrier against concurrent child insertion or reopening.

Persona consultations add a more structured review surface. [Consultation application](../repo/internal/persona/dispatcher.go), lines 490–535 and 592–690, validates output lines, checks whether an index was applied, optionally enforces purview and then calls an executor. It releases the lock before execution and records the applied index afterward. Two concurrent applies can pass the same check and both execute. A consult can also disappear before post-effect bookkeeping, yielding an error after an effect.

The [purview gate](../repo/internal/persona/purviewgate/gate.go), lines 1–100 and 114–196, gives configured manager authority real meaning in the applicable path. Its enforcement is conditional: coach/advisory behavior and dormant phases are allowed, and missing resolver/persona paths can skip it. This is not general authenticated RBAC over all task mutations.

## Escalation, events and missed information

[gemba-mcp](../repo/cmd/gemba-mcp/main.go), lines 160–243 and 319–396, implements four stdio tools: question, blocker, state and skill output. It appends structured frames to a local session log. This is a real agent bridge, distinct from the [MCP adapter host](../repo/internal/transport/mcp/host.go), lines 1–114, which negotiates adapter metadata. A manager-role string supplied to the blocker tool is a caller assertion, not proof of authority.

The [native escalation index](../repo/internal/adapter/native/escalations.go), lines 1–130 and 299–389, tracks open requests and can treat a user message as resolving the oldest pending item. Resolution sends terminal keys and removes the record. A send failure also removes it optimistically. Deferral sends no keys but clears the entry. These policies can make an unresolved request disappear from the operator's pending list.

[Bridge tailing](../repo/internal/adapter/native/bridge/tail.go), lines 56–157 and 264–294, reads from the start of a registered session file and reopens on rotation or truncation. No durable consumer cursor is used in that path. Replaying an old file is not the same as restoring the active session registry after server restart. [Frame parsing](../repo/internal/adapter/native/bridge/frame.go), lines 1–90, checks shape and identifiers, not a cryptographically authenticated task attempt.

[SSE streaming](../repo/internal/server/events_stream.go), lines 1–147, has keepalives but no `Last-Event-ID` replay. The [hub](../repo/internal/events/hub.go), lines 113–155, removes slow subscribers. The [web consumer](../repo/web/src/data/sse.ts), lines 1–201, invalidates queries on received events without a full reconnect refresh in the inspected lifecycle. [Session queries](../repo/web/src/hooks/useSessions.ts), lines 1–110, use stale-time caching rather than continuous polling. A dropped event can therefore require a later query/refocus/reload to regain a current view.

The [event writer](../repo/internal/events/log/writer.go), lines 1–135, retains rotated NDJSON, but normal writes are not synchronously fsynced. [Consultation audit records](../repo/internal/persona/auditlog.go), lines 1–150, use temporary-file replacement and overwrite an existing consult ID. [Dispatch records](../repo/internal/planner/dispatch/store.go), lines 128–200, are saved after dispatch as a separate database operation. These are useful investigation artifacts, not a single immutable transaction that couples ownership, effect and history.

## Failure, retry and restart

[HTTP nonces](../repo/internal/server/nonce.go), lines 1–202, cache responses in a bounded process-local LRU with a five-minute default TTL. The middleware performs cache lookup, runs the handler and then stores the response. Concurrent misses can both run. The cache key is the nonce alone, without method, route, body or actor binding. Reusing a nonce for another operation can replay the earlier response. This mechanism is neither human permission approval nor stale-attempt protection.

The native start cache has a related check-before-work/store-after-work boundary. Terminal end checks are useful for sequential repeat calls, but no nonce survives server restart. General task PATCH still accepts an old worker's write because it has no attempt precondition.

[EndSession](../repo/internal/adapter/native/end.go), lines 48–162, removes pane membership and marks a session terminal. Process termination and cleanup are best effort; ending one session preserves a pane that still has siblings. A completed session status is not task acceptance or a guarantee that every external effect has stopped.

[Pause/resume](../repo/internal/adapter/native/orchestration.go), lines 189–257, depends on a pausable backend and changes runtime status after the backend call. [Recycle](../repo/internal/adapter/native/recycle.go), lines 39–226, requires ready state, checks cleanliness, sends reset keys, attempts checkout/pull and mints a replacement ID. Several steps are best effort. A failed branch sync can still leave a new session record using the prior workspace state.

[Idle reaping](../repo/internal/adapter/native/reaper.go), lines 108–169, uses ready/idle observations and later calls end. [Closed-task reconciliation](../repo/internal/adapter/native/reconcile.go), lines 88–178, can mark an active session stalled. However, the native non-test package inventory found no nonempty producer for `ActiveTurnID` and no assignment of `LastHeartbeat`; those fields appear in contracts and fixtures. Do not infer a working task-heartbeat producer from their presence. These loops are runtime housekeeping, not lease expiry plus guarded reclaim.

## Permissions, deployment and operator usability

[API routing](../repo/internal/server/router.go), lines 359–432 and 450–520, can apply bearer/cookie authentication and explicitly wraps selected mutations with nonce middleware. It hardwires the [single-user tenant resolver](../repo/internal/server/middleware/tenant.go), lines 1–130. A tenant-aware workspace schema does not make every task route a multi-tenant authorization boundary. The reviewed [workspace SQL](../repo/internal/workspaces/sql_store.go), lines 1–110, scopes workspace resolution by tenant; the bound task host still needs separate scrutiny.

[Bind validation](../repo/internal/config/bind.go), lines 353–430, rejects unauthenticated non-loopback configuration and supports optional TLS. [Token verification](../repo/internal/auth/verifier.go), lines 1–102, reloads file-backed Argon2 hashes; [request authentication](../repo/internal/auth/token.go), lines 1–97, also accepts a valid session cookie. Rotating a bearer token file alone is not proof that existing valid cookies are revoked. This is source inspection, not a complete authentication audit.

Local worktrees separate files but are not an operating-system sandbox. Container launch provides a stronger optional boundary. [Spawn specification](../repo/internal/adapter/native/start.go), lines 642–750, defaults the container root filesystem to read-only, carries mounts, user identity and resource settings, and can combine a persona surface with operator mounts. [Docker arguments](../repo/internal/adapter/native/backend/docker.go), lines 169–241, drop capabilities, set no-new-privileges, default network to none and set a PID limit. Network, mounts and resource limits remain configuration-dependent; the full secrets and backend lifecycle were not certified.

The [board drag handler](../repo/web/src/pages/BoardPage.tsx), lines 356–421, supports pointer and keyboard sensors. It first persists a state or parent edit, then may launch a leaf session or cascade a wrapper. A launch failure is downstream of the successful task edit. The [state-drop helper](../repo/web/src/components/board/dragToRestage.ts) and [reparent helper](../repo/web/src/components/board/dragToReparent.ts) produce concrete patches from the displayed snapshot. They do not add revision preconditions. This is convenient direct manipulation with the same concurrent-edit boundary as the HTTP API.

The design is cohesive, with explicit interfaces and capability denials. It also carries visible implementation boundaries: `/work-items/ready` is still a 501 route, default sprint/evidence features are unavailable, and native session authority is volatile. Installation cost includes the tracker or Dolt service, agent binaries, backend, helper commands and workspace policy. No live setup, browser accessibility or LAN deployment was tested for this candidate.

## Test-source evidence and adoption work

Selected assertions were read, not run:

- [Nonce tests](../repo/internal/server/nonce_test.go), lines 1–101, cover cache eviction, expiry and already-cached replay. They do not prove concurrent-miss exclusion.
- [Start tests](../repo/internal/adapter/native/start_test.go), lines 254–296 and 336–370, cover sequential nonce reuse and a sequential duplicate bead. They do not establish a durable claim across processes.
- [Parallel tests](../repo/internal/adapter/native/parallel_test.go), lines 116–161, check a fake backend's pane limit. [Gate tests](../repo/internal/planner/dispatch_policy_test.go), lines 70–100, explicitly call completion to release a slot; that does not prove production wiring does so.
- [Ready-reader tests](../repo/internal/server/autodispatch_wire_test.go), lines 204–250, exercise soft-block and direct-blocker filtering with fixtures.
- [Bead-done tests](../repo/internal/adapter/native/state_events_beaddone_test.go), lines 1–95, inject clean/dirty predicates and check state/escalation behavior. They do not test remote push, acceptance or actual Git cleanup.
- [Dolt tests](../repo/internal/adapter/dolt/workplane_test.go), lines 275–344, use SQL mocks for read-only behavior and creation/readback. [Escalation tests](../repo/internal/adapter/native/escalations_test.go), lines 87–111, inspect resolution and pending-index removal. Neither proves deployed database compatibility or successful operator-to-agent delivery.

Adoption should first establish one durable task/attempt authority used by every writer. Reserve ownership before launching, fence old attempts, and make worker completion conditional on current ownership and pinned result evidence. Persist pending operations and active attempts so restart recovery can reconcile the tracker, workspace and actual process.

Next, make dispatch capacity a recoverable view of active assignments, connect completion to admission, and add explicit compensation or a visible reconciliation state for launch failures. Preserve unanswered escalations until delivery is acknowledged. Add durable event cursors or forced snapshot refresh after reconnect. Qualified review should control the transition from submitted work to accepted completion, including child-result integration.

Gemba's board, capability boundaries, launch context and operator escalation are useful components. Its central adoption question is whether those interfaces can sit on a stronger shared ownership and acceptance protocol without leaving the existing alternate write paths able to bypass it.
