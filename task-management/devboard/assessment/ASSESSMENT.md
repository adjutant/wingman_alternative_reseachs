# DevBoard task management assessment

Repository: https://github.com/RapidWebs-Enterprise/DevBoard

Commit: `cbe017a445fd4f9dee2de73f729c65b7fe0f9b9b`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 8, 2026. Full local checkout, static implementation review. Candidate code and tests were not executed.

## Fit decision

DevBoard is a small file-based tracker with a CLI, an agent-tool plugin and generated Markdown views.
It can support a trusted single writer who wants visible task files and simple priority selection.
It should not coordinate independent workers that compete for ownership.

The ownership operation is not atomic, task ID allocation races, and writes can lose a task during failure.
The advertised configurable timeout is not used by expiry checks.
Alternate status changes bypass both ownership and capacity rules.
These are implementation defects or incomplete mechanisms at the pinned revision, not merely missing enterprise features.

Its MIT license and small Python dependency set make inspection easy.
The coordination and durability gaps are large enough that adopting a different task store is preferable to relying on these claims as the shared authority.

## Architecture and retained state

The main implementation is a [Task dataclass and DevBoard class](../repo/src/devboard/__init__.py).
Tasks are Markdown bodies with YAML frontmatter.
A board directory holds `config.yml`, a `tasks/` directory, an activity log and generated coordination documents.
The [CLI](../repo/src/devboard/cli.py), lines 23–30, discovers a board by walking upward from the current directory.
The [Hermes plugin](../repo/hermes-plugin/rapidwebs-devboard/__init__.py), lines 23–35 and 182–228, exposes tool calls that invoke the same Python methods.
It does not provide a remote coordination server or a coding-worker runtime.

The [task model](../repo/src/devboard/__init__.py), lines 76–218, includes status, priority, timestamps, agent and claimant strings, dependencies, a project string, service class, tags, due date and body.
There are no project entities, agent sessions, execution attempts, parent tasks, comments, review records or authentication credentials.
Changing source metadata requires adapting the fixed serializer; unknown frontmatter fields are not preserved by its explicit parse-and-write model.

The [board implementation](../repo/src/devboard/__init__.py), lines 339–433, reads and writes config and task files directly.
`next_id` changes a counter in the config file.
`save_task` writes directly to the final task path and deletes the old path before a rename is written.
No lock, transaction, conditional version check or atomic replacement protects these operations.

## Requirement assessment

| ID | Verdict | Implementation and boundary |
|---|---|---|
| T01 | Resembles | Tasks have a project string, list filtering and generated groups. Projects do not have stable entities, leaders, scope or access boundaries. [Task model](../repo/src/devboard/__init__.py), lines 76–99; [overview](../repo/src/devboard/__init__.py), lines 818–859; [list filter](../repo/src/devboard/cli.py), lines 291–355. |
| T02 | Similar | Task IDs, descriptions, priority, state and dates persist in readable files. Counter allocation is unsafe under concurrent creation, and parsing replaces the saved updated timestamp in memory. [Model/parser](../repo/src/devboard/__init__.py), lines 101–218; [ID allocation](../repo/src/devboard/__init__.py), lines 386–416. |
| T03 | Absent | The complete model, add/edit operations and plugin surface have no parent/child relationship or linked follow-up type. [Model](../repo/src/devboard/__init__.py), lines 76–99; [creation](../repo/src/devboard/__init__.py), lines 594–616; [edit](../repo/src/devboard/cli.py), lines 602–661. |
| T04 | Similar | Pick and claim check that dependencies are Done. Cycle inspection exists, but adding/saving tasks does not enforce it. Generic moves can bypass readiness, and their auto-unblock ordering differs from completion. [Dependencies/move/add](../repo/src/devboard/__init__.py), lines 520–616. |
| T05 | Resembles | Agent and claimant names are strings on a task. Random-name generation is not an identity registry. There are no session, parent-agent or attempt records. [Model](../repo/src/devboard/__init__.py), lines 76–99; [name generator](../repo/src/devboard/__init__.py), lines 802–814. |
| T06 | Similar | CLI JSON modes and Hermes dictionary results support agent operations. There is no network API or MCP service, and many commands load the whole board. [CLI pick](../repo/src/devboard/cli.py), lines 474–507; [plugin operations](../repo/hermes-plugin/rapidwebs-devboard/__init__.py), lines 182–230. |
| T07 | Absent | Claim reads, checks and writes without a lock or compare-and-swap. Pick invokes that same operation. Two claimants can both succeed. The design note explicitly acknowledges separate reads and writes. [Claim](../repo/src/devboard/__init__.py), lines 437–478; [design note](../repo/docs/adrs/0003-atomic-claims.md), lines 9–21. |
| T08 | Resembles | Claim counts In Progress tasks per agent and applies the configured In Progress limit, except for expedited work. Moves do not enforce capacity, and the Review limit is not a general mutation gate. [Claim capacity](../repo/src/devboard/__init__.py), lines 455–464; [move](../repo/src/devboard/__init__.py), lines 565–590. |
| T09 | Absent | Tools create or assign flat tasks. They do not persist delegation, coordinate parallel children or gate parent completion. [Add/pick](../repo/src/devboard/__init__.py), lines 594–652; [plugin registration](../repo/hermes-plugin/rapidwebs-devboard/__init__.py), lines 23–35. |
| T10 | Resembles | Markdown bodies and project/tag fields can hold instructions and links. There is no artifact record, revision binding or retained project document relationship. [Serialization](../repo/src/devboard/__init__.py), lines 145–218. |
| T11 | Resembles | A worker can replace the body and read activity. There are no append-only task comments, structured results or checkpoints. Body edits are ordinary rewrites. [CLI edit](../repo/src/devboard/cli.py), lines 615–661; [activity](../repo/src/devboard/__init__.py), lines 771–798. |
| T12 | Absent | The source has no durable inbox, delivery queue, notification subscription or missed-event cursor. Plugin session hooks log counts and regenerate the overview only. [Plugin hooks](../repo/hermes-plugin/rapidwebs-devboard/__init__.py), lines 317–335; [activity read](../repo/src/devboard/__init__.py), lines 777–798. |
| T13 | Resembles | Dependencies and an optional Blocked state can show obstacles. Blocked is not in the default configured states, and no question/decision/escalation model exists. [Defaults](../repo/src/devboard/__init__.py), lines 317–325; [dependency handling](../repo/src/devboard/__init__.py), lines 520–561. |
| T14 | Resembles | A fixed one-hour age check can make a claim available again. The saved timeout and claim method's timeout argument do not control it. There is no renewal heartbeat; default pick does not recover expired In Progress work. [Expiry](../repo/src/devboard/__init__.py), lines 126–141; [claim/pick](../repo/src/devboard/__init__.py), lines 437–478 and 620–652. |
| T15 | Absent | No attempt token, task version or idempotency key exists. Complete compares a caller-supplied name; move and edit require no ownership. [Complete](../repo/src/devboard/__init__.py), lines 495–516; [move](../repo/src/devboard/__init__.py), lines 565–590; [edit](../repo/src/devboard/cli.py), lines 627–661. |
| T16 | Resembles | Files persist between invocations, and release can clear the claimant. There is no interrupted-attempt recovery or transaction across task, log and overview. Direct writes and delete-before-rename can lose data. [Storage](../repo/src/devboard/__init__.py), lines 418–433; [release](../repo/src/devboard/__init__.py), lines 480–491. |
| T17 | Absent | CLI and plugin operate on local paths. There is no authoritative remote service, replica synchronization or cross-host locking protocol. Sharing a directory does not repair the claim race. [Discovery](../repo/src/devboard/cli.py), lines 23–30; [claim](../repo/src/devboard/__init__.py), lines 437–478. |
| T18 | Resembles | JSONL activity has action, task and actor information. It is a separate append after mutation and can omit failed/partial operations. Parsing also overwrites a task's stored update time in memory. [Activity](../repo/src/devboard/__init__.py), lines 771–798; [post-init/parser](../repo/src/devboard/__init__.py), lines 101–105 and 199–218. |
| T19 | Similar | Terminal commands provide status, list filters, detail, board summary, log and flow; generated Markdown groups projects. No browser UI exists. Actual terminal framing and usability were not exercised. [CLI](../repo/src/devboard/cli.py), lines 131–229, 291–459 and 721–820; [overview](../repo/src/devboard/__init__.py), lines 818–859. |
| T20 | Resembles | Priority, service classes, due dates, backlog states and flow metrics support lightweight planning. There are no milestone/iteration entities or a planning calendar. [Fields](../repo/src/devboard/__init__.py), lines 76–99; [metrics](../repo/src/devboard/__init__.py), lines 684–767. |
| T21 | Resembles | Review is a state name. Complete requires the claimant's name but no result, acceptance checklist or reviewer decision; move to Done bypasses even that name check. [Completion/move](../repo/src/devboard/__init__.py), lines 495–516 and 565–590. |
| T22 | Absent | Filesystem access is the trust boundary. Actor strings are not authenticated, and all plugin/CLI users can call unrestricted moves and edits. [CLI edit](../repo/src/devboard/cli.py), lines 627–661; [plugin move](../repo/hermes-plugin/rapidwebs-devboard/__init__.py), lines 275–285. |
| T23 | Resembles | Configured status lists and labels provide some variation, but add, claim, expiry, completion, metrics and generated views hardcode default semantics. The fixed serializer drops unknown fields. [Config](../repo/src/devboard/cli.py), lines 84–98; [claim/add](../repo/src/devboard/__init__.py), lines 437–478 and 594–616; [serializer](../repo/src/devboard/__init__.py), lines 145–218. |
| T24 | Resembles | Small Python package and plain files are portable. The minimum Python version is inaccurate, durable writes and backup/migration workflows are incomplete, and repeated full scans limit scale. [Package](../repo/pyproject.toml); [imports](../repo/src/devboard/__init__.py), lines 15–26; [load/save](../repo/src/devboard/__init__.py), lines 396–433. |

## End-to-end lifecycle

Initialization writes states, priorities, WIP settings, a timeout and an ID counter.
Creation increments the counter and writes a Backlog task.
Pick scans tasks, filters by status/tags/readiness, orders by priority and calls claim.
Claim reloads the selected task, checks availability, dependencies and the claimant's capacity, then rewrites it as In Progress.

The worker edits the task body or other fields through a separate read-modify-write operation.
Completion compares the claimant name, saves Done, logs the event, updates dependents and rebuilds the overview.
Generic move is an alternate completion route with different ownership and ordering behavior.
The plugin calls the same methods and does not add a safer storage or authorization boundary.

## Coordination defects and failure conditions

### Concurrent claims and IDs can both collide

[Claim](../repo/src/devboard/__init__.py), lines 443–475, performs availability and readiness reads before an unguarded file write.
Two processes can both observe availability and then overwrite one another.
The design note's atomic-claim title does not change the implementation.

[ID allocation](../repo/src/devboard/__init__.py), lines 386–392, likewise reads and rewrites an unlocked counter.
Two creators can obtain the same ID.
With matching titles they target the same path; with different titles they produce multiple files that claim one ID.
Lookup returns the first matching task rather than refusing ambiguity, lines 411–416.

### Storage does not protect a task from partial writes

`save_task` writes directly to the destination path.
A process failure during the write can leave a truncated file.
Renaming first deletes the prior file and then writes its replacement, lines 425–431.
A failure between those steps can remove the only task record.
Malformed records are skipped with a warning by `load_tasks`, so the board can omit damaged work instead of exposing it as a recovery item.

Task, activity and overview changes are independent writes.
The overview is a projection, but there is no repair command that proves task/log consistency after interruption.

### Expiry does not follow configuration or the normal recovery queue

The CLI stores `claim_timeout`, and `claim_task` accepts a timeout argument.
The [expiry property](../repo/src/devboard/__init__.py), lines 126–134, uses the constant one-hour default instead.
The argument is not used in the claim body.
Changing the advertised setting therefore does not change claim expiry in this source revision.

Default pick selects Backlog only.
An abandoned claim remains In Progress, so it is not selected by the normal default queue even after expiry.
Direct claim can recover it, but that operation also lacks a status eligibility check.
It can reclaim an expired Done task and write In Progress without a deliberate reopen operation.

### Alternate completion is not equivalent

`complete_task` saves the predecessor before checking and releasing dependents.
`move_task(..., 'done')` calls auto-unblock before saving the predecessor.
The helper reloads the predecessor from disk, sees the old status and can leave its dependents Blocked.
The complete path also checks the claimant name, while move does not.
See [both paths](../repo/src/devboard/__init__.py), lines 495–590.

### Reading changes the reported update time

`from_file` passes the stored updated field into Task construction.
`__post_init__` immediately overwrites it with the current time, lines 101–105 and 199–205.
An ordinary read therefore reports a fresh in-memory update time even when nobody changed the task.
This weakens stale-work inspection and serialized round trips.
The finding follows construction and parsing; it was not reproduced by executing the candidate.

## Usability and operating design

Plain Markdown plus YAML is inspectable and easy to version with a repository.
The CLI has useful project, assignee, priority and tag filters.
The Hermes adapter exposes structured results and shares the core implementation rather than creating another store.
Generated Markdown is convenient for a small board.

The architecture remains synchronous full-file scanning.
Finding each dependency reloads tasks, and overview generation loads them again.
The log reader reads the complete log before taking its last requested entries.
These costs are acceptable only within an assessed small-board workload; no performance measurement was made here.

Configuration support is incomplete.
The CLI accepts custom states, but creation still writes Backlog and claim still writes In Progress.
Capacity and completion also depend on hardcoded state names.
A configured vocabulary can therefore disagree with the mutation paths.

Packaging declares Python 3.10 or later, while the module imports `datetime.UTC`.
Python documents that constant as added in 3.11, so the package's stated minimum permits an interpreter that cannot import this module as written.
Reference: https://docs.python.org/3/library/datetime.html#datetime.UTC

Installation, actual CLI JSON framing, plugin integration, throughput and recovery remain untested.

## Test-source review and completeness

The inspected tests cover task serialization, a second sequential claim, claimant-name completion, ordinary dependencies, capacity, invalid states, cycle detection, completion-based unblocking and simple metrics.
See [tests](../repo/tests/test_devboard.py), lines 61–94, 113–140, 150–166, 199–215 and 245–287.

The sequential second-claim test does not simulate two processes passing the availability check together.
The cycle test deliberately saves a cycle and then detects it; it does not prove insertion prevents cycles.
The unblock test uses `complete_task`, so it does not exercise move-to-Done's different write order.
No candidate test was run.

The principal implementation is readable and small enough to trace end to end.
Its claims, configuration, mutation rules and recovery behavior do not yet form a consistent coordinator for independent agents.
The missing project/leadership, delegation, review and communication models also require substantial additions.

## Adoption work and useful parts

Use the Markdown shape, simple filtering and human-readable overview as design references.
For autonomous coordination, replace or redesign the storage authority before extending the interface.
It needs transactional ID allocation and claims, safe writes, one state machine for every mutation, enforced expiry and recovery, durable attempts, project identities, permissions, structured handoff and versioned acceptance.

The [review ledger](review.json) records source ranges and hashes supporting this assessment.
It does not claim that static inspection establishes a successful deployment or a runtime result.
