# Muster task management assessment

Repository: https://github.com/eriky/musterai

Commit: `bb98b21a6ac0ed4cb095f948e55ae8a644e10c40`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 9, 2026. Full local checkout; static implementation and selected test-source review.
Candidate applications, installations and tests were not executed.

## Fit decision

Muster supplies a useful shared project workspace for agents and a human operator.
Its implemented features include project boards, persistent agents, permissions, task relationships, work links, versioned documents, knowledge records and a browser interface.
It can expose one central service to clients on different machines.
The MIT-licensed code is worth evaluating as the human and agent collaboration layer of the requested system.

Its main gap is the execution contract.
Atomic claims prevent simultaneous allocation to different agents, but later edits and completion do not require the current lease or an execution-attempt credential.
Assignments, claims and lane state are separate records with different authority rules.
Review instructions do not become acceptance gates on cards.
The baseline would still need attempt identity, stale-worker rejection, structured recovery, delegation and controlled task acceptance.

This is a source-based fit decision, not a deployment or reliability certification.
The assessment separates behavior enforced by services from the more demanding workflow described in the agent instructions.

## Architecture and domain model

The Node.js application uses Express for REST and MCP HTTP transport, React for the browser and SSE for activity notifications.
The package declares Node `>=22.13.0` and supports SQLite or PostgreSQL through an asynchronous database adapter.
The application composition root constructs shared services and card policies.
The transport runtime connects those services to REST, MCP and an in-process SSE manager.
See [package metadata](../repo/package.json), [composition](../repo/src/application/composition.ts), lines 34–85, and [transport runtime](../repo/src/application/transport-runtime.ts).

Cards are decomposed into access policy, lane policy, record queries, assignment operations, movement operations and relationship operations.
The `CardService` facade delegates to those collaborators.
Both REST and MCP call this same service graph.
Transport-level permissions and service-level workspace/assignment checks address different layers of authorization.
This is a useful architecture for extending interfaces without duplicating all lifecycle logic.

The schema models workspaces, human users, principals, agents, roles, memberships, projects, boards, columns, cards, assignments, relationships, comments, documents, versions, knowledge and events.
Projects have stable IDs, names, descriptions and card-number sequences.
Cards have a ULID, human-readable key, description, priority, due date, rank, archive flag, epic flag and lease fields.
They have multiple assignees but only one `claimed_by` value.
There is no task-attempt table, task revision, acceptance-result table or dedicated failed/interrupted outcome.
See [schema](../repo/src/db/migrations/001-initial.sql), lines 134–298.

Lane presentation and semantics are separate.
Persisted workflow roles are backlog, ready, active, review and terminal.
Display names can change without redefining completion.
Boards with missing/ambiguous classification refuse workflow-sensitive operations until configured.
Default simple and standard boards carry explicit roles and WIP limits.
See [board creation](../repo/src/services/board.service.ts), lines 42–100; [lane policy](../repo/src/services/card-lane.policy.ts), lines 91–150; and [role migration](../repo/src/db/migrations/011-workflow-lane-roles.sql).

Permanent agent rows belong to a workspace and can name their human operator, role and capabilities.
Browser sessions and API tokens establish access identities, but they are not execution attempts attached to each card.
There is no agent-to-agent reporting relationship or parent execution group.
See [agent schema](../repo/src/db/migrations/001-initial.sql), lines 134–145, and [agent selectors](../repo/src/services/agent-scope.authorization.ts).

## Requirement verdicts

The verdicts describe fit to the complete baseline and its operating boundaries.
They are not points in a product ranking.

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Workspace-scoped projects contain boards and linked documents/knowledge. The UI can select projects and combine boards within one project. No project-leader/accountability field or cross-project planning model is present. [Project creation/list](../repo/src/services/project.service.ts), lines 22–150; [project schema](../repo/src/db/migrations/001-initial.sql), lines 153–172. |
| T02 | Similar | Stable ULIDs/keys, description, priority, rank, due date, assignments, links, comments and lane state form durable work records. Acceptance criteria and terminal outcomes are free-form content rather than separate structured records. [Card schema](../repo/src/db/migrations/001-initial.sql), lines 186–237; [creation](../repo/src/services/card.service.ts), lines 111–230. |
| T03 | Similar | `parent_of`/`child_of`, epic flags and child completion counts expose decomposition. Relationship insertion has no hierarchy-cycle, single-parent or parent-type check, and parent closure has no child acceptance barrier. [Link insertion](../repo/src/services/card-relation.operations.ts), lines 81–121; [canonicalization](../repo/src/services/helpers/card-links.helper.ts); [epic progress](../repo/src/services/card.service.ts), lines 349–366. |
| T04 | Resembles | Canonical `blocks` relations prevent ordinary claims and moves into active lanes while the blocker is nonterminal and unarchived. No cycle detection or readiness queue is enforced; moves to review/terminal do not apply the blocker check. [Blocker query](../repo/src/services/card-lane.policy.ts), lines 135–150; [claim](../repo/src/services/card-assignment.operations.ts), lines 93–192; [move](../repo/src/services/card-move.operations.ts), lines 143–181. |
| T05 | Similar | Permanent agents have capabilities, operator, role and presence. User sessions/tokens are separate access records. There is no per-task attempt/session identity distinguishing successive executions by the same agent. [Agent/access schema](../repo/src/db/migrations/001-initial.sql), lines 94–145; [effective permissions](../repo/src/services/role.service.ts), lines 195–234. |
| T06 | Similar | REST and MCP expose structured tools over shared services, validation, permission errors and bounded reads. Some contracts differ: REST constrains claim TTL to an integer 1–86400; MCP accepts an optional number without those bounds. No execution-oriented task CLI is established by this review. [REST claim schema](../repo/src/api/schemas.ts), lines 198–202; [MCP claim](../repo/src/mcp/tools/card.tools.ts), lines 79–97; [card page](../repo/src/services/card.service.ts), lines 535–592. |
| T07 | Similar | Transactional claims lock the card on PostgreSQL and serialize writers on SQLite. A live different holder gets a structured refusal. Later updates/moves use assignment permissions, not claim authority; allocation exclusivity does not extend to the whole execution lifecycle. [Claim](../repo/src/services/card-assignment.operations.ts), lines 93–192; [mutation scope](../repo/src/services/card-access.policy.ts), lines 63–95. |
| T08 | Similar | Creates and lane changes enforce WIP under transaction/row locks, with explicit authorized overrides and events. Claims do not consume target-lane capacity until a separate move. No agent capacity or capability-aware dispatcher is modeled. [Create WIP](../repo/src/services/card.service.ts), lines 120–144; [move WIP](../repo/src/services/card-move.operations.ts), lines 93–166; [claim response](../repo/src/mcp/tools/card.tools.ts), lines 79–97. |
| T09 | Resembles | Agents can create, link and assign child work; a human sees epic progress. There is no delegation request/accept/result protocol, parent-agent identity, join barrier or replacement coordinator record. [Relationships](../repo/src/services/card-relation.operations.ts), lines 81–121; [progress](../repo/src/services/card.service.ts), lines 349–366. |
| T10 | Similar | Linked versioned documents, comments, knowledge facts/entities and branch/PR/commit/pipeline URLs retain context. Work links are supplied metadata, not fetched or verified deliverables. No task-attempt context snapshot or immutable handoff package is provided. [Work links](../repo/src/services/card-relation.operations.ts), lines 139–174; [document versions](../repo/src/services/document.service.ts), lines 164–225; [knowledge scope](../repo/src/services/kb-read-scope.ts), lines 28–95. |
| T11 | Similar | Attributed card comments and work links retain progress/results across conversations. Comments can be edited/deleted, and there is no typed checkpoint/result/verification state or automatic resume package. [Comments](../repo/src/services/comment.service.ts), lines 19–95; [card model](../repo/src/db/migrations/001-initial.sql), lines 186–249. |
| T12 | Similar | Durable project events, paged activity and bounded SSE replay provide shared updates. There is no addressed agent inbox, recipient acknowledgement or guaranteed complete replay; the stream route ignores replay truncation after 100 events. [Event tail](../repo/src/services/event.service.ts), lines 43–82; [stream route](../repo/src/api/routes/event.routes.ts), lines 51–111. |
| T13 | Resembles | Dependencies and comments can record obstacles; design documents can await approval. Cards have no distinct question owner, escalation destination, answer lifecycle or manual blocker state apart from linked tasks/free text. [Card schema](../repo/src/db/migrations/001-initial.sql), lines 186–249; [document transitions](../repo/src/services/document.service.ts), lines 228–327. |
| T14 | Similar | Heartbeats renew the agent's claims; a minute timer releases expired claims and presence becomes idle/offline. Renewal can extend an already-expired claim before cleanup, and expiry does not clear assignments or move the lane. [Renew/expiry](../repo/src/services/card-assignment.operations.ts), lines 195–251; [heartbeat](../repo/src/mcp/tools/agent.tools.ts), lines 73–81; [timer](../repo/src/server.ts), lines 197–200. |
| T15 | Resembles | Reclaimed allocation rejects a different live claimant, but ordinary mutations carry no attempt generation or lease secret. Old assignees may retain edit/move authority. There is no general request-key deduplication for card creation/comments/completion. [Lease fields](../repo/src/db/migrations/001-initial.sql), lines 186–204; [access policy](../repo/src/services/card-access.policy.ts), lines 63–95; [move write](../repo/src/services/card-move.operations.ts), lines 196–241. |
| T16 | Similar | Transactional writes, persisted comments, lease cleanup, credential revocation and explicit offboarding support manual recovery. Archive/delete can affect claimed work, and failure/cancellation are not distinct execution outcomes. No process cancellation or external-work rollback is implemented by the reviewed card lifecycle. [Archive/delete](../repo/src/services/card.service.ts), lines 825–857; [offboarding](../repo/src/services/agent.service.ts), lines 204–231. |
| T17 | Similar | One centrally hosted REST/MCP service and SQLite/PostgreSQL authority can serve different hosts. Remote binding requires enforced auth, an HTTPS public origin and OIDC configuration. SSE fanout is process-local; this is not evidence of a horizontally replicated event service. [Deployment config](../repo/src/config/index.ts), lines 97–123 and 188–242; [runtime wiring](../repo/src/application/transport-runtime.ts), lines 31–48. |
| T18 | Similar | Many lifecycle operations commit actor-attributed events with their data. Privileged operations have a separate server-written security audit. Coverage is incomplete: unassign, archive, label removal and relationship removal have no corresponding event in the reviewed paths. [Events](../repo/src/services/event.service.ts), lines 85–138; [audit](../repo/src/services/audit.service.ts), lines 36–70; [unjournaled mutations](../repo/src/services/card-assignment.operations.ts), lines 73–91, and [card mutations](../repo/src/services/card.service.ts), lines 705–723 and 825–830. |
| T19 | Similar | The browser has editable boards, linked details, work links, documents, agents, project navigation and mobile lanes. Modal semantics and sanitization have concrete source implementations. These were not rendered or accessibility-tested here; one move-error path can still announce success. [Refresh/navigation](../repo/src/web/App.tsx), lines 190–260 and 394–427; [mobile lanes](../repo/src/web/components/kanban/MobileLaneSwitcher.tsx); [move announcement](../repo/src/web/components/KanbanBoard.tsx), lines 147–154. |
| T20 | Resembles | Ranked cards, due dates, priorities, labels, epics and separate boards support continuous planning. A board named Sprint 1 is not a structured iteration; no milestone, estimate or capacity-planning entity is present in the inspected model. [Card/project schema](../repo/src/db/migrations/001-initial.sql), lines 153–237; [default board](../repo/src/services/project.service.ts), lines 73–75. |
| T21 | Resembles | Documents have version-checked forward approval and immutable approved content. Card review is only a lane: terminal moves do not require approved docs, linked work, reviewer identity, passing tests or accepted criteria. Qualified document self-approval is allowed. [Document enforcement](../repo/src/services/document.service.ts), lines 164–327; [card move](../repo/src/services/card-move.operations.ts), lines 143–241. |
| T22 | Similar | Enforced mode derives principals from credentials, intersects agent/operator roles, checks membership and workspace resources, and gates operator overrides. Open mode bypasses these boundaries. Project separation within one workspace is organizational, not a distinct per-project ACL. [Auth](../repo/src/api/middleware/auth.ts), lines 143–216; [permissions](../repo/src/shared/permission-enforcer.ts), lines 405–481; [workspace scope](../repo/src/services/card-access.policy.ts), lines 20–95. |
| T23 | Similar | Custom permission roles, labels, knowledge relation types, board columns and role-classified lanes provide extension points. Lane semantics remain five fixed roles; there is no arbitrary execution workflow or custom attempt schema. [Roles](../repo/src/services/role.service.ts), lines 62–88 and 195–234; [lane roles](../repo/src/db/migrations/011-workflow-lane-roles.sql); [link canonicalization](../repo/src/services/helpers/card-links.helper.ts). |
| T24 | Similar | Node package, SQLite for a small host, PostgreSQL option, migration checksums/transactions and deployment material are concrete. Remote operation adds OIDC/TLS/proxy administration. No install, live migration, backup/restore drill, load test or candidate suite was run. [Package](../repo/package.json); [migrator](../repo/src/db/migrator.ts), lines 156–215; [remote config](../repo/src/config/index.ts), lines 188–242. |

## Lifecycle and alternate mutations

Project creation inserts the project, event, default board/columns and protocol document through a shared transaction.
Card creation serializes the destination lane, checks WIP, allocates the project card key, inserts associations, rebalances ranks and records the event.
The board rank is an ordering aid, not an execution priority dispatcher.
See [project bootstrap](../repo/src/services/project.service.ts), lines 22–119, and [card create](../repo/src/services/card.service.ts), lines 111–230.

A worker reads the board and claims a card.
The claim transaction locks the card, validates workspace and agent selector, requires classified workflow lanes, checks another live holder and checks unresolved blockers.
It stores lease fields, inserts the claimant as an assignee and records a claim event.
An authorized blocker override is separately recorded.
SQLite's Immediate transaction or PostgreSQL's row lock protects the check/write span.
See [claim implementation](../repo/src/services/card-assignment.operations.ts), lines 93–192.

Claim does not restrict the source lane to ready/backlog, reject terminal cards or reject archive state.
`requireCard` loads the row without those filters.
Claim also does not move the card.
The client must make a second request to enter the active lane, where WIP and blockers are checked again.
If that move fails, the lease and assignment remain in the original lane.
The operating protocol asks for immediate movement but does not make the two requests atomic.
See [row lookup](../repo/src/services/card-record.queries.ts), lines 12–21, and [MCP next action](../repo/src/mcp/tools/card.tools.ts), lines 79–97.

During execution, progress is a card comment, with optional work links and document/knowledge changes.
The human and other workers can read the same persistent records.
There is no dedicated start/finish attempt object, checkpoint schema or required result summary.
See [comment creation](../repo/src/services/comment.service.ts), lines 19–45, and [work-link insertion](../repo/src/services/card-relation.operations.ts), lines 139–174.

To finish, a permitted caller moves the card into a terminal-role lane.
The service records moved and completed events in the transaction.
It does not consult a review decision, acceptance record, evidence list or current lease.
It also does not clear the existing claim.
Another move out of and back into terminal can produce another completion event.
See [move write/events](../repo/src/services/card-move.operations.ts), lines 196–241.

Direct assignment does not change claim ownership, and unassignment does not release a claim.
Expiry clears claim fields but preserves the assignment and lane.
Archive only changes its visibility flag.
Deletion removes related records and can remove a live claimed card; it is not a cancellation protocol that waits for the worker.
See [assignment](../repo/src/services/card-assignment.operations.ts), lines 41–91 and 195–251, and [archive/delete](../repo/src/services/card.service.ts), lines 825–857.

## Concurrency and recovery boundaries

### Allocation is atomic; execution is not fenced

SQLite root calls share a FIFO; transaction-scoped calls bypass that queue and join the owning transaction.
Accidental root calls from inside a transaction fail rather than silently join or deadlock.
`BEGIN IMMEDIATE` retries lock contention with an asynchronous bounded wait.
PostgreSQL transactions use one checked-out connection and explicit card/lane locks where the reviewed lifecycle needs them.
The move path locks lanes in stable order and retries specified conflicts.
See [SQLite adapter](../repo/src/db/sqlite-adapter.ts), lines 12–205; [PostgreSQL adapter](../repo/src/db/postgres-adapter.ts), lines 85–208; and [move locking](../repo/src/services/card-move.operations.ts), lines 93–134 and 249–273.

These mechanisms protect database consistency without establishing a per-attempt write credential.
Ordinary edit/move scope checks an assignment or broad `card.assign_others` permission.
When worker B takes an expired claim, worker A's assignment remains unless explicitly removed.
A can therefore retain mutation authority while B is the claimant, subject to A's role and membership.
Two sessions using one permanent agent identity also share the same claim identity.
There is no generation counter to reject the earlier execution.
See [mutation scope](../repo/src/services/card-access.policy.ts), lines 63–95, and [claim/expiry writes](../repo/src/services/card-assignment.operations.ts), lines 158–166 and 217–236.

Card edits lack an expected task version.
A transaction prevents partial writes, but it does not tell a caller that another editor changed the content it read earlier.
This is especially relevant for simultaneous descriptions or priority updates through different clients.
See [update](../repo/src/services/card.service.ts), lines 630–666.

### Heartbeat is shared identity activity

Heartbeat updates agent presence, then renews every card whose `claimed_by` is that agent.
Renewal has no unexpired-lease predicate.
A delayed heartbeat can extend an expired row if cleanup or another claimant has not changed it yet.
It can also keep multiple cards leased while only one activity loop is alive.
The heartbeat transaction and lease-renewal request are separate operations.
See [agent heartbeat](../repo/src/services/agent.service.ts), lines 379–393; [MCP heartbeat](../repo/src/mcp/tools/agent.tools.ts), lines 73–81; and [renewal](../repo/src/services/card-assignment.operations.ts), lines 199–208.

A minute timer performs presence reconciliation and expired-lease cleanup.
Passive offline status is telemetry and intentionally does not revoke credentials.
Explicit offboarding revokes credentials, clears claims and retains identity rows for attribution.
There is no automatic successor dispatcher or worker-process termination.
See [presence](../repo/src/services/agent.service.ts), lines 395–421; [offboarding](../repo/src/services/agent.service.ts), lines 204–231; and [timer](../repo/src/server.ts), lines 197–200.

### Dependency and hierarchy links are permissive

Relationship canonicalization rejects self-links and normalizes inverse/symmetric types.
The insertion path does not check transitive cycles, parent type or a single-parent invariant.
Mutually blocking cards can therefore produce an unusable selection graph.
Parent links organize the display, but they do not impose completion rules.
Archiving or deleting a prerequisite changes dependency eligibility without expressing whether its outcome was accepted or cancelled.
See [canonicalization](../repo/src/services/helpers/card-links.helper.ts), [insertion](../repo/src/services/card-relation.operations.ts), lines 81–121, and [blocker eligibility](../repo/src/services/card-lane.policy.ts), lines 135–150.

### Durable events do not guarantee complete delivery

Event creation allocates a database order and inserts the event in the mutation's transaction.
After-commit callbacks publish only after commit, and PostgreSQL returns the connection before waiting for listeners.
Listener errors are contained; event persistence remains the durable record.
The SSE manager bounds connections, queued bytes/events and replay size.
See [event transaction](../repo/src/services/event.service.ts), lines 85–138; [PostgreSQL callbacks](../repo/src/db/postgres-adapter.ts), lines 171–208; and [SSE limits](../repo/src/realtime/sse.ts), lines 8–18.

The persisted resume query returns `truncated` when more than 100 successors exist.
The stream route hands the first page to `completeReplay` without following or exposing that flag.
Events beyond that page can remain unseen until a separate history read; later live frames can advance the stream cursor past the gap.
Unknown/foreign cursors also fall back to a live tail.
Agent consumers that need full history must use paginated activity and reconciliation, not infer completeness from a healthy stream.
See [resume query](../repo/src/services/event.service.ts), lines 43–82, and [resume route](../repo/src/api/routes/event.routes.ts), lines 86–111.

Fanout is wired to an in-process listener, not a shared message bus.
PostgreSQL support should not be read as proof that every server replica receives another replica's events.
The browser continuously reloads project data every three seconds, which helps it recover current state even when events are lost.
That polling does not prove that an autonomous agent received every handoff or notification.
See [runtime binding](../repo/src/application/transport-runtime.ts), lines 31–48, and [browser refresh](../repo/src/web/App.tsx), lines 394–427.

## Review, permissions and operation

Document approval has meaningful enforcement.
Content edits lock the document and append a new version; approved content cannot be edited.
Status advances only draft → in_review → approved, requires the correct permission and expected content version, and uses a conditional write.
Status, event and security audit share the transaction.
Qualified authors can approve their own documents; this is a permission-controlled approval, not mandatory independent review.
See [document update/status](../repo/src/services/document.service.ts), lines 164–327.

This document mechanism does not gate card completion.
The agent instructions require verification notes, linked branches/PRs and reading approved designs.
The move service has no corresponding acceptance checks.
Using Muster for accepted outcomes therefore needs a separate task-review policy and service enforcement.
See [workflow instructions](../repo/AGENTS.md), lines 146–154, and [move service](../repo/src/services/card-move.operations.ts), lines 143–241.

Enforced authentication resolves the bearer/session principal rather than trusting comment attribution supplied by a client.
Agent permissions are intersected with the human operator's workspace role.
Missing membership removes authority; the card access policy also checks workspace scope and assignment.
MCP registration centralizes permission checks, while REST uses the same mapped operations through middleware.
These are concrete access boundaries, though this review did not audit every authentication protocol or endpoint.
Assignment scoping is not universal: the inspected label and relationship mutations check workspace resources but do not call the edit/move assignment policy.
Permission to modify a card must therefore be assessed per operation, not inferred from the stricter title-edit path.
See [auth resolution](../repo/src/api/middleware/auth.ts), lines 143–216; [role intersection](../repo/src/services/role.service.ts), lines 195–234; and [MCP wrapper](../repo/src/mcp/server.ts), lines 217–244.

Open mode deliberately skips authorization and accepts supplied identity labels.
On non-loopback addresses, configuration defaults to enforced mode and rejects an explicit open-mode request.
Remote setup also requires an HTTPS public origin, OIDC settings and a bootstrap owner subject.
That supports a central deployment, with more operating work than exposing a local board port.
No candidate listener or identity provider was started in this study.
See [listener/deployment checks](../repo/src/config/index.ts), lines 97–123 and 188–242.

Schema migrations have checksums and per-migration transactions with a ledger.
Successful earlier migrations remain committed if a later one fails.
This provides a recoverable upgrade structure, but it is not a demonstrated restore procedure.
SQLite state, PostgreSQL backups, identity configuration and linked external artifacts still need an operator-owned recovery plan.
See [migration runner](../repo/src/db/migrator.ts), lines 156–215.

## Human and agent usability

The browser provides a practical shared view: project/board navigation, an all-boards view within a project, card details, assignees, work links, document history and agent presence.
Mobile lane buttons and shared dialog semantics show deliberate interaction design.
Markdown rendering sanitizes untrusted bodies and falls back to escaped text when sanitization is unavailable.
These are source observations; visual quality, keyboard reachability and contrast were not tested in a running candidate.
See [project loading](../repo/src/web/App.tsx), lines 190–260; [mobile lanes](../repo/src/web/components/kanban/MobileLaneSwitcher.tsx); [dialog](../repo/src/web/components/AccessibleDialog.tsx); and [Markdown](../repo/src/web/markdown.ts).

Several browser failures are visible, including an upstream connection message and card-move refusal.
However, the parent move handler catches the error without rejecting, while the board wrapper announces that the card moved after awaiting it.
A refused move can therefore leave both a refusal message and a success announcement.
This is a static control-flow finding; no assistive-technology session was run.
See [parent error path](../repo/src/web/App.tsx), lines 478–488, and [announcement](../repo/src/web/components/KanbanBoard.tsx), lines 147–154.

Agent usability benefits from human-readable keys, canonical web links, bounded card summaries and explicit conflict messages naming the holder.
It requires agents to coordinate several requests: select, claim, move, comment, attach work, renew and move again.
There is no single acceptance/submission operation that validates the required handoff package.
REST and MCP TTL validation also differ, which can surprise a client moving between interfaces.
See [claim tool](../repo/src/mcp/tools/card.tools.ts), lines 79–97, and [REST schema](../repo/src/api/schemas.ts), lines 198–202.

## Completeness, design quality and test-source evidence

Muster has a coherent shared-service and presentation architecture.
Dependency injection, transaction-scoped adapters, role-based lane semantics, shared permission mapping and commit-after notification delivery are useful design choices.
Its board, document and knowledge features are substantial enough to support human inspection and agent collaboration.
The remaining baseline gaps sit mainly in task execution semantics, responsibility and controlled completion.

The security audit and collaboration feed have different purposes.
Neither should be described as a complete immutable history of all card changes.
Several association removals and archive paths emit no event, comments are mutable, and project deletion cascades project-scoped records.
The inspected schema has no append-only trigger on the general event table.
See [audit writer](../repo/src/services/audit.service.ts), lines 36–70; [event schema](../repo/src/db/migrations/001-initial.sql), lines 323–333; and [mutation paths](../repo/src/services/card.service.ts), lines 705–723 and 825–857.

Selected test bodies contain meaningful assertions:

- Two concurrent service claims must produce one winner, a refusal naming the holder and an assignment for the winner. This fixture uses one SQLite adapter and process; it is not a cross-host test. [Claim source](../repo/tests/card-claim.test.ts), lines 42–134.
- Expiry cleanup checks cleared lease fields/events, injects an event-write failure to require rollback, and races two sweepers to require one release event. [Expiry source](../repo/tests/card-claim.test.ts), lines 237–300.
- WIP and blocker tests assert refusals and separately recorded override events. [Rules source](../repo/tests/card-rules.test.ts), lines 51–141.
- Document tests assert stale-version refusal, one winner for simultaneous approval, immutable approved content and rollback when audit insertion fails. [Document source](../repo/tests/document-state-machine.test.ts), lines 88–145 and 169–219.
- A transaction-delivery test uses a second connection to check that live publication follows commit and rollback publishes nothing. The SSE replay test explicitly caps replay before queued live frames. [Delivery source](../repo/tests/event-transaction-delivery.test.ts), lines 73–136; [replay source](../repo/tests/realtime-sse.test.ts), lines 119–145.

These are inspected assertions, not passing results from this study.
No candidate test suite, database, browser or server was run.
The assessment did not fully audit OIDC/OAuth/token cryptography, every KB mutation, every route, all frontend components or PostgreSQL failure behavior.
Scale, cross-process races, deployment recovery and live usability remain unmeasured.

## Adoption work and useful components

For the full baseline, add a durable execution-attempt record with a generation/token, explicit outcome, checkpoint, artifacts and verification.
Require that authority on attempt-sensitive updates and completion.
Keep long-lived responsibility/assignment separate from a temporary lease, and define what remains authorized after expiry and reassignment.
Make claim-plus-start and submission-plus-review coherent service operations, with a documented recovery path when a request loses its response.

Add dependency/hierarchy validation, explicit delegation and child-result aggregation, structured questions/escalations, worker capacity and task acceptance rules.
Preserve the existing document approval, permission mapping and transaction infrastructure.
Extend event replay with a complete catch-up/resync contract and define multi-instance notification behavior before using multiple application servers.

The human board, shared knowledge, credential-derived identities, workspace roles and database abstraction are useful foundations.
They address the collaboration surface; the additional lifecycle work is necessary before treating that surface as the authority for autonomous execution and accepted delivery.
The [source review ledger](review.json) records the inspected ranges, hashes and all 24 verdicts at the pinned commit.
