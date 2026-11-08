# Beads task management assessment

Repository: https://github.com/gastownhall/beads

Commit: `2edea9ced8c6f6124b6c157896ae53a0e09ff7be`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 9, 2026. Full local checkout; targeted static implementation and selected test-source review.
Candidate applications, databases, dependencies, builds and tests were not installed or run.

## Fit decision and assessment boundary

Beads is a substantial native task authority for agents, rather than a board-shaped interface over uncoordinated files.
It implements durable issues, dependency-aware ready work, atomic claims, claim-next selection, hierarchical work, comments, change journals, revisions and claim leases with heartbeat/reclamation.
CLI, Go role interfaces, HTTP and an included MCP adapter make those records accessible to agents.
It is a strong candidate for the task-record component of the baseline.

It does not implement a complete agent organization.
Actors are caller-asserted provenance, not authenticated worker identities.
Revision guards are optional and do not establish a mandatory execution-attempt token.
The service does not launch or supervise child workers, enforce worker capacity or bind qualified reviewer approval to a delivered revision.
Its charter deliberately leaves orchestration policy above the issue primitives.
See [claim contract](../repo/issueops/claimer.go), lines 35–67, and [project charter](../repo/engdocs/PROJECT_CHARTER.md), lines 1–60.

Several distinctions materially affect adoption.
A named claim and claim-next do different work: the latter selects from a ready set, while the former checks status/assignment eligibility without querying readiness.
Durable claims have local leases; ephemeral work can be claimed without a lease or durable claim history.
Close verbs have holder and pin guards that a generic status patch into a done state does not apply.
These are source-level boundaries, not failures reproduced by running the product.

The repository is MIT licensed.
The preserved checkout contains 5,315 tracked files.
This review traces the shared task mutation bodies, Dolt wrappers/retries, ready/dependency predicates, leases and replicas, close/update alternates, HTTP authorization/events, molecule advancement and representative MCP forwarding.
It is not an every-line audit of every command, tracker integration, migration, backup/repair path or storage driver.
Source/test inspection does not establish successful installation, runtime concurrency, database durability, performance or live usability.
See [license](../repo/LICENSE) and [review ledger](review.json).

## Architecture and data model

The task model includes title, description, design, acceptance text, notes, status, priority, type, assignee, human owner, dates, external references, metadata, labels, dependencies and comments.
It also carries template/pin, async gate, formula/molecule and persistence-plane fields.
A detail projection can expose an opaque lifecycle revision while generic issue JSON deliberately omits the internal row token.
Lease fields are hydrated from a separate node-local table.
This is richer than a minimal ticket/status schema, but it is not a separate task-versus-execution-attempt model.
See [issue model](../repo/internal/types/types.go), lines 20–208.

Public roles separate lifecycle, reads, claims, ready claims, heartbeat, reclaim, graph operations and other capabilities.
Common transaction bodies sit below storage adapters.
A [static public role inventory](catalogue.json) is retained separately from implementation-body coverage.
The reviewed Dolt claim/ready-claim wrappers and embedded lifecycle wrapper delegate to those bodies rather than each implementing a different business rule.
HTTP reaches role accessors, while the Python MCP client invokes the CLI for its claim operation.
See [claim role](../repo/issueops/claimer.go), [ready-claim role](../repo/issueops/readyclaimer.go), [Dolt wrapper](../repo/internal/storage/dolt/issue_claimer.go), [embedded wrapper](../repo/internal/storage/embeddeddolt/issue_operations.go), lines 1–82, and [MCP forwarding](../repo/integrations/beads-mcp/src/beads_mcp/bd_client.py), lines 609–628.

Dolt provides the versioned store, in server and embedded configurations, with further unit-of-work/proxy layers.
The workspace declares Go 1.27.3 and specific Dolt/driver dependencies.
Contributor builds and test lanes use Bazel.
The public issueops package also marks its compatibility contract experimental and asks embedders to pin an exact version.
These are the pinned repository's requirements; no local build or database-mode compatibility result is claimed.
See [API stability](../repo/issueops/issueops.go), lines 1–6.
See [module metadata](../repo/go.mod), lines 1–55, and [contributor instructions](../repo/AGENTS.md), lines 121–180.

The source distinguishes an SQL transaction's durable branch working set from a later Dolt history commit.
The operation funnel commits SQL first and then attempts the history commit.
Failure of that trailing history step is logged rather than returned as though the task mutation failed.
Concurrent sessions may also have one writer's history commit absorb another writer's rows under its message.
Task events and version records therefore matter separately from grepping Dolt commit messages.
See [operation funnel](../repo/internal/storage/dolt/issue_operations_tx.go), lines 11–103.

## Requirement verdicts

The verdicts describe native mechanisms and their limits against the baseline.
They do not turn feature counts into a ranking or certify Dolt's implementation.

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Workspace stores, issue prefixes, source-repository routing and external references separate project data. This is not an organizational project registry with project managers, portfolio outcomes and tenant policies. [Model/routing](../repo/internal/types/types.go), lines 110–155; [scope charter](../repo/engdocs/PROJECT_CHARTER.md), lines 1–60. |
| T02 | Similar | Durable issues have stable IDs, outcome/acceptance text, metadata, dates, relationships and versioned changes. Ephemeral/no-history planes deliberately have different retention and audit semantics. No separate immutable execution result is required. [Model](../repo/internal/types/types.go), lines 20–208; [creation](../repo/internal/storage/issueops/execution.go), lines 37–137. |
| T03 | Similar | Parent-child dependencies, child IDs, labels, molecules and typed relationship records support decomposition. Creation writes its requested relationships atomically or refuses missing edges. Child work does not imply a launched/supervised child agent. [Creation](../repo/internal/storage/issueops/execution.go), lines 37–137; [dependency editor](../repo/internal/storage/issueops/dependency_editor.go), lines 119–170. |
| T04 | Similar | Shared readiness predicates, dependency type/hierarchy checks, recursive cycle checks and claim-next selection support ready work. Named claims do not recheck readiness; graph checks in a transaction do not by themselves prove every cross-replica/concurrent-graph invariant. [Readiness](../repo/internal/storage/issueops/ready_work.go), lines 45–155; [edge checks](../repo/internal/storage/issueops/dependencies.go), lines 246–355; [claim paths](../repo/internal/storage/issueops/claim.go), lines 48–145 and 266–325. |
| T05 | Resembles | Assignee/actor, created-by, closed-by-session and metadata retain provenance. Claim and heartbeat use actor strings; there is no mandatory registered worker/session/attempt hierarchy or proof of the calling process's identity. [Model](../repo/internal/types/types.go), lines 20–102; [claim contract](../repo/issueops/claimer.go), lines 35–67. |
| T06 | Similar | Structured CLI JSON, Go roles, typed HTTP requests/errors and the included MCP adapter expose substantial task operations. Caller guards and interface-specific policies still need explicit use; the adapter forwards claim to the CLI rather than adding execution semantics. [Roles](../repo/issueops/readyclaimer.go); [HTTP update](../repo/internal/httpapi/update.go), lines 35–100; [MCP claim](../repo/integrations/beads-mcp/src/beads_mcp/bd_client.py), lines 609–628. |
| T07 | Similar | Claims use a row-token CAS; ready selection, winning claim and hydration share a transaction. Whole-attempt retry handles known serialization losses. Actors and override requests are self-asserted, and ordinary updates have different authority rules. [Claim CAS](../repo/internal/storage/issueops/claim.go), lines 48–145; [ready claim](../repo/internal/storage/issueops/claim_next.go), lines 47–118; [update authority](../repo/internal/storage/issueops/aggregate.go), lines 200–240. |
| T08 | Resembles | Priority/age ordering, ready filters, claim-next and named claim pools support dispatch primitives. They do not enforce per-agent capacity, WIP limits, fairness across agents or a supervisor's routing policy. [Ready order/filter](../repo/internal/storage/issueops/ready_work.go), lines 40–155; [claim selection](../repo/internal/storage/issueops/claim.go), lines 266–328; [charter](../repo/engdocs/PROJECT_CHARTER.md), lines 29–43. |
| T09 | Similar | Molecule advancement can inspect ready steps and optionally claim one; close checks can refuse open children and optionally close a completed molecule. These are work-graph primitives, without child worker launch, result collection or supervised cancellation. [Stepper](../repo/issueops/moleculestepper.go), lines 115–209; [close policy](../repo/internal/storage/issueops/close.go), lines 132–213; [auto-close caller](../repo/internal/storage/issueops/execution.go), lines 328–368. |
| T10 | Similar | Description/design/acceptance/notes, spec IDs, external refs, arbitrary metadata, formula origins and version snapshots retain context. There is no enforced immutable input/artifact bundle or proof that a delivery matches a referenced revision. [Model](../repo/internal/types/types.go), lines 20–208; [mutation/version path](../repo/internal/storage/issueops/claim.go), lines 210–245. |
| T11 | Similar | Notes, append/merge operations, comments, close reasons, sessions and event/version records support durable progress and handoffs. They do not require acknowledged responsibility transfer or an attempt-bound result. [Model](../repo/internal/types/types.go), lines 20–208; [merge/update](../repo/internal/storage/issueops/update.go), lines 355–490. |
| T12 | Similar | The durable change journal has bounded checkpoint paging, a published head and explicit truncation errors; a sibling watch route is separate. This supports change-consumer recovery, not recipient mail delivery/acknowledgement or a management notification guarantee. [HTTP events](../repo/internal/httpapi/events.go), lines 12–184. |
| T13 | Similar | Blockers, comments and gate fields represent waits, timeout and waiter metadata. CLI close evaluates selected machine-checkable gate types. There is no universal manager/human decision contract across every mutation interface. [Gate fields](../repo/internal/types/types.go), lines 178–198; [CLI gate check](../repo/cmd/bd/close.go), lines 683–755; [HTTP close](../repo/internal/httpapi/close.go), lines 20–95. |
| T14 | Similar | Durable claims create node-local leases; heartbeat refreshes them and reclaim conditionally clears expired ownership. Generic assignment/status writes can remain unleased until heartbeat re-arms them; wisps are never leased. Expiry is recoverable state, not immediate process revocation. [Lease grant](../repo/internal/storage/issueops/claim.go), lines 210–245; [heartbeat](../repo/internal/storage/issueops/lease.go), lines 400–675; [reclaim](../repo/internal/storage/issueops/lease.go), lines 937–1066. |
| T15 | Similar | Optional revision/status/assignee guards reject stale expected state, and repeated same-holder claims or closes can be no-ops. The lifecycle token covers only part of the record and is not required on every progress/result write. No mandatory execution generation or general request idempotency key is established by these interfaces. [Guard contract](../repo/issueops/issueops.go), lines 254–365; [guard execution](../repo/internal/storage/issueops/execution.go), lines 138–253; [revision limits](../repo/internal/types/types.go), lines 75–102. |
| T16 | Similar | Reopen/release/reclaim, heartbeat re-arm, typed indeterminate commit outcomes and versioned records support task-state recovery. They do not resume/cancel an agent process or compensate its external effects. Ephemeral claims need separate recovery. [Reclaim](../repo/internal/storage/issueops/lease.go), lines 937–1066; [retry boundary](../repo/internal/storage/dolt/store.go), lines 1283–1400; [ephemeral contract](../repo/issueops/readyclaimer.go), lines 65–98. |
| T17 | Similar | A shared Dolt/server authority supports transactional concurrent clients; replicas/versioning support exchange and merge. Node-local leases are not global ownership, and foreign-lease reclaim protection needs node provenance. Independent replicas can make independent decisions before exchange. [Replica policy](../repo/internal/storage/issueops/lease.go), lines 864–920; [transaction wrapper](../repo/internal/storage/dolt/issue_operations_tx.go), lines 11–103. |
| T18 | Similar | Events, full version records, journal sequences and Dolt history retain changes and provenance. Actor strings are asserted, heartbeat refresh is intentionally not journaled, and a Dolt history message need not correspond one-to-one to one task mutation. [Claim events](../repo/internal/storage/issueops/claim.go), lines 210–245; [heartbeat policy](../repo/internal/storage/issueops/lease.go), lines 646–675; [history ordering](../repo/internal/storage/dolt/issue_operations_tx.go), lines 11–103. |
| T19 | Similar | Ready/list/show, graph-oriented records and structured HTTP reads provide inspectable task detail and machine-friendly views. The reviewed surface is CLI/API oriented; no human board or live accessibility/usability result is established here. [Ready command](../repo/cmd/bd/ready.go), lines 24–70; [detail/response](../repo/internal/httpapi/close.go), lines 45–95; [model](../repo/internal/types/types.go). |
| T20 | Similar | Epics/parent work, priority, due/defer dates, labels, custom statuses/types and molecules support backlog and workflow planning. Native agent-capacity/sprint control is not supplied by these primitives. [Model](../repo/internal/types/types.go), lines 20–208; [ready filters](../repo/internal/storage/sqlbuild/ready.go), lines 207–285; [charter](../repo/engdocs/PROJECT_CHARTER.md), lines 29–43. |
| T21 | Similar | Acceptance text, child/blocker close checks, template/pin/holder guards and selected CLI gate evaluation constrain completion. There is no required qualified reviewer/evidence revision approval; alternate status updates omit some close guards, and some gate-evaluation errors warn and allow. [Checked close](../repo/internal/storage/issueops/close.go), lines 42–110; [alternate update](../repo/internal/storage/issueops/update.go), lines 400–442; [gate error branch](../repo/cmd/bd/close.go), lines 706–755. |
| T22 | Similar | HTTP bind validation and reloadable bearer-token files can protect remote access. Tokens grant coarse service access; `actor`, force and expected-owner claims are caller-provided rather than authenticated role membership. [Bind/auth posture](../repo/internal/httpapi/server.go), lines 598–626; [token validation](../repo/internal/httpapi/auth.go), lines 115–145 and 251–262; [HTTP actor contract](../repo/internal/httpapi/update.go), lines 63–100. |
| T23 | Similar | Custom statuses/types, labels/metadata, typed roles, dependency kinds, formulas/molecules and adapters support composition. The charter deliberately leaves agent routing, scheduling and cross-system policy outside core. [Creation config](../repo/internal/storage/issueops/execution.go), lines 37–90; [model](../repo/internal/types/types.go), lines 110–208; [charter](../repo/engdocs/PROJECT_CHARTER.md), lines 29–60. |
| T24 | Similar | A substantial CLI/API/library and shared behavior contracts aid integration. Dolt mode/configuration, node identity, journal retention and history publication add operating requirements; Bazel/Go/Dolt compatibility and runtime recovery were not exercised. [Metadata](../repo/go.mod), lines 1–55; [build instructions](../repo/AGENTS.md), lines 121–180; [operation funnel](../repo/internal/storage/dolt/issue_operations_tx.go), lines 11–103. |

## Lifecycle and alternate mutation paths

Creation validates an attempt-local request, loads prefix/status/type configuration, assigns an ID and wires parent/dependency records in one transaction.
A guarded create refuses if its requested dependency edges were skipped; it does not report success with the relationship silently missing.
Results are hydrated before the transaction returns.
Configured infrastructure types and typed wisps can deliberately route to the ephemeral plane.
A supervisor must choose that persistence class knowingly because it changes history and recovery.
See [create body](../repo/internal/storage/issueops/execution.go), lines 37–137.

The ordinary ready reader derives filters through shared SQL builders and maintains a projection of blocked state.
It excludes pinned and, by default, ephemeral work; it supports priority, type, assignment and deferred/hierarchy-related filtering.
Dependency writes validate endpoints, type/hierarchy constraints and scheduling cycles, with a final batch cycle check.
Those are implemented graph rules, not just instructions for agents.
This review does not certify every concurrent graph interleaving or a merge of separately edited replicas.
See [readiness](../repo/internal/storage/issueops/ready_work.go), lines 45–155; [SQL predicate](../repo/internal/storage/sqlbuild/ready.go), lines 207–285; and [edge checks](../repo/internal/storage/issueops/dependencies.go), lines 246–483, plus [final batch check](../repo/internal/storage/issueops/dependency_editor.go), lines 226–254.

A direct named claim checks whether the issue's status and assignee are claimable and applies a row-token CAS.
It does not ask whether dependencies are satisfied.
A caller that wants select-and-claim uses claim-next, which reads candidate ready work, attempts claims and hydrates the winner in the same transaction.
The scan can continue past a row a competing actor took, and an empty front is a normal result.
It deliberately clears pagination/cap fields for its scan, so returning one issue does not imply the selection query did bounded work.
See [named claim](../repo/internal/storage/issueops/claim.go), lines 48–145, and [claim-next](../repo/internal/storage/issueops/claim.go), lines 266–328; [hydration](../repo/internal/storage/issueops/claim_next.go), lines 47–118.

A successful durable claim grants one local lease and records claim/event/version state.
Repeated same-actor in-progress claims return without refreshing that lease.
Heartbeat is the explicit keepalive operation.
A heartbeat refresh changes the lease row without reminting the task revision or writing noisy history; a rare missing-lease re-arm does remint and record a mutation so it conflicts with an ending claim.
See [claim post-state](../repo/internal/storage/issueops/claim.go), lines 155–245, and [heartbeat](../repo/internal/storage/issueops/lease.go), lines 400–675.

Progress is a typed patch, notes merge/append, label/metadata change or comment.
Expected revision/status/assignee checks are available and run inside the writing transaction.
They are optional, and actor identity is not authenticated by them.
An expected assignee can authorize a transfer based on known current state; force fields provide further explicit policy bypasses.
These controls are suitable for a trusted coordinator but do not constitute hostile-worker authorization.
See [request contract](../repo/issueops/issueops.go), lines 254–365; [guard execution](../repo/internal/storage/issueops/execution.go), lines 138–253; and [transfer predicate](../repo/internal/storage/issueops/aggregate.go), lines 200–240.

The close role checks an optional revision, then template, pin and holder guards, followed by children and live direct blockers.
Child-count policy writes coordination cells so a concurrent parent-child insertion cannot silently merge beside the stale close count without a conflict.
The close deletes its lease, records a close event/version and recomputes affected blocked state.
An optional flag can also close a completed molecule.
This is meaningful controlled task state, even though it does not verify acceptance evidence or run a worker's tests.
See [checked close](../repo/internal/storage/issueops/close.go), lines 42–213 and 333–417; [coordination cells](../repo/internal/storage/issueops/dependency_coordination.go), lines 1–60; and [molecule caller](../repo/internal/storage/issueops/execution.go), lines 328–368.

Generic update into a done category also checks child/blocker policy.
It deliberately does not apply the close verb's pin or foreign-holder guard when only status changes.
A client can therefore reach a done state for another actor's or pinned issue by using a status patch that the close verb would refuse.
This is a traced public alternate path: HTTP accepts status in a patch and delegates to Lifecycle.Update, whose common body reaches the generic update.
It is not inferred from an unused internal helper.
See [HTTP patch](../repo/internal/httpapi/update.go), lines 35–100; [update execution](../repo/internal/storage/issueops/execution.go), lines 138–253; and [done crossing](../repo/internal/storage/issueops/update.go), lines 400–442.

CLI close adds a selected gate-satisfaction check before the role call.
It checks GitHub run/PR, timer and bead conditions; a non-bead evaluation error emits a warning and permits close, while an unreadable bead condition refuses.
The reviewed HTTP close calls the role directly and has no equivalent external-condition check.
Gate issue state, parent completion and acceptance of a delivered artifact therefore remain distinct policies with different interface coverage.
See [CLI gate check](../repo/cmd/bd/close.go), lines 683–755, and [HTTP close](../repo/internal/httpapi/close.go), lines 20–95.

## Recovery, replicas and stale writers

A lease's clock expiring does not itself change issue ownership or revoke the process.
Reclaim selects sufficiently expired durable claims, repeats expiry/provenance predicates in its delete and resets the issue to open/unassigned with a fresh lifecycle token.
A racing heartbeat can rescue the lease, while row-token rewrites make competing close/update/reclaim mutations conflict rather than silently cell-merge.
The caller still needs to invoke recovery and reject stale writes through the available guards.
See [reclaim](../repo/internal/storage/issueops/lease.go), lines 937–1066.

A generic update can set in-progress/assignee without arming a lease.
The first legitimate heartbeat can re-arm that claim; until then, expiry-based recovery has no lease row to discover.
Wisps remain a sharper boundary: claim-next can admit them explicitly, but they receive no lease and heartbeat refuses them.
A vanished worker's ephemeral issue needs another release/finish or an external supervisor's recovery policy.
See [re-arm branch](../repo/internal/storage/issueops/lease.go), lines 550–675; [heartbeat refusal](../repo/internal/storage/issueops/heartbeat_role.go), lines 42–80; and [ready-claim contract](../repo/issueops/readyclaimer.go), lines 65–98.

Leases are node-local and excluded from Dolt history/replication.
Imported snapshots can nevertheless materialize a lease with granting-node provenance.
On a named node, reclamation protects positively foreign grants unless explicitly overridden.
An unnamed node or unknown provenance uses the permissive default.
Heartbeat refresh preserves an existing foreign node label, so renaming a node or importing a lease can require deliberate operator recovery rather than silently moving its enforcement authority.
See [replica rule](../repo/internal/storage/issueops/lease.go), lines 864–920, and [refresh provenance](../repo/internal/storage/issueops/lease.go), lines 400–477.

One shared database/server can serialize competing claims.
Two independent replicas do not share that live decision point, and node-local lease clocks are not a distributed fencing service.
A supervisor that needs one task owner across hosts should define which authority grants work and how replicas exchange changes, rather than assume versioned data automatically gives globally exclusive execution.
The storage driver's full merge/replication implementation was not audited here.

The lifecycle revision is equality-only and only partly covers record change.
The source explicitly excludes some direct text, label, relationship and other changes from its complete coverage.
It also exposes a generic issue JSON shape that omits the token, with detail/write responses carrying a separate revision where needed.
Clients must use the right projection and send their expected value; an unguarded write has no stale-attempt rejection promise.
See [revision model](../repo/internal/types/types.go), lines 75–102, and [HTTP close response](../repo/internal/httpapi/close.go), lines 69–91.

## Storage completion, retry and audit

The Dolt retry loop recreates the entire transaction on recognized serialization losses and selected pre-commit connection failures.
It explicitly refuses to replay an indeterminate commit that may already have landed.
That avoids converting an uncertain create/comment/claim into an automatic duplicate mutation.
The caller may still need to reread state after the error; a new external claim-next request has no operation key in its request type that pins it to the prior winner.
See [retry boundary](../repo/internal/storage/dolt/store.go), lines 1283–1400, and [claim-next request](../repo/issueops/readyclaimer.go), lines 1–48.

The SQL task mutation and trailing Dolt history publication are separate stages.
The funnel treats a failed trailing history commit as an audit-publication problem and returns the already-durable mutation as successful.
It logs a metric/warning, and the changed rows can ride a later commit.
A concurrent writer's history commit can also absorb this write under another message.
This preserves the distinction between applied task data and one expected log line; it does not establish one immutable history commit per request.
See [funnel](../repo/internal/storage/dolt/issue_operations_tx.go), lines 11–103.

The events API offers checkpointed change recovery with a configured journal, bounded pages, a published head and explicit retention-loss errors.
It refuses a disabled journal instead of returning a misleading empty feed.
Clients can checkpoint processed sequence records and reconcile after a truncation response.
Heartbeat refresh intentionally does not produce a task-change journal record, while re-arm/reclaim do.
This is a change feed rather than a recipient inbox or proof of work completion.
See [event handler](../repo/internal/httpapi/events.go), lines 12–184, and [heartbeat recording boundary](../repo/internal/storage/issueops/lease.go), lines 646–675.

## Human and agent usability, permissions and design

The CLI's ready command explicitly distinguishes ready listing from atomic selection with `--claim` and supplies structured JSON for agents.
Go roles and HTTP let clients avoid scraping terminal output.
The included MCP claim client delegates to `bd update --claim`; it does not add a separate lock or ownership interpretation.
The operating workflow is well suited to agents that can read issues and use precise mutation contracts.
Live installation, terminal interaction and a human visual board were not evaluated.
See [ready command](../repo/cmd/bd/ready.go), lines 24–70, and [MCP forwarding](../repo/integrations/beads-mcp/src/beads_mcp/bd_client.py), lines 609–628.

HTTP defaults and validation favor a local automation service.
Binding beyond loopback requires explicit opt-in and a token file, with a separately named insecure override.
Accepted tokens are compared against cached SHA-256 digests and can be reloaded without restarting.
This is service-access authentication: the request still supplies the actor and policy override fields.
It does not enforce project-scoped leader/worker/reviewer roles or bind a worker identity to one bearer credential.
See [bind validation](../repo/internal/httpapi/server.go), lines 598–626; [auth posture](../repo/internal/httpapi/auth.go), lines 251–262; [token check](../repo/internal/httpapi/auth.go), lines 115–145; and [actor contract](../repo/internal/httpapi/update.go), lines 63–100.

Shared mutation bodies, typed request/result contracts, copy-before-mutation and explicit refusal types are strengths.
The close/update distinction and separate CLI gate checks also show the integration cost: callers cannot assume that every path to one final status applies every policy.
A large command/storage surface, multiple persistence planes, proxy configurations, revisions, journal retention and driver publication semantics make operational expertise necessary.
The HTTP update/close contracts also omit per-command hooks and auto-commit machinery; an automation that relies on CLI hooks must account for that interface difference.
See [HTTP update contract](../repo/internal/httpapi/update.go), lines 63–75, and [HTTP close contract](../repo/internal/httpapi/close.go), lines 20–42.
The project deliberately provides primitives that an orchestrator must compose into one organizational contract.

## Test-source evidence and implementation limits

The selected ready-claim conformance body seeds durable and ephemeral work and asserts exactly one lease for the durable winner and none for the ephemeral winner.
The heartbeat conformance body asserts that two refreshes do not invalidate a guarded write using the claim's revision.
That heartbeat test explicitly skips when its fixture supplies no Lifecycle role; reading the test does not prove that a particular test lane ran it.
See [ready lease contract](../repo/backend/conformance/ready_claimer_contract.go), lines 405–448, and [heartbeat guard contract](../repo/backend/conformance/heartbeater_contract.go), lines 213–235.

The replica predicate test checks a named local node, an explicit any-replica override and the unnamed-node permissive case.
It establishes intended SQL-fragment selection, not a multi-host recovery experiment.
The HTTP close tests use fake role refusals and verify typed conflict mapping; they do not independently execute the database guards.
The event test likewise verifies a typed truncation error maps to HTTP 410 with checkpoint-window fields.
See [replica predicate test](../repo/internal/storage/issueops/lease_replica_test.go), lines 16–82; [HTTP close mapping](../repo/internal/httpapi/close_guards_test.go), lines 1–125; and [event error mapping](../repo/internal/httpapi/events_test.go), lines 201–239.

No candidate test, build or database service was run.
The shared conformance framework is useful source evidence, while actual backend/runtime equivalence, graph races, crash durability, performance and platform support remain unverified here.
The complete checkout and source ledger preserve the evidence needed for later experiments without presenting those experiments as already performed.

## Adoption gaps and useful components

Beads can supply the central issue graph and coordinated local/shared-server task transitions for the baseline.
Useful components include its atomic claim/ready-claim roles, explicit lease recovery, typed preconditions, parent-close coordination, change journal and common mutation bodies.
Those are substantial implementation assets.

The layer above it must establish authenticated agent and execution-attempt identities, mandatory stale-result fencing, capacity and dispatch policy, child-worker supervision, immutable context/artifact references and revision-bound reviewer approval.
It must also choose consistent close rules across status patches, close verbs, CLI gate checks and remote callers, and define explicit recovery for unleased/ephemeral work and replica authority.
The issue tracker is a capable foundation; the full organization lifecycle remains composition and policy work above it.
