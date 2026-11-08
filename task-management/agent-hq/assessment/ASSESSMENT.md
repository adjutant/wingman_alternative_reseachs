# Agent HQ task management assessment

Repository: https://github.com/tools-for-agents/agent-hq

Commit: `785cd8c9a55b2b517eb8eb8f680cd65985992282`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 8, 2026. Full local checkout, static implementation review. Candidate code and tests were not executed.

## Fit decision

Agent HQ is a small, understandable shared board with useful agent interfaces, messaging, memory and operator views.
It provides a real conditional task claim and real expiring reservations.
It is suitable as a reference implementation or a trusted team's cooperative tracker.

It is not a complete authority for independent workers against this baseline.
General task updates bypass the claim guard, direct claims bypass readiness, and the HTTP service does not authenticate the actor.
There is no parent/subagent model, attempt token, review gate or stale-worker rejection on completion.
These gaps affect the central coordination contract rather than peripheral presentation.

For adoption, keep the small API and board design but establish one enforced mutation policy before adding autonomous workers.
The source is MIT licensed. Its installation is small, but that does not remove the required coordination work.

## Architecture and domain model

The application is a Node HTTP service, a synchronous SQLite store, a browser dashboard and a separate stdio MCP proxy.
The [HTTP server](../repo/src/server.js), lines 49–102 and 130–195, exposes the domain operations directly and starts a stale-agent timer.
The [MCP process](../repo/mcp/mcp-server.js), lines 17–35 and 469–546, forwards requests to the HTTP service through `HQ_URL`.
It does not maintain a second database or execute the coding worker.

The [schema](../repo/src/db.js), lines 14–135, stores agents, boards, columns, tasks, task dependencies, comments, memory, messages, activity and a run/cost ledger.
An agent has a durable identifier, name, role, status and last-seen time.
A task belongs to a board and column and has description, assignee, priority and labels.
The task schema has no parent, acceptance policy, execution-attempt identifier or versioned review target.
The later schema additions provide claim time and lease expiry, not an attempt token.

SQLite opens with foreign keys, WAL, a busy timeout and retry handling around initial schema creation: [database initialization](../repo/src/db.js), lines 137–173.
That is a useful local persistence foundation.
Most domain operations then issue separate statements through small synchronous helpers.
The schema transaction is not a transaction around each task transition and its activity event.

## Requirement assessment

| ID | Verdict | Implementation and boundary |
|---|---|---|
| T01 | Resembles | Boards partition task records, but there is no project/leadership registry. The dashboard reads the default board, while agents, memory and messages are global. [Schema](../repo/src/db.js), lines 15–102; [board service](../repo/src/services.js), lines 231–319; [browser board](../repo/public/app.js), lines 223–248. |
| T02 | Similar | Stable task IDs, outcomes in descriptions, priority, labels and timestamps persist in SQLite. Status is column membership; required acceptance information is not structured. [Task schema](../repo/src/db.js), lines 42–55; [create/get](../repo/src/services.js), lines 455–537. |
| T03 | Absent | The complete task/dependency schema and task creation/update operations contain no parent relationship or child lifecycle. Dependencies are ordering edges, not decomposition. [Schema](../repo/src/db.js), lines 42–61; [task mutations](../repo/src/services.js), lines 508–627. |
| T04 | Similar | Dependency insertion checks reachability; next-task selection filters unfinished blockers. Direct claim and task moves do not apply that eligibility rule. Cross-board blockers are also displayed incorrectly by the board projection. [Dependencies/selection](../repo/src/services.js), lines 596–697; [projection](../repo/src/services.js), lines 252–288. |
| T05 | Resembles | Agents and accounting runs are separate durable rows. Runs do not authorize task mutations, and there is no parent-agent/session/attempt relationship. [Agent and run schemas](../repo/src/db.js), lines 15–25 and 104–119; [ledger](../repo/src/services.js), lines 889–942. |
| T06 | Similar | HTTP and MCP return structured records and explicit errors. MCP checks required fields, primitive types and enums. Detail bodies have token budgets, but whole-board and task-list cardinality is unbounded. [MCP dispatcher](../repo/mcp/mcp-server.js), lines 483–532; [reads](../repo/src/services.js), lines 455–505. |
| T07 | Resembles | Claim uses a conditional SQL update and refuses another live holder. Generic update can overwrite the assignee without a claim check; release with an empty actor can clear ownership. [Claim/release](../repo/src/services.js), lines 633–675; [update](../repo/src/services.js), lines 539–581. |
| T08 | Similar | Column limits are checked during creation and moves, and an explicit `force` option bypasses them. They are not limits on claimed execution, and the count/write sequence is not a shared transaction across multiple server processes. [Capacity](../repo/src/services.js), lines 407–418, 508–566. |
| T09 | Absent | Neither task mutations nor MCP tools create a durable delegated parent/child relationship or aggregate children for parent completion. [Task service](../repo/src/services.js), lines 455–709; [tool definitions](../repo/mcp/mcp-server.js), lines 39–418. |
| T10 | Similar | Descriptions, comments, labels and searchable namespaced memory retain useful context. Artifact revision and project-document relationships remain conventions in text. [Comments/memory](../repo/src/services.js), lines 584–593 and 712–784. |
| T11 | Similar | Persistent task comments and activity support progress and handoff. There is no structured result/checkpoint or required handoff record. [Task detail/comments](../repo/src/services.js), lines 455–469 and 584–593. |
| T12 | Similar | Directed messages, broadcasts and per-agent read receipts are durable. SSE gives live refresh hints but has no replay cursor; reconnect marks the UI live without reloading the board. [Messaging](../repo/src/services.js), lines 797–883; [events](../repo/src/events.js), lines 1–16; [client connection](../repo/public/app.js), lines 830–877. |
| T13 | Resembles | The board shows dependency blockers, and agents can message others. There is no question/decision state, leadership escalation or human-answer workflow. [Board projection](../repo/src/services.js), lines 252–288; [messages](../repo/src/services.js), lines 797–844. |
| T14 | Similar | Claims expire and a later claim can replace an expired holder. Agent heartbeats and offline detection are separate; a heartbeat does not renew the task lease. No task-expiry event or checkpoint recovery occurs. [Heartbeat/reaper](../repo/src/services.js), lines 210–226; [claim](../repo/src/services.js), lines 633–661. |
| T15 | Absent | Task updates require no attempt token, row version or idempotency key. A stale worker can move a replacement's task to Done. MCP idempotency annotations do not enforce that invariant. [Update](../repo/src/services.js), lines 539–581; [annotations](../repo/mcp/mcp-server.js), lines 431–460. |
| T16 | Resembles | SQLite retains work and comments, and claims can be manually released or reacquired. There is no supervised worker cancellation, interrupted-attempt state or atomic transition/event recovery. [Database](../repo/src/db.js), lines 137–194; [release](../repo/src/services.js), lines 664–675. |
| T17 | Similar | Remote MCP clients can target one HTTP authority with `HQ_URL`. Workers need not share the SQLite file. This is one service, without authenticated cross-host identities, consensus or failover. [Proxy](../repo/mcp/mcp-server.js), lines 7–35; [listener](../repo/src/server.js), lines 181–195. |
| T18 | Similar | Activity records include actor, timestamp, type and entity. Task writes and activity inserts are separate; an event is not an immutable, transactionally complete journal. [Activity insertion](../repo/src/db.js), lines 183–194; [task update](../repo/src/services.js), lines 566–580. |
| T19 | Similar | Source implements a board, assignee/label filters, task and agent details, activity, memory, messaging, flow and cost views. Task cards support keyboard activation and API failures get an alert. No candidate render or accessibility test was run. [Browser](../repo/public/app.js), lines 20–46, 223–278 and 394–487. |
| T20 | Resembles | Backlog columns, priorities, labels and flow metrics support continuous work. There are no sprint, milestone, estimate or planning-period records in the schema. [Board defaults](../repo/src/services.js), lines 239–249; [flow](../repo/src/services.js), lines 326–404; [schema](../repo/src/db.js), lines 14–135. |
| T21 | Resembles | Review and Done are configurable column names. Any updater can move a task there without acceptance criteria, reviewer identity or a version-bound approval. [Task update](../repo/src/services.js), lines 539–581. |
| T22 | Absent | HTTP routes dispatch without authentication or project permissions. Actor and agent identifiers are supplied by the caller; force/release are not privileged actions. [HTTP dispatch](../repo/src/server.js), lines 130–178; [mutations](../repo/src/services.js), lines 539–675. |
| T23 | Similar | Agent roles, board columns, labels and memory namespaces are configurable data. New authorization rules, task fields and lifecycle behavior require source changes. [Schemas](../repo/src/db.js), lines 15–80; [board/agent creation](../repo/src/services.js), lines 179–249. |
| T24 | Similar | Node standard-library runtime, SQLite, Docker volume and health check keep installation small. Schema changes are ad hoc, large views are unpaginated and backup/restore is not implemented as a product workflow. [Package](../repo/package.json), lines 1–28; [Dockerfile](../repo/Dockerfile), lines 1–19; [database](../repo/src/db.js), lines 167–173. |

## Work lifecycle and alternate paths

1. A client registers an agent or uses an existing actor string. Registration is not required for every claim.
2. A board supplies columns. Task creation stores the initial assignee and column after basic validation and a capacity check.
3. The coordinator adds dependency edges. Reachability is checked before insertion.
4. Next-task selection finds the highest-priority non-Done task with no unfinished blockers and an available reservation.
5. Claim separately updates assignee and lease through a conditional SQL statement. It does not move the card into In Progress.
6. The worker can write comments, messages and accounting runs. These are separate operations, not one execution transaction.
7. Generic update changes status or assignee. Moving to Done is the entire completion path; no result or approval is required.
8. Release clears ownership. Expired ownership is replaced lazily by a new claim; agent offlining does not itself release a task.

This path is concrete, but the interfaces do not share one complete state machine.
An agent can skip next-task selection and claim blocked or Done work directly.
Another client can bypass claim by editing the assignee.
A worker whose lease expired can still update the task because the update operation never checks lease ownership.

## Concurrency and recovery findings

### Claim exclusivity is narrower than work authority

The [claim statement](../repo/src/services.js), lines 652–655, is an actual conditional database mutation.
The competing claimant must satisfy the ownership/expiry predicate.
That is useful implementation depth, not a README-only feature.

However, [generic update](../repo/src/services.js), lines 539–574, copies the current fields and applies an arbitrary assignee patch.
It does not require the caller to hold the reservation.
Release also permits an empty agent to clear a claim, lines 664–672.
These alternate routes prevent the lease from serving as an enforced work authority.

### Readiness, capacity and cycles have different concurrency scopes

Next-task selection and direct claim have different eligibility predicates.
The direct path checks neither dependencies nor column state.
Next selection and claim are separate statements, so another database writer can change readiness between them.
The source does not recheck blockers in the claim update.

Capacity checks and graph-cycle checks are also read/check/write sequences outside a common transaction.
One Node server executes these synchronous handlers without an interleaving `await` inside the relevant sequence.
That local event-loop property does not serialize another process using the database.
Do not describe these checks as global transactional invariants.

### Cross-board blocker visibility disagrees with selection

Dependency insertion accepts any existing task; it does not require the blocker to share the board.
The [board projection](../repo/src/services.js), lines 260–279, builds its task map only from the current board.
Its `isDone` helper treats a missing mapped task as finished.
A blocker on another board therefore disappears from the blocked indicator, while next-task selection joins the actual blocker and can still refuse the task.
This finding follows the code path; it was not reproduced in a running candidate.

### Event and task state can diverge

Task changes and activity insertion are separate writes.
A failure after a mutation can leave the task changed without its corresponding event, even if the request returns an error.
Flow metrics read activity rather than a transactional transition journal.

SSE messages are kept only in an in-memory client set.
The browser reconnect handler marks the connection live but does not fetch a fresh board.
Missed refresh events can leave the board stale until another refresh-producing mutation or a page reload.
The periodic timer refreshes stats only: [browser refresh logic](../repo/public/app.js), lines 830–877.

## Usability, completeness and design quality

The small layering is easy to understand: transport, domain operations, SQLite and browser projection are distinct files.
The MCP proxy has actionable connection failures, required-argument checks and explicit tool errors.
Task detail and memory reads budget long text and announce truncation.
These decisions help agents recover from mistakes without guessing.

The browser source provides meaningful task detail, blocked indicators, filters and error presentation.
It also exposes ordinary task creation and a capacity override.
The default-board design is much narrower than a multi-project manager's workspace.
Board membership does not scope memory, messaging, permissions or agent responsibility.

The main design weakness is that several partial policies coexist without one authority boundary.
Claims, column state, activity and accounting runs can each report a different aspect of work.
No execution-attempt record binds them together.
Adding another dashboard would not resolve that gap.

The cost ledger records caller-supplied token counts and configured model prices.
It does not observe a coding process or enforce a work budget.
The run record therefore remains accounting evidence rather than proof that a task was executed or accepted.

## Test-source review and uncertainty

The [contention test](../repo/test/concurrency.test.js), lines 15–67, uses a worker-thread barrier and independent database imports to race claims.
It checks one winner and no lock errors across repeated tasks.
That exercises a meaningful storage invariant.
The [capacity tests](../repo/test/services.test.js), lines 415–457, check creation, movement, refusal and force override sequentially.

Other inspected test sections cover dependency selection, cycles, filter validation, message recipients and receipts, stale agents, expired reservations, output budgets and name/ID compatibility.
These are substantive tests in source.
They do not establish that alternate mutations enforce leases, that capacity is safe across processes, or that a stale worker cannot finish a replacement's work.
No test was executed for this assessment.

Installation, actual browser behavior, accessibility, recovery after process failure and cross-host operation remain unobserved.
The report distinguishes these limits from the specific implementation defects identified above.

## Adoption work

1. Introduce project membership and durable accountable roles.
2. Define a task/attempt model and enforce it in every mutation, including reassignment, release, move and completion.
3. Apply readiness and capacity rules within the authoritative claim transaction.
4. Add parent/child relationships and explicit parent acceptance.
5. Add authentication, project permissions and recorded privileged overrides.
6. Persist transitions and notifications together, and resynchronize views after reconnect.
7. Add revision-bound results and review, with stale-attempt rejection.
8. Define backup, restore, schema upgrades and limits for growing boards.

The useful components are the compact HTTP/MCP surface, readable SQLite model, agent-friendly validation, message receipts and connected operator views.
Adopting the product as-is would leave the central ownership and verification requirements to cooperative agent behavior.

## Source review record

The [review ledger](review.json) records the revision, inspected source ranges, file hashes and review status.
It is an inventory of evidence, not proof that every line of the repository was audited.
