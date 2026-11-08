# Vikunja: agent interfaces over a shared task service

Source: https://github.com/go-vikunja/vikunja

Reviewed commit: `d2c9aee4f8894edc02611a8b40becbd5dfc95e33`.
Assessment date: November 9, 2026.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Evidence ledger: [review.json](review.json).

## Fit decision

Vikunja supplies more agent integration than an ordinary board with a generic API. This checkout contains persistent bot users, scoped API tokens, a native HTTP MCP endpoint and the `veans` agent CLI. Agents and people can use the same projects, tasks, relations, comments and Kanban views. The CLI teaches a claim, work, review and human-close workflow.

The ownership and acceptance rules remain weaker than that workflow suggests. `veans claim` moves a task, adds the configured bot as an assignee and attaches a branch label through separate requests. Multiple assignees are valid. The command does not reserve an unowned ready task, establish an attempt identity or grant expiring ownership. Its instruction to leave completion to a human is prompt policy: the same CLI accepts a completed status, and ordinary project writers can set the server's done field.

The implementation does enforce useful local invariants. Selected writes lock views and tasks, reload permissions after locking, enforce bucket limits and reject cyclic parent/subtask relations. These mechanisms deserve credit. They protect board records and access boundaries; they do not supply a distributed execution scheduler, stale-worker fencing or accepted-child completion protocol.

Vikunja is a plausible shared task and human inspection service beneath a separate coordinator. It is insufficient as the sole authority for autonomous allocation, retries, attempts, review and recovery. Adding those rules only to an agent prompt would leave alternate API and browser writers able to bypass them.

## Scope and evidence level

The full checkout contains 2,501 tracked files. This targeted review follows task create/update/delete/restore, bulk field updates, assignees, relations, bucket transitions, selected locking and permissions, bot creation and API-token validation, MCP dispatch, CLI selection/claim/update, comments, notifications, event publication, selected webhook delivery and frontend mutation/reconnect paths. It also reads selected test assertion bodies. No candidate application, install, build, migration or test was executed.

This is not an every-line or complete security audit. Full imports, duplication, every permission mutation, all migrations, attachment storage and cleanup, complete OAuth/login, every frontend screen, all notification providers and deployed database/scaling behavior are outside certification. The external Huma dependency was read at the version pinned by this checkout. A test-source assertion is not a passing experiment. Absence findings apply to the inspected task model, mutation paths and operation inventory.

The [README license declaration](../repo/README.md), lines 58–62, identifies most of the repository as AGPL-3.0-or-later and the desktop directory separately as GPL-3.0-or-later. The [frontend manifest](../repo/frontend/package.json), lines 1–20, declares AGPL-3.0-or-later. Desktop behavior was not assessed. Optional audit logging is license gated in executable code; its presence is not credited as unconditional default behavior.

## Architecture and records

The [Go manifest](../repo/go.mod), lines 18–50, declares Go 1.27.0 and dependencies including Huma and Watermill. The root instructions identify a Go API and Vue 3/TypeScript frontend. The [frontend manifest](../repo/frontend/package.json), lines 1–80, declares pnpm 12.16.1, Node 24 or later, Vue Query and TipTap dependencies. These are the pinned source requirements, not a claim that this checkout was built successfully here.

The [project model](../repo/pkg/models/project.go), lines 40–61, holds project title, description, identifier, owner, parent and archive state. The [task model](../repo/pkg/models/tasks.go), lines 93–203, holds title, HTML description, project, done/done-at, dates, recurrence, priority, progress fraction, multiple assignees, labels, related tasks, attachments, timestamps and per-view presentation data. Its UID is identified as a CalDAV identifier, not an execution idempotency key. This review inspected the field declarations with long documentation tags omitted from the display; other cited write bodies establish mutation behavior.

The [v2 routes](../repo/pkg/routes/api/v2/tasks.go), lines 59–124 and 244–315, expose task reads, creation, full replacement, deletion and generated partial updates. Creation takes the project from the URL. The shared [CRUD pipeline](../repo/pkg/web/handler/core.go), lines 30–65 and 138–211, checks model permissions, performs the model operation, commits SQL state and only then dispatches pending events. Model failure rolls back and discards pending events. Event delivery is consequently outside the committed record transaction.

The [bot creation body](../repo/pkg/user/user_create.go), lines 139–195, rejects bot owners, requires a `bot-` username and creates a user with a durable human owner. [Bot permissions](../repo/pkg/models/bot_users_permissions.go), lines 25–62, restrict management to the owner and reject link-share ownership. [Token creation](../repo/pkg/models/api_tokens.go), lines 126–168, can issue a token for the caller or an owned bot, validates route permissions and stores a SHA-256 token hash. This separates bot attribution from a human's current session. It does not create a worker process or a task execution attempt.

## Requirement assessment

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Projects have owners, descriptions, identifiers, parents and access checks. Leadership, specification continuity and portfolio decisions remain coordination conventions. |
| T02 | Similar | SQL task records have stable IDs, project indices, dates, descriptions and completion. No structured accepted outcome or encompassing transaction across CLI steps and external delivery. |
| T03 | Similar | Parent/subtask and other relations support decomposition. Hierarchy cycle checks are implemented; child execution, result acceptance and governed follow-up creation are not. |
| T04 | Similar | Blocking relations and CLI ready filtering exist. Readiness is a caller-visible snapshot, not a server claim condition; cycle checking covers hierarchy rather than all blocking relations. |
| T05 | Similar | Owned bot users and their tokens provide persistent agent attribution. Sessions, branch labels and task assignees do not identify or fence an execution attempt. |
| T06 | Similar | Native HTTP MCP, scoped structured HTTP APIs and JSON CLI output are implemented. The surfaces manage records rather than providing an atomic claim-next/execution protocol. |
| T07 | Resembles | Claim means bucket move, add-assignee and branch tagging. Multiple assignees and unconditional ordinary task writes prevent exclusive ownership guarantees. |
| T08 | Similar | Bucket limits are checked in server write paths protected by view locks. This is board WIP control, not per-worker capacity, fair dispatch or a reservation. |
| T09 | Resembles | Real subtasks, relationships and assignees can organize parallel work. No child-worker launch, attempt join or accepted-child parent-finish barrier. |
| T10 | Similar | Project/task descriptions, comments, attachments and branch labels retain context. They do not pin an immutable result, artifact digest and reviewer decision to an attempt. |
| T11 | Similar | Progress, done state, comments, dates and CLI review summaries are durable records. A required structured result and acknowledged handoff remain conventions. |
| T12 | Similar | Database notifications, comments, live connections and retrying webhooks support communication. Process-local events and reconnect invalidation are not a durable agent mailbox/replay protocol. |
| T13 | Resembles | Blocking relations and comments express questions or impediments. No inspected typed pending decision with accountable resolution and guarded continuation. |
| T14 | Absent | Reviewed task/claim paths have no renewable work lease, execution heartbeat or expiry-based reclaim. Authentication expiry is not ownership expiry. |
| T15 | Resembles | Duplicate-assignee checks and client timestamp checks offer limited safeguards. Inspected storage writes lack expected-revision/attempt predicates; multi-request commands lack operation-wide idempotency. |
| T16 | Similar | Tasks can be reopened, soft-deleted and restored with permission checks. These are record operations, not worker cancellation, checkpoint resume or recovery of an interrupted multi-step command. |
| T17 | Similar | Hosts can share one HTTP/SQL task authority. Event queues and socket connections are process local in the inspected implementation; execution ownership across hosts is not supplied. |
| T18 | Similar | Creator attribution, comments, timestamps, request metadata and optional audit events aid inspection. Audit logging is license gated and asynchronous to task commit, not an atomic immutable execution journal. |
| T19 | Similar | Shared task details and routed list, table, Gantt and Kanban components support human inspection. Client rollback/reconnect paths are implemented; actual browser usability was not tested. |
| T20 | Similar | Ordered views, priorities, dates, labels, recurrence and relations support backlog planning. Explicit sprint/milestone governance is not established by these generic task fields. |
| T21 | Resembles | The CLI prompt asks for a summary and human review. CLI completed status, direct done updates and done-bucket moves do not require a qualified reviewer or accepted evidence/children. |
| T22 | Similar | Bot ownership, token expiry/scopes, project permissions, under-lock rechecks and MCP restrictions provide access controls. They do not separate worker submission rights from reviewer completion rights. |
| T23 | Similar | Typed APIs, an MCP allow-list/catalog, CLI hooks, labels, relations and webhooks permit integration. New authority rules need server enforcement across alternate writers. |
| T24 | Similar | Separate CLI, structured errors, paginated reads and credential trust controls help operation. API/CLI/frontend maintenance, external delivery recovery and deployment still need operational work. |

## Lifecycle, readiness and delegation

Creation enters the shared permission/commit pipeline, validates task limits, locks project views, assigns indices, inserts records and places tasks in views. It then handles assignees/reminders/subscriptions and queues creation events. See [creation](../repo/pkg/models/tasks.go), lines 1051–1068 and 1136–1250. The HTTP handler adds positions to the response after `DoCreate` has committed. A failure in that later response-building step must not be treated as proof that creation did not happen. No inspected request key makes a retry return the original creation result.

[CLI list](../repo/veans/internal/commands/list.go), lines 79–163, fetches project tasks and applies ready, mine, branch and status filters locally. [The client](../repo/veans/internal/client/tasks.go), lines 56–99, iterates all pages rather than silently returning the first 50 tasks. Ready means not done, in the configured Todo bucket and without a visible incomplete `blocked` task. It does not mean unassigned, reserved or within the worker's capacity. Parent/subtask relationships have no effect on this readiness test.

There is an access-boundary qualification. [Related-task loading](../repo/pkg/models/tasks.go), lines 685–742 and 909–945, includes only related tasks from accessible projects and skips missing/inaccessible related records. The CLI can therefore evaluate only blockers included in that response. A blocker hidden by permission changes is not an authoritative satisfied dependency. Claim does not re-evaluate dependencies on the server.

[Relation creation](../repo/pkg/models/task_relation.go), lines 146–315, sorts endpoint locks, requires write access to the base task and read access to the other, rejects self-relations and duplicates, and inserts forward/inverse relations. The cycle walker bounds its visits and rejects cyclic parent/subtask structure. The conditional invokes cycle checks only for parent/subtask kinds. A blocking graph is not covered by that check. Nor does ordinary completion consult these relations to require finished or accepted children.

[Claim](../repo/veans/internal/commands/claim.go), lines 28–89, resolves the task, moves it to In Progress, adds the configured bot, optionally creates/attaches a branch label and finally reads the task. Conflict errors on assignment/label attachment are treated as soft skips. This makes selected repeats convenient, but it is not an all-or-nothing claim transaction. A failed later call can leave the bucket moved or the bot assigned. Two different bots can both be added. Reusing one configured bot across sessions also makes its membership insufficient to identify which process currently owns work.

The separate [assignee update](../repo/pkg/models/task_assignees.go), lines 64–151 and 211–306, reconciles a set of users, checks access and suppresses duplicate membership for the same user. Its locking protects the stored task/project access boundary. It does not reject a second distinct worker, compare a prior owner or return an execution token. A parent task can organize a team through these records, but creating subtask links does not launch, supervise or join child agents.

## Writes, WIP and stale work

[Task locking](../repo/pkg/models/tasks.go), lines 409–485, uses `FOR UPDATE` for MySQL/PostgreSQL, reloads the task, clears memoized state and checks write permission on its current project. The multi-task path gathers views and locks sorted task IDs, rejecting a project change between preliminary and locked reads. [View locking](../repo/pkg/models/task_position.go), lines 241–303, serializes selected view writes in ascending deduplicated order; SQLite relies on its single-writer behavior instead of `FOR UPDATE`.

[Bucket limits](../repo/pkg/models/tasks.go), lines 947–980, count tasks in the relevant bucket, including filter scoping where applicable, and reject a positive limit overflow. [Bucket movement](../repo/pkg/models/kanban_task_bucket.go), lines 1–285, validates task/view compatibility, locks before mutation and changes done state when crossing a configured done bucket. These checks are stronger than a visual WIP warning. A bucket limit still says nothing about one bot holding several tasks in different views or whether the worker is healthy.

[General update](../repo/pkg/models/tasks.go), lines 1390–1793, merges the submitted state into the locked record and writes selected columns by task ID. Bulk updates use an explicit field whitelist and preserve fields outside that set; see [bulk entry](../repo/pkg/models/bulk_task.go), lines 1–98. Ordinary full replacements do not carry that same omitted-field contract. Locks serialize writes and recheck authorization, but do not reject an old worker whose previously read content is now stale.

Partial update needs a precise distinction. [Local AutoPatch registration](../repo/pkg/routes/api/v2/huma.go), lines 135–151, delegates to Huma 2.40.0. Its external implementation reads the current representation, merges the patch and sends an internal PUT; it supplies `If-Match` from the read ETag when no client conditional header exists. Source: https://raw.githubusercontent.com/danielgtaylor/huma/v2.40.0/autopatch/autopatch.go

That header alone does not establish atomic stale-write rejection here. The inspected [task update input](../repo/pkg/routes/api/v2/tasks.go), lines 273–295, binds no write precondition, and the [final SQL update](../repo/pkg/models/tasks.go), lines 1769–1793, has no expected revision/updated/attempt predicate. A search of production Go source found no `If-Match`/`If-Unmodified-Since` enforcement or Huma precondition use. The source-based conclusion is that these task writes do not establish a storage-level comparison-and-swap guarantee. The GET ETag read optimization must not be presented as one.

[CLI update](../repo/veans/internal/commands/update.go), lines 98–237, first reads the task. `--if-unchanged-since` compares that response timestamp locally, then performs later writes. Another writer can act after the check. The CLI correctly sends a changed-field merge patch, but comments, field update, bucket movement and label changes are separate commits. A scrap reason can persist even if a later status change fails; a status change can persist before labels fail. The final refresh is best effort. Recovery requires reading actual server state and reconciling which steps happened.

No inspected task fields or claim operations establish heartbeat renewal, ownership expiry or an attempt generation. An expired API token stops future authenticated requests. It does not revoke an already recorded assignment or prove a worker is dead. Cancellation/reassignment therefore needs an external execution authority and a server-enforced stale-attempt rule if old workers must be prevented from writing.

## Review, completion and recovery

The [agent prompt](../repo/veans/internal/commands/prompt.tmpl), lines 1–65, labels project/task content untrusted, directs separately assignable work into real subtasks, requests a review summary and tells the agent never to close its own task. This is useful workflow guidance. [Status conversion](../repo/veans/internal/status/status.go), lines 85–112, nevertheless maps Completed and Scrapped to done, and the CLI update path accepts both. Scrapped requires a reason in that CLI; direct task writers do not acquire the same obligation from the prompt.

[Done handling](../repo/pkg/models/tasks.go), lines 2119–2147, handles timestamps and recurrence, including reopening repeating tasks and resetting their description checklist. It does not verify reviewer identity, acceptance evidence or child results. Moving to a done bucket is another completion writer. A coordinator that requires controlled acceptance must enforce it across direct updates, bucket moves and relevant bulk paths, rather than relying on the chosen command or column name.

[Deletion](../repo/pkg/models/tasks.go), lines 2251–2310, locks the task/views, removes positions/bucket membership, stops running timers and soft-deletes the task while preserving other related records for later cleanup. [Restore](../repo/pkg/models/task_trash.go), lines 112–165, reloads under lock, checks current project permission, conditionally clears deletion fields and places the task back into views. These are meaningful record recovery operations. They do not stop an agent process or restore its execution context. Full purge/file compensation was not assessed.

## Communication, delivery and multi-host behavior

[Comments](../repo/pkg/models/task_comments.go), lines 32–110, store task text, author and timestamps and queue a creation event. [Database notifications](../repo/pkg/notifications/database.go), lines 32–155, persist recipient/project scope and read time. Their listing requires a permission filter, and read marking has a recipient check. These provide durable human-visible records, but a notification is not a typed assignment acknowledgement or an unresolved management decision.

The [event system](../repo/pkg/events/events.go), lines 98–180 and 240–339, initializes an in-memory Watermill GoChannel and uses retry middleware with five retries. Pending events are stored by session pointer in a process-local map, removed after commit and published afterward. Publication failures are logged. The poison queue uses the same local channel mechanism. A process exit after SQL commit but before publication can lose a notification trigger. A failed delivery is not a durable transactional outbox entry recoverable on another API host.

[Webhook delivery](../repo/pkg/models/listeners.go), lines 1267–1298, reloads the configured webhook and returns failures to that retry middleware. [The HTTP sender](../repo/pkg/models/webhooks.go), lines 342–402, uses an SSRF-safe client, configured timeout, optional HMAC and optional basic authentication, and reports unsuccessful responses. This is implemented retry behavior, not fire-and-forget success. Its retry state still resides in the process event system; duplicate effects and restart recovery require integration-side handling.

The [socket hub](../repo/pkg/websocket/hub.go), lines 24–103, keeps user connections in memory and drops a message when a connection's send buffer is full. [The client](../repo/frontend/src/composables/useWebSocket.ts), lines 1–255, refreshes authentication, reconnects with jittered backoff, resubscribes and marks possible missed events. [Cache-event integration](../repo/frontend/src/composables/useServerCacheEvents.ts), lines 1–34, sends a reconnect invalidation. [The handler](../repo/frontend/src/client/queries/serverEvents.ts), lines 101–145, invalidates relevant notifications, comments, task details and membership queries. This refreshes selected views; it does not replay a durable event cursor or guarantee every transient notification was retained.

One shared API/SQL deployment can serve agents on many hosts. The inspected local bus and connection hub do not prove reliable cross-process event propagation. A shared database choice alone does not supply that missing delivery channel, task leases or host-independent attempt ownership.

## Agent and human usability, permissions and operation

[MCP exposure](../repo/pkg/modules/mcp/exposure.go), lines 29–155, uses an explicit operation allow-list with typed tools and catalog actions. Account, credentials, webhooks, shares, file transfer and administration are intentionally outside that allow-list. [The handler](../repo/pkg/modules/mcp/mcp.go), lines 24–135 and 147–226, creates stateless request servers, requires an API token with MCP access, checks origin and limits request size/batch count. User JWT access is deliberately rejected at this endpoint.

[MCP loopback](../repo/pkg/modules/mcp/loopback.go), lines 45–165, checks authorization before dispatch, builds an internal HTTP request and re-enters the API with the authorized token. It does not write directly to a second task store. [Route scopes](../repo/pkg/models/api_routes.go), lines 526–594, and [API-token middleware](../repo/pkg/routes/api_tokens.go), lines 103–145, retain route and expansion checks. [Token validation](../repo/pkg/models/api_tokens.go), lines 350–380, checks expiry and retrieves an authenticatable owner. These controls limit the bot's accessible API surface, while model project checks limit records. They do not constrain the bot to only its current execution or reserve completion for a reviewer.

The CLI offers JSON results, project IDs, status aliases, branch labels, list filters and explicit errors. Its [trust gate](../repo/veans/internal/trust/trust.go), lines 39–69 and 148–179, normalizes origins, rejects URL user info and requires stored/interactive trust or a matching configured server environment value. This matters because repository configuration chooses the destination for credentials. The [file credential backend](../repo/veans/internal/credentials/file.go), lines 29–150, requests mode 0600 for saves and serializes its read/mutate/save under a lock. Complete keychain, filesystem helper and OAuth security were not certified.

The [project view component](../repo/frontend/src/views/project/ProjectView.vue), lines 1–131, selects list, Gantt, table and Kanban components and handles project/view selection. [Task mutations](../repo/frontend/src/client/queries/taskMutations.ts), lines 49–182, send writable fields through generated clients and reconcile caches. [Context-aware mutation handling](../repo/frontend/src/client/queries/contextMutation.ts), lines 1–63, snapshots optimistic caches, rolls back on errors and avoids applying callbacks after a client context change. This is useful account/session safety, not a task attempt fence. Rendering, keyboard access, latency and large-project usability remain untested here.

Optional [audit registration](../repo/pkg/audit/listener.go), lines 43–68, checks the audit feature license for each event. [The writer](../repo/pkg/audit/writer.go), lines 106–160, assigns event IDs and writes local JSON log lines under a mutex. Audit delivery follows the event system, outside the task transaction. It must not be described as a complete, universally enabled, immutable execution history.

## Completeness, tests and adoption work

The inspected mechanisms have substantive implementations rather than interface stubs. Shared model permission/commit functions, under-lock access rechecks, explicit bulk field selection, view-scoped limits, native token-scoped MCP and CLI pagination form a coherent foundation. The API/CLI/frontend separation also makes consistency dependent on correctly preserving invariants in every entry point. Source presence does not certify all providers or deployments.

Selected assertion bodies were read: [CLI claim](../repo/veans/e2e/claim_test.go), lines 28–77, checks assignment, bucket and branch label; [bucket tests](../repo/pkg/models/kanban_task_bucket_test.go), lines 32–64 and 125–159, check limits and task movement after a prior permission check; [relation tests](../repo/pkg/models/task_relation_test.go), lines 129–178, check hierarchy cycles; [MCP tests](../repo/pkg/modules/mcp/loopback_test.go), lines 121–143, check scope errors and unknown input; [client tests](../repo/frontend/src/client/queries/taskMutations.test.ts), lines 144–181, check rollback and avoiding unrelated cache rollback. None establishes a passing test run, two-agent exclusive claim, conditional-write race guarantee, crash-safe notification delivery or accepted-child completion.

Adoption for the baseline needs a work authority that transactionally selects ready work, enforces exclusive ownership/capacity, issues attempt generations, renews leases and rejects stale writes through every mutation route. It also needs structured result/evidence submission, reviewer rights and accepted-child gates, durable questions/handoffs, an outbox/replay strategy and recovery for interrupted multi-request CLI operations. Keep project descriptions, views, bot attribution, API/MCP interfaces and their useful local invariants. Give the additional coordinator enforceable storage contracts before treating this board as an autonomous execution authority.
