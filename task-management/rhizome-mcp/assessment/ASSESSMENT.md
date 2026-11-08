# Rhizome MCP task management assessment

Repository: https://github.com/Odrin/rhizome-mcp

Commit: `03fffd7d1410ddccadf7c199f5d6e796a497b1f0`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 8, 2026. Full local checkout; static implementation and selected test-source review.
Candidate applications and tests were not executed.

## Fit decision

Rhizome is a useful local coordination core for agents that share one trusted machine.
It directly models the failures that interrupt agent work: abandoned claims, lost responses, changed requirements and stale review targets.
Its SQLite implementation contains concrete transaction boundaries, attempt-specific lease credentials, checkpoints and version checks.
These are implemented mechanisms, rather than instructions that merely ask agents to coordinate carefully.

Evaluate it as a local task authority and as a reference for execution-attempt and recovery design.
The full baseline still needs durable organizational responsibility, worker dispatch, delegation, human editing and access across hosts.
HTTP is deliberately restricted to literal loopback addresses.
The tool has no authenticated users or project permissions.
A local status board provides inspection, not a shared browser workspace for managing projects.

The source carries Apache License 2.0.
The adoption decision depends primarily on deployment scope and missing management features.
This assessment does not establish runtime reliability, accessibility, throughput or deployment readiness.

## Architecture and domain model

A Go process exposes MCP tools over stdio or optional local HTTP.
The CLI provides initialization, connection configuration, read commands, board output, backup, diagnostics, migration and maintenance.
Ordinary task mutation is concentrated in MCP; the CLI command catalog does not expose a corresponding full task-editing interface.
See [CLI dispatch](../repo/internal/adapters/cli/commands.go), lines 26–115, and [MCP registrations](../repo/internal/adapters/mcp/adapter.go), lines 205–400.

The implementation separates domain rules, application services, ports, composition, SQLite adapters and transport adapters.
The application layer generates identifiers and random credentials before passing commands to repositories.
Repositories enforce mutable-state conditions inside transactions.
Pure domain functions decide claim eligibility and completion targets.
This separation makes the important rules inspectable without treating transport handlers as the whole application.
See [claim service](../repo/internal/application/attempt_service.go), lines 57–112, and [attempt policy](../repo/internal/domain/attempt_policy.go), lines 13–94.

Each repository has a `.agent-tracker.json` marker with its project ID.
Task data lives in a separate application-data directory, in a SQLite database for each project.
The marker is an identity link; committing it does not commit the database or synchronize work to another machine.
A router selects a project bundle for each request and manages a bounded cache of open bundles.
A separate inventory command inspects local project directories.
See [project identity](../repo/internal/projectconfig/projectconfig.go), lines 19–64; [router](../repo/internal/compose/router.go), lines 20–160; and [inventory](../repo/internal/inventory/list.go), lines 38–89.

Issues have stable ULIDs and project-local `ISSUE-N` numbers, type, title, description, acceptance criteria, priority, labels, parent epic and version.
Stored states are open, ready, blocked, review, done and cancelled.
`in_progress` is derived from an active unexpired attempt.
An epic is a non-executable grouping record; only tasks and bugs can hold attempts.
Hierarchy is limited to a task or bug under a root epic.
There is no recursive executable subtask tree.
See [issue fields](../repo/internal/domain/issue_projection.go), lines 6–26, and [state/type definitions](../repo/internal/domain/issue.go), lines 10–138.

Sessions, work attempts, notes, comments, decisions, artifacts, relations, review requests, review approvals, policies and resource reservations are separate records.
An attempt records its start issue version, event position, kind, status, lease and result.
A session records client/model metadata and activity.
Neither is a permanent agent roster with organizational responsibility or reporting relationships.
The schema also lacks a permanent task assignee.
See [initial schema](../repo/internal/migrations/sql/001_initial_schema.sql), lines 17–209; [session service](../repo/internal/application/session_service.go), lines 18–132; and [explicitly deferred features](../repo/docs/06-deferred-and-open.md), lines 15–57.

## Requirement verdicts

Verdicts describe fit to the complete baseline.
They are not a product score or a claim that all source lines were audited.

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Stable project identity, separate databases, local inventory and explicit request routing support several projects. The project model lacks leadership, portfolio planning and an organization-wide workspace. [Identity](../repo/internal/projectconfig/projectconfig.go), lines 19–64; [routing](../repo/internal/compose/router.go), lines 20–160. |
| T02 | Similar | Stable IDs, outcome text, criteria, priority, state, version, relations and retained attempts provide durable work records. Responsibility is a temporary attempt rather than a permanent accountable owner. [Issue record](../repo/internal/domain/issue_projection.go), lines 6–26; [schema](../repo/internal/migrations/sql/001_initial_schema.sql), lines 29–59 and 120–158. |
| T03 | Similar | Tasks and bugs can belong to a non-archived root epic. Related/duplicate links and atomic plans connect discovered work. No nested epics or executable child hierarchy; epic completion does not aggregate child acceptance. [Parent validation](../repo/internal/adapters/sqlite/issues.go), lines 989–1035; [patch](../repo/internal/domain/issue_patch.go), lines 210–265. |
| T04 | Similar | Direct claims and read projections check unresolved blockers; relation writes reject cycles under the writer transaction. Plans validate combined edges. Done, cancelled or archived prerequisites cease blocking by explicit SQL semantics. No cross-project dependency authority. [Eligibility](../repo/internal/adapters/sqlite/issue_list.go), lines 23–60; [relations](../repo/internal/adapters/sqlite/relations.go), lines 69–213; [plans](../repo/internal/adapters/sqlite/planning.go), lines 209–273. |
| T05 | Similar | Durable client sessions are separate from attempt records and transport connections. Labels, model and instance key aid attribution. There is no permanent agent identity, manager relationship or capability roster. [Sessions](../repo/internal/application/session_service.go), lines 18–132; [attempt insertion](../repo/internal/adapters/sqlite/attempts.go), lines 341–411. |
| T06 | Similar | Structured MCP schemas, domain errors, bounded reads, profiles and JSON CLI output are concrete machine interfaces. Mutation depends mainly on MCP, and the named agent profile omits incremental sync. [Tool catalog](../repo/internal/adapters/mcp/adapter.go), lines 205–400; [profile selection](../repo/internal/adapters/mcp/profile.go), lines 59–120. |
| T07 | Similar | `BEGIN IMMEDIATE`, eligibility checks and a partial unique index give one active attempt per issue. Lease-sensitive changes authenticate the attempt token. Planning edits are separate versioned operations available to trusted clients; there is no authenticated manager/worker authority model. [Claim](../repo/internal/adapters/sqlite/attempts.go), lines 222–440; [unique index](../repo/internal/migrations/sql/001_initial_schema.sql), lines 228–230. |
| T08 | Resembles | Readiness, priority, active-attempt inspection and resource conflicts assist selection. There is no worker dispatch service, worker capacity, project WIP quota or capability assignment in the inspected model and command catalog. [Claim policy](../repo/internal/domain/attempt_policy.go), lines 13–48; [catalog](../repo/internal/adapters/mcp/adapter.go), lines 205–400. |
| T09 | Resembles | An agent can create related issues or a batch plan and let others claim them. No parent-agent ownership, child execution group, join barrier or recoverable coordinator relationship is modeled. [Issue fields](../repo/internal/domain/issue_projection.go), lines 6–26; [planning](../repo/internal/adapters/sqlite/planning.go), lines 65–112 and 298–352. |
| T10 | Similar | Work context combines issue, parent, instructions, blockers, decisions, checkpoint, attempts and artifact references. Sections have limits and truncation signals. Artifacts are references and metadata, not verified or hosted content. [Context](../repo/internal/adapters/sqlite/work_context.go), lines 29–241; [artifact schema](../repo/internal/migrations/sql/001_initial_schema.sql), lines 160–169. |
| T11 | Similar | Leased notes include progress, findings, warnings, checkpoints and next steps. Finish records summary, verification, reason and artifacts atomically. Resume means another attempt reads these records; the tracker does not restore a model context or running process. [Notes](../repo/internal/adapters/sqlite/attempts.go), lines 641–768; [finish](../repo/internal/adapters/sqlite/attempts.go), lines 1419–1565. |
| T12 | Similar | Comments, decisions, activity and ordered event polling retain collaboration context and recover missed changes. There is no addressed inbox, delivery acknowledgement or remote notification. `get_changes` requires a profile/toolset that includes sync. [Change cursor](../repo/internal/adapters/sqlite/search.go), lines 162–225; [profiles](../repo/internal/adapters/mcp/profile.go), lines 59–97. |
| T13 | Resembles | Dependency blockers, manual blocked reasons, comments and supersedable decisions retain obstacles and answers. No structured question owner, recipient, response deadline or escalation state exists in the inspected entities and tool catalog. [Issue schema](../repo/internal/migrations/sql/001_initial_schema.sql), lines 29–53 and 93–118; [deferred scope](../repo/docs/06-deferred-and-open.md), lines 15–57. |
| T14 | Similar | Renewable leases expire lazily on mutations and through cleanup; expiry releases reservations and review claims in the transaction. Derived activity avoids a permanently stored In Progress flag. No automatic replacement worker is dispatched. [Renew/sweep](../repo/internal/adapters/sqlite/attempts.go), lines 442–542 and 1963–2003; [sweeper](../repo/main.go), lines 47–70. |
| T15 | Similar | Attempt ID, live status, expiry and a constant-time token check reject stale attempt-sensitive writes. Keyed claim retry rotates the token; keyed finish/note retries replay stored results. Ordinary planning changes and external work remain outside lease fencing. [Authentication](../repo/internal/adapters/sqlite/attempts.go), lines 38–90; [claim retry](../repo/internal/adapters/sqlite/attempts.go), lines 250–315; [finish replay](../repo/internal/adapters/sqlite/attempts.go), lines 1220–1243. |
| T16 | Similar | Failed/interrupted/expired attempts retain history; new attempts can retrieve checkpoints. Maintenance can force release; cancellation/archive reject live attempts. New blockers can also reject failed/interrupted finish reports, requiring expiry or maintenance. No external process cancellation or rollback is provided. [Finish guards](../repo/internal/adapters/sqlite/attempts.go), lines 1191–1280; [release](../repo/internal/adapters/sqlite/attempts.go), lines 1567–1626; [cancel/archive](../repo/internal/adapters/sqlite/issues.go), lines 310–331 and 459–536. |
| T17 | Resembles | Several local processes can share the same project database. HTTP rejects LAN, wildcard and hostname binds. A marker and separate databases on different machines do not create one authority; a remote deployment needs a different transport/access design. [Address validator](../repo/internal/runtime/http_lifecycle.go), lines 365–403; [local race source](../repo/integration/claim_race_test.go), lines 20–81. |
| T18 | Similar | Issue events are append-only at the database layer; attempts and review approvals retain history. Session attribution is optional, and several issue/relation mutations explicitly store NULL session IDs. There is no authenticated identity or tamper-resistant external audit. [Event triggers](../repo/internal/migrations/sql/001_initial_schema.sql), lines 171–193; [create/update](../repo/internal/adapters/sqlite/issues.go), lines 121–158 and 398–402. |
| T19 | Similar | Terminal/JSON reads, graph output, self-contained HTML, a live read-only board, search and linked issue details expose the work. The board shows truncation and refresh failures. No browser editing, portfolio dashboard or observed accessibility result. [Board routes](../repo/internal/adapters/cli/board_http.go), lines 27–67; [refresh](../repo/internal/adapters/cli/board_assets/board_live.js), lines 1–145; [detail](../repo/internal/adapters/cli/board_assets/issue_detail_page.tmpl). |
| T20 | Resembles | Open/ready, priority, labels, epics and dependency plans support a backlog. No estimates, milestones, due dates, iterations or manual rank appear in the work model. [Issue fields](../repo/internal/domain/issue_projection.go), lines 6–26; [deferred planning](../repo/docs/06-deferred-and-open.md), lines 25–41. |
| T21 | Similar | Configurable gates check criteria, recorded attempt evidence and fresh purpose-scoped approvals. Review targets pin issue version/event position/artifact IDs. Review is optional without a matching policy; there is no independent authenticated reviewer or automatic test execution. [Gate evaluator](../repo/internal/domain/workflow_gate.go), lines 13–143; [finish](../repo/internal/adapters/sqlite/attempts.go), lines 1284–1417; [target](../repo/internal/adapters/sqlite/reviews.go), lines 890–951. |
| T22 | Resembles | Separate databases, loopback Host/Origin checks and server-wide catalog profiles reduce exposure. Session handles provide attribution, and leases protect attempt operations. These do not provide account authentication, project ACLs or a human-only override boundary. [HTTP validation](../repo/internal/runtime/http_lifecycle.go), lines 192–234; [profiles](../repo/internal/adapters/mcp/profile.go), lines 59–120; [maintenance](../repo/internal/application/maintenance_service.go), lines 18–44. |
| T23 | Similar | Labels, instructions, policy requirements, review purposes, resource names and selectable tool groups provide useful extension points. Types, statuses and enforcement points remain fixed; arbitrary organizational roles and workflows need code changes. [Gate points](../repo/internal/domain/workflow_gate.go), lines 13–34; [profile groups](../repo/internal/adapters/mcp/profile.go), lines 22–56; [deferred workflow](../repo/docs/06-deferred-and-open.md), lines 25–41. |
| T24 | Similar | One Go executable, local SQLite, versioned migrations, backup validation, logical interchange and diagnostic/maintenance commands limit infrastructure needs. The database is outside Git and needs its own backup process. No installation, restore drill, load test or power-loss test was run. [Package](../repo/go.mod), lines 1–12; [backup](../repo/internal/runtime/runtime.go), lines 407–481; [commands](../repo/internal/adapters/cli/commands.go), lines 26–115. |

## Lifecycle and mutation authority

Creation allocates the project sequence, validates the parent, inserts the issue and labels, records an event and stores any keyed response in one write transaction.
The same transaction evaluates applicable policy gates when the requested initial state is review or done.
Creation is not universally proof that an implementation attempt occurred: without a matching requirement, a terminal initial state can pass.
See [creation](../repo/internal/adapters/sqlite/issues.go), lines 68–198.

An agent reads the planning graph or issue projections, then claims a selected ready or review issue.
The claim transaction expires old attempts, checks blockers and existing ownership, evaluates policy, inserts the new attempt and snapshots its requirements.
The database partial unique index is a second guard against two active attempts.
An optional set of resource reservations is acquired in that same transaction.
A conflict rolls back the attempt and all reservations.
This is a useful pattern for shared files or logical resources, but it cannot stop an agent editing an unreserved file or calling an external service directly.
See [claim and reservations](../repo/internal/adapters/sqlite/attempts.go), lines 315–440, and [overlap checks](../repo/internal/adapters/sqlite/reservations.go), lines 208–286.

The worker retains its returned lease token, renews before expiry and saves restartable notes.
Checkpoint text, next steps, artifact references and the note event are persisted together.
The worker must save real information; the tracker cannot reconstruct unsaved output after a crash.
The replacement's work-context query returns the latest checkpoint across attempts, plus the previous terminal attempt and bounded surrounding context.
See [notes](../repo/internal/adapters/sqlite/attempts.go), lines 641–768, and [recovery reads](../repo/internal/adapters/sqlite/work_context.go), lines 796–825.

Successful finish authenticates the active lease, reloads the issue, checks blockers, checks changed context and derives the target state.
Description, criteria, status and blocked-reason changes require acknowledgement of the current version and event position.
Other classified changes produce warnings.
Configured gates use the attempt's frozen requirements with current evidence.
Result, artifacts, status, reservation release and event are committed together.
The returned verification list is recorded testimony, not a test runner result obtained by the tracker.
See [finish](../repo/internal/adapters/sqlite/attempts.go), lines 1191–1565, and [change classification](../repo/internal/domain/attempt_policy.go), lines 111–160.

A review attempt can approve, request changes or block.
When bound to a request, approval checks the frozen target against issue/event changes before resolving the request.
Stale targets are superseded, and the attempt is cancelled in the same transaction.
Approval writes immutable records for the request's purposes.
Freshness excludes defined review bookkeeping and priority-only changes; it is not equality with the latest global event ID.
See [staleness](../repo/internal/adapters/sqlite/reviews.go), lines 42–90; [finish enforcement](../repo/internal/adapters/sqlite/attempts.go), lines 1284–1417; and [approval lookup](../repo/internal/adapters/sqlite/reviews.go), lines 1118–1209.

Ordinary issue edits use an expected version.
They cannot directly set an executable issue to review or done.
They can change planning context during an attempt, which the finish path must then reconcile.
Cancellation and archive refuse active attempts rather than silently ending a worker's execution.
The operator can release the attempt first.
Epic completion remains a manual grouping transition; the update path has no child-completion barrier.
See [patch rules](../repo/internal/domain/issue_patch.go), lines 210–265, and [update/archive](../repo/internal/adapters/sqlite/issues.go), lines 274–428 and 459–576.

The repository also has low-level review claim/resolve methods.
They must not be mistaken for the exposed lease-authenticated finish contract.
The inspected MCP catalog routes review completion through `finish_attempt`; it does not register an unrestricted `resolve_review_request` tool.
This distinction matters when reusing repository interfaces in a new application.
See [repository resolve](../repo/internal/adapters/sqlite/reviews.go), lines 767–830, and [MCP catalog](../repo/internal/adapters/mcp/adapter.go), lines 205–400.

## Concurrency, recovery and failure conditions

### Local transaction authority

Every reviewed lifecycle write uses a short `BEGIN IMMEDIATE` transaction.
The DB wrapper adds process-local writer admission and bounded whole-transaction retries for SQLite BUSY/LOCKED results.
The database lock, rather than that local channel alone, coordinates independent processes.
Read-context operations use a consistent read transaction.
The opener configures WAL, foreign keys, a five-second busy timeout and `synchronous(NORMAL)`.
This is a concrete local durability design; it is not evidence of a distributed database or a measured power-loss guarantee.
See [transaction helper](../repo/internal/adapters/sqlite/transaction.go), lines 71–187, and [connection settings](../repo/internal/adapters/sqlite/sqlite.go), lines 111–130.

### Retry credentials and response freshness

A keyed claim retry returns the same attempt, but generates a new secret and replaces the stored lease hash.
The previous token stops working after the retry commits.
This recovers a lost claim response without storing its raw secret, but two clients sharing the same retry key can invalidate each other's credentials.
Clients must retain the newest response and avoid treating an idempotency key as an ownership identity.
The saved claim payload is also not a substitute for fetching current work context after intervening edits.
See [replay implementation](../repo/internal/adapters/sqlite/attempts.go), lines 250–315, and [test assertions](../repo/internal/adapters/sqlite/attempts_test.go), lines 28–115.

Completed finish and note retries can return their prior stored responses before authenticating a currently active attempt.
That permits retrieval after a successful transition without repeating its effects.
It does not create a new active claim or authorize a fresh mutation.
Keys are scoped to operations in the project database; there is no tenant/principal namespace.
See [finish replay](../repo/internal/adapters/sqlite/attempts.go), lines 1220–1243, and [note replay](../repo/internal/adapters/sqlite/attempts.go), lines 657–685.

### Recovery can require an operator

Expiry terminates the attempt, releases its reservations and reopens or supersedes its claimed review request.
The issue itself retains its stored state and can become claimable again.
The server sweeper and lazy mutation checks provide cleanup opportunities; there is no supervisor that launches the successor agent.
See [expiry](../repo/internal/adapters/sqlite/attempts.go), lines 1963–2003, and [sweeper](../repo/main.go), lines 47–70.

The finish path checks unresolved dependencies before branching on successful, failed or interrupted outcome.
Adding an unfinished blocker can therefore prevent a worker from recording a terminal failure or interruption through this operation.
The worker can preserve a note, while an operator releases the attempt or waits for expiry.
The same early archive/cancellation guards also apply before outcome-specific processing.
This behavior needs an explicit client recovery procedure; a failed finish call is not proof the attempt has ended.
See [unconditional guards](../repo/internal/adapters/sqlite/attempts.go), lines 1255–1280.

Force release requires an attempt ID and local operator access, not the lease token.
It records an interruption and releases associated authority.
It does not terminate an external worker process or revoke that process's filesystem credentials.
See [maintenance release](../repo/internal/adapters/sqlite/attempts.go), lines 1567–1626.

### Review freshness is tracker freshness

Review pins issue metadata, event position and artifact IDs.
It cannot detect an unreported edit to a mutable file URI, branch or external document.
A commit artifact can identify an immutable revision, but the record is not proof that the reviewer inspected it or that tests passed.
Policies also do not enforce separation between implementer and reviewer identities.
Use immutable deliverable references and an external acceptance procedure where that distinction matters.
See [artifact model](../repo/internal/migrations/sql/001_initial_schema.sql), lines 160–169, and [target creation](../repo/internal/adapters/sqlite/reviews.go), lines 890–951.

Gates are optional, limited to the fixed enforcement points, and frozen when an attempt or review target starts.
Changing a live policy does not retroactively replace an existing snapshot.
Missing historical snapshots are treated as empty requirements for compatibility.
A claim/gate success must be interpreted in that policy/version context.
See [snapshot enforcement](../repo/internal/adapters/sqlite/gate_enforcement.go), lines 38–111.

### Import and administrative scope

Logical import requires an empty destination, checked inside the write transaction.
It validates imported issue fields but deliberately restores historical terminal state without evaluating live workflow gates.
It is not a general merge into an active backlog.
The agent catalog excludes migration and governance tools; the default full catalog includes them.
That is a server-wide exposure choice, not a per-user permission system.
See [empty-destination guard](../repo/internal/adapters/sqlite/projects.go), lines 301–332; [imported issue handling](../repo/internal/adapters/sqlite/projects.go), lines 412–457; and [profiles](../repo/internal/adapters/mcp/profile.go), lines 59–120.

## Human and agent usability

For agents, explicit error codes, stable IDs, version checks and bounded context are useful.
The work-context response combines the material needed to resume without replaying an entire conversation.
Truncated sections are signalled instead of silently presenting a complete-looking result.
However, agents must understand project references, session handles, lease tokens, idempotency and review targets.
They also need disciplined checkpoint and renewal loops.
The tracker records the work; it does not run those loops on the agent's behalf.

The agent profile removes governance and migration, which reduces accidental administrative exposure.
It also removes `get_changes` through the sync group.
A coordinator that relies on incremental polling needs an explicitly chosen toolset or a different profile.
Read-only selection is based on tool annotations and is applied at registration, so excluded tools are not merely hidden in documentation.
See [catalog selection](../repo/internal/adapters/mcp/profile.go), lines 59–120.

For the human owner, the board shows active leases, reservations, blocked issues, review requests, counts, search and linked detail.
HTML templates distinguish empty lists and truncated collections.
Live refresh polls with ETags, pauses when hidden, retries with backoff and exposes stale status on failure.
It preserves open detail sections and selected focus/scroll state during refresh.
These are source-observed design choices; no browser interaction or accessibility audit of the candidate was performed.
See [board template](../repo/internal/adapters/cli/board_assets/board_served_page.tmpl), lines 1–95; [detail template](../repo/internal/adapters/cli/board_assets/issue_detail_page.tmpl); and [refresh client](../repo/internal/adapters/cli/board_assets/board_live.js), lines 1–145.

The board handler accepts only GET and HEAD.
It is an inspection surface with no card editor, drag/drop state mutation or human acceptance action.
The user would still need an MCP-capable client or additional application for project management.
There is also no combined browser portfolio across all local projects.
See [route enforcement](../repo/internal/adapters/cli/board_http.go), lines 27–67.

## Completeness, design quality and test-source evidence

The inspected lifecycle is cohesive.
Atomic claims, per-attempt secrets, a shared blocker query, transactionally paired events, frozen policies and review freshness all address real coordination failures.
The application/service/adapter split provides reusable boundaries.
SQLite files and a Go executable keep the local operating footprint small.

Completeness is strongest for a trusted local coordination kernel.
It is weaker for the baseline's organization and project-management layer: permanent responsibility, worker capacity, delegation, structured decisions awaiting a person, human write workflows and service permissions.
Adding these is a domain change, not just adding a board skin.
Some inline comments still describe earlier implementation stages even where later code supplies the missing path; executable call sites are the basis of the findings here.

Selected test bodies contain meaningful assertions:

- Claim retry checks token rotation, stored token hash, request conflicts and exactly one durable attempt/start event/idempotency record. A separate assertion checks that the raw token is absent from the saved response. [Tests](../repo/internal/adapters/sqlite/attempts_test.go), lines 28–115.
- The stale-review test injects an event-write failure and checks that request/attempt binding remains unchanged when the transaction rolls back. It then expects a stale-target error after removing the injected fault. [Test slice](../repo/internal/adapters/sqlite/attempts_test.go), lines 589–674. The rest of this test was not inspected for this claim.
- The integration race creates five independent tasks and races an HTTP process against a stdio process sharing the database. A barrier releases both requests together. Assertions demand one winner, a stable domain conflict for the loser and one active attempt through a third connection. [Race setup](../repo/integration/claim_race_test.go), lines 20–81; [barrier](../repo/integration/claim_race_test.go), lines 95–123; [assertions](../repo/integration/claim_race_test.go), lines 220–276.

These are source assertions, not test results from this study.
No candidate tests, binaries, package installations or services were run.
The review did not certify every repository method, migration, transport edge or resource-overlap pattern.
Runtime race behavior, unsupported filesystem effects, backup recovery and large-project performance remain unmeasured.

## Adoption work and useful components

For the complete baseline, add a permanent participant/role model and task accountability separate from execution attempts.
Add explicit delegation and child-result aggregation, capacity-aware dispatch, structured questions and human review actions.
Provide an authenticated remote service with project permissions and a human editing interface.
Define whether the local databases remain authoritative or migrate into a central service; copying project markers cannot solve that question.

Preserve the separation between task, session and attempt.
Retain transactionally guarded claims, lease-specific credentials, replay semantics, bounded recovery context and version-bound review targets.
Define the operator-release and blocked-finish behavior before connecting an autonomous worker loop.
Use immutable artifact revisions and a verification executor where completion must establish more than reported evidence.

The [source review ledger](review.json) records the inspected implementation ranges, hashes and all requirement verdicts.
This report establishes source-based fit at the pinned commit; live acceptance remains separate work.
