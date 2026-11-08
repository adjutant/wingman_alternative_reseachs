# beads-viewer: planning and inspection over an external task authority

Source: https://github.com/Dicklesworthstone/beads_viewer

Reviewed commit: `516e96aa1ac78d6f634b0d394f5102bf430de016`.
Assessment date: November 9, 2026.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Evidence ledger: [review.json](review.json).

## Fit decision

beads-viewer is a useful planning and inspection companion for a Beads task system. It supplies graph analysis, ranked recommendations, parallel work tracks, project aggregation, terminal board/detail views and static browser reports. It can help a project leader identify ready work, blocking work and stale assignments without asking every worker for a status report.

It does not replace the authoritative task tracker or agent runtime. Creating, claiming and closing tasks remain operations of the selected `br` or `bd` installation. The viewer generates routed claim commands and can run tracker updates from its editor. It has no native worker roster, execution-attempt ownership, lease authority, agent inbox or process dispatcher. Its analytical track is a graph grouping, not a delegated worker assignment.

The source has meaningful safeguards against confusing a display snapshot with a live mutation route. Incomplete sources can remain inspectable while action suggestions are withheld. The main coordination gap is still the time between observation and execution. Suggestions do not reserve work. The TUI checks an issue before saving but does not pass an atomic updated-at precondition to the tracker.

The [license](../repo/LICENSE) is an MIT grant with an OpenAI/Anthropic rider. It restricts parties and activities. This is source available with restrictions, not an unqualified MIT open-source adoption option. Licensing is recorded separately from technical fit.

## Scope and evidence level

The full pinned checkout contains 5,133 tracked files. This review inspects targeted source bodies and selected test assertions. It covers issue/readiness models, source-route binding, JSONL and SQLite ingestion boundaries, workspace aggregation, triage and track construction, metric status and cache admission, tracker editing, watcher/background recovery, sprint persistence helpers, estimates, static publication and preview controls. No candidate application, installer, build or test was run.

The review is not an every-line audit. The main command and TUI model are large, and the vendored libraries, complete numerical algorithms, installers, deployment adapters, all search/correlation paths and browser rendering are outside certification. Source-based usability findings are distinguished from live interaction. The ledger records actual inspected ranges and separates test-source inspection from execution.

## Architecture and data ownership

[go.mod](../repo/go.mod), lines 1–70, requires Go 1.26.10 and identifies Bubble Tea/Lip Gloss for terminal UI, Gonum for graph work, modernc SQLite for database reading/export and fsnotify for refresh. The [robot context and registry](../repo/cmd/bv/robot_registry.go), lines 1–100, carry issue data, source authority, readiness, candidate scope and command-specific handlers. This is a local CLI interface, not an MCP or authenticated remote task service.

The [issue model](../repo/pkg/model/types.go), lines 13–196, contains task descriptions, acceptance criteria, notes, assignee, dates, labels, dependencies, comments and source repository. Its `Origin` is transient and excluded from JSON. A separate live loader establishes the local tracker ID, executable, working directory, database and capabilities. This distinction prevents an imported issue from manufacturing a live action route merely by including similarly named JSON fields.

Analysis owns copied issue snapshots. [NewAnalyzer](../repo/pkg/analysis/graph.go), lines 1559–1676, assigns stable numeric graph nodes in sorted issue-ID order, adds blocking edges and indexes hierarchy separately. Related/informational relationships do not become hard execution dependencies. The analyzer separates the full readiness authority from selected output candidates and the graph used for scoped metrics. See [readiness scope](../repo/pkg/analysis/graph.go), lines 1304–1405.

The viewer also writes its own artifacts: analytical caches/feedback, static reports, instruction preferences and sprint helper output. It can refresh a Go Beads compatibility export during loading. Therefore, describe task analysis as a companion role rather than calling the entire executable side-effect free. A native task mutation still goes through a tracker subprocess in the inspected editor path.

## Requirement assessment

These verdicts measure fit to the common baseline. They do not rank numerical algorithm quality or grant the viewer credit for unreviewed behavior of an installed tracker.

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Workspace configuration aggregates repository sources, namespaces IDs and reports partial loads. It is not a leadership/project registry or common write authority. |
| T02 | Resembles | Rich task records are loaded, analyzed and exported. The authoritative lifecycle and durable writes belong to `br`/`bd`. |
| T03 | Similar | Hierarchy, dependency context, follow-up relationships and parent/child views support decomposition analysis. Creating and governing assignments remains external. |
| T04 | Similar | Full-source readiness, missing-reference handling, hierarchy propagation, cycles and what-if plans. These are snapshot decisions; tracker eligibility can differ and must be checked at execution. |
| T05 | Absent | The inspected task model, registry and `pkg/agents` implementation provide no agent/session/attempt registry. `pkg/agents` detects and maintains instruction files. |
| T06 | Similar | Structured robot commands, common provenance envelopes, command argv and schemas serve agents. No native remote mutation API or task MCP server in the inspected surfaces. |
| T07 | Resembles | Suggestions use a verified tracker route and its advertised `--claim`. The tracker supplies atomic ownership; the viewer does not reserve or enforce it. |
| T08 | Resembles | Scored recommendations, parallel tracks and agent-count ETA inputs assist planning. No enforced WIP admission, capacity reservation or worker dispatch. |
| T09 | Resembles | Related ready work is grouped into tracks, and hierarchy affects readiness. No worker child launch, join, result integration or enforced parent completion. |
| T10 | Similar | Descriptions, design, notes, comments, references, history and provenance remain visible. No native immutable artifact/result authority or review-version contract. |
| T11 | Resembles | Existing progress/comments can be inspected and selected fields edited through the tracker. Durable structured handoff and result submission are external. |
| T12 | Resembles | Watchers and snapshots refresh shared views. They are coalesced invalidations, not recipient messages, acknowledgements or replayable task events. |
| T13 | Similar | Blockers, stale issues, abandoned-claim advice and sprint risk expose coordination needs. Escalation delivery and human decision handling remain external. |
| T14 | Resembles | Updated-at/assignee heuristics identify stale claims. No native task lease expiry, renewal, authenticated heartbeat or reclaim operation. |
| T15 | Resembles | Snapshot hashes, editor source checks and internal worker generations reject some stale presentation work. They do not fence stale task attempts; editor writes omit atomic conditional-update flags. |
| T16 | Similar | Last-good snapshots, load retries, watcher fallback, saved drafts and export retry support viewer recovery. They do not resume, cancel or compensate an agent task. |
| T17 | Resembles | Local multi-repository aggregation and publishable reports support inspection across machines. They do not provide shared online claim authority between independent stores. |
| T18 | Similar | Source/scope hashes, historical snapshots and confidence-bearing commit correlation aid traceability. They do not establish authenticated mutation attribution or acceptance. |
| T19 | Similar | Terminal Kanban/detail/search/graph views and static browser reports provide substantial inspection. Custom workflow states are folded into fixed board columns; runtime accessibility was not tested. |
| T20 | Similar | Backlog priority, labels, tracks, sprint records, risk, velocity and ETA help planning. Sprint writes lack shared concurrent-edit authority, and estimates are heuristics. |
| T21 | Resembles | Acceptance text and review status can be displayed; tracker completion must apply its own gates. No viewer-owned qualified review or controlled acceptance workflow. |
| T22 | Resembles | Native-route validation, literal arguments, read-only sources and loopback preview controls protect local operations. No authenticated per-agent/project role model. |
| T23 | Similar | Custom states/types are retained, with configurable analysis, ranking, source selection and structured output. Unknown states do not automatically acquire tracker readiness semantics. |
| T24 | Similar | Local Go binary and static bundles reduce service requirements. A compatible tracker, export freshness, data volume and substantial client assets remain operational concerns. |

## From source discovery to a proposed assignment

### Loading a source is not acquiring work

The loader can read JSONL or SQLite. JSONL line handling records malformed/invalid issues as errors while preserving valid rows for inspection. Recognized non-issue records are skipped rather than misparsed as tasks. See [line processing](../repo/pkg/loader/loader.go), lines 1437–1557. An output with rows is therefore not automatically a complete task graph.

SQLite uses `mode=ro` and connection-local `query_only`, with a deferred transaction that reads the issue graph and related tables from one snapshot. It validates rows, records duplicates/errors and detaches the load report from mutable reader state. `LoadIssueAuthorityContext` rejects incomplete authority. See [SQLite reader](../repo/internal/datasource/sqlite.go), lines 44–112 and 230–327. Read-only access still participates in SQLite WAL reader coordination; it is not a promise of zero filesystem-side effects.

The live route binder accepts supported tracker metadata, resolves the declared source/database and verifies an installed executable's help flags under a bounded probe. Arbitrary file imports cannot borrow a nearby tracker merely because their IDs match. It records the original local ID before workspace namespacing. See [origin binding and revalidation](../repo/pkg/loader/loader.go), lines 96–271. Help advertising `--claim` establishes a capability token, not proof of every semantic safeguard in that installed version.

Go Beads loading may invoke `bd export` to refresh `issues.jsonl`. It stages the export, validates it and renames the staged file over the compatibility file. On failure, an existing export can remain available with a warning and stale-source diagnosis. See [compatibility export](../repo/pkg/loader/loader.go), lines 553–700. This review did not certify the full validation helper or concurrent publication behavior. A compatibility export is still a snapshot and can become old immediately after publication.

### Portfolio aggregation and scope

[Workspace configuration](../repo/pkg/workspace/types.go), lines 13–115, names repository paths, prefixes, optional discovery and enabled state. The aggregate loader continues after individual repository failures, but rejects an all-failed workspace and duplicate namespaced IDs. It preserves tombstone IDs as satisfied dependency references while removing their visible cards. Origins are attached before display IDs and dependency references are namespaced. See [aggregation](../repo/pkg/workspace/loader.go), lines 94–180, 453–558 and 584–623.

This gives a useful portfolio view without pretending every repository loaded successfully. It does not create a distributed transaction or let a namespaced display ID stand in for an actual tracker ID. Dependency suggestions across different trackers remain analytical because a single tracker cannot safely interpret another store's local IDs.

The robot envelope carries data, source authority and scope hashes. Completeness is distinct from a live route: complete in-memory data can support analysis without any actionable tracker command. Failed/stale sources make readiness provisional; zero loaded sources are unknown. See [authority construction](../repo/cmd/bv/main.go), lines 7172–7315, and [envelope](../repo/cmd/bv/robot_registry.go), lines 234–309. These hashes describe inspected input. They are not authenticated identities, leases or mutation preconditions.

### Ready, claimable and recommended mean different things

[ReadinessIndex](../repo/pkg/model/readiness.go), lines 1–264, distinguishes satisfied, unsatisfied and unknown dependency state. Missing prerequisites withhold work. Parent dependency state propagates down the hierarchy; unresolved parent cycles remain unknown. Closed and tombstoned prerequisites satisfy that reference. Full-source readiness can survive display filtering that hides an external blocker.

`Ready` includes open and in-progress issues without future deferral and with satisfied dependencies. `Claimable` is narrower: open, exactly unassigned, non-epic and without open children. A worker reading a plan must therefore not claim every planned item. The model accepts custom statuses, but only the explicitly recognized statuses become ready. It does not load an arbitrary tracker's configured ready-status group. See [status semantics](../repo/pkg/model/types.go), lines 286–325. An upstream custom ready state or different hierarchy policy can make tracker and viewer selection differ.

Triage ranks the full scored set, then applies candidate/actionable filters. It computes claimability, constructs source-bound actions and separately limits visible recommendations. Quick wins come from the claimable subset. See [triage assembly](../repo/pkg/analysis/triage.go), lines 592–745, and [claimable top picks](../repo/pkg/analysis/triage.go), lines 1157–1210. Ranked recommendations can include useful blocked or assigned work when inactive work is requested. They are not all instructions to start execution.

Robot handlers suppress claim suggestions when source authority is incomplete. `robot-next` additionally requires a safe candidate, acceptable PageRank/betweenness status and an available live route. Its metric gate does not require every metric or completed cycle analysis. It can return a diagnostic candidate without an actionable assignment. See [handler checks](../repo/cmd/bv/robot_registry.go), lines 2184–2228 and 2459–2568, and [metric gate](../repo/pkg/analysis/graph.go), lines 202–229. Suggestion mutation actions are also removed for historical contexts. See [suggestion handler](../repo/cmd/bv/robot_registry.go), lines 1273–1328.

### A suggested command is still only a suggestion

[Issue actions](../repo/pkg/model/types.go), lines 75–196, construct literal argv and a shell-quoted rendering using captured directories, database and local ID. Claim uses native `update --claim --json`. A missing/read-only route or unsupported claim capability prevents that command. Dependency/label hygiene suggestions have route checks; cross-tracker edges are withheld from executable suggestions.

The viewer does not execute these robot claim suggestions or mint an ownership token. Two agents can receive the same suggestion. The later native claim must decide whether it still wins. All lease, attempt, review and completion behavior must be attributed to the installed tracker, not inferred from a viewer recommendation or its `claim_safe` source field.

## Planning depth and its limits

[Execution plans](../repo/pkg/analysis/plan.go), lines 1–258, take ready items, calculate what they would unblock and group them by connected components of blocking/hierarchy relationships. Members are ordered by priority and ID. This is useful for identifying separate work streams. It is not resource scheduling: tracks do not account for shared files, tool slots, credentials, worker skills or external service limits. They contain issue IDs, not assigned agent identities or durable parent/child attempt records.

Analysis runs a fast first phase and an asynchronous second phase. Size-based configuration can use approximate betweenness, shorter timeouts or skip cycles/HITS. The default XL branch disables cycle computation. Representative cycles can be capped. See [configuration](../repo/pkg/analysis/config.go), lines 1–229, [async analysis](../repo/pkg/analysis/graph.go), lines 1695–1804, and [cycle/status publication](../repo/pkg/analysis/graph.go), lines 2193–2265 and 2321–2367. Empty cycle output after a skipped or timed-out computation cannot prove acyclicity.

Metric status and worker completion are separate. Cache admission requires published phase-two readiness and acceptable per-metric states; cancellation closing a done channel does not itself certify metrics. See [cache publication gate](../repo/pkg/analysis/graph.go), lines 149–190, and [phase-two wrapper](../repo/pkg/analysis/graph.go), lines 2420–2466. These are useful design choices. This assessment did not mathematically verify every metric or reproduce timing behavior under load.

Sprint records carry ID, name, dates, issue IDs and velocity target. Loading validates entries and can skip malformed rows with warnings. The helper writer replaces the complete sprint file through a temporary file and rename. It has no lock or expected-content precondition in that body. Concurrent load/edit/save callers can therefore lose one another's changes; this is a source-derived interleaving, not a reproduced race. The production call inventory found no caller beyond the helper's own delegation, so do not present it as a fully wired concurrent sprint editor. See [sprint model](../repo/pkg/model/types.go), lines 498–535, and [sprint persistence](../repo/pkg/loader/sprint.go), lines 1–155.

ETA uses estimated/heuristic complexity and recent closure velocity, scales capacity by a supplied agent count and returns a confidence-derived range. It does not inspect actual agent processes or enforce dependencies as an execution schedule. See [ETA](../repo/pkg/analysis/eta.go), lines 31–94 and 151–224. Sprint risk uses task and dependency timestamps as approximations of inactivity/block duration, rather than complete transition history. See [risk evaluation](../repo/pkg/analysis/sprint.go), lines 73–100 and 131–246.

## Editing, completion and recovery

The terminal editor can change title, status, priority, assignee, type and description through the captured tracker. It validates the selected source/session, revalidates metadata, reloads source selection and fetches the current native issue. It compares fields and updated-at before saving. The subprocess uses literal arguments, explicit database routing, bounded output and a 30-second command context. See [editor checks and command runner](../repo/pkg/ui/model.go), lines 375–655.

The read and write are separate subprocesses. The generated update arguments omit `--if-unchanged`. A writer can change the task after `show` passes but before `update` executes, allowing the viewer to overwrite the changed fields. This source-derived gap remains even when the tracker offers conditional updates. The preflight check is useful conflict detection, but it is not an atomic comparison and write.

The viewer passes status edits to the tracker. It does not introduce a viewer-owned acceptance decision, qualified reviewer, child completion barrier or cancellation action. The selected tracker may reject a requested closed status or require a separate close operation. Acceptance text in a displayed card is not proof of accepted implementation.

After a successful tracker update, compatibility export can fail. The viewer keeps the saved draft, marks the source stale, records pending refresh and blocks another edit until refresh succeeds. Export retry does not rerun the field update. Source-version/session checks prevent an old completion from approving a newly selected source. See [save/export outcomes](../repo/pkg/ui/model.go), lines 2781–2857, and [retry export](../repo/pkg/ui/model.go), lines 353–374. Cancellation can race a committed tracker mutation; the source comments and error handling explicitly preserve recovery context instead of promising rollback.

File watching coalesces changes into invalidations. Backend failure starts polling, schedules a rescan and retains prior fingerprints. Polling checks source file and WAL changes. Generation checks stop a notification from an old watcher run entering a replacement run. See [watcher recovery](../repo/pkg/watcher/watcher.go), lines 397–495 and 526–606. This is refresh recovery, not a replayable task-event stream with consumer acknowledgements.

The background snapshot worker has its own generation fence. A late calculation from an earlier worker generation is dropped, and stopped workers cannot publish a new snapshot. See [snapshot publication](../repo/pkg/ui/background_worker.go), lines 1132–1194. This protects the UI's state. It must not be counted as stale execution-attempt rejection for tasks owned by agents elsewhere.

Stale and abandoned-claim alerts derive from issue update/create time, status, assignee, label thresholds and multipliers. They recommend asking or releasing; they do not inspect authenticated worker heartbeats or revoke a lease. See [staleness and abandoned claims](../repo/pkg/drift/drift.go), lines 571–652 and 959–1011. An old task can still have a live worker, while an abandoned worker can leave a recently edited task. Recovery requires the external coordinator and tracker.

## Human inspection, provenance and operation

The terminal board supports search, detail and alternative status/priority/type groupings. Its status board has four columns. Custom, deferred and review states fall through into the first column rather than acquiring dedicated workflow columns. See [board model and grouping](../repo/pkg/ui/board.go), lines 17–75 and 291–351. This makes the board compact but requires detail inspection when the tracker uses a richer workflow.

Static export builds a separate SQLite snapshot, then publishes it and JSON/graph artifacts into a bundle. Each file uses a constrained root and temporary-file replacement; the full bundle is not one atomic multi-file transaction. A failure after publishing the database can leave older auxiliary files. See [export ordering](../repo/pkg/export/sqlite_export.go), lines 84–245, and [bundle writer](../repo/pkg/export/viewer_embed.go), lines 73–145. The export's SQLite is a reporting database, not the original mutable tracker.

The browser client fetches exported data and runs local visualization/query code. The inspected markdown functions use DOMPurify. The page includes bundled dependencies and a CSP, but retains `unsafe-eval` for its Alpine build. These are source observations, not a browser-security certification. See [page head](../repo/pkg/export/viewer_assets/index.html), lines 1–100, and [viewer helpers](../repo/pkg/export/viewer_assets/viewer.js), lines 551–582 and 2236–2269.

The local preview binds `127.0.0.1`, serves files/status/live-reload and admits only GET/HEAD requests with acceptable local Host/Origin. It is not a LAN agent API. Serving an exported bundle elsewhere is a separate hosting/access-control decision. See [preview](../repo/pkg/export/preview.go), lines 213–244 and 447–519.

Historical source loading pins Git repository context and strips ambient routing/configuration variables. Correlation report assembly combines co-commit, explicit-ID and temporal-author evidence with confidence and optional feedback. This helps investigation but does not authenticate a task mutation or prove that a commit satisfies acceptance criteria. See [Git loader](../repo/pkg/loader/git.go), lines 1–112, [correlation model](../repo/pkg/correlation/types.go), lines 70–122, and [report assembly](../repo/pkg/correlation/correlator.go), lines 403–480.

Search configuration exposes hybrid ranking and a deterministic hash embedder. Python sentence-transformer and OpenAI embedding provider branches return unimplemented errors at this revision. Do not interpret a selectable provider name as a working semantic-model integration. See [search configuration](../repo/pkg/search/config.go), lines 1–118.

## Test-source review and implementation quality

Selected assertions were read, not run:

- [Scoped planning](../repo/pkg/analysis/plan_test.go), lines 399–505, compares selected candidates against full-source readiness, including hidden blockers, missing references, hierarchy, assigned work and epics. Lines 89–118 verify two independent graph chains form two tracks, not two running workers.
- [Robot authority](../repo/cmd/bv/robot_envelope_test.go), lines 13–110, preserves diagnostic suggestions while removing executable actions for incomplete/historical contexts. Complete in-memory authority still does not manufacture a live tracker route.
- [Action construction](../repo/pkg/model/types_test.go), lines 38–108 and 156–168, checks literal shell arguments, original IDs, read-only route refusal and non-importable origins. This uses a recorder fixture, not a real tracker ownership race.
- [Editor recovery](../repo/pkg/ui/coverage_extra_test.go), lines 439–515 and 546–586, keeps failed-save drafts, bounds a hung fake tracker, retains the captured executable and retries export separately. These fixtures do not prove atomic protection between native show and update.
- [Partial SQLite recovery](../repo/pkg/ui/background_worker_authority_test.go), lines 21–152, damages a blocker/deferral, retains the prior complete snapshot and recovers after repair without enabling file notifications. Its local test database is not certification of every supported tracker engine or host.

The implementation has substantive analysis and recovery logic. Its strongest architectural distinction is between source completeness, candidate selection, displayed IDs and live action routes. The weak point for the full baseline is not missing graph mathematics. It is the lack of one authenticated, attempt-aware task authority and complete execution lifecycle.

Before adoption, verify real terminal/browser behavior, source-version compatibility, large-graph latency, cache behavior, cancellation timing, platform filesystem semantics and required export freshness. Review the complete deployment and installer paths separately. Keep diagnostic warnings visible; neither a source hash nor a computed score is proof that a later claim or completion is valid.

## Integration work for the baseline

Use the viewer as a read/plan layer over an authoritative task service. Keep task creation, ownership, review and completion in that authority. Add persistent agent/attempt identities, mandatory conditional writes, authenticated review, durable communication, process dispatch/cancellation and parent result integration through the coordinator.

For its own editor, pass the tracker's supported updated-at precondition with the mutation and report unsupported conditional-write capability clearly. Preserve the useful existing designs: full-source readiness under filtered views, explicit partial-source diagnosis, local-ID routing, literal argv, metric status, last-good snapshots and saved-draft/export recovery. Confirm the restricted license independently before adopting the component.
