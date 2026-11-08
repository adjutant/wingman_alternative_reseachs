# Rust Agent Mail task management assessment

Repository: https://github.com/Dicklesworthstone/mcp_agent_mail_rust

Commit: `49866939b1f52af5741bd3c87145d01846b93a38`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 9, 2026. Full local checkout; targeted static source and test-assertion review.
Candidate applications, dependencies, builds and tests were not installed or run.

## Fit decision and assessment boundary

Rust Agent Mail is a substantial communication and resource-coordination service for a trusted operator's agents.
It supplies persistent project/agent identities, mail and shared project mailboxes, recipient receipts, ordered delivery events, keyed mutation retries, file reservations, build slots and operational inspection.
It also has an automated controller for liveness and coordination advisories.
These mechanisms can complement an agent task system.

It does not supply the baseline's complete task authority.
The mailbox schema has no task/attempt/acceptance model.
The embedded Beads command surface queries external issues through ready, list, show and status operations; the reviewed dispatcher does not add task creation, claims or completion there.
Threads and reservation reasons can reference those external issue IDs.
Those links do not make a message acknowledgement, file lease or controller decision an accepted task result.
See [mailbox schema](../repo/crates/mcp-agent-mail-db/src/schema.rs), lines 15–165; [Beads commands](../repo/crates/mcp-agent-mail-cli/src/lib.rs), lines 1207–1273; and [dispatcher](../repo/crates/mcp-agent-mail-cli/src/lib.rs), lines 22863–22926.

This implementation must be assessed separately from Python Agent Mail.
The Rust reserve path excludes conflicting paths and rechecks grants inside a transaction.
It also implements inbox event cursors and idempotency keys that are absent from the inspected Python send interface.
These are concrete implementation differences, not a general reliability ranking.
The [Python assessment](../../agent-mail-python/assessment/ASSESSMENT.md) retains its own revision and evidence limits.

The pinned license has an OpenAI/Anthropic rider, and workspace metadata identifies `LicenseRef-MIT-Rider`.
It is not classified here as unrestricted MIT or unqualified open source.
That adoption constraint is separate from the technical assessment.
See [license](../repo/LICENSE) and [workspace metadata](../repo/Cargo.toml), lines 1–70.

The review covers core schema/type inventory, tool registration, registration and session/lifecycle authorization, message persistence and archive dispatch, event cursors, file and slot leases, selected HTTP/browser checks, representative TUI structure, Beads query dispatch and selected tests.
The complete 3,928-file checkout was preserved, but this is not an every-line audit of its search engines, repair framework, export/crypto stack, installers or controller mathematics.
No live interface, performance, crash-recovery or accessibility acceptance was established.

## Architecture and authority

The workspace separates core configuration/types, database access, Git storage, tool implementations, server/TUI, CLI, guards, search, sharing and test support.
Tools run through FastMCP and the Asupersync runtime.
Database work uses SQLModel/FrankenSQLite dependencies; storage and operational recovery include additional layers.
The source pins a nightly toolchain and declares Rust 1.100.
The specialized dependency graph increases the need to validate the actual production feature build before adoption; no build result is claimed here.
See [workspace](../repo/Cargo.toml), lines 1–100, and [toolchain](../repo/rust-toolchain.toml).

The [static catalogue](catalogue.json) records 45 tool names in `TOOL_CLUSTER_MAP` and 33 resource-handler registrations in the server builder.
Resource handlers include exact/query variants, so 33 is not a count of independent logical products or workflows.
The tool builder applies configuration filtering before registration.
The inventory reads literal declarations without compiling or executing the candidate; older descriptive counts do not override these declarations.
See [tool map](../repo/crates/mcp-agent-mail-tools/src/lib.rs), lines 3893–3973, and [builder/filter](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 635–704 and 965–1036.

Persistent mailbox entities include projects/products, agents, messages, direct recipient state, project-addressed deliveries and receipts, file reservations and release state.
Migrations also declare event cursors, delivery-signal receipts, idempotency records and controller state.
Agent records retain focus and lifecycle information, but do not identify an execution attempt with its own immutable inputs, lease token and accepted output.
See [schema declarations](../repo/crates/mcp-agent-mail-db/src/schema.rs), [agent row](../repo/crates/mcp-agent-mail-db/src/models.rs), lines 122–164, and [reservation row](../repo/crates/mcp-agent-mail-db/src/models.rs), lines 377–435.

The database is authoritative for message and reservation state.
Git/archive publication can lag message persistence through a write-behind queue and retry backlog.
Reservation grants have a stronger foreground requirement: their guard-visible JSON must be published before successful admission, although the database lease may already have committed when publication fails.
These are distinct durability contracts.
See [message dispatch](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 48–158; [reservation publication](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 329–399 and 2630–2778.

## Requirement verdicts

Verdicts apply to this service and its included query integrations.
They do not attribute the external Beads database's complete behavior to Agent Mail.

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Projects, products and links partition communication and group repositories. Project identifiers remain client-selected coordination keys, rather than an organization registry with managers, outcomes and tenant access. [Schema](../repo/crates/mcp-agent-mail-db/src/schema.rs), lines 15–68; [trust boundary](../repo/SECURITY.md), lines 31–43. |
| T02 | Resembles | Durable messages and reservations have IDs; included Beads commands expose existing issue reads. The mailbox has no native bounded task/outcome or execution model and this dispatcher adds no task writes. [Schema](../repo/crates/mcp-agent-mail-db/src/schema.rs); [Beads dispatch](../repo/crates/mcp-agent-mail-cli/src/lib.rs), lines 22863–22926. |
| T03 | Resembles | Threads and direct reply arguments structure conversation; external issue detail can be queried. This is not native parent/child work decomposition or linked result-bearing follow-ups. [Message transaction inputs](../repo/crates/mcp-agent-mail-db/src/queries.rs), lines 8926–8960; [Beads surface](../repo/crates/mcp-agent-mail-cli/src/lib.rs), lines 1207–1273. |
| T04 | Resembles | `am beads ready` delegates readiness to the external issue tool. Mailbox reservations check path conflicts, not task dependencies or graph cycles. No native dependency/start invariant is supplied. [Ready caller](../repo/crates/mcp-agent-mail-cli/src/lib.rs), lines 22889–22926; [tool map](../repo/crates/mcp-agent-mail-tools/src/lib.rs), lines 3893–3973. |
| T05 | Similar | Persistent agent identities, registration tokens, pane context and optional session bindings distinguish identities from connections. They do not establish independent work attempts or per-attempt authority. [Agent row](../repo/crates/mcp-agent-mail-db/src/models.rs), lines 122–164; [session implementation](../repo/crates/mcp-agent-mail-tools/src/session_identity.rs), lines 1–110 and 317–386. |
| T06 | Similar | MCP tools/resources and structured CLI readers provide extensive agent access. Catalogue filtering and typed errors aid integration. The interface is a mail/resource API, with task state delegated elsewhere. [Catalogue](catalogue.json); [builder](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 635–704; [event tool](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 5462–5606. |
| T07 | Similar | File grants exclude conflicts and repeat conflict checks in the write transaction; keyed retries preserve the original grant. This establishes a scoped resource lease among cooperating users, not an exclusive task claim or right to submit an execution result. [Grant filtering](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 2330–2485; [transaction](../repo/crates/mcp-agent-mail-db/src/queries.rs), lines 15506–15655. |
| T08 | Resembles | Build slots enumerate conflicts but still grant a lease, and controller actions can advise or probe agents. Neither provides task WIP limits, worker capacity admission or an executable dispatch policy. [Slots](../repo/crates/mcp-agent-mail-tools/src/build_slots.rs), lines 435–488; [controller action type](../repo/crates/mcp-agent-mail-server/src/atc_engine.rs), lines 12376–12381. |
| T09 | Resembles | Mail and macros can communicate delegated requests. The tool catalogue and controller action type contain no child-execution supervisor, worker launch or parent completion barrier. [Catalogue](catalogue.json); [controller actions](../repo/crates/mcp-agent-mail-server/src/atc_engine.rs), lines 12376–12381. |
| T10 | Similar | Markdown messages, attachments, replies and archives retain project conversation. Message archive metadata aids recovery. No task input snapshot or version-bound artifact acceptance is enforced. [Message model](../repo/crates/mcp-agent-mail-core/src/models.rs), lines 108–158; [archive envelope](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 3949–3993. |
| T11 | Similar | Durable progress messages, recipient receipts and project mailboxes support handoffs. Receipt/acknowledgement records do not transfer exclusive assignment responsibility or prove work success. [Schema](../repo/crates/mcp-agent-mail-db/src/schema.rs), lines 75–143; [ACK entry](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 6270–6378. |
| T12 | Similar | Ordered body-free delivery events, explicit cursor errors, `has_more`, receipt lookup and notification signals support restart-safe monitoring. Clients still must persist cursors after handling pages and distinguish signal delivery from task completion. [Event tool](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 5462–5606; [snapshot/cursor query](../repo/crates/mcp-agent-mail-db/src/sync.rs), lines 1014–1210. |
| T13 | Similar | Urgent/ACK-required mail, overdue views and controller advisory/probe actions can surface stalled communication. They do not implement a structured task blocker, manager decision or human approval lifecycle. [Tool/resource catalogue](catalogue.json); [controller actions](../repo/crates/mcp-agent-mail-server/src/atc_engine.rs), lines 12376–12381. |
| T14 | Similar | Agent activity, reservation expiry/renewal and stale-signal analysis support abandoned-resource discovery. Forced release compares the observed expiry before mutation. There is no execution heartbeat whose expiry revokes an old worker's result authority. [Renewal](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 3071–3160; [stale analysis/release](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 3250–3442. |
| T15 | Similar | Four named mutation families expose keyed replay and request-fingerprint conflicts; database keys are recorded with the corresponding mutation. Release replay also uses temporal cutoffs. These are scoped retry/recovery guards, not task-attempt fencing; keys expire and other mutations have different contracts. [Reservation key/commit](../repo/crates/mcp-agent-mail-db/src/queries.rs), lines 15506–15590 and 15770–15806; [release cutoffs](../repo/crates/mcp-agent-mail-db/src/queries.rs), lines 16215–16275; [catalogue](catalogue.json). |
| T16 | Similar | Durable ACK/release intents, archive retry/reconciliation, lifecycle transitions and extensive operator surfaces support service recovery. They do not resume or cancel a worker's task attempt. Some archive fallback states are explicitly ephemeral or dropped. [Archive fallback](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 48–92; [release intent](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 2790–2880; [ACK intent](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 6270–6378. |
| T17 | Similar | Clients can coordinate through one HTTP/mailbox authority, with database transactions and local file locks. Independent mailbox copies do not form a consensus service; session and controller admission state are process-local. No cross-host task-claim protocol exists. [Session state](../repo/crates/mcp-agent-mail-tools/src/session_identity.rs), lines 1–110; [slot lock](../repo/crates/mcp-agent-mail-tools/src/build_slots.rs), lines 240–262; [controller epoch](../repo/crates/mcp-agent-mail-server/src/atc.rs), lines 1–70. |
| T18 | Similar | Messages, recipient/event records, reservation artifacts and controller evidence support inspection. Verified token/session send markers are distinguishable from unverified local sends. This is not an immutable organizational task/attempt audit. [Sender proof](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 2523–2625; [schema](../repo/crates/mcp-agent-mail-db/src/schema.rs). |
| T19 | Similar | A 16-screen TUI registry covers messages, threads, agents, reservations, search, history, projects and controller inspection. Browser writes have explicit role/CSRF gates. This is an operations/mail interface, with no native task acceptance dashboard; live usability and accessibility remain untested. [Screen registry](../repo/crates/mcp-agent-mail-server/src/tui_screen_registry.rs), lines 1–170; [browser mutation gate](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 12524–12565. |
| T20 | Resembles | External Beads readers expose status/priority summaries and ready work. The mail schema lacks native backlog ordering, milestone/iteration ownership and planning writes. Build slots are not sprint capacity. [Beads enum](../repo/crates/mcp-agent-mail-cli/src/lib.rs), lines 1207–1273; [schema](../repo/crates/mcp-agent-mail-db/src/schema.rs). |
| T21 | Absent | No task acceptance, qualified reviewer or evidence-bound completion operation appears in the mailbox schema/tool catalogue. ACK is receipt; the optional cryptographic proof gate concerns registration identity, not deliverable approval. [Catalogue](catalogue.json); [registration proof caller](../repo/crates/mcp-agent-mail-tools/src/identity.rs), lines 3075–3124. |
| T22 | Similar | Bearer/JWT roles, browser mutation checks, optional session identity and optional registration proofs provide controls. Defaults are trusted-local and allow self-asserted identities; authenticated transport is not hostile tenant isolation. Lifecycle tools require tokens over HTTP. [Defaults](../repo/crates/mcp-agent-mail-core/src/config.rs), lines 1716–1720 and 1797–1798; [lifecycle auth](../repo/crates/mcp-agent-mail-tools/src/identity.rs), lines 2231–2318; [role checks](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 13333–13408; [security model](../repo/SECURITY.md), lines 31–43. |
| T23 | Similar | Tool/cluster filters, proof verification interface, mail profiles, controller configuration and shared model/storage crates provide extension points. They are not a task-role/workflow/schema engine. [Tool filtering](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 635–663; [proof interface](../repo/crates/mcp-agent-mail-tools/src/proof_gate.rs), lines 1–100; [workspace](../repo/Cargo.toml). |
| T24 | Similar | A substantial CLI/TUI, diagnostics, pinned toolchain and modular workspace support operation. Specialized database/runtime dependencies and several persistence representations add maintenance cost. Build/install portability, operator repairs and production feature compatibility were not exercised. [Workspace](../repo/Cargo.toml), lines 1–100; [toolchain](../repo/rust-toolchain.toml); [license](../repo/LICENSE). |

## Work lifecycle and enforcement

A leader creates a project namespace and agents register identities with program/model and focus metadata.
Registration generates a token and can rotate an existing named identity's token.
By default this is a self-asserted trusted-local identity model, not proof that a specific process or human owns the name.
Optional session binding restricts a session that already holds an identity from acting as another identity in that project.
A fresh unconstrained session still has the trusted-local fallback described by the implementation.
See [registration/token policy](../repo/crates/mcp-agent-mail-tools/src/identity.rs), lines 2924–2968 and 3035–3288; [session authorization](../repo/crates/mcp-agent-mail-tools/src/session_identity.rs), lines 317–386.

An optional registration proof gate is wired before explicit identity writes, with separate rejection of implicit registration when enabled.
It is disabled by default.
This review traces the caller and interface; it does not certify its cryptography, issuers or deployment key management.
A signed identity grant would still not establish a task's acceptance criteria or the revision delivered by one attempt.
See [gate caller](../repo/crates/mcp-agent-mail-tools/src/identity.rs), lines 3075–3124, and [proof interface](../repo/crates/mcp-agent-mail-tools/src/proof_gate.rs), lines 1–100.

Task selection remains in the external issue system.
The included Beads dispatcher sends read-oriented requests and renders issue summaries.
There is no mailbox transaction that claims a ready issue and reserves files together.
The coordinator must resolve that split across systems and decide which failure leaves work assigned, reserved or merely announced.
See [Beads dispatcher](../repo/crates/mcp-agent-mail-cli/src/lib.rs), lines 22863–22926.

File reservation validates count, TTL, scope and patterns, resolves the actor and checks session context.
It builds a current conflict view and proposes only clear paths.
The database then begins an immediate transaction, checks idempotency and agent lifecycle, repeats conflict detection and inserts or renews leases.
A late conflict is rolled back and converted to a structured conflict response by the tool.
This is stronger than a read-only preflight followed by unconditional inserts.
See [validation/entry](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 1989–2178; [grant path](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 2330–2485; and [database checks](../repo/crates/mcp-agent-mail-db/src/queries.rs), lines 15506–15655.

This lease protects a named edit surface among cooperating callers.
It does not stop direct filesystem edits, enforce a task owner, or reject a late result from a worker whose reservation expired.
Build-slot leases are weaker admission signals: under their local slot lock they report conflicts and still write a granted lease.
Their atomic temporary-file replacement and propagated I/O errors improve persistence but do not make the slot single-winner.
See [slot locking/write](../repo/crates/mcp-agent-mail-tools/src/build_slots.rs), lines 240–337, and [grant](../repo/crates/mcp-agent-mail-tools/src/build_slots.rs), lines 435–488.

Agents communicate progress and questions through messages.
The send path distinguishes token/session-verified senders from unverified local names and can require proof under a fail-closed profile.
Message creation deduplicates recipients and groups row insertion and optional idempotency result in a database transaction.
Archive publication and notification signals happen afterward.
A task supervisor must treat the durable mail record, signal receipt, worker outcome and accepted deliverable as separate facts.
See [sender verification](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 2523–2625; [transaction](../repo/crates/mcp-agent-mail-db/src/queries.rs), lines 8926–9045 and 9630–9758; [post-commit effects](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 3798–4008.

Recipient acknowledgement and reservation release update communication/resource state.
They do not evaluate tests, pin artifacts, enforce child completion or close an external issue.
Retiring or deregistering an identity also does not cancel a worker process.
HTTP lifecycle calls require the registration token; a same-user stdio pane can supply a different local proof path.
See [lifecycle authorization](../repo/crates/mcp-agent-mail-tools/src/identity.rs), lines 2231–2318; [transport stamping](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 17460–17535; and [ACK/release](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 6270–6378, and [release entry](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 2790–2880.

## Recovery and concurrency boundaries

### Database retries are stronger than external-effect replay

The reservation idempotency record is committed with its lease rows.
A replay returns the historical grant and checks current conflicts/coverage instead of silently acquiring newly available paths from an old partial request.
The message path similarly records its key with the message and skips one-time indexing, signal and archive dispatch on replay.
These are meaningful protection against duplicate database work after an uncertain response.
See [reservation replay](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 2404–2485 and 2630–2725; [key commit](../repo/crates/mcp-agent-mail-db/src/queries.rs), lines 15770–15806; and [message replay](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 3798–3886.

They do not make post-commit side effects exactly once.
A crash after the message transaction but before a signal/archive enqueue can leave those effects absent; replay deliberately skips them.
Background archive recovery is a separate mechanism and must converge the missing materialization.
The reviewed dispatch fallback explicitly distinguishes durable backlog entries from ephemeral entries and dropped operations.
The database message can remain valid in all three cases.
No crash experiment or complete proof of background convergence was performed.
See [archive dispatch outcomes](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 48–92, and [effect ordering](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 3880–3993.

### A failed reservation reply can follow a committed grant

A fresh lease can commit before guard-visible JSON publication fails.
The foreground path reports a typed publication error, with committed IDs and recovery guidance, rather than reporting successful edit admission.
It does not roll back that database lease as though nothing happened.
Renewal can repair publication, and exact keyed replay checks coverage before certifying the historical grant.
See [publication contract](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 329–399 and 2630–2778.

This is a deliberately recoverable partial state, not an atomic database-plus-filesystem transaction.
Another agent can see the committed reservation while a local guard artifact is missing.
Callers must inspect the error's committed IDs and follow its recovery path rather than switch to a new request key or assume the lease never existed.
The selected regression test creates that disk-pressure state and checks replay refusal and renewal guidance.
See [regression](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 4271–4385.

### Cursor delivery is distinct from inbox snapshots

The event reader uses one read snapshot for retained range, cursor state and visible events.
It orders by independent delivery sequence, returns one extra row to determine continuation, and distinguishes a future cursor from a cursor whose relevant history was pruned.
It also includes shared project-mailbox visibility rather than treating a missing shared schema as an honest empty page.
See [event query](../repo/crates/mcp-agent-mail-db/src/sync.rs), lines 1014–1210, and [tool response](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 5462–5606.

This directly addresses monitoring gaps that a bounded newest-first snapshot cannot solve by itself.
The caller must still store `next_cursor` only after handling the returned page and explicitly recover from retention loss.
An event says mail was delivered; it is not an execution checkpoint or task acceptance event.
The selected test checks two-page ordering, independence from read receipts and explicit ahead/expired errors.
See [cursor test](../repo/crates/mcp-agent-mail-db/src/sync.rs), lines 3002–3087.

### Expiry and release protections are scoped to reservations

Force release evaluates activity and then supplies the observed expiry to the database mutation.
A changed lease can cause a conflict instead of allowing an old heuristic decision to release a renewed lease.
Degraded release replay also has creation and optional holder-activity cutoffs to avoid releasing a newer acquisition or revived holder merely because an old queued release-all exists.
These safeguards should not be conflated with fencing an old worker's task updates.
See [force release](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 3372–3442, and [replay-cutoff API](../repo/crates/mcp-agent-mail-db/src/queries.rs), lines 16215–16275.

ACK/release calls can durably queue future intent during selected database failures.
The entry paths capture session authorization first and refuse unresolved actors when that context is constrained.
A queued intent is a pending future mutation, not a completed database acknowledgement or released lease.
The complete intent file verification and replay machinery received only targeted boundary review, not an exhaustive audit.
See [release entry](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 2790–2880, and [ACK entry](../repo/crates/mcp-agent-mail-tools/src/messaging.rs), lines 6270–6378.

### Generation markers are not execution-attempt tokens

Reservation artifacts can carry a database-generation marker so reused numeric IDs from reconstructed databases are distinguishable from older files.
Session bindings compare project, ID and canonical name, but explicitly do not identify a new database generation whose values all remain the same.
Neither marker issues a new per-task attempt token that every progress/result write must present.
See [artifact replay checks](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 2630–2725, and [session binding](../repo/crates/mcp-agent-mail-tools/src/session_identity.rs), lines 78–102.

## Permissions, controller and human operation

Defaults bind HTTP to loopback, leave fail-closed sender proof and session identity disabled, and document a trusted-local operator.
Naming an existing agent can rotate its registration token under the default registration model.
Optional session restrictions and proof-gated registration strengthen particular paths, but do not make a shared OS account or bearer token a hostile-client isolation boundary.
Project keys are also client-selected.
See [defaults](../repo/crates/mcp-agent-mail-core/src/config.rs), lines 1716–1720 and 1797–1798; [token rotation](../repo/crates/mcp-agent-mail-tools/src/identity.rs), lines 2924–2968 and 3250–3288; [security model](../repo/SECURITY.md), lines 31–43.

The HTTP server applies reader/writer checks to tool calls and separately gates browser POST mutations with CSRF and configured writer roles.
This is an explicit alternate-interface boundary, rather than an assumption that all ordinary browser requests look like MCP calls.
Lifecycle transport stamping also overwrites a caller's claimed transport so an HTTP request cannot select the stdio pane-only authorization rule.
These controls were traced in source and selected tests, not exercised on a deployed server.
See [browser guard](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 12524–12565; [MCP guard](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 13333–13408; and [transport injection](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 17460–17535.

The automated controller has typed advisory, reservation-release and probe actions.
Its current module adds epoch/report admission so a reset or stale report cannot simply spend a newer in-process notification budget.
The reviewed action type does not launch a worker, create a child issue, submit a result or close a task.
Load-routing concepts in the engine are therefore not credited as a complete task scheduler.
The statistical model, policy calibration and every runtime delivery effect remain outside this targeted review.
See [controller admission](../repo/crates/mcp-agent-mail-server/src/atc.rs), lines 1–70; [action type](../repo/crates/mcp-agent-mail-server/src/atc_engine.rs), lines 12376–12381; and [load actions](../repo/crates/mcp-agent-mail-server/src/atc_engine.rs), lines 388–443.

The 16-screen registry provides stable screen IDs, keyboard jump keys and ordered navigation for mail operations.
It includes messages, threads, agents, search, reservations, health, history, projects, attachments and controller inspection.
This is useful situational awareness, but it does not supply a native agile board or acceptance dashboard.
Representative registry and handler source cannot establish visual quality, screen-reader behavior or day-to-day operating ease.
No candidate terminal or browser was launched.
See [screen registry](../repo/crates/mcp-agent-mail-server/src/tui_screen_registry.rs), lines 1–170.

## Design quality, tests and adoption work

The separation of tool, database, storage and server layers makes several contracts inspectable.
Strong examples include conflict checks inside the reservation transaction, keyed mutation/result commits, explicit cursor-loss responses, guard-visible publication errors and transport-owned lifecycle policy.
The design also has substantial complexity: database snapshots, caches, archive queues, retry journals, JSON guard artifacts, session context and controller epochs have different lifetimes and authorities.
Their relationship needs operational verification, not only unit-level reasoning.

Several comments and reference tables retain earlier counts or durability descriptions.
The report uses live registration and mutation code where these differ.
The foreground reservation path and best-effort message path are a concrete example: a general statement that every successful call means a completed Git archive would be wrong.
The pinned source's large modules also make change review costly even with workspace-level separation.

Selected test bodies establish intended contracts, not executed results.
The reservation conflict test checks exact/glob/ancestor conflicts, excludes the caller's own and expired/released/shared reservations, and compares before/after state for a read-only check.
The publication regression checks a committed but unpublished lease and keyed replay recovery guidance.
See [conflict test](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 5309–5455, and [publication test](../repo/crates/mcp-agent-mail-tools/src/reservations.rs), lines 4271–4385.

The cursor test checks ordered pagination and explicit retained-history failures.
The lifecycle test expects HTTP pane assertions without tokens to be refused with a structured explanation.
The browser role test expects reader/unknown and unconfigured writer labels to be refused before creating a cold mailbox or archive state.
These selected assertions do not certify every JWT configuration, replay interleaving, deployment or repair operation.
See [cursor test](../repo/crates/mcp-agent-mail-db/src/sync.rs), lines 3002–3087; [lifecycle test](../repo/crates/mcp-agent-mail-tools/tests/lifecycle_auth_transport.rs), lines 151–208; and [browser test](../repo/crates/mcp-agent-mail-server/src/lib.rs), lines 25880–25945.

For adoption, this is a communication/resource service to pair with one authoritative task/attempt system.
Retain its ordered inbox events, explicit delivery facts, scoped idempotency and reservation diagnostics as useful components.
Add or integrate authenticated task claims, worker capacity, supervised children, durable execution checkpoints, stale-attempt result rejection and revision-bound review.
Define how those task transitions and mail/resource side effects recover when only one system commits.

Before operational selection, validate the production feature build, supported platforms, sustained multi-client behavior, archive convergence under crash/disk pressure, recovery authority and usable human controls.
Those are unresolved validation needs, not failures established by this static review.
The pinned license restriction also remains an adoption constraint.
The service has deep coordination mechanisms, while the full organizational task lifecycle remains outside its authority.
