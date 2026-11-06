# CLI Agent Orchestrator (CAO) assessment

**Repository:** https://github.com/awslabs/cli-agent-orchestrator  
**Local checkout:** `researchs/cli-agent-orchestrator/repo`  
**Revision inspected:** `8b962ee515caf9351838c1805f4cfef969e04dda`  
**Package version:** 2.5.4 ([package metadata][package], lines 1–5).  
**Assessment date:** 2026-11-05.  
**Basis:** [Wingman purpose](../../WINGMAN_PURPOSE.md) and the complete [assessment guide](../../generic/assessments/ASSESSMENT_GUIDE.md). Source inspection only; no dependencies installed, services launched, provider conversations run, or checkout files changed.

CAO is a strong candidate for Wingman's **coding-agent execution and coordination substrate**, but a substantial organizational application must sit above it. It launches real independent coding CLI processes, supports heterogeneous specialists, asynchronous assignments, synchronous handoffs, durable inboxes, scoped discovery, local worktree isolation, actual remote-node placement, scheduled flows, workflow recovery, and useful operational interfaces. Those are considerably more than personas inside one model conversation.

Its native unit is a **terminal-bound CLI instance**, grouped into a terminal session. A named profile is reusable configuration. It is not a standing employee with its own durable organizational history. Projects are working directories, grouping metadata and memory identities rather than a portfolio of products with intake, ProductMaster/TechMaster ownership, shared tickets, rooms and acceptance criteria. The bundled coding supervisor's organization is principally a prompt directing a developer/reviewer loop. Telegram/Butler, the product discovery process, persistent role-instance identities, ProjectTracker, organizational chat, and meaningful executive briefings remain Wingman work.

## Architecture and execution model

The installed commands select four distinct control surfaces: `cao` (Click), `cao-server` (FastAPI), `cao-mcp-server` (tools used inside running agents), and `cao-ops-mcp-server` (operator integration); see [entry points][package], lines 130–134. The browser application is React source in `web/`, with xterm for the live terminal. These are clients of the same server rather than alternative agent runtimes.

The concrete execution chain is: a CLI/UI/MCP operation calls an HTTP route; `session_service.create_session` delegates to `terminal_service.create_terminal`; terminal creation allocates backend resources, records a terminal, creates a provider adapter, and initializes the provider CLI. [Session creation][session], lines 71–176, forwards provider, profile, working directory, tools, initial message, optional provider conversation ID and worktree choice. [Terminal creation][terminal], lines 2852–3061 and 3117–3299, creates a backend session/window, writes registry facts, then creates and initializes the provider. The default [tmux backend][tmux], lines 34–81 and 105–143, actually delegates session/window/pane creation to `TmuxClient`. It does not simulate agents in an in-process LLM loop. Its input methods send keys to the terminal (lines 160–181). There is also an alternate herdr backend, so terminal mechanics and provider adapters are separate interfaces.

Provider adapters own native CLI flags, system-prompt delivery, initialization, output interpretation and status detection. For Codex, [the implementation][codex], lines 1647–1900, constructs the `codex` command, chooses `--profile` versus `--yolo`, injects developer instructions, and maps MCP settings. Completion and permission detection involve terminal-frame parsing, not a uniform typed provider SDK: Codex tracks a dispatch and its pre-send screen baseline (lines 1495–1597), and detects native footer/prompt evidence. This retains native coding-tool behavior but creates version-sensitive integration work and an important distinction between “the CLI finished a turn” and “the product is accepted.”

Persistence is divided among SQLite, files, terminal processes and provider storage. [Database models][database], lines 177–317, store terminal identity, parent/caller, configuration and inbox state; lines 1034–1155 add project aliases, outcomes, flows, handoff results and idempotency keys. Workflow run/step/event journals are separate tables (lines 2141–2405). The [memory service][memory], lines 379–398, uses Markdown wiki content plus SQLite metadata. tmux preserves a live CLI independently of a browser connection. It does not by itself recreate a dead provider conversation after machine loss.

At server startup, [the lifespan code][api], lines 1592–1815, initializes/reconciles state and starts terminal-output consumers, status monitoring, inbox delivery and scheduled flows. Output reaches an event bus and log/status consumers; inbox readiness is derived from provider status. The [inbox consumer][inbox], lines 90–158, runs delivery independently per terminal, coalesces readiness events and serializes each receiver's delivery to avoid interleaved or duplicate pastes. This is operational coordination infrastructure, not a product-level task state machine.

## Feature matrix

Verdicts describe implementation at this revision, not what arbitrary new prompts or integrations could eventually achieve. Every row has its own source anchor and boundary.

| ID | Capability | Verdict | Implementation evidence and difference from Wingman |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Exact** | [Terminal creation][terminal], lines 2852–3061, 3117–3299, and [tmux creation][tmux], lines 68–143, create separate terminal resources and native CLI instances. Multiple instances of the same profile are possible. Their lifetime is a terminal lifetime, not an enduring organizational employee. |
| F02 | Extensible agent profiles, roles and team composition | **Similar** | [Profile model][profile], lines 35–85, carries prompt, role, provider, tools, delegation ceiling, skills and metadata; [profile API][api], lines 2886–3345, supports discovery, validation and CRUD. Supervisors can launch profiles dynamically, but no standing team/leadership schema binds them to Wingman products. |
| F03 | Agent directory and visible working relationships | **Resembles** | [Dashboard][dashboard], lines 78–183 and 380–440, lists running instances by session/profile and filters them by profile/status. [Terminal model][terminal-model], lines 126–185, exposes caller and consumer-defined group relationships at the API/model level. The inspected Web UI does not render those as working relationships. [SupervisorDashboardStream][supervisor-view], lines 129–178, is a reusable library fold deriving session membership, not evidence of a wired-in relationship view. A visible role/project/team directory with reporting and collaboration relationships remains to build. |
| F04 | Telegram main channel and Butler routing | **Absent** | The [entry points][package], lines 130–134, and [HTTP surface][api], lines 3925–4310, expose CLI/HTTP/MCP/session operations. Searches of `src/` and `web/src/` for Telegram/Butler found no corresponding adapter or routing service. External event plugins are an integration seam, not an implemented Butler. |
| F05 | Cross-project registry, intake and existing/new routing | **Resembles** | [Memory identity][memory], lines 329–375, derives a project ID from override, normalized Git remote or cwd; [terminal grouping][terminal-model], lines 172–185, is consumer-defined. Neither interprets new requests against a product registry or creates project leadership. Searches of API models, services and UI found sessions/workflows rather than a product-intake model. |
| F06 | Per-project product and technical leadership | **Resembles** | [Built-in supervisor][supervisor-profile], lines 14–25 and 37–59, coordinates developer and reviewer work. The reusable role field in [profile model][profile], lines 38–47, can describe new leaders, but ProductMaster/TechMaster collaboration and per-project ownership are not implemented as application behavior. |
| F07 | Proportionate research/discovery and iterative clarification | **Resembles** | [Explicit prompt-answer tool][mcp], lines 1062–1077, and [waiting state][terminal-model], lines 14–22, allow a CLI to request input. These handle provider interaction; no discovery lifecycle, uncertainty record or project-routed clarification loop was found in services/models/UI. The supervisor prompt starts with coding delegation, [lines 37–50][supervisor-profile]. |
| F08 | Product scope, specifications, scenarios and DoD | **Resembles** | [Supervisor profile][supervisor-profile], lines 31–33 and 52–57, requires task files; [workflow model][workflow-model], lines 180–207, offers prompts and output schemas. Those permit supplied artifacts and machine-readable output validation, but do not define or maintain product scope/acceptance documents or enforce product DoD. |
| F09 | Technical decomposition, assignments and shared tracking | **Similar** | [Assignment implementation][orchestration], lines 2664–2801, creates real assigned workers; [workflow engine][workflow], lines 738–969 and 1017–1123, tracks step attempts/states. [Supervisor prompt][supervisor-profile], lines 22–33, delegates decomposition/tracking to the model and task files. There is no common ticket backlog, assignee/comment/blocker record spanning ordinary agent sessions. |
| F10 | Portfolio/project dashboard | **Resembles** | [Dashboard][dashboard], lines 78–183, aggregates sessions, profiles and terminal status; [workflow run view][run-detail], lines 38–78 and 145–193, provides run controls. These are real operational dashboards, but have no product goals, acceptance progress, backlog or portfolio status model. |
| F11 | Agent chat, rooms and direct collaboration | **Similar** | [Messaging][orchestration], lines 2826–2926, routes replies and checks explicit targets against caller/child/discovered-sibling permissions; [inbox API][api], lines 9017–9094, persists and exposes messages. Direct agent messaging exists. [Inbox UI][inbox-ui], lines 49–75 and 93–105, is receiver-scoped, not a room application with participants, project discussion threads and Room1/Room2 history. |
| F12 | Management escalation and human decisions/approvals | **Similar** | [Prompt-answer tool][mcp], lines 1062–1077, handles native questions; [approval gate][approval], lines 188–234, refuses unapproved script plans; [run UI][run-detail], lines 62–75 and 177–193, supports approval/resume. These are substantial human-control mechanisms, but no worker → project room → management → Butler escalation chain. |
| F13 | Durable project knowledge/directives | **Similar** | [Memory service][memory], lines 329–398 and 731–797, supplies stable project IDs and scoped Markdown wiki storage. [Profile fields][profile], lines 51–56 and 74–85, add skills/resources/instructions. Wingman's SCOPES/SPECS/HARNESS taxonomy and links to product acceptance must be supplied. |
| F14 | Persistent identity, conversation and work continuity | **Similar** | [Registry][database], lines 177–305, and [terminal model][terminal-model], lines 213–225, retain launch and initial-delivery facts; [workflow resume][workflow], lines 1342–1465 and 1573–1706, rebuilds journaled runs. [Launch option][launch], lines 220–224, explicitly resumes a prior Claude Code conversation. This is not general cross-provider Codex identity restoration or an immutable organizational agent history. |
| F15 | Proactive supervision/periodic wake/blocker follow-up | **Resembles** | [Flow daemon][api], lines 236–254, wakes every 60 seconds to execute due flows; [flow execution][flows], lines 220–288 and 290–388, renders a scheduled prompt and launches/recycles its session. A supervisory prompt can be scheduled, but no built-in project/tracker blocker inspection and follow-up policy exists. |
| F16 | Parallel products/concurrent specialists | **Similar** | [Async assign][orchestration], lines 2679–2697 and 2767–2801, permits concurrent worker initialization; [Python workflow shim][shim], lines 220–248, supports threaded fan-out with explicit step IDs. Separate directories/sessions can run concurrently. Wingman project boundaries are consumer-owned; YAML `parallel`/`pipeline`/`loop` remain unimplemented ([engine][workflow], lines 1557–1571 and 1972–1990). |
| F17 | Real multi-host execution/shared coordination | **Similar** | [Remote assignment][orchestration], lines 2456–2588, posts to a remote CAO node and installs callback routing to the supervisor inbox. This is real remote placement, not local subprocesses. Each node must already have its profile/workspace/auth/network setup; remote+worktree is rejected (2520–2528), and shared cross-host product records are not automatically established. |
| F18 | Executive current/recent/next/blockers overview | **Resembles** | [Fleet summary][supervisor-view], lines 168–218, reports counts, providers, waiting terminals and last activity; [dashboard][dashboard], lines 78–131, adds descriptions/status. These identify active or waiting processes. They do not generate semantic accomplishments, planned next work and actionable product blockers. |
| F19 | Per-agent summary timeline linked to work | **Resembles** | [Session timeline construct][timeline], lines 1–14, 33–45 and 96–170, records delegation/message metadata and timestamps; [workflow timeline][workflow-timeline], lines 121–160, renders durable run events. Neither is a persistent per-agent narrative briefing connected to tickets, edits and acceptance evidence. Event history is credited without treating it as the requested summary feed. |
| F20 | Detailed per-agent coding workspace | **Similar** | [Live terminal view][terminal-view], lines 15–61 and 85–119, exposes the actual CLI through xterm/WebSocket; [agent panel][agent-panel], lines 25–65 and 93–145, adds output, inbox and lifecycle actions. It provides authentic coding-session drill-down, but not an integrated files/diff/artifact/review browser and typed conversation workspace matching all Wingman controls. |
| F21 | Live activity/lifecycle controls/steering | **Similar** | [Agent panel][agent-panel], lines 93–139, supports delete, graceful exit and message input; [terminal socket][terminal-view], lines 47–60 and 85–103, streams/input/resizes; [API][api], lines 4929–5094, supports input, keys, output and exit. Workflow cancel/resume also exists. Cross-provider fork/compact/archive, continuing-goal budgets and usage accounting are not a unified control model. |
| F22 | Testing/integrated verification/acceptance/delivery | **Resembles** | [Supervisor review loop][supervisor-profile], lines 37–50, requires reviewer approval as instructions; [structured workflow output][workflow], lines 673–735 and 738–969, validates results/retries. Coding CLIs can run tests, but no native TestMaster acceptance process, enforced integrated product DoD or acceptance-to-delivery transition exists. |
| F23 | Autonomous operation with human direction | **Similar** | [Supervisor prompt][supervisor-profile], lines 14–50, drives developer/reviewer iteration; [scheduled execution][flows], lines 220–288 and 371–388, can trigger autonomous work; [assignment][orchestration], lines 2664–2801, permits the model to grow execution. This supports autonomous supervised coding, but the complete research-to-product delivery organization is user-authored. |
| F24 | New profiles accommodated by connected views | **Similar** | [Profile APIs][api], lines 2886–3345, and [dynamic UI profile list][agent-panel], lines 141–145, accept added profiles; [dashboard filtering][dashboard], lines 104–108, derives types from running instances. Messaging, workflows and fleet controls are profile-generic. The absent room/tracker/product views still need implementation, so the complete connected-view requirement is not met. |

## Agent definition, creation and lifecycle

### What an agent actually is

An `AgentProfile` defines reusable frontmatter plus Markdown instructions. [The model][profile], lines 35–85, distinguishes name, description, provider, body/system prompt, role, tool policy, delegation policy, advertised skills, capabilities/tags, MCP servers, resources, model and permission mode. Provider-specific fields follow: Codex named configuration and inline TOML overrides (lines 88–108), Claude/Kiro effort knobs and other provider options. `role` changes defaults and guidance. It does not instantiate a person or create a management position.

A live `Terminal` has a generated eight-hex ID and a backend session/window. It records the provider, optional profile/model, caller, effective/delegable tools, group, description, metadata, lifecycle facts and status. See the [terminal model][terminal-model], lines 10–22 and 126–229. Multiple terminals can share one profile. A `session` groups backend terminals and their environment. Provider conversations and products have different identities. The terminal is the independent execution instance. Its prompt defines behavior. Workflow runs and steps add separate durable units of work.

The grouping field is intentionally general-to-specific prefix metadata. CAO explicitly leaves its meaning to consumers ([terminal model][terminal-model], lines 172–185). Wingman could encode organization/project/team here, but that would be its schema. Identity must also be separated from a profile: agent-scoped memory uses profile-scoped storage ([memory path rules][memory], lines 752–786), so two workers with the same profile do not automatically receive independent personal memories.

### Defining and launching instances

Profiles can be installed/created/updated through the [profile API][api], lines 2886–3345, with validation/template support. The [search service][profile-search], lines 1–14 and 23–25, indexes name/description/capabilities/tags rather than the full prompt and rebuilds its corpus each query. This supports a supervisor discovering suitable specialist definitions, not automatic team staffing against a product plan.

`cao launch` resolves tools from explicit flags and profile/role defaults. It resolves a delegation ceiling, selects a provider and sends the launch request ([launch command][launch], lines 256–315). [Session creation][session], lines 139–162, forwards the effective parameters into the terminal service. Terminal creation optionally prepares an isolated Git worktree (lines 2689–2705). It creates a backend session/window under lifecycle ownership and inserts terminal registry facts (2852–3061). It then builds the provider (3139–3150). Initialization runs synchronously or through a deferred task (3158–3196). Creation returns a terminal backed by a process.

Optional ephemeral profile creation is a distinct, gated surface ([MCP implementation][mcp], lines 1759–1930). The [orchestration claim code][orchestration], lines 856–925, requires a creator-owned claim for reserved ephemeral targets and can return an already-recorded terminal on keyed retry. It is useful for bounded task-specific agents, but it is not an unrestricted durable organization designer; remote ephemeral placement is refused by the assignment path (lines 2699–2701).

### Tools, authority and execution isolation

The native provider remains responsible for filesystem edits, commands and its own tools. CAO adds orchestration/memory/workflow MCP tools, scoped catalogs and role/tool mappings. The effective child capability must be capped by the recorded parent delegation ceiling; remote placement checks that the other node supports this policy before it sends the ceiling ([remote placement][orchestration], lines 2534–2547). Explicit messaging targets are also checked, rather than allowing arbitrary terminal IDs (lines 2898–2907). This is a meaningful capability boundary around coordination.

Those controls do not imply identical enforcement of native tools across providers. [Codex launch][codex], lines 1647–1732, explicitly uses `--yolo` unless an applicable `codexProfile` preserves the native sandbox/approval policy; unrestricted `*` forces yolo, and narrower tools also add prompt constraints. Therefore a Wingman deployment must select provider-native permission configuration deliberately. “CAO allowed tools” is not a uniform OS sandbox.

The default workspace is shared. Opting into [worktrees][worktrees], lines 1–20 and 100–123, creates `.cao/worktrees/<terminal_id>` and branch `cao/<terminal_id>` from the repository's HEAD. This isolates concurrent edits, not credentials, machine access or external side effects. There is no automatic merge-back pipeline. On cleanup, force-removal discards uncommitted/untracked worktree content but safe branch deletion leaves unmerged commits recoverable (lines 148–185). Wingman must arrange committing, integration and verification before worker retirement.

### Routing and concurrency

`assign` creates a worker and returns quickly while server-owned initialization/task delivery continues. [The implementation][orchestration], lines 2679–2687 and 2767–2801, explicitly decouples initialization so several assigns can initialize concurrently. `caller_id` stores the creator relationship for automatic replies. `handoff` uses the shared run-step substrate to wait for a result; [orchestration helpers][orchestration], lines 1605–1844 and 1996–2454, handle blocking execution, transport ambiguity and cleanup/result reporting. These are execution semantics rather than a hierarchy of organizational accountability.

The [inbox][inbox], lines 65–158, serializes one receiver while permitting other receivers to proceed. Readiness events trigger delivery. The service also reconciles orphaned messages (lines 547–560 onward). Delivery is not synonymous with agent acceptance: `after_dispatch` means only that the immediate attempt has been decided, explicitly not acknowledgment (lines 180–186). There are submit-confirmation/redelivery paths for swallowed Enter or stale terminal state. Wingman would still need explicit task acknowledgment/completion records above message transport.

Remote assignment creates a session on the selected CAO server. It resolves that server's profile and sets `CAO_CALLBACK_URL`/`CAO_CALLBACK_TERMINAL_ID` to route replies back. See the [remote implementation][orchestration], lines 2473–2505 and 2555–2588. The remote filesystem interprets cwd (2558–2562). Assignment does not copy code or create project records. `target_host` and local worktree provisioning cannot be combined (2520–2528). Callback context lives in the process-local session environment. A server restart can lose it ([terminal model][terminal-model], lines 146–155). Wingman's Mac/Endeavour continuity must account for this limit.

### Persistence, scheduling and resumption

A running terminal can outlive the viewing UI. The browser closes only its socket and xterm instance ([terminal view][terminal-view], lines 113–119); backend/provider lifecycle is separately managed. SQLite and output logs permit rediscovery. They do not guarantee that every provider's internal conversation can be reconstituted. The public resume launch option specifically promises Claude Code `--resume` ([launch][launch], lines 220–224). No equivalent general Codex conversation restoration was established in the inspected launch path.

Workflow continuity is stronger than ordinary terminal continuity. The [YAML engine][workflow], lines 1342–1465 and 1573–1706, reconstructs state from the journal and resumes from unfinished steps while preventing overlapping live drive loops. The Python script tier starts a subprocess ([script runner][script-runner], lines 1356–1570), whose [shim][shim], lines 64–158, sends run ID, generation and explicit step identity over HTTP. On resume the script executes top-to-bottom and stored agent-step results may be replayed after fingerprint/provenance checks. **Arbitrary Python side effects between step calls are not automatically rolled back or deduplicated.**

[Scheduled flows][flows], lines 220–231 and 284–388, advance their next schedule before execution, optionally run a script, render a prompt, skip busy conductors, and otherwise recycle/create a named flow session. The [daemon][api], lines 236–254, checks due work every minute. This can run a configured “inspect projects” supervisor, but CAO does not supply ProjectMaster's domain-specific inspection/follow-up behavior, and recycling flow sessions is different from waking the same durable employee conversation.

### Interruption, failures, recovery and completion

Human steering is available through ordinary input, key events and graceful exit/delete actions ([agent UI][agent-panel], lines 93–139). Native dialogs have a separate explicit `answer_user_prompt` path ([MCP tool][mcp], lines 1062–1077). [Terminal error types][terminal-model], lines 25–106, distinguish a live CLI waiting for a human from an exited provider or failed initialization; orchestrated task delivery must not become an accidental menu answer or shell command.

Deferred initialization failures are persisted rather than silently turning into an idle worker. [Recovery implementation][terminal], lines 4022–4218, revisits interrupted ownership and initial deliveries; failure sidecars preserve outcomes across database-write trouble. These mechanisms protect transport/lifecycle truth, not the semantic success of an implementation. The [recovery tests][restart-tests], lines 29–79 and 83–105, explicitly model unreadable rows, preserved prior failure, restart interruption and capped retry backoff.

For workflow steps, [agent execution][agent-step], lines 436–594 and 813–919, waits for provider completion, extracts output and handles cancellation/teardown. [YAML retries][workflow], lines 738–969, retry run failures, separately handle output-schema reprompts, and apply halt/continue policy. Cancellation sets a flag and event to interrupt the in-flight wait (1259–1284), rather than only waiting for the next step boundary. This should not be confused with undoing already-completed edits or external actions.

Script-tier recovery uses a deliberately conservative [replay decision][replay], lines 19–73 and 129–141: replay/execute/diverged/decision-required depend on identity, stored envelope, outcome and declared recovery policy. Human-authorized skip/rerun does not bypass all provenance checks. The `reconcile` policy currently behaves like idempotent re-execution because generic external reconciliation is deferred (52–60). Approval gating is separate: [the gate][approval], lines 188–234, checks the frozen plan identity, distinguishes unavailable identity/store from absent approval, and refuses execution when needed.

Completion in the ordinary agent layer means the adapter observed the end of a CLI turn or the worker sent a result. A workflow can additionally validate structured output, but completed transport/workflow state is not proof that tests passed or requirements were satisfied. The shipped supervisor's developer/reviewer cycle ([profile][supervisor-profile], lines 37–50) is an instruction to the LLM. There is no mandatory product acceptance state machine. Wingman must supply integrated verification, acceptance evidence, delivery assessment and “stop until further request” policy.

Retirement is explicit for long-lived assignments: the returned assignment message asks the caller to delete its worker ([orchestration][orchestration], lines 2788–2797). Handoff/run-step paths can tear down workers after successful extraction, while errors expose terminal IDs for inspection. [Teardown][terminal], lines 6616–6662 and 6805–6876, removes runtime resources before registry rows and retains retry handles when cleanup is uncertain. Exact identity checks for failure tombstones avoid killing a later session that reused the same name. Deletion is lifecycle cleanup, not an archive of a persistent organizational employee.

## Coordination trace: a supervisor assigns coding work

The following is a source-traced request path, not a live run conducted for this assessment.

1. The human launches `code_supervisor` in a product directory. [CLI permission/provider resolution][launch], lines 256–315, and [session service][session], lines 139–176, produce the initial supervisor terminal. The [profile][supervisor-profile], lines 28–33, instructs the supervisor to put task descriptions in files and delegate coding to `developer`.
2. The supervisor calls MCP `assign(agent_profile="developer", message=...)`. [MCP registration][mcp], lines 647–691, checks its tool authorization and forwards to `_assign_impl`; [assignment implementation][orchestration], lines 2716–2786, resolves caller identity, adds callback instructions where appropriate, and requests deferred creation. Parent tools/cwd/provider are read in `_create_terminal` (1034–1060 onward), with profile overrides and delegation constraints applied.
3. The server allocates a new window/process and database row, returns the terminal ID, then initializes and sends the accepted initial message. [Creation][terminal], lines 2852–3196, and [deferred initialization][terminal], lines 5019–5086, separate admission from provider readiness. The supervisor can assign another specialist without waiting for the first CLI to finish its startup.
4. The developer uses native CLI coding tools. Its progress is visible as terminal output/status. No ticket record appears automatically: the supervisor's task file is the shared assignment artifact, while the terminal row stores execution metadata.
5. The developer calls `send_message(message=...)` without receiver ID. [Reply routing][orchestration], lines 2832–2879, chooses its recorded caller or cross-node callback supervisor. An explicitly named colleague is allowed only through the target binding/discovery rules (2898–2907). [Inbox route][api], lines 9017–9094, records the message and attempts delivery; [consumer][inbox], lines 90–158 and 160–218, delivers when the supervisor can receive it. This wakes interaction through ordinary provider input rather than a room subscription model.
6. The supervisor sends the code to `reviewer`, discusses changes via messages/files, and repeats as the [profile requests][supervisor-profile], lines 37–50. The operator may inspect the receiver inbox or open its [real live terminal][terminal-view], lines 47–103. Questions can surface through native CLI prompts, but no Butler carries them to Telegram.
7. When the result is satisfactory, the supervisor reports to the user and deletes assigned worker terminals. [Cleanup][terminal], lines 6856–6876, confirms runtime teardown before deleting registry state. Worktree commits must first be integrated or preserved. The framework does not decide product DoD or create a delivery acceptance record.

For remote execution, step 2 instead reaches `_assign_remote`, posts to the other node's `/sessions`, forwards the delegation ceiling, and installs callback environment ([remote code][orchestration], lines 2531–2588). This provides a concrete Mac-to-Linux primitive. A shared filesystem or repository synchronization and shared product/tracker identity remain deployment/application responsibilities.

## Major capabilities beyond Wingman's stated product

**Heterogeneous provider orchestration.** Wingman specifies Codex agents. CAO's [provider-aware profile model][profile], lines 40–49 and 88–141, and [Codex adapter][codex], lines 1647–1900, support cross-provider staffing with native authentication, model/config choices and provider-specific tool mapping. That could allocate reviewing or execution to other coding CLIs. Integration costs include different status parsers, permission semantics, prompt delivery, availability and resume guarantees. It is not a drop-in uniform provider protocol.

**A durable, inspectable workflow runtime with replay and plan approval.** [Script execution][script-runner], lines 1356–1570 and 1572–1897, [shim identity][shim], lines 104–157, [replay gate][replay], lines 19–73, and [approval gate][approval], lines 188–234, go beyond Wingman's described coordination records. They can make repeatable delivery operations recoverable and reviewable. Wingman could use this for bounded validation/build/release procedures, but must model external side effects deliberately and keep run identity separate from product/ticket identity. YAML accepts several reserved constructs it cannot execute: [the engine][workflow], lines 1972–1990, explicitly raises for parallel/loop/guards. Python-authored branching/concurrency is a different, implemented route.

**Elastic worker placement.** [The elastic assign tool][mcp], lines 784–931, acquires a broker lease, waits for the worker, passes a broker callback gateway and assigns remote work. `complete_assignment` first returns the final message then releases capacity (972–1010). This is useful if Wingman expands beyond two fixed hosts. The completion protocol is cooperative: a worker that never acknowledges completion can look like a slow worker; infrastructure/lease cleanup and deployment setup remain necessary. The ordinary `target_host` API is already useful without adopting the EKS topology.

**Cross-session memory, wiki projection and opt-in instruction learning.** [Memory storage][memory], lines 379–398 and 731–797, supplies inspectable scoped knowledge beyond individual CLI transcripts. [Promotion service][promotion], lines 1–24, 116–176 and 178–190, can turn recalled agent-scope lessons into a bounded Learned Patterns block with planning/apply separation and opt-in gating. Wingman could carry conventions and lessons across new conversations. Recall count is reinforcement evidence, not measured quality improvement, which the source explicitly acknowledges (lines 3–9); evaluation must precede automated promotion of consequential guidance.

**Protocol-level embedding and operational observability.** The [AG-UI supervisor construct][supervisor-view], lines 53–127, folds snapshots/deltas and lifecycle counters; [session timeline][timeline], lines 33–82, exposes delegation/message metadata. [API routes][api], lines 2161–2679, provide event and AG-UI surfaces; workflow UI supports playback/diagnostics. These are useful building blocks for Wingman's custom dashboards and external operator clients. They carry runtime state and events, so Wingman must add product/task semantics and narrative summaries instead of presenting protocol counters as executive progress.

**Pluggable launch decisions.** The [decision engine][decisions], lines 1–47, 54–73 and 133 onward, separates policy checks, decision answers, fallbacks and shadow work; profiles include model/effort/provider knobs. This can experiment with routing a delegation to an appropriate model/effort within policy. It does not solve product prioritization or human business decisions, and should be evaluated as a bounded launch policy rather than autonomous organizational judgment.

## Distinctive mechanisms and grounded innovation

CAO's most useful distinctive mechanism is retaining **full native coding CLI processes while exposing a common orchestration interface**. A worker can preserve its native tool repertoire and authentication, yet another independent model can assign it work and receive an inbox callback. The concrete backend/provider split ([tmux][tmux], lines 68–181; [provider launch][codex], lines 1647–1900) makes this adaptable. Its cost is substantial engineering around TUI status, disappearing processes, modal dialogs, stale output and dropped submission. Codex's dispatch baseline attribution ([adapter][codex], lines 1495–1597) shows that the project addresses those failure modes instead of assuming every captured “done” footer belongs to the latest request. This is a mechanism assessment, not a claim of industry uniqueness.

A second strong mechanism is **layered execution truth**: admission, initialization, initial-message delivery, provider status, workflow step outcome and product success are distinguishable. [Terminal lifecycle fields][terminal-model], lines 186–225, persist failure/initial-delivery/incarnation facts, and [cleanup][terminal], lines 6635–6656, refuses to destroy resources on uncertain identity. That separation is directly valuable for Wingman because a dashboard must not turn an accepted assignment into an apparent accomplishment. It still requires Wingman to create the product-level truth above it.

The script workflow's **fingerprinted replay with human recovery decisions** is another substantial mechanism. [The gate][replay], lines 19–73, checks provenance before equality and refuses changed/unsafe replay rather than quietly repeating an effect. The shim makes replay visible to authors ([shim][shim], lines 144–157), including the fact that a replayed terminal ID may no longer identify a live process. Limits are explicit: reconciliation is not a distinct implemented operation, arbitrary script effects remain outside step replay, and recovery declarations do not prove external idempotence.

Finally, **delegation authority is transported with work**, including remote placement ([orchestration][orchestration], lines 2534–2547), while message targets stay bound to creation/discovery relationships (2898–2907). This provides a useful foundation for a growing organization in which specialists should not automatically inherit their supervisor's unrestricted privileges. Native provider enforcement must still be configured correctly. The Codex yolo path demonstrates why a coordination capability boundary alone is insufficient.

## Practical Wingman fit and gaps

CAO could be used directly for launching Codex supervisors/specialists, parallel assignments and callbacks, operator terminal drill-down, scheduled entry points, structured workflow steps, scoped memory, and explicit Mac/Endeavour node targeting. Its profile CRUD and discovery reduce the cost of adding BackendCoder/FrontendCoder/MobileCoder/TestMaster definitions. Existing browser controls provide a workable operations console while Wingman builds its richer views.

The most important adaptation is to introduce stable organizational identity **above** CAO terminal identity. A Wingman agent instance should retain role, project, team, responsibilities, personal timeline and conversation history while it acquires/replaces terminal sessions. Profile names, backend session names, workflow runs, tickets and organizational agents need explicit separate identifiers. Persist remote callback/host bindings in Wingman records rather than relying only on process-local session environment.

Wingman must build these product capabilities:

- Intake, a portfolio registry, and routing for new or existing products.
- Telegram Butler and question/answer correlation.
- ProductMaster discovery and specification records.
- TechMaster ticket decomposition and dependencies.
- A shared tracker with comments and blockers.
- Management and project room histories.
- TestMaster integrated acceptance and deliverable assessment.
- Executive current/recent/next summaries linked to original evidence.

Metadata groups and inboxes can carry references to these records. Wingman still needs durable schemas and views for them.

For concurrent coding, choose explicit integration ownership. Shared cwd is vulnerable to concurrent edits; optional local worktrees isolate source but do not merge results. Remote nodes need usable repo paths, credentials, profiles and common coordination records; CAO does not automatically transfer the Mac workspace to Endeavour. Provider-native sandbox/approval settings and terminal-status compatibility should be verified on the exact deployed Codex version. A standing organizational service must also decide when to relaunch a dead employee session, what context to restore and how to avoid duplicate work.

Overall, adopt CAO most plausibly as an execution adapter beneath Wingman's own organization model. Treating it as the full Wingman product would leave the central product-discovery, project-management, human-channel and executive-continuity requirements implicit in prompts.

## Verification scope and confidence

This is a fresh static assessment of the checked-out revision. Parent directories and the checkout were checked for applicable `AGENTS.md`; no additional on-disk instructions were found along this checkout's path. The supplied global instructions were followed. No browser or external lookup was needed to assess local source, and no runtime behavior is described as exercised here.

Implementation inspection followed:

- entry points.
- launch/session/terminal creation.
- tmux backend.
- Codex command/permission/status behavior.
- profile/terminal/workflow models.
- SQLite persistence.
- MCP orchestration and authorization.
- direct/remote assignments and callbacks.
- inbox delivery.
- flow scheduling.
- workflow agent-step/retry/cancel/resume.
- Python shim/replay/approval.
- worktree creation/cleanup.
- memory identity/storage.
- learning promotion.
- launch decisions.
- browser fleet/agent/terminal views and AG-UI derived views.

Source links above identify the inspected regions rather than relying on README claims.

Relevant test bodies inspected include:

- [workflow service tests][workflow-tests], lines 120–179 (schema success and crash retries), 496–579 (in-flight cancellation) and 637–664 (reserved parallel/loop seams).
- [restart recovery tests][restart-tests], lines 29–105 (durable failure/retry/cancellation).
- [cross-node notification tests][remote-tests], lines 30–95 (mocked supervisor callback and gateway credentials).

[Worktree tests][worktree-tests], lines 101–120 and 155–215, cover real temporary-Git checkout isolation, retained unmerged commits and forced worktree cleanup. These are repository evidence, not tests executed in this assessment. Mocked HTTP/provider tests do not prove a live two-machine deployment or current provider CLI compatibility.

Absence findings were checked across likely paths: `src/cli_agent_orchestrator/{api,models,services,mcp_server,cli,agent_store}`, `src/cao_workflow`, and `web/src`, including searches for Telegram, rooms, tickets, project registry/portfolio, product leadership and conversation lifecycle controls. Related hits were followed rather than counted as exact equivalents: project aliases belong to memory identity, ticket mentions to guidance/logging, timelines to event metadata, and dashboards to fleet/run state. Examples and deployment documentation demonstrate intended compositions but were not promoted into guarantees about native organizational behavior. A source-reference search for `SupervisorDashboardStream` found library exports, tests, documentation and examples, but no production Web UI consumer; F03 therefore credits the visible session/profile list separately from API-level caller/group relations. The broad plugin/provider surface and alternate herdr backend were not exhaustively audited; security posture, capacity, real provider authentication, reboot recovery and distributed reliability need deployment-specific testing.

[package]: ../repo/pyproject.toml
[api]: ../repo/src/cli_agent_orchestrator/api/main.py
[profile]: ../repo/src/cli_agent_orchestrator/models/agent_profile.py
[terminal-model]: ../repo/src/cli_agent_orchestrator/models/terminal.py
[session]: ../repo/src/cli_agent_orchestrator/services/session_service.py
[terminal]: ../repo/src/cli_agent_orchestrator/services/terminal_service.py
[tmux]: ../repo/src/cli_agent_orchestrator/backends/tmux_backend.py
[codex]: ../repo/src/cli_agent_orchestrator/providers/codex.py
[database]: ../repo/src/cli_agent_orchestrator/clients/database.py
[mcp]: ../repo/src/cli_agent_orchestrator/mcp_server/server.py
[orchestration]: ../repo/src/cli_agent_orchestrator/utils/orchestration.py
[inbox]: ../repo/src/cli_agent_orchestrator/services/inbox_service.py
[flows]: ../repo/src/cli_agent_orchestrator/services/flow_service.py
[workflow-model]: ../repo/src/cli_agent_orchestrator/models/workflow.py
[workflow]: ../repo/src/cli_agent_orchestrator/services/workflow_service.py
[agent-step]: ../repo/src/cli_agent_orchestrator/services/agent_step.py
[script-runner]: ../repo/src/cli_agent_orchestrator/services/script_runner.py
[shim]: ../repo/src/cao_workflow/__init__.py
[replay]: ../repo/src/cli_agent_orchestrator/services/step_replay.py
[approval]: ../repo/src/cli_agent_orchestrator/services/approval_gate.py
[worktrees]: ../repo/src/cli_agent_orchestrator/services/worktree_service.py
[memory]: ../repo/src/cli_agent_orchestrator/services/memory_service.py
[promotion]: ../repo/src/cli_agent_orchestrator/services/promotion_service.py
[decisions]: ../repo/src/cli_agent_orchestrator/decisions/engine.py
[launch]: ../repo/src/cli_agent_orchestrator/cli/commands/launch.py
[supervisor-profile]: ../repo/src/cli_agent_orchestrator/agent_store/code_supervisor.md
[profile-search]: ../repo/src/cli_agent_orchestrator/services/profile_search.py
[supervisor-view]: ../repo/src/cli_agent_orchestrator/services/agui/supervisor_dashboard.py
[timeline]: ../repo/src/cli_agent_orchestrator/services/agui/session_timeline.py
[dashboard]: ../repo/web/src/components/DashboardHome.tsx
[agent-panel]: ../repo/web/src/components/AgentPanel.tsx
[terminal-view]: ../repo/web/src/components/TerminalView.tsx
[inbox-ui]: ../repo/web/src/components/InboxPanel.tsx
[run-detail]: ../repo/web/src/components/workflow/RunDetail.tsx
[workflow-timeline]: ../repo/web/src/components/workflow/WorkflowTimeline.tsx
[workflow-tests]: ../repo/test/services/test_workflow_service.py
[restart-tests]: ../repo/test/services/test_deferred_restart_recovery.py
[remote-tests]: ../repo/test/services/test_cross_node_notify.py
[worktree-tests]: ../repo/test/services/test_worktree_service.py
