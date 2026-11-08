# agent-kanban-rs task management assessment

Repository: https://github.com/fxeqxmulfx/agent-kanban-rs

Commit: `3ab1218eac51edca8556e6dfbeea322477e7a444`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 8, 2026. Full local checkout, static implementation review. Candidate code and tests were not executed.

## Fit decision

This is a coherent local coordination tool for cooperating developer and reviewer agents.
It has substantially more lifecycle enforcement than a board whose cards simply change columns.
Claims, dependency checks, guarded edits, review submission and acceptance decisions have real database invariants.

Evaluate it as a small single-host work queue and as a reference for transactional lifecycle design.
It does not supply a project-management service for the complete baseline.
There is no project registry, durable delegation hierarchy, authenticated remote access, execution-attempt identity or general progress/checkpoint record.
Two sessions using the same agent name remain indistinguishable when one reclaims a task.

The source is MIT licensed.
Its compact CLI and explicit SQLite rules are useful components, but turning it into a shared multi-host project system would require a service and a richer identity/context model.

## Architecture and domain model

The application is a Rust command-line program.
[Command dispatch](../repo/src/main.rs), lines 400–503, routes creation, list/detail, claim, review, editing, export/import, mail and waiting into separate modules.
Each invocation discovers one local `.kanban/board.db` or uses an explicit `--db` path.
There is no daemon or HTTP/MCP server in that command surface.

The [schema](../repo/src/db.rs), lines 22–128, has agents, tasks, dependencies, acceptance results, review history and messages.
Roles are the fixed enum Developer and Reviewer.
Task states are Backlog, Todo, In Progress, Review and Done.
Each task requires at least one acceptance specification, stores a revision number and can have an executor with a claim time and lease expiry.
SQL checks require the ownership fields to be present or absent together.

Task IDs use `AUTOINCREMENT` to avoid reusing a deleted task's identifier.
Review and acceptance records copy the executor name, so attribution remains meaningful after an agent is removed.
There is no task description, project entity, parent task, session identity or separate attempt row.
Acceptance specifications and messages carry most contextual information.

The [database opener](../repo/src/db.rs), lines 146–184, sets a busy timeout, WAL and foreign keys.
[Lifecycle writes](../repo/src/commands/lifecycle.rs), lines 31–37, acquire an Immediate transaction before checking mutable state.
This protects the check/write span across processes, rather than relying on one process's event loop.

## Requirement assessment

| ID | Verdict | Implementation and boundary |
|---|---|---|
| T01 | Resembles | Separate database paths distinguish workspaces. There is no project entity, project leader or portfolio registry within the schema. [Discovery](../repo/src/db.rs), lines 6–19 and 131–184; [schema](../repo/src/db.rs), lines 22–128. |
| T02 | Similar | Durable non-reused task IDs, priority, states, dates, criteria and revision exist. Outcome/context is narrow because there is no description or artifact model. [Task schema](../repo/src/db.rs), lines 33–54; [creation](../repo/src/commands/task.rs), lines 23–84. |
| T03 | Absent | The complete task schema and create/edit command shapes contain dependencies but no parent, child or follow-up provenance relationship. [Schema](../repo/src/db.rs), lines 33–104; [commands](../repo/src/commands/task.rs), lines 47–84 and 303–405. |
| T04 | Exact | Developer claims use the same dependency predicate inside the authoritative mutation. Graph changes hold an Immediate transaction; imports validate missing prerequisites and cycles. Scope is the cooperating local CLI and its supported import path. [Claims](../repo/src/commands/lifecycle.rs), lines 89–99 and 153–174; [edges](../repo/src/commands/deps.rs), lines 76–119; [import graph checks](../repo/src/commands/full_dump.rs), lines 1089–1148. |
| T05 | Resembles | Durable agents and revisioned review results exist, but a claimant identifies an agent name, not a process/session/attempt. Two invocations using one name share authority. [Identity/claim](../repo/src/commands/lifecycle.rs), lines 40–97; [model](../repo/src/db.rs), lines 33–95. |
| T06 | Similar | CLI commands have a compact escaped record format, bounded default listing and actionable refusals. It is not JSON or an authenticated service API, and inbox/full exports can be unbounded. [List](../repo/src/commands/task.rs), lines 87–108 and 174–207; [work order](../repo/src/commands/view.rs), lines 207–265; [dispatch](../repo/src/main.rs), lines 412–503. |
| T07 | Similar | Claims condition on state, owner/expiry and readiness under a write transaction. Ordinary edit, remove and move paths preserve the live-lease and review boundaries. Agent removal and full restore remain unrestricted administrative operations in the same filesystem trust domain. [Claim](../repo/src/commands/lifecycle.rs), lines 149–177; [edit/remove](../repo/src/commands/task.rs), lines 370–399 and 450–467; [agent removal](../repo/src/commands/agent.rs), lines 107–172. |
| T08 | Resembles | Claim-next prioritizes already held work, unfinished work, priority and age. Direct claim can acquire multiple different tasks, with no WIP or per-role capacity limit. [Selection](../repo/src/commands/lifecycle.rs), lines 245–282; [direct claim](../repo/src/commands/lifecycle.rs), lines 153–174. |
| T09 | Absent | Agents can create tasks and dependencies, but there is no delegated child ownership, parent coordination or parent completion operation. [Task creation](../repo/src/commands/task.rs), lines 47–84; [schema](../repo/src/db.rs), lines 33–128. |
| T10 | Resembles | Titles, acceptance triples, tags, review notes and task-linked mail can carry context. There is no project knowledge store, source/artifact reference type or immutable artifact binding. [Criteria](../repo/src/commands/task.rs), lines 31–54; [mail](../repo/src/commands/mail.rs), lines 38–68. |
| T11 | Resembles | Submission records a result and evidence for every criterion; reviewer notes return with the next work order. There is no general checkpoint or append-only task progress/comment interface. [Submission](../repo/src/commands/lifecycle.rs), lines 334–408; [handoff](../repo/src/commands/view.rs), lines 187–223. |
| T12 | Similar | Durable task-linked mail, unread hints and polling waits support cooperation. Inbox marks messages read before CLI output is delivered; there is no separate acknowledgement/replay command. [Mail](../repo/src/commands/mail.rs), lines 17–107; [wait](../repo/src/commands/wait.rs), lines 23–53. |
| T13 | Resembles | Readiness and status expose dependency blockers; mail can carry a question. There is no structured decision, management escalation or human-answer workflow. [Status](../repo/src/commands/status.rs), lines 23–80; [mail](../repo/src/commands/mail.rs), lines 38–68. |
| T14 | Similar | Claims carry a configurable duration, repeated claim renews it, expired work is reclaimable and status hides expired holders. There is no process heartbeat or attempt-aware liveness supervisor. [Claim predicates](../repo/src/commands/lifecycle.rs), lines 79–99 and 245–282; [status](../repo/src/commands/status.rs), lines 48–53. |
| T15 | Resembles | A stale different owner or expired lease cannot submit/review. A stale session using the same durable agent name can regain authority after that identity reclaims the task; no fencing token or request idempotency key distinguishes attempts. [Ownership check](../repo/src/commands/lifecycle.rs), lines 136–145 and 418–440. |
| T16 | Similar | Transactional mutations roll back on refusal, leases allow replacement, release retains task state and removing an agent releases its tasks atomically. There are no explicit failed/interrupted/cancelled attempt states or work checkpoints. [Write wrapper](../repo/src/commands/lifecycle.rs), lines 31–37; [release](../repo/src/commands/lifecycle.rs), lines 592–615; [agent removal](../repo/src/commands/agent.rs), lines 107–172. |
| T17 | Absent | The supported authority is one SQLite file opened by local processes. No network transport, authenticated remote worker service or replica protocol exists in the complete command dispatcher. Remote invocation would be an added integration. [Discovery/open](../repo/src/db.rs), lines 131–184; [dispatch](../repo/src/main.rs), lines 412–503. |
| T18 | Resembles | Review decisions and per-criterion evidence have revision and copied actor attribution. Claims, edits and ordinary state changes have no complete event journal. Removing eligible tasks also removes their attached history. [History schema](../repo/src/db.rs), lines 71–95; [mutations](../repo/src/commands/task.rs), lines 336–467. |
| T19 | Similar | Status, filtered list, detail, review history and wait provide usable terminal inspection surfaces. Listing defaults to 20 and reports hidden results. There is no browser/project overview. Actual terminal or accessibility behavior was not tested. [List](../repo/src/commands/task.rs), lines 87–108 and 174–207; [detail](../repo/src/commands/view.rs), lines 228–265; [status](../repo/src/commands/status.rs), lines 23–80. |
| T20 | Resembles | Backlog/Todo, priority and tags support ordering. No milestones, dates for planning, estimates, iterations or portfolio planning are modeled. [Schema](../repo/src/db.rs), lines 33–54; [move](../repo/src/commands/lifecycle.rs), lines 553–573. |
| T21 | Similar | Every task needs criteria. Submission requires complete non-empty evidence; approval requires a reviewer holding a live lease and all results passing for the current revision. Evidence is reported text, not executed verification, and revision is not a source commit. [Submission/approval](../repo/src/commands/lifecycle.rs), lines 334–408 and 485–550. |
| T22 | Resembles | Roles and mutation guards are real application rules, but `--agent` is a freely supplied name. Local database access grants administrative capabilities including agent removal and replacement imports. There is no authenticated principal or project permission boundary. [Role lookup](../repo/src/commands/lifecycle.rs), lines 45–76; [admin paths](../repo/src/main.rs), lines 417–420 and 450–453. |
| T23 | Resembles | Tags, criteria and explicit database paths vary data. Roles, states, schema and output grammar are fixed in code; new management roles or workflows require changes. [Role enum](../repo/src/commands/agent.rs), lines 7–48; [schema](../repo/src/db.rs), lines 33–64. |
| T24 | Similar | Single binary, bundled SQLite, schema versions, migrations and full transactional dump/load are concrete operating features. Requires the declared Rust toolchain to build; no deployment, restore rehearsal or scale measurement was performed. [Package](../repo/Cargo.toml), lines 1–31; [migration](../repo/src/db.rs), lines 266–312; [export/import](../repo/src/commands/full_dump.rs), lines 169–256. |

## Lifecycle and mutation authority

Creation validates the title, priority and non-empty acceptance list.
It inserts the task and dependencies in one Immediate transaction.
Unknown or cyclic prerequisites reject the transaction.

A developer claims Todo or reclaimable In Progress work.
The claim statement checks unfinished dependencies and updates ownership and state together.
Claim-next uses one update with a selection subquery, rather than a separate availability read followed by an unguarded write.
Repeated claims by the current identity renew its lease.

Submission checks the live holder and requires one result per criterion, without duplicates or empty evidence.
It increments the revision, stores the results, clears ownership and moves to Review atomically.
A reviewer claims Review work and receives the developer's results.
Approval checks that every result in that revision exists and passed.
Requesting changes requires notes and returns the task to unclaimed In Progress work.

Ordinary moves only operate between Backlog and Todo.
They cannot bypass review by moving directly to Done.
Edits and removal reject live claims, Review and Done.
Dependency edits share a transaction with the guarded task update.
This is a consistent normal lifecycle, with important administrative exceptions below.

## Concurrency and recovery boundaries

### Shared predicates and upfront write locking

The [ready predicate](../repo/src/commands/deps.rs), lines 8–15, is reused by direct and next-task developer claims.
Cycle checks run while their caller holds the write lock.
This avoids the split selection/claim and check/write gaps found in several simpler trackers.
The schema also prevents partially populated ownership fields and Done tasks retaining an executor.

The reviewed code does not establish a performance result.
SQLite still serializes writers, and a busy timeout can fail after contention rather than guaranteeing progress.
The design is appropriate to a local cooperative queue, not distributed consensus.

### Agent identity does not fence an old attempt

[Submission and review checks](../repo/src/commands/lifecycle.rs), lines 418–440, compare current executor and live expiry.
They do not compare an attempt token.
An old invocation of agent Alice is rejected while Alice's lease is expired or another agent owns the task.
If a new Alice invocation claims it, the old invocation using the same name can satisfy the renewed identity check.

The task revision protects submitted result history, not process identity or external code changes.
This distinction matters when a project leader expects a restarted agent to invalidate all of its prior sessions.

### Administration shares the worker's trust boundary

Any local caller can remove a registered agent; the [removal transaction](../repo/src/commands/agent.rs), lines 107–172, clears all of that agent's leases.
Any caller with filesystem access can also invoke `load --replace`.
[Replacement import](../repo/src/commands/full_dump.rs), lines 185–256, deletes and restores board state in one transaction.
It is a deliberate maintenance facility, but there is no separate privileged principal or active-worker drain protocol.

Restoring data is not a promise that old workers are fenced.
Operators would need to quiesce workers and define ownership recovery around a restore.
The normal CLI's guarded mutations should not be generalized into an authenticated security boundary.

### Message retrieval is not acknowledged delivery

[Inbox](../repo/src/commands/mail.rs), lines 74–107, marks all unread messages read in its transaction and returns their text.
The database change commits before the process prints its result.
A broken output pipe or lost caller response can therefore consume messages without the recipient seeing them.
Full export retains the underlying messages, but normal inbox has no separate acknowledgement or replay selector.
The unread hint is useful; it is not an exactly-once delivery guarantee.

## Human and agent usability

The CLI deliberately keeps responses compact.
Work orders include criteria and reviewer evidence; rework includes the latest requested changes.
Filtered lists report omitted tasks instead of silently truncating them.
Status shows columns, blockers and live task holders.
These source-level interface decisions suit agents working on a small local board.

The data model is narrow for project leadership.
There is no long description, durable project specification, shared decision record, dedicated progress note or parent outcome.
Free-text mail and acceptance fields can carry references, but they do not make those relationships inspectable entities.
Human inspection is terminal-based; a browser board would be an additional interface.

No process is launched or monitored by the tracker.
The external agent must execute work, renew ownership, record truthfully what it verified and respond to mail.
One criterion may be satisfied by any non-empty evidence text; the tracker cannot verify the truth of that report.

## Completeness and operating design

The small module boundaries are clear: command parsing, persistence, lifecycle, dependency graph, mail and output projection.
Database constraints reinforce application checks.
Unlike a flexible status editor, alternate ordinary commands do not silently bypass the acceptance path.

Migration uses schema-version checks and a transaction, while task IDs remain non-reused across deletion and supported restore.
Full dump reads a snapshot, checks that its result can be loaded, and preserves criteria, history, mail and the next-ID high-water mark.
Import checks cross-record references and dependency cycles before its transaction commits.
See [dump/load](../repo/src/commands/full_dump.rs), lines 169–256 and 1045–1148.

These are meaningful completeness features for a local tool.
They do not supply backups scheduled off-host, high availability, a fleet identity model or an operator access policy.
The overview uses several reads rather than one consistent read snapshot, so concurrent changes can also make its counts represent slightly different moments.

## Test-source review

The [claim race tests](../repo/tests/claim_race.rs), lines 13–125, launch separate processes for repeated contention on developer and reviewer claims.
They check one winner, useful refusal errors and agreement between the returned work order and stored state.
They also explicitly test same-agent overlapping claims as renewals.
These tests target actual process concurrency rather than only sequential calls.

Inspected implementation tests and test declarations cover dependency rules, guarded edits/removal, role restrictions, complete review results, mail retrieval, formatting, migration and export/import.
The repository also has mutation, claim-next and initialization race test files.
No tests or candidate binary were executed in this study.
Their presence is evidence of intended checks, not a current pass result.

Installation, terminal behavior, restore under real failure, sustained contention and coordination through a remote invocation layer remain unobserved.

## Adoption work

For the full baseline, add durable projects and leadership, decomposition and parent completion, richer context and progress records, and an authenticated service for workers on different hosts.
Introduce per-attempt fencing rather than identifying an execution only by agent name.
Separate worker and maintenance privileges, add acknowledged message consumption, and bind acceptance to the actual delivered artifact revision.

Retain the transactional lifecycle, shared readiness predicate, explicit review results, guarded edits and non-reused task identifiers as useful design patterns.
The [review ledger](review.json) records the source evidence and its limits.
