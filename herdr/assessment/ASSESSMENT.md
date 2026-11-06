# Herdr assessment against Wingman

## Identity and verdict

- Repository: https://github.com/herdrdev/herdr
- Local checkout: `research/herdr/repo/`
- Assessed commit: `ee5bfb5041bb3e4a49d591c72308aae3c81ecdde` (actual local `HEAD`; source checkout clean when inspected).
- Assessment date: 2026-11-05.
- Product: a Rust terminal runtime and mouse/keyboard TUI for independently running coding-agent CLIs, with background servers, a JSON control API, persistence, plugins and SSH-connected machines.
- License: Apache 2.0, [LICENSE](../repo/LICENSE), lines 1–16.

**Verdict: strong candidate for Wingman's execution and detailed-agent-workspace layer; weak substitute for Wingman as a persistent development organization.** Herdr really runs multiple coding agents, keeps their PTYs alive independently of viewers, exposes launch/prompt/read/wait controls, and aggregates real remote servers. It does not supply Butler, project/product/technical leadership, product discovery, a shared ticket system, collaboration rooms, acceptance workflows or executive work summaries. Those are application responsibilities that would have to be built around its runtime. Its agent list is operational visibility, not an organizational directory with reporting relationships; its workspaces are execution containers, not a project registry with intake semantics.

This assessment describes the checked-out implementation, including unreleased source, rather than assuming the root README, published stable docs and checkout have identical capabilities. All findings below are static source findings; no Herdr binary, agent CLI, remote machine, plugin or service was launched.

## Architecture and execution model

The binary has three relevant entry paths. `main()` configures a named session, parses remote targeting, runs CLI commands, and dispatches explicit `server`, hidden `client`, or remote bridges: [src/main.rs](../repo/src/main.rs), lines 511–578. This is not an application that calls model APIs itself. Its runtime owns terminals containing already installed external tools such as Codex and Claude. Agent executable selection is explicit in [src/detect/mod.rs](../repo/src/detect/mod.rs), lines 41–96 and 153–175.

The headless server owns `App`, terminal runtimes, clients, rendering interests, shutdown and handoff state. It receives internal events and API requests, maintains terminals, renders a virtual Ratatui buffer and streams results to clients. Client disconnection does not stop the server: [src/server/headless.rs](../repo/src/server/headless.rs), lines 1–15, 133–167 and 191–247. Shared runtime and presentation are partly separated, but this is an ongoing migration: `TerminalState` explicitly describes the current one-to-one terminal/pane relationship, and `TerminalRuntime` still wraps `PaneRuntime`: [src/terminal/state.rs](../repo/src/terminal/state.rs), lines 124–165; [src/terminal/runtime.rs](../repo/src/terminal/runtime.rs), lines 12–21. Wingman should integrate with the public API rather than depend on private presentation structures.

The actual process path is PTY-backed. `spawn_command_builder()` creates a Ghostty terminal parser and compression task, calls the platform PTY backend, and starts a blocking child watcher. That watcher reports `PaneDied` with a classified exit reason. It is not a simulated agent persona: [src/pane.rs](../repo/src/pane.rs), lines 2687–2768. Each terminal runs the external CLI's own inference/tool loop. Herdr handles byte input, screen state, foreground-process detection, attachment and lifecycle visibility. It does not own the CLI's model selection, token budget, coding tools, sandbox or conversation database.

The JSON API is a local socket service with restrictive Unix permissions (`0600`), bounded initial requests and a worker per connection. It dispatches operations into the application while special wait/subscription paths maintain longer-lived connections: [src/api/server.rs](../repo/src/api/server.rs), lines 13–35, 81–93 and 120–175. The exhaustive operation declaration includes workspaces, worktrees, tabs, agents, panes, events, integrations and plugins: [src/api/schema.rs](../repo/src/api/schema.rs), lines 45–148. It includes no product, ticket, team, room or acceptance domain model.

Persistence is a versioned JSON session snapshot, optional terminal ANSI history, plugin registry and saved endpoint configuration. The snapshot holds workspace identity/CWD, tabs, layout, pane labels, agent names, kinds and native-session/resume references: [src/persist/snapshot.rs](../repo/src/persist/snapshot.rs), lines 14–135. The writer preserves unloaded snapshots and recovery copies; its recovery history is capped at 48 snapshots with a 15-minute interval and avoids identical layouts: [src/persist/writer.rs](../repo/src/persist/writer.rs), lines 8–58 and 78–119. These records are runtime recovery material, not project knowledge or an agent work timeline.

## Feature comparison

“Absent” refers to the checked-out core and bundled integration surfaces, not every possible third-party plugin. The negative-search scope is documented at the end. Each row distinguishes built-in behavior from what an external controller could construct.

| ID | Wingman capability | Verdict | Source evidence and concrete difference |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | Separate PTY processes are real ([pane.rs](../repo/src/pane.rs), 2726–2768); named managed agents launch installed executables ([app/agents.rs](../repo/src/app/agents.rs), 145–235). Several Codex instances can work independently, but specialist responsibilities and assignments come from their prompts/controller, not Herdr. |
| F02 | Extensible agent profiles, roles and team composition | **Resembles** | Agent launch accepts a name, known CLI kind and arguments ([schema/agents.rs](../repo/src/api/schema/agents.rs), 184–207); kind selection uses a compiled 24-agent enum ([detect/mod.rs](../repo/src/detect/mod.rs), 41–96). Plugins and metadata extend behavior/display, but there is no persisted role/profile/team definition with instructions, tools and organization membership. |
| F03 | Agent directory and visible working relationships | **Resembles** | Agent enumeration and `AgentInfo` expose name, kind, status, session, workspace/tab/pane and CWD ([app/agents.rs](../repo/src/app/agents.rs), 23–37; [schema/agents.rs](../repo/src/api/schema/agents.rs), 209–260). Cross-machine lists exist ([endpoint_agents.rs](../repo/src/client/shell/endpoint_agents.rs), 132–175); leadership, team and reporting relationships do not. |
| F04 | Telegram main channel and Butler routing | **Absent** | Core notification transport is terminal/system/Herdr/off ([server/notifications.rs](../repo/src/server/notifications.rs), 9–18). Plugin-install parser tests reference an external `agent-telegram-notify` example ([cli/plugin.rs](../repo/src/cli/plugin.rs), 1531–1559), but that is not a bundled conversational bot or Butler/project router. External example behavior is unverified. |
| F05 | Cross-project registry, intake and existing/new routing | **Resembles** | Workspaces can be created/listed/renamed and carry CWD, labels, environment and metadata ([schema/workspaces.rs](../repo/src/api/schema/workspaces.rs), 9–28 and 82–106; [schema.rs](../repo/src/api/schema.rs), 61–69). No semantic interpretation of product requests or registry of product scope/history exists. |
| F06 | Per-project product and technical leadership | **Absent** | Agent records carry runtime identity, not product/technical leadership ([schema/agents.rs](../repo/src/api/schema/agents.rs), 209–260). Launch and prompt operations are generic ([app/agents.rs](../repo/src/app/agents.rs), 145–235); naming agents `productmaster`/`techmaster` would not implement their responsibilities or lifecycle. |
| F07 | Proportionate research, discovery and clarification | **Absent** | `AgentPromptParams` is target/text/wait and submission is generic terminal input ([schema/agents.rs](../repo/src/api/schema/agents.rs), 199–207; [app/api/agents.rs](../repo/src/app/api/agents.rs), 139–207). No discovery state, uncertainty/question records, research policy or iterative human clarification router was found. An installed coding agent can research under outside instructions. |
| F08 | Scope, specs, acceptance scenarios, definition of done | **Absent** | Session persistence stores layout/CWD/agent resume data ([persist/snapshot.rs](../repo/src/persist/snapshot.rs), 52–135), not product-definition records. Neither the complete operation set nor workspace model introduces specifications or acceptance ([schema.rs](../repo/src/api/schema.rs), 45–148). Files written by a hosted agent remain external project content. |
| F09 | Technical decomposition, assignment and shared tracker | **Resembles** | Prompt/start/wait and metadata tokens can carry assignment-like information ([schema/agents.rs](../repo/src/api/schema/agents.rs), 184–252); metadata is a key/value patch with optional TTL ([metadata_tokens.rs](../repo/src/metadata_tokens.rs), 43–103). No ticket IDs, assignees, dependencies, comments or durable task transition model is supplied. |
| F10 | Human portfolio/project management dashboard | **Resembles** | Workspace information includes pane/tab counts, aggregate agent status and worktree details ([schema/workspaces.rs](../repo/src/api/schema/workspaces.rs), 82–106). The TUI can navigate execution containers, but not product goals, tickets, completion, blockers and deliverables as a project management system. |
| F11 | Agent chat, rooms and direct collaboration | **Resembles** | Real direct prompt delivery exists ([app/api/agents.rs](../repo/src/app/api/agents.rs), 139–268), and an agent can read another terminal (271–309). No room membership, shared discussion threads or durable conversational envelopes; messages are submitted into the target CLI conversation. |
| F12 | Management escalation and human decisions/approvals | **Resembles** | Runtime recognizes `Blocked` as needing input ([detect/mod.rs](../repo/src/detect/mod.rs), 9–19), emits contextual attention notifications ([server/notifications.rs](../repo/src/server/notifications.rs), 21–60), and rejects normal prompts to blocked agents ([app/api/agents.rs](../repo/src/app/api/agents.rs), 168–177). The human can steer through keys; no management escalation graph or structured business-decision/approval record exists. |
| F13 | Durable project knowledge/reusable directives | **Resembles** | Workspace CWD and native CLI-session references restore access to existing files/context ([persist/snapshot.rs](../repo/src/persist/snapshot.rs), 52–129; [agent_resume.rs](../repo/src/agent_resume.rs), 199–255). There is no DIRECTIVES-like knowledge schema, artifact registry or policy to read/update project specifications. |
| F14 | Persistent identity, conversation/work continuity | **Similar** | Named agents and native session references are saved ([persist/snapshot.rs](../repo/src/persist/snapshot.rs), 99–129); resume plans invoke the original CLI's native session ([agent_resume.rs](../repo/src/agent_resume.rs), 199–255). Detachment preserves live work, restart reconstructs supported sessions. Identity belongs to runtime/session ownership, not a permanent employee with a separate history and task ledger. |
| F15 | Proactive supervision, periodic wake/blocker follow-up | **Resembles** | Detection periodically inspects live state ([detect/mod.rs](../repo/src/detect/mod.rs), 1–4); event waits and plugin hooks react to status ([schema/events.rs](../repo/src/api/schema/events.rs), 63–84; [plugins/runtime.rs](../repo/src/app/api/plugins/runtime.rs), 203–240). This detects attention but does not wake a ProjectMaster to assess progress, chase stalled tasks or resolve blockers. |
| F16 | Parallel products/concurrent specialists | **Similar** | Workspaces/tabs/panes enumerate separate live agents ([app/agents.rs](../repo/src/app/agents.rs), 23–37); worktree creation is asynchronous ([worktrees/deferred.rs](../repo/src/app/api/worktrees/deferred.rs), 14–35 and 100–140). Execution concurrency is substantial; product teams, their definitions and assignment coordination need an upper layer. |
| F17 | Real multi-host execution/shared coordination | **Similar** | Saved SSH bridges connect to actual remote Herdr servers ([remote/saved.rs](../repo/src/remote/saved.rs), 20–56 and 68–121), CLI `--machine` routes operations ([cli/target.rs](../repo/src/cli/target.rs), 27–54 and 66–100), and the UI combines endpoint agents ([endpoint_agents.rs](../repo/src/client/shell/endpoint_agents.rs), 132–175). This is real multi-host control/visibility; servers do not share an organizational tracker, room history or replicated project knowledge. |
| F18 | Executive overview: current/recent/next/blockers | **Resembles** | Agent status, title, tokens and completion sequence are visible ([schema/agents.rs](../repo/src/api/schema/agents.rs), 209–251), with attention-sort/filter primitives (70–181). There is no producer of factual recent accomplishments, current ticket, planned next work and explicit blocker summaries. A `summary` metadata key is only externally supplied text. |
| F19 | Individual summary timeline linked to work | **Absent** | Event history is an in-memory, capped 512-event buffer ([api/event_hub.rs](../repo/src/api/event_hub.rs), 1–30); saved history is terminal ANSI ([persist/snapshot.rs](../repo/src/persist/snapshot.rs), 31–49 and 131–135). Neither is a durable plain-language agent timeline linking tickets, discussions, changes and tests. |
| F20 | Detailed individual coding workspace drill-down | **Similar** | Agent focus navigates to its pane and terminal mode ([app/agents.rs](../repo/src/app/agents.rs), 75–87); read exposes terminal output ([app/api/agents.rs](../repo/src/app/api/agents.rs), 271–309). External CLI UI can show conversation/tools/edits. Herdr does not normalize these into structured tool-call, artifact, diff and test views connected to project tasks. |
| F21 | Live activity/lifecycle/steering/execution visibility | **Similar** | Start, rename, focus, read, prompt, send-keys and wait are implemented ([schema.rs](../repo/src/api/schema.rs), 81–92); pane close shuts down detached runtimes ([app/api/panes.rs](../repo/src/app/api/panes.rs), 1966–2028). Fork/compact/agent budgets remain CLI-specific actions rather than a uniform lifecycle API. |
| F22 | Testing, integrated verification, acceptance/delivery | **Resembles** | Terminals can run any test CLI and wait on output substring/regex ([api/wait.rs](../repo/src/api/wait.rs), 22–128; [schema/events.rs](../repo/src/api/schema/events.rs), 94–112). There is no TestMaster workflow, acceptance criterion linkage, integrated verification gate or delivered-product state. Agent-idle/completion is not evidence of tests passing or human acceptance. |
| F23 | Autonomous operation with human organizational direction | **Resembles** | Background server continuity and programmable controls allow an external lead agent to orchestrate peers ([server/headless.rs](../repo/src/server/headless.rs), 1–15; [api/wait.rs](../repo/src/api/wait.rs), 177–321). No autonomous intake-to-delivery organization, periodic manager agent or role-responsibility policy is bundled. |
| F24 | New profiles accommodated by chat/tracker/dashboards | **Resembles** | Generic metadata/filter/sort and plugin panes provide extension points ([schema/agents.rs](../repo/src/api/schema/agents.rs), 70–181; [plugins/manifest.rs](../repo/src/app/api/plugins/manifest.rs), 11–85). More named instances can appear, but chat/tracker/organizational dashboards do not exist to extend. Adding a recognized launch kind is distinct from adding an organizational role. |

## Agent definition, creation and lifecycle

### What is actually an agent?

There are several identities to keep separate. A workspace is a CWD/repository-oriented collection of tabs and pane layouts. A pane is a view attached to a server-owned terminal. A terminal has its own identity, process runtime and agent-detection state. An “agent” in the public API is the recognized CLI currently owning such a terminal, optionally given a managed name. A native agent-session reference points into that CLI's conversation persistence. None of these is a task or a standing organizational role.

The concrete record in [src/terminal/state.rs](../repo/src/terminal/state.rs), lines 129–165, includes detection and hook authority, native-session references, labels/name ownership, launch state, sequence counters and restore error. It has no biography, product assignment, supervisor, permission policy or task queue. `AgentInfo` projects those runtime facts, including its location and CWD, rather than synthesizing an employee profile ([src/api/schema/agents.rs](../repo/src/api/schema/agents.rs), 209–260).

### Definition and configuration

A managed launch specifies `name`, `kind`, `pane_id`, argument vector and optional startup timeout. The schema contains no system prompt, tool registry or role definition. Herdr accepts known interactive agent kinds and sends their executable plus arguments to the pane's shell. A user/controller can pass CLI-specific model, permission or resume arguments, and project files can instruct that CLI, but responsibility remains outside Herdr: [src/api/schema/agents.rs](../repo/src/api/schema/agents.rs), 184–207; [src/app/agents.rs](../repo/src/app/agents.rs), 145–210.

Detection manifests are also not agent profiles. Their rules classify UI states using screen regions, regex/contains checks, priorities, AND/OR/NOT gates and OSC strings. They can identify working/blocked/idle and suppress historical-view updates, but do not define what work an agent should do: [src/detect/manifest.rs](../repo/src/detect/manifest.rs), 14–47 and 139–190. The compiled list of recognized CLI kinds should not be mistaken for a catalog of ProductMaster/BackendCoder-style roles.

### Creation and launch readiness

The caller creates or selects a shell pane before `agent.start`. The implementation validates a lowercase 1–32-character name, known kind, safe arguments, uniqueness, existing target, available shell and valid timeout. It rejects an agent-occupied pane. It constructs a shell command and preflights input before beginning the managed-launch state. An input-send failure clears the reserved name. It persists state and returns the initial agent plus argv: [src/app/agents.rs](../repo/src/app/agents.rs), 8–19 and 145–235. Error codes distinguish invalid input, missing/busy/unavailable pane, duplicate name and submission failure (238–294).

Launch has a three-second settle window and default 30-second timeout, with a maximum of 300 seconds. That is readiness orchestration, not a deadline on the agent's assignment. The CLI dispatch includes start and attach as distinct operations: [src/cli/agent.rs](../repo/src/cli/agent.rs), 9–10 and 52–64. A process being created does not guarantee that authentication, onboarding, model readiness or product work has succeeded.

### Execution, permissions, identity and routing

Each CLI executes its own independent tool/model loop in a real PTY. Herdr's local-socket permissions control access to the runtime, not what the coding agent may read, write or execute. The launch schema has no sandbox/allowlist or role-level capability grants. Plugin commands similarly spawn ordinary OS child processes with environment/context, not an isolated capability runtime: [src/app/api/plugins/runtime.rs](../repo/src/app/api/plugins/runtime.rs), 31–75 and 119–141. Wingman would need to set policy through Codex/host configuration and design its own authorization boundary for any network-facing Butler controller.

Agent-target resolution accepts a current public pane ID hosting an agent or its assigned agent name, and reports ambiguity rather than silently selecting an instance: [src/app/terminal_targets.rs](../repo/src/app/terminal_targets.rs), 74–129. General terminal targeting also supports terminal IDs and labels (33–69), so the target contracts are not interchangeable. The prompt test explicitly rejects using the CLI kind `opencode` as the named prompt target: [src/app/api/agents.rs](../repo/src/app/api/agents.rs), 661–672.

Concurrency comes from multiple terminals, workspaces and machines, not an internal task scheduler. Each instance can receive a separate prompt; dependencies and fan-in are composed by a caller with wait/read operations. There is no global assignment lock or protection from two independent controller processes deciding to prompt the same agent. The system preflights and serializes terminal input mechanics, which is a different guarantee from work ownership.

### Status authority and live supervision

Status combines process identity, terminal/UI detection and supported hook reports. `AgentState` has `Idle`, `Working`, `Blocked`, and `Unknown`, with additional confidence flags for visible idle/blocker/working chrome and transcript viewers: [src/detect/mod.rs](../repo/src/detect/mod.rs), 9–39. Terminal state tracks hook and metadata sequence sources, stale/suppressed sessions and name ownership rather than treating every incoming report as current: [src/terminal/state.rs](../repo/src/terminal/state.rs), 129–165. The source contains substantial source-arbitration logic, so integrators should consume its public status rather than reconstruct status by scraping arbitrary scrollback.

A useful stabilizer holds ambiguous working-to-idle transitions for repeated confirmations, bounded by 700 ms, while visible blockers/process exits bypass the plain-idle hold: [src/pane/agent_detection.rs](../repo/src/pane/agent_detection.rs), 5–13 and 29–77. This reduces misleading transients. It does not determine whether an assignment met its acceptance criteria. Periodic detection, endpoint reconnect and persistence timers are infrastructure housekeeping, not proactive project management.

### Persistence, resume and restart

Detaching a client leaves the server, original processes and terminals alive. A server/machine restart is different: restore constructs fresh shells in saved CWDs and optionally resumes supported native sessions, with deduplication: [src/persist/restore.rs](../repo/src/persist/restore.rs), 26–45 and 65–92. Resume plans produce commands such as `codex resume <id>` or `claude --resume <id>`. They rely on that external tool retaining its session: [src/agent_resume.rs](../repo/src/agent_resume.rs), 199–255. Reported resume argv is validated for length, controls and plain executable syntax, and the working directory contributes to deduplication identity (30–88).

Resumes can be staged with per-agent spacing and readiness/geometry/theme prerequisites rather than simultaneously spawning everything: [src/app/agent_resume.rs](../repo/src/app/agent_resume.rs), 17–96 and 99–139. This is startup pacing, not recurring autonomous work. A persisted native-session pointer does not make Herdr the owner of the transcript, nor restore externally managed tickets or conclusions.

Identity is tied to ownership, including real exit versus shell suspension. Inspected tests assert that real exit clears prior session/name/authority, suspended agents retain them, and same-kind replacements drop previous identity: [src/app/agent_suspend_tests.rs](../repo/src/app/agent_suspend_tests.rs), 154–247 and 254–284. This is a useful guard against attributing a new CLI process to an old agent. It also demonstrates why Wingman needs a separate durable directory identity across instances and runtime replacement.

### Interruption, errors, retry, completion and retirement

`agent.send_keys` supplies interactive input, including CLI-understood interruption keys; `pane.close` removes the view/runtime and emits close events. Runtime shutdown aborts detection/compression, closes the PTY actor and shuts down pane processes: [src/app/api/panes.rs](../repo/src/app/api/panes.rs), 1966–2028; [src/pane.rs](../repo/src/pane.rs), 2233–2246. This provides execution control, but no uniform “cancel task and roll back changes” transaction. Fork, compact and native conversation archive operations are commands understood by the hosted CLI, not a shared Herdr conversation lifecycle.

Prompt delivery separates preflight rejection, asynchronous write completion and later state waiting. Blocked/not-ready/lost-foreground agents are rejected before submission; waiter-thread creation failure also fails before writing. PTY disappearance and timeouts become explicit errors: [src/app/api/agents.rs](../repo/src/app/api/agents.rs), 82–136 and 139–207. The controller must interpret such failures; no durable job retry policy or assignment replay is built in.

Remote endpoints reconnect independently using backoff state with cancellation and connection generations ([src/client/endpoint/supervisor.rs](../repo/src/client/endpoint/supervisor.rs), 11–17 and 48–103). Remote CLI routing explicitly permits retrying only the read-only status probe, not ambiguously failed mutations, to avoid duplicate effects: [src/cli/target.rs](../repo/src/cli/target.rs), 103–148. Wingman should likewise make assignment delivery idempotent and reconcile outcomes before re-prompting after transport loss.

Completion means an observed runtime state transition. `completion_seq` records a completed-work idle transition independently of viewing state ([src/api/schema/agents.rs](../repo/src/api/schema/agents.rs), 242–246), but no evaluator checks code quality, test results, definition of done or human acceptance. Retirement is closing panes/workspaces or releasing agent ownership, not archiving a standing role with its project history. Product-delivery shutdown rules therefore remain Wingman logic.

## Coordination mechanics and one request traced through code

Consider a lead agent issuing a prompt to a previously started named reviewer and waiting for idle or blocked. This is a trace of an implemented request path, not a runtime exercise performed during assessment.

1. CLI parsing dispatches `agent prompt` to the prompt operation ([src/cli/agent.rs](../repo/src/cli/agent.rs), 39–64); its typed request contains target, text and optional wait settings ([src/api/schema/agents.rs](../repo/src/api/schema/agents.rs), 45–57 and 199–207). For a remote target, `--machine` selects an endpoint and obtains an SSH API bridge ([src/cli/target.rs](../repo/src/cli/target.rs), 27–54 and 66–100).
2. The API wait path records the pre-prompt agent identity/status, remaining timeout and current event sequence before dispatch. It does not simply see an already-idle agent and immediately declare the new request finished: [src/api/wait.rs](../repo/src/api/wait.rs), 177–250.
3. Application preflight resolves the exact agent, rejects empty text, blocked state, pending launch, absent runtime or a CLI that no longer owns the foreground process: [src/app/api/agents.rs](../repo/src/app/api/agents.rs), 139–207. A blocked reviewer must be handled interactively. The API does not pretend an approval dialog is its normal prompt.
4. The submission path encodes paste/text and Enter separately, applies relevant CLI/platform accommodations, and queues them with a 300 ms submit delay. A completion receiver acknowledges the actual PTY submission rather than only request enqueue: [src/app/api/agents.rs](../repo/src/app/api/agents.rs), 13–32, 97–117 and 209–268. The test at lines 599–659 asserts the actual bracketed-paste bytes, separate carriage return and delayed completion.
5. The wait path rechecks terminal/name/kind identity, observes activity or a post-submission sequence change, and imposes a five-second prompt-effect window if no activity was seen. It can report a stalled prompt rather than equate old idle state with completed new work: [src/api/wait.rs](../repo/src/api/wait.rs), 235–289.
6. Subsequent status/detection events trigger re-probes; replacement, move, exit and close are handled explicitly. Relevant transient matched statuses can be retained, while identity changes fail the wait: [src/api/wait.rs](../repo/src/api/wait.rs), 364–465. Success returns agent state, not a structured review result or artifact. The lead must read the terminal or obtain a file-based result and determine the next action.

This permits real agent-to-agent coordination through terminal submissions and waits. Shared state consists of server-owned workspace/pane/terminal records, metadata and event envelopes; source files are shared according to filesystem/CWD arrangement. There is no built-in ticket dependency DAG, room history, conversation participant list, handoff receipt or business decision queue. A lead can implement a review loop using these primitives, but Herdr does not spontaneously create the lead or sustain the loop after its native agent stops.

Events are operational signals: workspace/worktree/tab/pane changes, detected agents, output matches and status changes ([src/api/schema/events.rs](../repo/src/api/schema/events.rs), 11–112). The hub retains 512 events in memory and has a checked history API that distinguishes a gap from an empty result ([src/api/event_hub.rs](../repo/src/api/event_hub.rs), 18–74). A controller must maintain its own durable audit/coordination log and resynchronize after gaps or restart.

## Major capabilities beyond the described Wingman product

### Heterogeneous CLI compatibility and terminal-state intelligence

Wingman specifies Codex agents; Herdr supports multiple installed CLI families with process recognition, state manifests, integrations and native resume strategies. The agent enum and executable mapping are concrete ([src/detect/mod.rs](../repo/src/detect/mod.rs), 41–175). This could let Wingman diversify providers or retain existing specialized tooling. The consequence is that common terminal control does not normalize tool permissions, model semantics, artifacts or conversation lifecycle. Each CLI version can change screen/OSC behavior. Compatibility would need live agent-specific validation beyond the source review.

Detection explanation is unusually useful integration infrastructure: matched rules, priorities, regions, confidence flags, fallback reasons, source/version and local-override shadowing are structured diagnostic data ([src/detect/manifest.rs](../repo/src/detect/manifest.rs), 27–81 and 93–121). That can make a stalled-agent incident diagnosable instead of opaque. It is evidence about observed UI/process status, not evidence that product work is correct.

### Real machine aggregation with independent connection ownership

Herdr can maintain local and saved SSH endpoints, show their agents together, reconnect endpoints independently and route CLI requests to a selected machine. Saved SSH configuration carries a label, target, explicit session and enabled state; SSH retains credential ownership, and removing a profile leaves remote work running ([src/cli/machine.rs](../repo/src/cli/machine.rs), 10–25). That is stronger runtime/machine handling than merely starting local subprocesses.

The value for Wingman is a ready route to agents executing on appropriate hosts while preserving a single operator surface. The integration consequence is host-scoped runtime state: Wingman still must route product records, files and agent relationships across those servers. A shared list does not synchronize repositories or turn server-local event histories into a distributed collaboration system.

### Server replacement with live PTY handoff

On Unix, handoff transfers live runtime file descriptors/state to a replacement server. Its state includes child PID, geometry, terminal protocol state, history and agent identity. It intentionally excludes in-flight waits, subscriptions, sockets and transient coordination ([src/handoff_runtime.rs](../repo/src/handoff_runtime.rs), 4–31). Runtime methods explicitly duplicate/preserve/import handoff resources ([src/terminal/runtime.rs](../repo/src/terminal/runtime.rs), 24–81).

This gives an upgrade/maintenance continuity path distinct from ordinary restore, which starts new shells. Wingman could benefit from keeping costly coding sessions alive through runtime replacement. It must still reconcile pending control operations and reconnect subscriptions. The handoff comment explicitly disclaims preserving them. Platform capability rather than a blanket cross-platform guarantee should control adoption.

### Worktree-aware execution organization

Herdr manages Git worktree list/create/open/remove and records membership in restored workspaces. Creation runs asynchronously and resolves source repository, branch/base and checkout path ([src/app/api/worktrees/deferred.rs](../repo/src/app/api/worktrees/deferred.rs), 14–35 and 100–140). Removal commands recognize dirty/untracked-file and submodule restrictions ([src/worktree.rs](../repo/src/worktree.rs), 175–203).

This is useful for independently editing specialists or comparing attempts. It does not implement code integration, conflict resolution, PR review or acceptance. Wingman needs explicit ownership and integration policy so a worktree is connected to the right ticket and so completed work reaches the product branch.

### Executable plugins as an application extension surface

Plugin manifests define platform-aware build/startup commands, contextual actions, event hooks, panes and link handlers ([src/app/api/plugins/manifest.rs](../repo/src/app/api/plugins/manifest.rs), 11–95). Runtime invocation supplies JSON context, event payload and IDs in environment variables, starts an OS process, captures output/status and limits concurrent commands to 32 with a bounded 200-log history ([src/app/api/plugins/runtime.rs](../repo/src/app/api/plugins/runtime.rs), 11–13 and 16–158).

This could host a Wingman tracker pane or event-to-Butler bridge without rebuilding terminal internals. The consequence is an ordinary trusted subprocess extension model, not a secure hosted plugin sandbox or durable workflow engine. External marketplace examples must be assessed independently; references to them in parser tests do not establish that a complete Telegram workflow is available in this checkout.

## Grounded mechanisms worth carrying forward

The distinctive combination is operational rather than a claim of historical novelty.

1. **Separate process/session/view identities.** The terminal-state/runtime split, agent-name ownership, session references and tests for suspension versus replacement address a real source of attribution errors. An employee directory should retain its own ID and map explicitly to these replaceable runtime identities; otherwise a new process could inherit old work claims. Evidence: [src/terminal/state.rs](../repo/src/terminal/state.rs), 112–165; [src/app/agent_suspend_tests.rs](../repo/src/app/agent_suspend_tests.rs), 154–284.
2. **Observe the effect of a prompt before accepting a later state.** Pre-submission identity/event cursors, prompt-effect timeout and post-state-change waiting are stronger than naive “send text; wait until idle.” They can detect a paste that never started work and stop a replacement agent from satisfying an old wait. They still cannot distinguish successful review from an idle agent that misunderstood the instruction. Evidence: [src/api/wait.rs](../repo/src/api/wait.rs), 196–289 and 364–465.
3. **Make status classification explainable and updateable.** Rule evidence, source precedence diagnostics, live-bottom-buffer state and bounded idle confirmation make UI-based monitoring maintainable. The limit is classifier compatibility, not semantic project understanding. Evidence: [src/detect/manifest.rs](../repo/src/detect/manifest.rs), 14–121 and 139–190; [src/pane/agent_detection.rs](../repo/src/pane/agent_detection.rs), 29–77.
4. **Do not replay ambiguous remote mutations automatically.** The remote controller retries read-only discovery/status but explicitly excludes blindly replaying later requests. That is a good starting discipline for avoiding duplicate prompt assignment after SSH failures. It leaves the higher layer responsible for request IDs, durable intent and reconciliation. Evidence: [src/cli/target.rs](../repo/src/cli/target.rs), 103–148.
5. **Expose extensible metadata without conflating it with authority.** Tokens and UI filters can carry summaries, model names or role labels, with source sequences and expiry. The primitive is useful for Wingman projection, but a token named `task` is not a tracker record, and text named `summary` is not a verified timeline. Evidence: [src/metadata_tokens.rs](../repo/src/metadata_tokens.rs), 15–103; [src/api/schema/agents.rs](../repo/src/api/schema/agents.rs), 70–181.

## Practical adoption path and remaining work

**Use directly:** terminal runtime ownership, background execution, named CLI instances, prompt/read/wait/send-key operations, workspaces/worktrees, native-session resume, status notifications, per-agent terminal drill-down and SSH endpoint control. These provide much of the infrastructure beneath F01/F14/F16/F17/F20/F21. A Codex-only first deployment could reduce compatibility breadth while retaining Herdr's runtime benefits.

Adapt:

- Write a runtime adapter mapping durable Wingman agent IDs to machine/session/terminal/pane/native-session IDs.
- Translate lifecycle events into a durable organizational log.
- Use explicit assignment IDs and reconciliation around prompt delivery.
- Project role/task/summary metadata to Herdr only as views of authoritative Wingman records. Build a controller that resubscribes and reconciles after server replacement, event-history loss or SSH failure. Treat current runtime separation as evolving and rely on advertised/public operations rather than internal pane structs.

Build:

- Butler/Telegram conversational routing.
- Portfolio registry and intake.
- Persistent role/profile/team directory.
- ProductMaster and TechMaster discovery/planning policies.
- Scope/specification/acceptance records.
- Shared tracker with dependency and assignment semantics.
- Room1/Room2 collaboration with durable message context.
- Periodic ProjectMaster supervision.
- Executive current/recent/next/blocker summaries.
- Per-agent factual timelines linked to tasks, conversations, changes and tests.
- Delivery/acceptance and stop-after-delivery rules. An external agent prompted to do these things is a possible implementation route, not an already supplied Herdr capability.

The main architectural fit is therefore **runtime component underneath Wingman**, potentially with a plugin operator surface. Choosing Herdr does not remove the need for Wingman's domain model, durable coordination engine, cross-host shared records or business-level decision policies. Its terminal UI is a valuable operator fallback even if Wingman eventually builds web dashboards and chat views.

## Verification scope and uncertainties

Read [WINGMAN_PURPOSE.md](../../WINGMAN_PURPOSE.md), the complete [ASSESSMENT_GUIDE.md](../../generic/assessments/ASSESSMENT_GUIDE.md), and the checkout's [AGENTS.md](../repo/AGENTS.md). No source file was edited. No dependencies were installed, no tests/builds were run and no services or external CLI processes were launched. The report is static inspection of the exact local commit; behavior above is implementation-supported, not runtime-verified on this machine.

Inspected implementation paths:

- entry dispatch.
- headless server ownership.
- API schema/server/waits/event hub.
- managed agent launch and target resolution.
- PTY creation/shutdown.
- terminal identity/state.
- detection manifests and idle stabilization.
- persistence snapshot/writer/restore/resume.
- SSH bridge and machine routing.
- endpoint aggregation/reconnect.
- plugin manifests/runtime.
- worktree commands/deferred operations.
- notification projection.

These paths are linked at the relevant claims rather than inferred from marketing text.

Tests inspected, not executed:

- Prompt submission bytes/delayed Enter, waiter-spawn-before-mutation behavior, blocked/startup rejection and key validation: [src/app/api/agents.rs](../repo/src/app/api/agents.rs), 599–877.
- Exit, suspension and same-kind replacement identity cases: [src/app/agent_suspend_tests.rs](../repo/src/app/agent_suspend_tests.rs), 154–284.
- Event-history retention/lost-boundary behavior: [src/api/event_hub.rs](../repo/src/api/event_hub.rs), 91–125.
- Restore opt-in/allowlist, duplicate-session suppression, reported argv preference and rehydration cases: [src/persist/restore.rs](../repo/src/persist/restore.rs), 1172–1424.
- Metadata source bounds and patch semantics: [src/metadata_tokens.rs](../repo/src/metadata_tokens.rs), 117–158.
- Endpoint activation tests concerning source release, exact snapshot/surface revisions and stale generation/boot evidence were inspected around [src/client/endpoint/activation_tests.rs](../repo/src/client/endpoint/activation_tests.rs), 256–532. This supports the caution that cross-endpoint activation is stateful, not proof of live network reliability.

Negative checks searched likely implementation paths under `src/` (especially `api`, `app`, `cli`, `config`, `integration`, `server` and `remote`), plus `skills/` and `tests/`, for Telegram/Butler, task tracker/tickets, roles/profiles, rooms, discovery, definition of done, cron/scheduling, supervision, approvals and acceptance. Matches were reviewed in context: keybinding/machine “profiles” are not agent roles; scheduled autosave/resume/reconnect is not manager wakeup; PTY “acceptance” is input acceptance. The Telegram matches were plugin example/parser fixtures. The complete API operation set and persisted schemas were then cross-checked for the absent domain concepts. This does not exclude someone building them as an external controller or third-party plugin.

Unverified areas include current installed CLI compatibility, actual native conversation restore after machine reboot, live PTY handoff reliability/platform availability, multi-machine failure/reconnect behavior on real networks, plugin marketplace implementations and performance at organizational scale. The checked-out code gives concrete mechanisms and tests, but none of those deployment outcomes should be claimed as observed here.
