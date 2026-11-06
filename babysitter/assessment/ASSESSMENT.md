# Babysitter assessment against Wingman

## Identity and fit verdict

- Repository: https://github.com/a5c-ai/babysitter
- Local checkout: `research/babysitter/repo`
- Inspected commit: `feb68abe397acc14f32b34984975c48fedba2b33` (`git rev-parse HEAD`); root package version `6.0.3`.
- Assessment date: 2026-11-05.
- Baseline: [Wingman purpose](../../WINGMAN_PURPOSE.md); [assessment guide](../../generic/assessments/ASSESSMENT_GUIDE.md).
- Method: read-only source assessment. No dependency installation, services, model calls, Kubernetes deployment, browser session, or runtime test execution.

**Verdict: a strong implementation source for Wingman's execution and governance substrate, and a substantial partial organizational platform, but not a ready-made Wingman organization.** This checkout is considerably broader than a workflow plugin. Alongside the Babysitter event-sourced workflow SDK it contains Genty's tool-capable sessions and autonomous orchestration, adapters for coding harnesses, and Kradle's Kubernetes-backed identities, dispatch runs, projects, boards, approvals, memory records and web views. Those implementations deserve credit independently of the older “workflow layer” classification.

The components do not establish Wingman's complete management chain. Telegram Butler, portfolio supervision, separate product/technical leaders, and a standing specialist organization remain application work. Durable persona records and executable coding processes exist. The default progress unit is a **workflow run or dispatch**. It does not represent an enduring employee responsibility with a maintained executive briefing.

Wingman still needs project-aware intake, management rooms, and summaries of recent results, current work, and next work. Several Kradle paths also need verification before adoption. Cancellation updates status without stopping the Kubernetes Job. Identity-targeted HTTP dispatch loads fewer permission resources than stack-targeted dispatch. Detailed session workspace panels contain placeholders.

## Architecture and actual execution model

### Three layers with different meanings of “agent”

The root [package manifest][manifest] lists SDK, Genty, adapters, Atlas, KIP and Kradle workspaces (lines 1–50). The metapackage is only an entry surface. The execution boundary is inside those packages. The short [runtime reference][runtime-reference] accurately describes the core replay contract, but it is important to inspect the implementation rather than infer a whole organization from that description.

**Babysitter SDK:** a process is an imported JavaScript/TypeScript function with `(inputs, ctx)`. A run stores metadata, inputs, tasks, results, and an append-only journal. [createRun][create-run], lines 16–70, allocates a ULID by default and resolves the runs root. It records the process entry point and optional nested ancestry. It validates inputs and hashes process code. Lines 72–107 append `RUN_CREATED` under a lock. This creates durable work state. It does not launch an LLM worker.

[orchestrateIteration][iterate], lines 47–92, acquires the run lock and initializes replay. It rejects unassigned bare runs, loads the process function, and executes it in process context. The [task intrinsic][task], lines 68–105, derives an invocation identity and looks for a journal effect. It returns a recorded result or throws a pending-effect exception. New effects serialize task descriptors, pass hooks and policy, and receive an effect ID (lines 108–180 onward).

Replay can execute the process body again while reusing resolved effect results. Actual side effects must remain behind task boundaries. The mechanism replays workflow decisions and returned values. It does not replay arbitrary external tools or guarantee exactly-once external mutations.

**Genty runtime/platform:** connects pending effects to executable workers. [Effect resolution][effects], lines 252–283, handles MCP tasks. It separately gates cross-agent dispatch and shell/Node execution. Plugin and host contexts default to pending work. The standalone [create-run entry][genty-entry], lines 56–63, sets two flags for autonomous dispatch when they are unset.

[Delegated execution][delegate], lines 101–174, creates fresh tool-capable sessions. It loads skills, checks policy, prompts the session, and disposes it. Lines 177–187 invoke an external harness when selected. These are independent execution contexts. The common internal delegated worker is temporary. [AgentCoreSessionHandle][core-session], lines 1291–1358, owns its history, session ID, listeners, and provider/tool loop. It rejects overlapping prompts to one handle. Separate handles or processes provide parallel execution.

**Kradle control plane:** provides organization resources and cloud execution. [resource model][resources] lines 32–77 distinguishes persona/definition/stack configuration, dispatch run, execution attempt, adapter session, context bundle, workspace and transcript. Its declared storage split is etcd for configuration and Postgres for aggregated operational records. The concrete HTTP dispatch path inspected here goes through Kubernetes resource APIs and status subresources. Do not assume every returned object in a pure controller helper has been durably saved merely because its kind declares a storage class. [API dispatch][api-controller] lines 252–318 explicitly applies the run and its status, memory snapshot and optional PVC after calling the dispatch controller.

The [dispatch controller][dispatch] lines 296–348 resolves identity and stack, runs permission review, snapshots context/memory, optionally returns `AwaitingApproval`, provisions/reuses workspace, and creates run/attempt records (lines 350–510). It builds and submits an actual Kubernetes Job (lines 512–618). [Job client][job-client] lines 417–579 constructs an agent container with harness/provider/model, task, org/run identity, service account, granted model secret, resources and either a PVC or ephemeral `emptyDir`. Lines 588–595 applies the Job through a resource gateway. This is real cluster execution infrastructure capable of using multiple nodes. It is not merely a local subprocess described as distributed execution.

A fourth, complementary surface is the **Observer dashboard**, which discovers configured filesystem run sources and groups them by project ([source discovery][observer-discovery], lines 12–25, 90–97 and 112–135). Its [executive banner][observer-summary], lines 7–14 and 37–91, summarizes active/failed/stale runs and pending approvals. This is a useful portfolio alarm, but its name does not make it a Wingman per-agent current/recent/next briefing. Its [approval action][observer-approval], lines 52–129, resolves a run directory and checks both task metadata and journal kind before recording a breakpoint answer through the SDK. It supplies a concrete human interaction surface for local workflow runs independently of Kradle.

The runtime container [entrypoint][pod-entry] clones a target repository, creates a branch, launches the coding harness, stages/commits/pushes edits and opens a Gitea PR (lines 93–164, 216–253, 281–324). Results return through a per-run callback. Kubernetes, registry images, model credentials, git backend and callback connectivity are actual deployment dependencies, not bundled guarantees.

### Gateway Kanban, remote adapters and Commander are separate product surfaces

The **adapters gateway** is not simply a proxy for Kradle or a copy of the Observer's run list. [Gateway server][gateway-server] lines 172–196 constructs its own run manager, workspace service, HTTP/WebSocket server and Kanban routes. Authenticated session creation dispatches through `runManager.start`, optionally carrying a source session for a fork (lines 381–414); authenticated dispatch/stop routes call the live manager (lines 484–535). The stop implementation actually aborts its active handle ([gateway run manager][gateway-manager], lines 214–219), unlike Kradle's status-only cancel route. Its static [WebUI loader][gateway-static], lines 37–58 and 76–84, searches an optional installed `genty-webui` package or configured build directory and returns 404 if absent. This assessment establishes the checked-out backend and its UI-serving seam. It does not assert that an installable UI build was present or rendered.

The gateway owns separate project, backlog, review, and automation records. [Backlog service][gateway-backlog], lines 109–164, accepts project/parent IDs, assignees, typed dependencies, acceptance criteria, and decomposition. It also links sessions and runs. Lines 1653–1695 create and normalize an issue in its project. Lines 1774–1786 persist and reload it. Lines 1790–1835 check board movement and reject policy violations. Lines 2502–2535 reject a session link to a second issue before persisting dispatch links.

[Kanban storage][gateway-storage], lines 23–58, stores projects, issues, tags, context labels, automation rules, and executions. The default path is `~/.a5c/kanban-backlog.json`. Lines 73–92 read and write the whole JSON file. This provides a local tracker independent of Kubernetes. It does not establish transactional multi-writer or cross-host storage.

[Automation service][gateway-automation] lines 37–65 defines draft/active/paused/disabled/archived rules with timer/webhook triggers; lines 841–863 validates target and route before creation, lines 925–960 enforces lifecycle transitions, and lines 977–1043 records rejected events for inactive rules or missing routing. Lines 1068–1085 materialize an issue with configured assignees, criteria and decomposition, and lines 1101–1133 append execution/audit records. [Kanban routes][gateway-kanban-routes] lines 974–1045 expose rule CRUD, lifecycle and webhook delivery. This is a configurable recurring/event-driven **work intake** plane. It does not itself prove that materialized issues autonomously become staffed specialist work or that the HTTP server alone runs cron without the daemon/timer execution component.

[Gateway review service][gateway-review], lines 39–87, models decisions, anchored comments, follow-up targets, linked PRs, and CI status. Lines 530–555 record submitted reviews. Lines 580–599 reopen approved work when comments arrive. Without stored artifacts, `readArtifacts()` returns seeded review data (lines 501–519). The create-pull-request branch constructs a local linked-PR record with an incremented number and pending CI gates (lines 609–641). That branch makes no provider HTTP call. Actual Gitea publication belongs to the pod entry point.

Wingman could reuse these review and tracker mechanisms. It still needs real artifact/provider ingestion, explicit authoritative-record rules, and reliable persistence.

The **remote runner** is another execution route besides local spawn and Kubernetes Jobs. [Remote runner][remote-runner] lines 78–110 calls a `RemoteAdapter.connect`, binds supported live user-message injection and interaction responses, and streams received events onto the run handle. Lines 43–69 apply inactivity/run timeouts and disconnect on abort; lines 112–127 finalize completion/crash and cleanup. This is executable remote-session plumbing, but the connected adapter, endpoint, authentication and host-specific filesystem continuity still determine what a given deployment can do. It does not automatically create the Mac/Endeavour host registry or synchronize their projects.

**Commander** is an additional board/inspection/control client, not evidence that every visible simulated control is live. [WarRoom][commander-warroom] lines 46–66 composes board, inquiry/chat dock, review, steering, registry, run, memory and IDE overlays. [Backend factory][commander-factory] lines 56–66 explicitly selects a real gateway backend only for configured real mode; otherwise it creates a seeded mock. In Kradle-only real mode the gateway transport is inert (lines 19–53) and the separate Kradle snapshot/client path supplies resources. [Real backend][commander-real] lines 551–576 fetches authenticated agent/session/run lists, while lines 579–609 returns an empty task list and no-ops gateway-only board mutations. [Kradle orders][commander-orders] lines 126–167 resolves actual stack/definition targets, and lines 571–611 dispatches tasks through the controller client, but roster creation/assignment remain documented no-ops at lines 686–763. Commander is a useful operational console and UX reference; simulated employee/team behaviors must not be counted as implemented standing-organization capabilities.

## Feature comparison

“Similar” means substantial implemented behavior with a material difference from Wingman; “Resembles” means useful primitives without the complete capability. Each row is judged separately. No “Exact” rating is inferred simply from a resource name or prompt instruction.

| ID | Capability | Verdict | Implementation evidence and concrete Wingman difference |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | [Delegated execution][delegate], lines 114–187, creates fresh coding-tool sessions or invokes another harness; [Job client][job-client], lines 512–575, runs independent containers. These are executable workers, not only personas. The usual lifecycle is bounded task/run completion rather than standing BackendCoder/FrontendCoder/TestMaster employees. |
| F02 | Extensible profiles, roles and team composition | **Similar** | [Persona controller][persona], lines 27–113, validates and resolves persona → definition → stack, with soul/appearance/voice references. [Subagent controller][subagent], lines 28–69 and 139–150, supplies role lookup and tool scoping. Arbitrary specialist profiles are possible; no default organization-wide/project leadership staffing policy was established. |
| F03 | Agent directory and visible relationships | **Similar** | [Directory routes][directory], lines 9–36, render actual persona profiles and creation wizard; [identity mapping][identity-map], lines 55–64, associates definitions with stacks. This is more than a catalog of prompt files. It shows profile/deployment bindings, but does not establish Wingman's project/team/reporting and current-assignment relationship graph. |
| F04 | Telegram main channel and Butler routing | **Absent** | Searches for `telegram`, `Butler`, `ProjectMaster`, `Room1` and `Room2` across package source found upstream Atlas descriptions and [MCP channel classifier][channel-manager], line 182, which recognizes a tool-name prefix. That classifier is not a Telegram bot, inbound update loop, project routing or answer correlation implementation. No first-party Butler channel path was located. |
| F05 | Cross-project registry, intake, existing/new routing | **Resembles** | [Projects UI][projects], lines 9–51, lists and creates projects; [project controller][project-controller], lines 19–62 and 86–114, validates org, columns and board state. This is a real registry primitive, but incoming natural-language requests are not automatically matched to existing projects or turned into new product teams. |
| F06 | Per-project product/technical leadership | **Resembles** | [GSD new project][new-project], lines 176–203, prompts a product-manager-like research task; later tasks plan requirements and roadmap. [Persona controller][persona], lines 88–113, can define separate leaders. These are configurable workflow roles, without the established persistent ProductMaster/TechMaster partnership and continuing accountability described by Wingman. |
| F07 | Proportionate research/discovery and iterative clarification | **Similar** | [GSD process][new-project], lines 57–145, captures vision, requests human reviews, runs four parallel domain research tasks and scopes requirements. [Question tool][delegation-tools], lines 8–75, supports structured user questions through an injected handler. Process selection and prompting can adapt discovery, but fixed review points alone do not implement a portfolio-aware iterative interview through Butler. |
| F08 | Scope, specs, acceptance scenarios, definition of done | **Similar** | [GSD process][new-project], lines 104–159 and 193–223, produces scoped requirements, vision and roadmap outputs. [Automation storage][automation], lines 30–53 and 184–205, stores acceptance criteria and decomposition. [TDD process][tdd], lines 175–228, performs integration checks/review. Product documents and gates exist; no universal organization-owned scope/spec/DoD contract is imposed on every project. |
| F09 | Technical decomposition, assignment, shared task tracking | **Similar** | [Delegation tools][delegation-tools], lines 92–139, expose create/assign/search/escalate routed tasks. [Automation storage][automation], lines 30–53, includes assignees, dependencies, criteria and children; [project board][projects], lines 54–105, links workspaces/sessions to board items. [Gateway backlog CRUD][gateway-backlog], lines 1653–1695, 1774–1835 and 2502–2535, independently persists issues, enforces moves and links sessions/runs. Workflow effects, gateway JSON backlog, native routed tasks and Kradle issue cards are distinct stores/models needing reconciliation. |
| F10 | Human portfolio/project dashboard | **Similar** | [Projects UI][projects], lines 21–49 and 79–118, renders a cross-project list, editable project metadata, linked stacks, board and issue views. The [Observer dashboard][observer-discovery], lines 90–135, also groups filesystem runs by project. [Gateway Kanban routes][gateway-kanban-routes], lines 443–463 and 974–1045, additionally expose independent backlog and automation management. These are genuine project/run-management surfaces. Product goals, delivery readiness, unresolved product decisions and organizational responsibility summaries are not all derived automatically. |
| F11 | Agent chat app, rooms and direct collaboration | **Resembles** | [Cross-run mailbox][mailbox], lines 18–24 and 32–82, persists addressed data/signal/query/response messages. [Session view][sessions], lines 52–78, displays session transcripts, while [GitHub issue adapter][github-issues], lines 1–5 and 80–86, supports comments. Neither is the management/project multi-participant room application with durable membership and agent-to-agent discussions. Searches across session, communication, Kradle web and resource kinds found no corresponding Room1/Room2 system. |
| F12 | Escalation and human decisions/approvals | **Similar** | [Approval controller][approval], lines 15–89, creates deduplicated review/secret/tool/write/release/escalation requests and records decisions. [Question/delegation tools][delegation-tools], lines 129–139, expose task escalation. [Observer approval action][observer-approval], lines 52–129, checks task and journal breakpoint identity before accepting an answer. SDK breakpoints are durable effects. Missing is the organizational routing policy from worker to leadership to Butler with correlated product decisions. |
| F13 | Durable project knowledge and reusable directives | **Similar** | [Memory controller][memory], lines 32–108, pins snapshot digests and supports graph/grep queries; [session persistence][session-state], lines 16–44 and 89–117, stores findings/preferences/file changes. [GSD process][new-project], lines 155–159, identifies project/research artifacts. There is no mandated `DIRECTIVES/SCOPES`, `SPECS`, `HARNESS` contract; knowledge retrieval and directive conventions require integration. |
| F14 | Identity, conversation and work continuity | **Similar** | [Persona resolution][persona], lines 88–113, retains role/configuration identity separately from runs; [run creation][create-run], lines 28–35 and 54–70, records ancestry and metadata; [effect commit][commit], lines 24–107, journals outcomes. [Session state][session-state], lines 101–117, is durable. Internal worker sessions are ephemeral and core history is in memory; complete identity → conversation → assignment continuity is not automatically one persistent agent. |
| F15 | Proactive supervision, periodic wake, blocker follow-up | **Resembles** | [Daemon loop][daemon], lines 44–79 and 98–123, schedules concurrent durable-trigger dispatch and retries; [timer scheduler][timer], lines 1–5, implements cron checks. [Subagent controller][subagent], lines 11–15 and 124–133, returns supervision configuration but does not itself run a monitor. [Gateway automation lifecycle/materialization][gateway-automation], lines 925–960 and 977–1085, provides a substantial recurring/event-driven work-intake primitive. A recurring manager could be built, but no default ProjectMaster reviewing tracker/chat and resolving blockers was found. |
| F16 | Parallel products and concurrent specialists | **Similar** | [GSD research][new-project], lines 80–91, emits parallel research; [effect dispatcher][effect-dispatch], lines 46–84 and 136–176, runs bounded worker pools and commits in action order. [Daemon][daemon], lines 44–79, defaults to four concurrent runs; Kradle projects isolate grouping. Parallel effects need a concurrency-capable/configured executor; multiple parallel runs are not yet multiple fully staffed product teams. |
| F17 | Real multi-host execution with shared coordination | **Similar** | [Job client][job-client], lines 546–595, creates and applies real cluster Jobs, with shared org-scoped run records and callbacks. [Remote runner][remote-runner], lines 78–110, also connects real remote adapters and streams session events. These can cross hosts/nodes when configured. They do not provide Wingman's Mac/Endeavour host directory, routing and location affinity for existing product checkouts; local SDK state/mailboxes alone do not cross machines. No multi-node run was exercised. |
| F18 | Executive current/recent/next/blocker agent overview | **Resembles** | [Run status reconciler][run-status], lines 60–68 and 119–147, maps lifecycle to board column and numeric progress. [Directory][directory], lines 9–25, displays profiles; [session flow][session-flow], lines 113–139, counts tools/files/cost. [Observer executive banner][observer-summary], lines 7–14 and 37–91, reports run/approval health counts. These are useful execution views, but do not establish semantic current/recent/next accomplishments and blockers per standing agent. Searches across Kradle agent components and Genty UI found event timelines and run state rather than this briefing contract. |
| F19 | Individual agent summary timeline linked to work | **Resembles** | [Session flow model][session-flow], lines 29–42 and 82–105, derives timeline items with run ID, tool/node title, timestamp and file references. It is an execution/transcript projection. There is no demonstrated maintained plain-language personal timeline of accomplishments, decisions, blockers and explicitly planned next work across an agent's assignments. |
| F20 | Drill-down detailed per-agent coding workspace | **Similar** | [Session detail][sessions], lines 52–78, links identity, run, transcript, and cost into [SessionShell][session-shell]. The shell renders tool cards, transcripts, and activity. Its workspace shows “File tree not available” and “git status not available” (lines 67–95). The Kradle page therefore provides partial inspection. It does not establish a complete file/edit/review/browser workspace. |
| F21 | Live activity, lifecycle, steering, visibility | **Similar** | [Core session][core-session], lines 1598–1618 and 1668–1677, exposes queued instructions, event subscriptions, abort/dispose; [sessions][sessions], lines 22–45, exposes live updates and terminate/delete actions. [Cancel route][cancel], lines 12–27, only patches run status, so it does not prove execution stops. [Gateway session creation/stop][gateway-server], lines 381–414 and 524–535, supports source-session forking and invokes the manager stop path, which aborts its active handle ([manager][gateway-manager], lines 214–219). Full cross-surface fork/compact/archive/attachments/budget control is not uniformly implemented. |
| F22 | Testing, integrated verification, acceptance/delivery | **Similar** | [TDD convergence][tdd], lines 69–128 and 175–228, coordinates test/implementation, quality checks, final integration/review and approval. [Deterministic gate][quality-gate], lines 116–170, captures command exit codes. [Pod entrypoint][pod-entry], lines 141–164, publishes a PR. Runtime “completed” means the process returned or a callback said so; product DoD and accepted delivery must be explicitly enforced by the chosen workflow. |
| F23 | Autonomous operation with human organizational direction | **Similar** | [Genty entry][genty-entry], lines 56–63, enables autonomous execution; [effect resolver][effects], lines 257–283, gates it in host contexts; [daemon][daemon], lines 98–123, continues trigger processing/retries. [GSD][new-project], lines 65–74 and 110–145, inserts human reviews. Autonomous workflows are implemented, but human direction is through harness/web/CLI interactions rather than the complete Wingman management organization. |
| F24 | Chat/tracker/dashboards accommodate new profiles | **Similar** | [Directory/create routes][directory], lines 29–36, populate from resource collections; [projects][projects], lines 28–35 and 63–76, use stack/workspace/session references; [identity mapping][identity-map], lines 105–136, resolves dynamically named definitions. New profiles can participate in existing resource views. A room/chat system and organization-wide briefing layer must still be supplied, so extension across every Wingman view is incomplete. |

## Agent definition and lifecycle

### Definition, creation and identity

There are three different definitions to keep separate. A library `AGENT.md` and a task's `agent.prompt.role` describe behavior. Neither creates a running agent. An `AgentStack` defines executable harness/model/tool/skill/permission settings. `AgentPersona` adds a durable identity profile, and `AgentDefinition` binds that persona to a stack and role context. [Persona controller][persona] lines 88–113 resolves references within organization scope and reports missing resources instead of fabricating identity. [Directory routes][directory] lines 29–36 supplies UI creation over discovered stacks and skills. These constructs could represent multiple BackendCoders and project leaders, but instance responsibility/assignment history must be attached by a Wingman application.

A run has a separate ID. Core runs use a ULID unless specified; Kradle manual dispatch currently uses `dispatch-${Date.now()}` and an `attempt-1` name ([dispatch][dispatch], lines 459–509). An attempt snapshots stack/persona/definition specifications, making a later profile edit distinguishable from what a run actually used. This is valuable provenance, but timestamp IDs and pure object helpers should not be mistaken for a globally transactional identity service.

### Execution, tools, permissions and routing

In core mode the process requests effects. The executor chooses who resolves them. Genty can route through task adapters, execute a fresh internal worker with coding or readonly tools, invoke an external harness, or leave effects pending. [Delegated execution][delegate] lines 116–158 explicitly builds file/bash tools: `toolsMode` alone does not magically give an LLM filesystem access. Tool scope and permission enforcement must exist at the executing harness, not only in a persona description.

Kradle dispatch reviews permissions before constructing the Job, resolves a model-provider secret by grant, assembles context, and sets a service account and resource limits ([dispatch][dispatch], lines 343–348, 530–594; [Job client][job-client], lines 502–575). The broader proof-policy layer has a meaningful activation boundary: [tool gate wiring][policy] lines 29–33 and 111–139 requires a pinned `POLICY_CONFIG_ROOT_FP` for enforcement. An unpinned deployment keeps backward-compatible execution. With an anchor pinned, missing policy infrastructure produces deny-all rather than silently dropping the gate. Wingman would have to choose and configure this trust model.

Routing can use named definitions or stacks, task role lookup, selected harness/model and task-adapter responder hints. The generic [subagent helper][subagent] lines 84–117 creates a **queued dispatch record**, not an execution session; its scope explicitly excludes adapter-session ownership. Its role-match method also does not consume `taskKind` to make an elaborate staffing decision. The executable job path is the separate dispatch controller.

### Concurrency and project/workspace isolation

A single run's journal transitions are locked. Parallel intrinsics emit pending groups, and Genty's [dispatcher][effect-dispatch] lines 94–120 groups them only when concurrency is enabled. Lines 136–176 execute a bounded pool and return results in original index order. There is no reason to equate simultaneous effect requests with proven simultaneous coding sessions unless the host actually dispatches them. Separate Kubernetes Jobs are independently schedulable. The manifest uses `restartPolicy: Never` and `backoffLimit: 0` ([Job client][job-client], lines 559–571).

Kradle reuses a matching reusable workspace when available and otherwise creates ephemeral storage ([dispatch][dispatch], lines 414–450). That keeps one-shot runs isolated and cheap, but work in `emptyDir` is lost with the pod unless published. PVC-backed reuse can retain a workspace; coherent per-product host affinity and multi-worker source integration remain policies to define. The container's repository branch/PR path supplies a concrete delivery boundary, which is safer to integrate than treating transient pod files as the durable product.

### Persistence, resume and scheduling

Workflow continuity is strongest at the effect boundary. [Effect commit][commit] lines 24–42 rejects unknown/already-resolved effects, validates outputs and signed breakpoint answers, persists result references, appends `EFFECT_RESOLVED` and rebuilds derived state (lines 63–107). A restarted orchestrator can replay these records and advance. This preserves completed work decisions, but a tool side effect that succeeded just before result posting failed can still need reconciliation or idempotency in the adapter/application.

Conversation continuity is different. [Core session][core-session] lines 1291–1298 stores history in memory; `dispose()` clears it (lines 1672–1677). Genty's [persistent session store][session-state] separately saves findings, preferences, modifications and breakpoint patterns atomically via temporary-file rename, rather than automatically serializing a live employee's full mind. Kradle transcript resources persist messages, and identity/configuration can outlive executions. Wingman needs a deliberate resume assembler joining these objects by project, role, assignment and conversation.

Periodic work is available through cron, file and webhook triggers. [Daemon loop][daemon] lines 44–79 and 98–123 uses a durable queue when a log directory is provided, claims due work, acknowledges success and records/retries failure. An injected `onTrigger` callback performs actual work (lines 92–95). The queue is not itself a product manager. [Automation executor][automation] lines 208 onward creates tracked issues from templates. A scheduled supervision workflow can be authored, but the system does not inherently know to inspect all product blockers and contact the correct leaders.

### Interruption, steering, failure and recovery

Core `steer()` and `followUp()` merely append strings to `queuedFollowUps`. The next `prompt()` consumes them ([core session][core-session], lines 1323–1325 and 1598–1604). That is queued next-turn input, not guaranteed immediate injection into an active tool loop. `abort()` signals the current provider request; `dispose()` also clears listeners/history. Durable SDK cancellation is another operation: [commitEffectCancellation][commit], lines 129–165 onward records a cancelled result under the run lock. Recording cancellation does not by itself kill a remote process.

This distinction is particularly visible in Kradle: [HTTP cancel][cancel] lines 12–27 sets `Cancelled` on the run status, with no Job deletion or adapter stop call. A subsequent [callback][callback] lines 52–64 can write terminal completion/failure without checking whether the run was already cancelled. Execution interruption and terminal-state arbitration need hardening before this path controls expensive autonomous workers.

[Iteration handling][iterate] lines 162–213 separates waiting, explicit halt, process runtime error and run failure. Unexpected process-code errors get `PROCESS_RUNTIME_ERROR` with a recovery command and last-effect context; explicit `RunFailedError` produces `RUN_FAILED`. The runtime reference identifies rebuild-state, recover-process-error and journal-repair operations. These are practical recovery seams, but repairing process code/journal is an operator action, not autonomous evidence that the original product outcome was recovered. Pod job submission failure leaves a queued run with a failure condition ([dispatch][dispatch], lines 611–619); Kubernetes does not retry that job automatically with the current zero-backoff setting. Trigger retry and model retry are separate mechanisms and should not accidentally duplicate partially completed repository work.

### Completion, acceptance, retirement and cleanup

A core process returning a value writes output and `RUN_COMPLETED` ([iterate][iterate], lines 127–159). A declared output-schema mismatch at that top-level return is logged as a warning (lines 127–131). It is not a universal hard acceptance test. An effect's output validation is a separate commit-time path. In Kradle, a `completion` event sets phase completed ([dispatch][dispatch], lines 237–256), or the pod callback does so after exit/publish processing. None establishes that ProductMaster accepted the integrated product unless the process explicitly encoded the relevant checks and decision gate.

[The TDD workflow][tdd] demonstrates how to encode that policy: bounded refinement, real check effects, integration verification, a final review and a human merge decision. It can return `success: false` after exhausting iterations while the workflow itself completes normally (lines 214–221). Wingman should distinguish process execution success, test evidence and product acceptance in its tracker.

Retirement is also layered: ephemeral workers are disposed after their delegated task, Jobs terminate, workspaces follow retention/volume policy, and directory personas remain configuration. [Run archive][archive] lines 39–93 writes compressed archive data/manifests. It does not remove the original run. Lines 99–121 restores files. [Fork helper][fork] lines 51–85 only validates a fork point and prepares IDs/metadata. This file alone is not an implemented clone of run directories or an end-to-end conversation fork. [Iteration cleanup][iterate] lines 214–219 runs process-local cleanup on non-waiting outcomes and checks scratch leaks. Wingman still needs explicit policy for archiving employees/conversations, retaining audit records and stopping development after accepted delivery.

## Coordination mechanics and a concrete request trace

The core coordination mechanism is not chat: it is a serializable effect graph and append-only result journal. Process code determines dependencies through awaited return values; parallel groups expose independent work; breakpoints and sleeps are effects that suspend progress; result posting allows a later iteration to continue. Task adapters add responder routing and escalation. The [channel runtime][channels], lines 117–155, resolves extensible backends and routes replies by the originating source token. This is useful inbound-event/reply plumbing, distinct from multi-agent chat-room membership and discussion history. Projects/issues/boards add shared tracking. Cross-run mailboxes add explicitly addressed messages. These mechanisms are complementary, but the inspected code does not show them as one unified employee-room-tracker system.

The [mailbox][mailbox] is also a small local primitive with a real limit: `send()` appends JSONL, but `receive()` reads all messages and rewrites only the unconsumed remainder (lines 42–67, 89–103). No lock or transactional compare-and-swap is used there. Concurrent append/receive consumers require protection before treating this as a reliable distributed organizational bus. Its “append-only” header describes sending, not an immutable complete history after consumption.

A concrete implemented workflow is `gsd/new-project`, beginning with `{projectName, projectType, initialIdea}`:

1. [Process][new-project] lines 46–62 requests vision capture. Its task definition at lines 176–233 contains an agent prompt, result schema and effect-specific I/O. This is a worker task, not creation of a standing ProductMaster.
2. [Task intrinsic][task] lines 76–105 derives invocation identity. On the first pass it serializes a new effect and the runtime reports waiting; on later passes it returns the recorded result instead of creating another vision task.
3. Genty [resolver][effects] lines 257–275 either leaves the effect pending under host defaults or dispatches through a task backend; [delegation][delegate] lines 135–174 shows the concrete internal tool-capable worker alternative. External host orchestrators may instead perform it and post the result.
4. [Result commit][commit] lines 24–107 verifies the requested effect, writes result artifacts and appends the resolution. The next iteration replays vision capture and reaches the human vision review ([process][new-project], lines 65–74). The durable pending breakpoint is distinct from the answering UI or a Telegram channel.
5. After review, four research effects run through `ctx.parallel.all` ([process][new-project], lines 80–91). Their returned values become explicit inputs to requirements scoping, then roadmap generation (lines 104–131). The executor's capability and concurrency configuration determine actual simultaneous work.
6. Requirements review and final initialization review expose artifact links and human questions (lines 110–145). The process returns structured vision/requirements/research/roadmap data and artifact paths (lines 148–164), causing the runtime's completion path. These references and prompt instructions should not be assumed to prove every promised Markdown file was written; that must be verified in execution.

The cloud execution path has these stages:

1. The [dispatch HTTP route][dispatch-route], lines 7–43, authenticates and loads organization-scoped target resources. It passes task, repository, and ref to `dispatchAgent`.
2. The [API controller][api-controller], lines 252–318, invokes [manual dispatch][dispatch]. It applies run/status and workspace resources.
3. The [Job client][job-client], lines 546–595, submits a Kubernetes Job.
4. The [pod entry point][pod-entry] launches the harness and posts final output.
5. The [callback][callback], lines 38–98, updates run status and persists the transcript.

The implementation supports this trace. The assessment did not deploy a cluster.

Two boundaries in that path deserve attention. The route's `loadIdentityResources` loads only six identity/stack kinds (lines 56–58), while the stack path includes service accounts, role bindings, grants and workspace policy (lines 67–76). Since permission review consults these objects, identity dispatch may be denied despite valid configured grants; source inspection identifies the mismatch, while a live failure was not reproduced. Also, the callback is intentionally not session-authenticated and relies on knowing the org/run binding (lines 6–8, 25–43). The inspected handler contains no callback-token/signature check. Deployment isolation and authenticated result provenance should be designed before exposing that endpoint.

## Major capabilities beyond Wingman's described product

**Replayable workflow programming and repair tooling.** Wingman describes persistent agents and shared records, but does not prescribe deterministic replay. Babysitter offers an explicit effect journal, invocation identity, input/output schemas, process code hashes, replay caches and typed repair paths. This can make long discovery/build/test workflows restartable and inspectable. The integration cost is architectural: arbitrary side effects in process functions are unsafe, workflow evolution must preserve invocation meaning, and tool side effects/result posting need reconciliation. Replay is an execution kernel to adopt deliberately, not a wrapper that makes any chat organization durable.

**Proof-bound command governance.** [Policy wiring][policy] lines 44–82 binds decisions to actual executing tool-call/run/session IDs and denies exceptions; lines 111–139 gates activation on the external trust anchor. This goes beyond ordinary UI approvals toward signed evidence and configuration integrity. It could let Wingman enforce a review/test/approval chain before a command runs. It also introduces key/configuration management and policy-coverage work; unpinned environments are pass-through, and an enforced gate covers only what the configured matching rules describe. No end-to-end cryptographic enforcement was exercised here.

**Independent local tracker, review and automation plane.** The gateway Kanban backend described above is a substantial alternative to adopting Kradle wholesale. It combines issue dependencies/acceptance/decomposition, run/session/workspace references, policy-checked board moves and automation-rule audit state in local JSON stores. That supplies much of the tracker vocabulary Wingman needs while allowing local harness execution. Its review artifacts and PR/CI projections need real evidence/provider ingestion; seeded defaults and local “create PR” metadata are not equivalent to delivered changes. The principal integration consequence is choosing whether the gateway backlog, Kradle issues or another tracker is authoritative and designing safe writes/synchronization; adopting every surface together would multiply overlapping state.

**Event-origin-preserving agent activation.** The channels package contains executable [GitHub polling/reply][channels-github], lines 376–406, and [Jira polling/reply][channels-jira], lines 237–294, with cursors/seen sets and HTTP comment posting. [SessionSpawner][channel-spawner], lines 148–219, turns a surviving event into worker launch options and injects the same channel MCP server/config plus origin `reply_to` token. Lines 383–428 launches through the adapter client under a semaphore so the worker can answer the original issue without losing its routing coordinates. This is a meaningful foundation for proactive issue-driven agents and escalations beyond a passive event log. Its at-most-once dispatch stance marks events before launch settles (lines 392–399), so failed launches are not automatically redelivered. The [generic webhook backend][channels-webhook], lines 191–229, consumes normalized inline/directory queues and explicitly rejects reply (lines 232–244); generic webhook input is not a two-way conversation. A Telegram Butler would still need a Telegram-specific backend, project/conversation correlation and organizational routing.

**Cloud development platform and git/CI integration.** Kradle adds Kubernetes jobs, identity/grants, ephemeral/PVC workspaces, organization scoping, external git/issue/CI provider contracts and artifacts. [GitHub issue adapter][github-issues] lines 19–56 is executable HTTP integration with injected fetch and normalized records, not just a provider name. [Pod publishing][pod-entry] lines 141–164 turns successful repository work into a pushed branch and PR. Wingman could use this for distributed execution and reviewable delivery, at the cost of operating Kubernetes, storage, secrets, images and git services. It is a much heavier substrate than running two Codex hosts and appending local Markdown records.

**Versioned knowledge graph SDK.** KIP provides signed facts and temporal retrieval, independently of Kradle's simpler memory-resource projection. [KIP implementation][kip] lines 1482–1533 publishes sorted fact snapshots into Git and advances a durable tip; lines 2235–2277 implement as-of recall and validation; lines 3122–3141 merge admitted fact sets; lines 3736 onward perform authorized excision. This could support provenance-aware product decisions and cross-agent memory. It is not evidence that every Kradle dispatch automatically retrieves useful company knowledge: the inspected dispatch initializes snapshot records with empty selected-record/document arrays ([dispatch][dispatch], lines 350–369). KIP recall also explicitly documents a scope/tenancy filtering gap (lines 2264–2268), so it should not become Wingman's cross-project isolation boundary without further evaluation.

**Discovery and reusable process library.** Atlas [discovery types][atlas], lines 18–61, describe processes, skills, and agent roles with paths, expertise, and metadata. The [index builder][atlas-indexer], lines 361–420, reads graph YAML and merges patch records. It accumulates edges and counts. [AtlasGraph][atlas-graph], lines 43–75 and 115–169, supports record/kind lookup and relationship maps. Ranked text search can filter by kind or cluster.

The catalog can help select compatible harnesses, models, processes, and skills with traceable evidence. The library includes GSD-style discovery and TDD convergence code. These procedures can guide product-work depth and reuse specialist knowledge. A catalog agent remains instructions until dispatch. Metadata and graph edges do not establish an active team. Wingman must curate the processes and align their artifacts and gates with project contracts.

**Synchronous meeting participation.** Kradle's [meeting bridge][meeting-bridge] lines 24–37 and 77–108 binds a dispatched agent to a meeting; [Job client][job-client] lines 498–500 and 542–544 mounts a shared socket and adds a Jitsi sidecar. [Sidecar construction][job-client] lines 144–155 includes resource settings and a graceful-leave hook. This offers a different human/agent collaboration medium beyond Telegram/text dashboards. It brings realtime media, meeting authentication and resource dependencies and should not be credited as persistent management/project chat rooms.

## Distinctive mechanisms and grounded innovation

The strongest mechanism is **separating process replay from effect execution**. Task identity and persisted return values let a process use ordinary control flow while suspending for agent work, human decisions and time. The result is particularly useful for a Wingman clarification cycle that might last days. Its limit is the boundary: the system only knows about journaled effects, and process-side filesystem/network mutation is outside its replay discipline. This is a noteworthy implementation choice, not a claim of historical novelty.

A further useful mechanism is **event-origin self-association**: channel-spawned sessions inherit the MCP reply server and opaque origin token rather than having to rediscover where a question came from. This preserves response routing across a fresh worker context. The at-most-once launch policy trades duplicate prevention against automatic recovery from launch failure, so supervisory retry must be designed deliberately.

A second useful mechanism is **concurrent resolution with ordered commit**. [Dispatcher][effect-dispatch] lines 46–84 resolves configured groups concurrently and posts results in original action order; lines 136–176 bounds workers. This helps make parallel specialist work reproducibly visible even when completion order varies. It does not automatically merge source changes, resolve interface conflicts or impose task dependency semantics across independently created projects.

A third is **identity/configuration/run/attempt separation**. Persona and definition resources survive beyond a run, while attempt snapshots preserve the configuration actually executed. That offers a practical path toward Wingman agent identity without conflating a profile with a process. The limit is that durable organizational responsibility still has to be modeled, and the inspected API persistence path explicitly saves some returned resources rather than all helper outputs.

A fourth is **human decisions as durable work objects with optional trusted proofs**. SDK breakpoint answers can be checked before effect commit; Kradle approval resources retain action, requester, decision and reason. This can support auditable acceptance and escalation. It does not determine which product decisions need the human or how to correlate answers across concurrent Telegram conversations.

Finally, **hard command outcomes alongside model-scored convergence** is a useful combination. The library's [deterministic gate][quality-gate] lines 134–170 emits per-check exit evidence, whereas [TDD convergence][tdd] lines 114–151 uses an agent's score to guide improvement. Wingman should retain that distinction: an agent score can guide prioritization but should not substitute for acceptance scenarios or passing integrated tests. The checked-out processes make these mechanisms explicit, but process naming and declared “hard” behavior still require validation against the chosen executor.

## Practical adoption path and remaining work

Use the **SDK execution kernel directly** for a bounded pilot: intake/discovery → requirements approval → technical plan → specialist effects → test gates → delivery decision. Its run journal, result posting, typed waiting/errors and cleanup give a better recovery foundation than a free-running manager prompt. Consider the gateway JSON-backed backlog/review/automation API as a lighter tracker starting point if Kubernetes is unnecessary, and use Commander only with its configured real backend and documented live controls. Use the Observer dashboard for inspecting local run state and answering workflow breakpoints, while retaining the distinction between run health and employee summaries. Use Genty workers/adapters where their supported coding sessions meet the desired Codex integration; verify tool availability, cancellation and model/harness continuity in the actual host combination.

Reuse **Kradle's persona/definition, project/issue and approval concepts** if adopting its deployment model. The directory and project board are meaningful UI starting points. Before taking the cloud path, test persona-targeted dispatch permissions, run/attempt/context/session persistence, stop propagation, callback authentication, artifact resource kinds and terminal-state races. The callback creates `AgentArtifact` (lines 104–119), whereas the inspected resource catalog declares `KradleArtifact` ([resources][resources], line 55). This is another concrete contract to validate rather than assuming artifact publication is complete. The placeholder workspace UI also needs actual file/git/review integration.

Build the organizational application around these primitives:

- Telegram bot and Butler conversation correlation.
- Semantic new/existing-project routing.
- Project leadership identities.
- Staffing and assignment policy.
- Management/project rooms with dependable shared messaging.
- Durable `DIRECTIVES` knowledge layout.
- Periodic portfolio supervision that acts on blockers.
- Current/recent/next executive summaries linked to source events. These should be explicit state/contracts, with role prompts supplying judgment inside them.

For Mac plus Endeavour, decide whether to adopt Kubernetes or build a smaller host dispatcher. Current cluster Jobs are a credible multi-node mechanism, but they do not route into existing host-resident Codex conversations or preserve product location across those two machines. A lightweight two-host approach could reuse the journal/protocol while replacing cloud workspace and scheduler assumptions. Avoid splitting source of truth among SDK effects, task-adapter tasks and Kanban issues without clear IDs and synchronization rules.

The most appropriate short-term position is therefore **selective infrastructure adoption and architectural reference**, with a possible heavier Kradle platform evaluation. A direct replacement claim would overstate the conversational organization, room collaboration, employee continuity and executive visibility currently established by source.

## Verification scope and limits

All findings refer to the local commit above. Repository instructions were read: [AGENTS.md][agents] explicitly exempts agent-to-agent delegated requests from the mandatory Babysitter-skill workflow. No source file in the checkout was modified. Only this report was written.

The implementation review covered these areas:

- Run creation, iteration, task identity, result commits, and replay contracts.
- Delegated coding sessions, execution flags, parallel dispatch, history, steering, abort, and disposal.
- Daemon queues, timers, automation, and persona/definition/stack resolution.
- Kubernetes permissions, Job submission, pod entry, status, callbacks, and cancellation.
- Project/directory/session UI, Observer source discovery, executive metrics, and breakpoint actions.
- Channel replies, GitHub/Jira/webhook backends, and self-associated session creation.
- Gateway backlog, reviews, automation CRUD/storage, remote runners, and Commander real/mock/Kradle boundaries.
- Mailboxes, session state, approvals, memory, and policy gates.
- Deterministic, TDD, GSD, KIP, and Atlas implementations selected for this assessment.

The cited line ranges identify the review boundaries. The review did not audit every package.

Relevant tests read, **not run**:

- [SDK concurrent execution tests][test-parallel], lines 33–83 and 92–124: limits simultaneous thunks and checks pending group identity. These do not exercise live model workers.
- [Kradle dispatch tests][test-dispatch], lines 16–23 and 91–124: uses a mock resource gateway and asserts Job creation/run status. This supports the manifest/controller contract, not live Kubernetes/provider health.
- [Genty execution-gating tests][test-gating], lines 9–36 and 38–79: mock shell/session/task-adapter seams to check emit-versus-execute behavior. A “RED until” comment is historical test prose, not proof the checked-out suite fails or passes.
- [Core session tests][test-core], lines 377–401, 466–514 and 596–678: queued follow-ups, history retention/trimming, provider abort and disposal under mocked provider requests.
- [Session-flow tests][test-flow], lines 10–66 and 137–160: event/transcript-to-lane/timeline projection, not organizational summary generation.

Negative-feature searches covered package source and likely session, daemon, harness, task, channel, Kradle web, and resource paths. Terms included Telegram, Butler, ProjectMaster, rooms, projects, supervision, schedules, timelines, cancellation, and lifecycle controls. The review also inspected workflow files for product, research, and testing procedures. Atlas descriptions received credit only as catalog evidence. External MCP servers, plugins, or deployment changes could add behavior. The inspected paths did not demonstrate those additions as a Wingman implementation.

The assessment did not exercise runtime behavior. Unverified areas include coding performance, crash replay, cross-node dispatch, model credentials, secrets, and backend storage. PR publication, active cancellation, UI rendering, external issue synchronization, and accepted product delivery also remain unverified. Source inconsistencies identify adoption risks. They are not reproduced runtime failures.

[manifest]: ../repo/package.json
[agents]: ../repo/AGENTS.md
[runtime-reference]: ../repo/docs/agent-reference/runtime-and-layout.md
[create-run]: ../repo/packages/babysitter-sdk/src/runtime/createRun.ts
[iterate]: ../repo/packages/babysitter-sdk/src/runtime/orchestrateIteration.ts
[task]: ../repo/packages/babysitter-sdk/src/runtime/intrinsics/task.ts
[commit]: ../repo/packages/babysitter-sdk/src/runtime/commitEffectResult.ts
[archive]: ../repo/packages/babysitter-sdk/src/runtime/runArchival.ts
[fork]: ../repo/packages/babysitter-sdk/src/runtime/runForking.ts
[genty-entry]: ../repo/packages/genty/platform/src/harness/internal/createRun/index.ts
[effects]: ../repo/packages/genty/platform/src/harness/internal/createRun/orchestration/effects.ts
[delegate]: ../repo/packages/genty/platform/src/harness/internal/createRun/planProcess/delegation.ts
[effect-dispatch]: ../repo/packages/genty/platform/src/harness/internal/createRun/orchestration/dispatch.ts
[core-session]: ../repo/packages/genty/core/src/session.ts
[delegation-tools]: ../repo/packages/genty/platform/src/harness/agenticTools/tools/delegation.ts
[resources]: ../repo/packages/kradle/core/src/resource-model.js
[dispatch]: ../repo/packages/kradle/core/src/agent-dispatch-controller.js
[api-controller]: ../repo/packages/kradle/core/src/api-controller.js
[job-client]: ../repo/packages/kradle/core/src/adapters-client.js
[pod-entry]: ../repo/packages/adapters/cli/kradle-agent-entrypoint.mjs
[persona]: ../repo/packages/kradle/core/src/agent-persona-controller.js
[subagent]: ../repo/packages/kradle/core/src/agent-subagent-controller.js
[directory]: ../repo/packages/kradle/web/app/pages/agent-identity-pages.jsx
[identity-map]: ../repo/packages/kradle/web/app/lib/agent-identity.js
[projects]: ../repo/packages/kradle/web/app/pages/agent-project-pages.jsx
[project-controller]: ../repo/packages/kradle/core/src/agent-project-controller.js
[channel-manager]: ../repo/packages/genty/platform/src/mcp/channels/channelManager.ts
[new-project]: ../repo/library/methodologies/gsd/new-project.js
[tdd]: ../repo/library/tdd-quality-convergence.js
[quality-gate]: ../repo/library/processes/shared/deterministic-quality-gate.js
[automation]: ../repo/packages/genty/platform/src/daemon/automationExecutor.ts
[mailbox]: ../repo/packages/genty/platform/src/session/crossRunComm.ts
[sessions]: ../repo/packages/kradle/web/app/pages/agent-session-pages.jsx
[session-shell]: ../repo/packages/kradle/web/app/components/agent/session-shell.jsx
[session-state]: ../repo/packages/genty/platform/src/session/persistence.ts
[session-flow]: ../repo/packages/genty/ui/src/session-flow/model.ts
[run-status]: ../repo/packages/kradle/core/src/agent-run-status-reconciler.js
[approval]: ../repo/packages/kradle/core/src/agent-approval-controller.js
[memory]: ../repo/packages/kradle/core/src/agent-memory-controller.js
[daemon]: ../repo/packages/genty/platform/src/daemon/loop.ts
[timer]: ../repo/packages/genty/platform/src/daemon/timerScheduler.ts
[dispatch-route]: ../repo/packages/kradle/web/app/api/orgs/[org]/agents/dispatch/route.js
[cancel]: ../repo/packages/kradle/web/app/api/orgs/[org]/agents/runs/[name]/cancel/route.js
[callback]: ../repo/packages/kradle/web/app/api/orgs/[org]/agents/runs/[name]/callback/route.js
[policy]: ../repo/packages/adapters/tools/src/policy-verifier-wiring.ts
[github-issues]: ../repo/packages/kradle/core/src/external/github/issue-tracking.js
[kip]: ../repo/packages/kip-sdk/src/kip-repo.ts
[atlas]: ../repo/packages/atlas/src/catalog/discovery.ts
[meeting-bridge]: ../repo/packages/kradle/core/src/jitsi-agent-bridge.js
[test-parallel]: ../repo/packages/babysitter-sdk/src/runtime/__tests__/concurrentExecution.test.ts
[test-dispatch]: ../repo/packages/kradle/core/tests/agent-dispatch-controller.test.js
[test-gating]: ../repo/packages/genty/platform/src/harness/internal/createRun/orchestration/__tests__/effectExecutionGating.test.ts
[test-core]: ../repo/packages/genty/core/src/session.test.ts
[test-flow]: ../repo/packages/genty/ui/src/session-flow.test.ts

[observer-discovery]: ../repo/packages/observer-dashboard/src/lib/source-discovery.ts
[observer-summary]: ../repo/packages/observer-dashboard/src/components/dashboard/executive-summary-banner.tsx
[observer-approval]: ../repo/packages/observer-dashboard/src/app/actions/approve-breakpoint.ts
[channels]: ../repo/packages/adapters/channels/src/runtime.ts

[gateway-server]: ../repo/packages/adapters/gateway/src/server.ts
[gateway-manager]: ../repo/packages/adapters/gateway/src/runs/manager.ts
[gateway-static]: ../repo/packages/adapters/gateway/src/static/webui-server.ts
[gateway-backlog]: ../repo/packages/adapters/gateway/src/kanban/lib/services/backlog-query-service.ts
[gateway-storage]: ../repo/packages/adapters/gateway/src/kanban/lib/services/kanban-storage.ts
[gateway-automation]: ../repo/packages/adapters/gateway/src/kanban/lib/services/automation-rule-service.ts
[gateway-kanban-routes]: ../repo/packages/adapters/gateway/src/kanban/routes.ts
[gateway-review]: ../repo/packages/adapters/gateway/src/kanban/lib/review-service.ts
[remote-runner]: ../repo/packages/adapters/core/src/remote-runner.ts
[commander-warroom]: ../repo/apps/commander/src/components/WarRoom.tsx
[commander-factory]: ../repo/apps/commander/src/backend/factory.ts
[commander-real]: ../repo/apps/commander/src/backend/real/realBackend.ts
[commander-orders]: ../repo/apps/commander/src/backend/kradle/kradleOrders.ts
[channels-github]: ../repo/packages/adapters/channels/src/backends/github.ts
[channels-jira]: ../repo/packages/adapters/channels/src/backends/jira.ts
[channels-webhook]: ../repo/packages/adapters/channels/src/backends/webhook.ts
[channel-spawner]: ../repo/packages/adapters/channels/src/spawner.ts

[atlas-indexer]: ../repo/packages/atlas/src/indexer.ts
[atlas-graph]: ../repo/packages/atlas/src/index.ts
