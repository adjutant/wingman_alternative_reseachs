# Agent of Empires assessment against Wingman

Assessed 2026-11-05 against [Wingman's purpose](../../WINGMAN_PURPOSE.md). Repository: https://github.com/agent-of-empires/agent-of-empires

Local checkout: `research/agent-of-empires/repo`. Actual Git commit: `db073acb257e666264e0309c683d38bbbfe1c46a`. [Cargo.toml](../repo/Cargo.toml), lines 5–20, declares version `1.21.0`, a terminal session manager for AI coding agents, with MIT and Apache-2.0 licensing. This assessment describes that local revision, not a current hosted service or downloaded plugin.

**Verdict:** Agent of Empires (AoE) provides a strong execution and individual-workspace foundation. It launches independent coding processes and retains development sessions. It supports terminal and structured conversations through desktop and mobile clients. Worktrees, containers, input queues, approvals, recovery, and plugin automation support those sessions.

Wingman still needs product ownership, enduring agent responsibilities, shared tickets, collaboration rooms, and portfolio intake. Telegram routing, product supervision, and accepted delivery also need implementation.

Useful mechanisms include detached Agent Client Protocol (ACP) workers, replayable SQLite events, and conversation summaries. A shared session service controls execution. Capability checks limit automation. Resource ownership checks control destructive cleanup. These mechanisms do not supply a product portfolio, shared ticket graph, or enduring specialist organization.

## Architecture and actual execution model

### Entry points and ownership boundaries

The Rust `aoe` binary parses CLI commands, selects a daemon URL when requested, dispatches session/project/plugin commands, starts `serve`, or enters the TUI. Hidden commands also execute worker and environment helpers. See [main.rs](../repo/src/main.rs), lines 57–121 and 432–470. The daemon is part of the core build. The `web` feature adds the embedded browser client and its build dependency on Node. [Cargo.toml](../repo/Cargo.toml), lines 204–245, makes that distinction explicit.

There are two execution paths:

- **Terminal view:** a session launches the selected coding CLI in tmux, on the host or in a sandbox. AoE observes status through the harness's integration/hooks or terminal heuristics. Tmux preserves the interactive process when a viewer disconnects. The [AgentDef contract](../repo/src/agents.rs), lines 379–410, declares launch, detection, instruction, permission, resume and fork behavior per harness. Recovery has explicit native-resume eligibility and live-process detection rather than simply rerunning every saved command; see [recovery.rs](../repo/src/session/recovery.rs), lines 14–117.
- **Structured view:** the daemon's SessionService and ACP Supervisor control a detached per-session runner, which owns an ACP adapter and its agent subprocess. The runner outlives the daemon; clients receive structured messages, tools, plans and permission requests. [SessionService](../repo/src/server/session_service.rs), lines 1–36, is shared by HTTP and plugin callers; [Supervisor](../repo/src/acp/supervisor/mod.rs), lines 1–47 and 142–215, separates worker kinds and lifecycle authority; [runner launch](../repo/src/acp/acp_client/runner.rs), lines 166 onward, implements detached ownership. ACP is an execution/control protocol, not AoE's own product-team coordination protocol.

The session row is a persistent `Instance`: UUID, title, project/group, optional parent session, harness/command, status, native and ACP conversation information, queue and lifecycle metadata. [instance/mod.rs](../repo/src/session/instance/mod.rs), lines 393–670 and 719–963. A **session** can remain while its worker is stopped. A **worker** is one execution incarnation. A **turn** is a prompt/response cycle. A native harness's subagent can appear as a nested tool or background transcript without becoming an AoE session. A profile is a configuration/storage scope, and an ACP AgentProfile is a protocol-capability description. Neither is automatically a Wingman role.

### Persistence, projection and launch

Session/group persistence uses per-profile JSON with in-process locks, cross-process flocks and atomic replacement. The code documents lock ordering, title/lifecycle authority and failure windows for cross-profile moves; see [storage.rs](../repo/src/session/storage.rs), lines 1–95 and 131–197. This is inspectable local state, not a networked tracker database. The global/profile [project registry](../repo/src/session/projects.rs), lines 1–5 and 127–159, stores named repository paths, base branches, pinning and configuration overrides.

Structured conversation events use SQLite and sequence-based insertion that ignores duplicate sequence numbers. Retention preserves selected context/lifecycle/background-work events. It is not an unlimited audit guarantee. [event_store/mod.rs](../repo/src/acp/event_store/mod.rs), lines 25–150. A separate plugin host event schema and bounded key/value storage let plugins persist their own state; [host_api.rs](../repo/src/plugin/host_api.rs), lines 16–61. Queued prompt metadata is mirrored into the Instance, while attachment bytes are kept separately. [session_service.rs](../repo/src/server/session_service.rs), lines 85–104 and 1406–1477; [queue.rs](../repo/src/server/api/queue.rs), lines 137–228.

Creation plans an Instance and its owned resources before provisioning. A worktree can be attached or created. A multi-repository workspace has several tracked worktrees; scratch sessions get managed directories. Build results remember which checkouts and branches were actually created so rollback need not delete pre-existing resources. [builder.rs](../repo/src/session/builder.rs), lines 21–204. The shared spawn service then applies profile, model/mode, plugin provenance, idempotency, initial-turn, callback and import/fork state, persists the session and arranges launch; [session_spawn.rs](../repo/src/server/session_spawn.rs), lines 11–69 and 193–287. This is useful transactional execution infrastructure, but it does not create project leadership or assign a product ticket.

## Feature-by-feature comparison

**Exact** means the described Wingman behavior is implemented within the stated boundary. **Similar** is substantial behavior with a scope or workflow difference. **Resembles** is a related primitive requiring additional product logic. **Absent** reflects implementation searches in the paths described below. External plugin implementations are not credited from an index entry alone.

| ID | Wingman capability | Verdict | Implemented behavior, source evidence and concrete gap |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | Real CLI/tmux or ACP subprocesses can run independently, including multiple Codex sessions. [Supervisor](../repo/src/acp/supervisor/mod.rs), L142–215; [builder](../repo/src/session/builder.rs), L54–106. Specialization can be supplied through instructions/configuration, but BackendCoder or TestMaster is not a built-in durable responsibility or assignment model. |
| F02 | Extensible profiles, roles and team composition | **Similar** | [Custom agent configuration](../repo/src/session/config/mod.rs), L1268–1345, adds commands, status mapping, execution contracts, ACP commands and config stores; [plugin catalog](../repo/src/plugin/agent_integration.rs), L51–126, adds noncolliding agent launch commands. [Profiles](../repo/src/session/config/profile_config.rs), L12–65, carry sparse overrides. These extend harnesses/configuration, not role specifications, project leadership or workload-driven team composition. |
| F03 | Agent directory and visible working relationships | **Resembles** | [Instance](../repo/src/session/instance/mod.rs), L393–436, has identity, project, group and optional parent; [session-list MCP](../repo/src/server/mcp.rs), L37–81, filters by group or direct children. A navigable session directory exists, but parentage/grouping does not establish managerial or collaboration relationships, role ownership or linked tickets. |
| F04 | Telegram main channel and Butler routing | **Absent** | Searches across `src`, `acp-worker`, plugin APIs and the featured index found no Telegram bot, Butler ingress or project-aware answer routing. The [prompt endpoint](../repo/src/server/api/acp/prompt.rs), L87–149, addresses a chosen session; [plugin message API](../repo/src/plugin/session_api.rs), L791–915, is an integration seam, not a Telegram representative. |
| F05 | Cross-project registry, intake and existing/new project routing | **Resembles** | A real global/profile [repository registry](../repo/src/session/projects.rs), L1–5, L67–91 and L127–159, saves paths/defaults for creating sessions. It has no natural-language intake classification, product-history matching, autonomous project creation/notification or portfolio manager. |
| F06 | Per-project product and technical leadership | **Absent** | [Session metadata](../repo/src/session/instance/mod.rs), L393–436, and [spawn configuration](../repo/src/server/session_spawn.rs), L11–69, contain project/group/parent and launch values, not ProductMaster/TechMaster appointments, mandates or handoff. Searches through session, server, plugin and worker paths found no corresponding leadership workflow. |
| F07 | Proportionate research, discovery and iterative human clarification | **Resembles** | Agents can research with their own tools and ask questions; [structured workspace](../repo/web/src/components/acp/StructuredView.tsx), L324–354, renders approvals and elicitations. AoE does not decide discovery depth, keep a product uncertainty register or route clarification across Butler and product leadership. A question form is an agent interaction primitive. |
| F08 | Product scope, specs, acceptance scenarios and definition of done | **Resembles** | File-oriented agents can create such records, and [context primers](../repo/src/acp/context_primer.rs), L114 onward, preserve plan/message/tool context. No scope/specification/acceptance schema or readiness gate was found in session, project, API or worker models. A plan or filesystem does not enforce a product definition. |
| F09 | Technical decomposition, assignment and shared task tracking | **Resembles** | Plans/tool-todo rendering and [plan-progress badges](../repo/web/src/components/sidebar/RowBadges.tsx), L215–246, expose progress inside a session. The core lacks shared tickets with assignees/dependencies and a decomposition/dispatch loop. [Featured kanban entry](../repo/plugins/featured.toml), L47–49, points to external source. It is not sufficient evidence of an implemented core tracker. |
| F10 | Human-facing portfolio/project management dashboard | **Resembles** | [Dashboard](../repo/web/src/components/Dashboard.tsx), L12–60 and L126–170, counts sessions, projects, waiting/errors and recent sessions; project/sidebar views group execution work. Goals, ticket ownership, acceptance progress and portfolio decisions are absent from the inspected registry/dashboard. A session dashboard is valuable but narrower than ProjectTracker. |
| F11 | Agent chat application, rooms and direct collaboration | **Resembles** | [Plugin host](../repo/src/plugin/host_api.rs), L178 onward, exposes topic events; [sessions.message.send](../repo/src/plugin/session_api.rs), L791–915, delivers plugin-marked text to another selected session. There are no built-in rooms, participant histories or agent-to-agent conversation application. A coordinator plugin could supply them. |
| F12 | Management escalation and human decisions/approvals | **Similar** | [Permission bridge](../repo/src/acp/permissions.rs), L10–35, and [workspace controls](../repo/web/src/components/acp/StructuredView.tsx), L339–354, support real tool decisions and structured input. This meets direct agent/human approval needs, while Room2 → Room1 → Butler escalation, decision ownership and project-level business tradeoffs remain absent. |
| F13 | Durable project knowledge and reusable directives | **Resembles** | Repository files remain available; [skills model](../repo/src/session/skills_model.rs), L23–139, discovers native/shared skill roots and distinguishes managed from external skills. [Project MCP configuration](../repo/src/session/mcp/project_mcp.rs), L10–109, adds reusable tooling. There is no Wingman DIRECTIVES structure, product-knowledge model or mandatory context consultation by leadership. |
| F14 | Persistent identity, conversation and work continuity | **Similar** | [Instance](../repo/src/session/instance/mod.rs), L393 onward; [conversation binding](../repo/src/session/instance/execution.rs), L9–143; [event store](../repo/src/acp/event_store/mod.rs), L71–150, preserve session and conversation continuity across worker/viewer restarts. The identity is a coding session, not an employee whose assignments and organization persist across conversations. Native exact resume is harness-dependent; primer fallback is lossy. |
| F15 | Proactive supervision, periodic wake and blocker follow-up | **Resembles** | [Reconciler](../repo/src/server/acp_reconciler/mod.rs), L1–35 and L118–129, periodically repairs worker state; [wakeup parsing](../repo/src/acp/acp_client/raw_input.rs), L1–83, and [wakeup store](../repo/src/acp/event_store/wakeups.rs), L11–98, reflect agent-native schedules/monitors. They do not read project tickets, contact responsible leaders or resolve product blockers. General cron is an external plugin in [featured.toml](../repo/plugins/featured.toml), L43–45. |
| F16 | Parallel products and concurrent specialists | **Similar** | Multiple sessions/workspaces can execute concurrently; [Supervisor](../repo/src/acp/supervisor/mod.rs), L94–106 and L196–215, enforces worker capacity, and [builder](../repo/src/session/builder.rs), L109–204, provisions separate worktrees/workspaces. Parallel product teams still need leaders, assignments, interface coordination and integration policy. |
| F17 | Real multi-host execution with shared coordination | **Resembles** | [Custom agent settings](../repo/src/session/config/mod.rs), L1268–1315, explicitly allow an SSH command, so remote execution is possible as a user-defined launch. [main](../repo/src/main.rs), L115–119, also selects a remote daemon. Neither supplies a federated host registry, placement policy, shared tracker/rooms or cross-host project identity. Remote access to one daemon and SSH wrappers are narrower than Wingman's two-host organization. |
| F18 | Executive agent overview: current/recent/next and blockers | **Resembles** | [Dashboard counts](../repo/web/src/components/Dashboard.tsx), L35–60, status/plan badges and [generated conversation summaries](../repo/src/session/conversation_summary.rs), L78–180, help inspect current activity and recap work. There is no required current/recent/next/blocker briefing tied to assignments and outcomes. Waiting/Error is a process/session signal, not a product-blocker explanation. |
| F19 | Individual agent summary timeline linked to underlying work | **Resembles** | [Summaries](../repo/src/session/conversation_summary.rs), L78–180, carry the event sequence they cover, and the [lifecycle feed](../repo/src/server/lifecycle_feed.rs), L1–5 and L85–120, reports session mutations. Structured messages/tools are replayable. This is not a curated per-agent accomplishment timeline with ticket, discussion and verification links. |
| F20 | Drill-down into detailed per-agent coding workspace | **Similar** | [StructuredView](../repo/web/src/components/acp/StructuredView.tsx), L93–136, L238–245 and L324–354; [thread tool rendering](../repo/web/src/components/acp/ThreadMessages.tsx), L238–310, expose conversation, tool activity, plans, approvals and subagents; terminal/file/diff views complement it. This is a strong workspace for a session, without the organizational task/room links or universal harness parity Wingman expects. |
| F21 | Live activity, lifecycle controls, steering and execution visibility | **Similar** | [Dispatch](../repo/src/acp/dispatch.rs), L1–95, implements send/steer/queue decisions; [fork contracts](../repo/src/session/fork.rs), L7–54, [stop](../repo/src/session/stop.rs), L5–35, and [Instance triage](../repo/src/session/instance/mod.rs), L460–578, support substantial control. Resume, compaction, fork and permission capabilities vary by adapter; organization-wide goals/budgets are not a demonstrated common contract. |
| F22 | Testing, integrated verification and acceptance/delivery | **Resembles** | Agents can execute tests through native tools or the bundled agent's [Read/Write/Bash tools](../repo/acp-worker/aoe-agent/src/index.ts), L181 onward. Tool results/diffs can be reviewed. [Completion callbacks](../repo/src/server/callback.rs), L1–12 and L48–58, report Idle/Waiting/Error, not integrated-test success or accepted delivery. No TestMaster/definition-of-done pipeline was found. AoE's own test suite is not that product capability. |
| F23 | Autonomous operation with human direction through the organization | **Resembles** | Detached execution, native agent tool loops and [plugin creation/turn RPCs](../repo/src/plugin/session_api.rs), L1–10 and L73–135, permit unattended work under policy. They do not implement the request → discovery → planning → specialists → verification → delivery organization. The human or an external coordinator still selects sessions and organizes outcomes. |
| F24 | Chat, tracker and dashboards accommodate new profiles | **Resembles** | New harness commands appear through [agent configuration](../repo/src/session/config/mod.rs), L1268–1345; [plugin UI/state API](../repo/src/plugin/host_api.rs), L23–61 and L178 onward, can extend presentation. Session views accept new tools, but there is no built-in role-aware chat/tracker schema or guarantee that a new organizational profile automatically participates in all connected Wingman views. |

## Detailed agent definition and lifecycle

### What is defined, and what actually exists

AoE has a central built-in `AgentDef` table describing binaries and execution integration. It is not a collection of employee personas. Its fields cover launch subcommand, aliases, status detection, instruction and one-shot flags, hooks, session support, fork strategy, permission response and lifecycle; [agents.rs](../repo/src/agents.rs), lines 379–410 and 626 onward. For structured use, [ACP AgentProfile](../repo/src/acp/agent_profiles.rs), lines 3–31 and 89–145, describes clear/compact commands, parent-tool metadata, wakeup support and bypass modes. These distinctions prevent a custom name mapped to Claude's status heuristics from silently becoming a fully supported Claude execution/resume contract.

The user can add a `name=command` custom harness, map detection separately from execution, select a native config directory, and provide an ACP command. Native custom commands are shell commands in tmux; custom ACP commands are split into argv and executed directly unless the user explicitly wraps a shell. A custom entry without ACP launch configuration is terminal-only. [config/mod.rs](../repo/src/session/config/mod.rs), lines 1268–1345. Global settings, sparse profile overrides and repository settings customize execution. A role such as ProductMaster could be represented by a profile, instructions, skill and named session, but AoE would not thereby enforce its authority or link it to the product's technical leader.

Plugin agent integration adds another concrete extension route. Active plugins declaring integration capability can contribute commands, with built-in/custom precedence and duplicate-provider refusal. [agent_integration.rs](../repo/src/plugin/agent_integration.rs), lines 21–42 and 51–126. That enables new harnesses to join existing session UI. It still leaves role composition and organizational contracts to another layer.

### Creation, identity and execution

A session starts from a CLI/UI/API specification with a tool, path/group, optional worktree/branch, sandbox/image, environment, arguments and command override. The builder applies per-session values ahead of configured defaults and plans owned resources; [builder.rs](../repo/src/session/builder.rs), lines 21–106 and 109–204. The server's shared creation path adds model/effort/mode, pending initial turn, plugin owner/idempotency, import or fork seed and callback. A profile namespace and identity lock protect session creation. See [session_spawn.rs](../repo/src/server/session_spawn.rs), lines 193–287. The creation registration also permits an immediately returned session to be stopped/deleted while its asynchronous ACP handshake remains unfinished. The regression scenario is encoded at lines 1170–1274 of that file.

There are several identities, each with different authority. The AoE Instance UUID identifies the durable UI/session row. A native or ACP conversation ID identifies harness state. The worker's PID/generation/birth fingerprint identifies a process incarnation. [ConversationBinding](../repo/src/session/instance/execution.rs), lines 9–143, qualifies a conversation by agent, stores, filesystems and provenance: Unknown, Preallocated, Observed, Asserted or Imported. Merely allocating an ID does not prove that the intended native conversation exists. [RunnerIdentity and Lease](../repo/src/acp/runner_lifecycle.rs), lines 9–64 and 123–157, keep process authority separate from display status. This is a particularly useful foundation for Wingman because a reused name, cwd or PID is not a safe worker identity.

Native sessions run installed agent CLIs with their own tools and credentials. Structured sessions use registered ACP adapters. The daemon supervises each worker and projects its events to clients.

AoE also owns an ACP agent built with Vercel AI SDK. It starts one Node process per session and selects a provider. Its model/tool loop has a 16-step limit. Read, Write, and Bash tools call AoE's ACP filesystem and terminal services. See [aoe-agent/index.ts](../repo/acp-worker/aoe-agent/src/index.ts), lines 3–15, 30–75, and 181 onward. Transcript persistence records completed text exchanges. It omits cancelled, errored, and tool-only turns (lines 131–158). This differs from Codex's native conversation and tool history.

### Tools, permissions and routing

AoE is primarily the controller of a harness, not a universal tool-policy engine replacing the harness. Native capabilities and permission modes differ. For example, the ACP profile maps Claude to `bypassPermissions` and Codex to `agent-full-access`, while the OpenCode profile deliberately does not guess an unverified bypass mode. [agent_profiles.rs](../repo/src/acp/agent_profiles.rs), lines 89–145. Structured tool permission requests get nonces, options, a destructive classification and one-time resolution; [permissions.rs](../repo/src/acp/permissions.rs), lines 10–35. Questions/elicitation are distinct from permission approval. These interactions can capture human intent, but have no built-in management escalation semantics.

Tools can be extended through native harness configuration, shared skills and managed MCP server configuration. The project `.mcp.json` model supports stdio, HTTP and SSE servers with display redaction and trust fingerprinting; [project_mcp.rs](../repo/src/session/mcp/project_mcp.rs), lines 1–109. It is a tool-configuration seam, not a claim that every harness exposes identical tools. Optional sandboxing introduces container filesystem/configuration lifecycle, while non-sandbox host sessions retain the selected CLI's execution scope.

Prompt routing targets an AoE session ID. It does not infer a project or role from ordinary language. The shared submission path holds a per-session guard before waking, checking worker state or changing queues. It decides sent, steered or queued; cancellation and compaction outrank steering, and clear/compact commands must run alone. [prompt.rs](../repo/src/server/api/acp/prompt.rs), lines 193–390; [dispatch.rs](../repo/src/acp/dispatch.rs), lines 1–95. That arbitration is valuable for multiple browser/CLI/plugin inputs, but Wingman still needs a higher-level router that knows which product and agent should receive them.

### Concurrency, persistence and scheduling

Several native/structured sessions run concurrently. ACP has a configurable worker-capacity gate, serialized first-use adapter warmup and per-session admission. Reconciler boot/resume work has a separate cap of four concurrent resumes; [supervisor/mod.rs](../repo/src/acp/supervisor/mod.rs), lines 94–106 and 196–215; [acp_reconciler/mod.rs](../repo/src/server/acp_reconciler/mod.rs), lines 28–35. Worktree separation helps concurrent coding avoid direct working-directory interference. AoE does not infer dependency order, resolve simultaneous API changes or decide when branches should integrate.

Durable Instance state, native conversation binding and the ACP event log let a session outlive its viewer and execution incarnation. Exact load/resume depends on the adapter and available native store. When an ACP conversation cannot be loaded, a bounded context primer reconstructs recent prompts, assistant text, plans and tool intent. Its default budget is 24,000 characters and 20 turns, with omission/truncation notices and special handling for unprocessed prompts; [context_primer.rs](../repo/src/acp/context_primer.rs), lines 1–87 and 114 onward. This gives useful continuity while honestly being different from restoring hidden model state and complete history.

Delivery persistence also has an important boundary. `send_turn` publishes the admitted prompt before forwarding it, so a recorded prompt is not conclusive proof that the agent received it. The pending-initial-turn drain documents an at-least-once contract: a crash or failed disk clear after forwarding can redeliver the turn after restart. [session_service.rs](../repo/src/server/session_service.rs), lines 999–1040. Creation idempotency protects a different operation, keyed by plugin/key/payload. It does not make every downstream coding effect exactly once. [session_service.rs](../repo/src/server/session_service.rs), lines 20–81. Wingman should correlate requests and reconcile task outcomes before retrying potentially completed work.

Scheduling has three separate meanings:

1. The two-second reconciler maintains desired worker state and stops idle workers. This is process supervision.
2. AoE records native `ScheduleWakeup` and `Monitor` signals. It displays countdowns and detects a fired wake's prompt for push notification. The tool or adapter supplies the schedule.
3. The featured index lists an external cron plugin. Its implementation is outside this checkout.

See [raw_input.rs](../repo/src/acp/acp_client/raw_input.rs), lines 1–83; [wakeups.rs](../repo/src/acp/event_store/wakeups.rs), lines 11–188; and [acp_events.rs](../repo/src/server/acp_events.rs), lines 173–229. These paths do not establish a general organization scheduler. Wingman still needs ProjectMaster to inspect the tracker, contact owners, resolve blockers, and escalate decisions.

### Interruption, failure, retry and recovery

Turn cancellation and whole-worker/session stop are different operations. Prompt submission and cancellation share the submission guard so a cancel cannot overtake the prompt it intends to stop; [prompt.rs](../repo/src/server/api/acp/prompt.rs), lines 1–5. Stopping a terminal session uses shared stop logic and updates persisted session state; [stop.rs](../repo/src/session/stop.rs), lines 5–35. Structured shutdown has lease/generation authority, pending spawn cancellation and stop fences. A still-unproven-dead runner blocks replacement rather than authorizing a duplicate; [supervisor/mod.rs](../repo/src/acp/supervisor/mod.rs), lines 67–106. The `Stopped` display value is not by itself proof that all previous process resources have been retired.

Crash recovery is bounded. In-memory supervisor restarts allow three respawns in 60 seconds with 500 ms backoff. The reconciler separately permits five resume decisions per 60 seconds before parking pending explicit retry. Attached workers have no cached launch configuration to respawn from and can hand recovery back to the reconciler. [supervisor/mod.rs](../repo/src/acp/supervisor/mod.rs), lines 42–47 and 142–160; [drain.rs](../repo/src/acp/supervisor/drain.rs), lines 910–962 and 1194–1255; [acp_reconciler/mod.rs](../repo/src/server/acp_reconciler/mod.rs), lines 28–82. Native recovery uses a machine-local cross-process recovery lock, supported-resume checks and orphan detection to avoid reopening a second copy; [recovery.rs](../repo/src/session/recovery.rs), lines 14–117.

Rate-limit recovery is another distinct, opt-in mechanism. It waits for reported reset plus grace or a minimum park floor; unknown resets back off from an hour, with at most five automatic redeliveries. The interrupted prompt can be reconstructed as the next turn, but a newly queued prompt can supersede that continuation. [rate_limit.rs](../repo/src/server/acp_reconciler/rate_limit.rs), lines 1–110 and 114 onward. This is useful for long unattended coding, but bounded transport/model recovery is not project-level replanning after failed acceptance tests.

### Completion, acceptance and retirement

A completed turn or Idle status means that the harness can accept more input. It does not prove the assigned product outcome. Completion callbacks send HTTP notifications for Idle, Waiting, and Error states. They use a 500 ms debounce, bounded concurrency, connection and total deadlines, and a process-local sequence number. See [callback.rs](../repo/src/server/callback.rs), lines 1–58. An external dispatcher can consume these notifications. It must reconcile durable state and tolerate missing, duplicate, or reordered callbacks. A callback is not a delivery transaction.

Fork is supported only where a harness and qualified parent conversation permit it. A terminal fork carries the parent's execution binding and a one-shot child seed. A structured fork invokes ACP fork semantics. Refusal distinguishes a missing parent from a recorded-but-unqualified/preallocated identity. [fork.rs](../repo/src/session/fork.rs), lines 7–81 and 106–166. Clear, compact and reset are capability-specific conversation operations. They do not terminate a durable organizational employee or transfer its obligations.

Archive and snooze change visibility and revival behavior. Idle dormancy suppresses automatic worker respawn. Trash stops processes but retains transcripts, worktrees, and container resources for restore. See [Instance](../repo/src/session/instance/mod.rs), lines 460–578. Managed worktrees can move to a holding path and return later. Expiry triggers purge. See [trash.rs](../repo/src/session/trash.rs), lines 327–443, 457–545, and 919–956. Permanent deletion controls branch, worktree, sandbox, and scratch cleanup. It checks lifecycle and generation authority. See [deletion.rs](../repo/src/session/deletion.rs), lines 20–87 and 123–166. Wingman's agent-retirement workflow must also reassign tickets, retain knowledge, and preserve accountability.

## Coordination mechanics and one traced request

The core coordination record is session metadata plus per-session events. Groups and parent IDs permit organization by execution context. Plugin topic events, metadata CAS and storage can support an external coordinator. None of these defines shared tickets, blocked-by dependencies, room participants, project decisions or agent obligations. The distinction is observable in the [host API dispatch](../repo/src/plugin/host_api.rs), lines 178 onward, and the [session message implementation](../repo/src/plugin/session_api.rs), lines 791–945: a message becomes input for one session, not a contribution to a shared room.

A concrete code path is a human sending “implement the API change” to an existing structured session while a previous turn is active. This is a source trace, not an executed request:

1. `acp_prompt` receives `POST /api/sessions/{id}/acp/prompt`, rejects read-only/unsupported requests and constructs `PromptSubmission`. [prompt.rs](../repo/src/server/api/acp/prompt.rs), lines 87–149. The caller already chose the session; no project intake occurs.
2. `submit_prompt` claims submission authority, touches/wakes eligible dormant work, validates attachments and reads any named queued row. It refuses changed/missing queue entries rather than silently delivering different content. It asks SessionService for the dispatch decision under the same guard. [prompt.rs](../repo/src/server/api/acp/prompt.rs), lines 193–274.
3. For a running nonsteerable turn, or cancellation/compaction, dispatch returns Queued with a reason. The API persists prompt metadata and stores attachment bytes through `buffer_and_enqueue`. A stable prompt ID prevents accidental duplication. A queued prompt is not yet a sent transcript event. [dispatch.rs](../repo/src/acp/dispatch.rs), lines 51–95; [prompt.rs](../repo/src/server/api/acp/prompt.rs), lines 275–320; [queue.rs](../repo/src/server/api/queue.rs), lines 137–228.
4. When a turn may run, SessionService's `send_turn` coordinates worker admission/resume and sends through the supervisor; queued prompts later use the shared drain. [session_service.rs](../repo/src/server/session_service.rs), lines 915–1038 and 1717–1868. Structured message, tool, plan and approval events are persisted and broadcast through the event store/supervisor path.
5. Tool permission or structured questions appear in the agent workspace. The human resolves the nonce/options for that worker. [StructuredView.tsx](../repo/web/src/components/acp/StructuredView.tsx), lines 339–354. This can unblock coding, but does not escalate through management rooms or ask ProductMaster to update product specifications.
6. At turn end, the next queued prompt can drain, status/notification state changes, and a configured callback can notify an external dispatcher. A later incremental conversation summary can recap the work. [callback.rs](../repo/src/server/callback.rs), lines 1–58; [conversation_summary.rs](../repo/src/session/conversation_summary.rs), lines 78–180. There is no core step that validates the definition of done or hands a completed ticket to TestMaster.

Plugins can automate more of this path. Session creation is guarded by declared capability, host approval classification, rate limits, trust, ownership and idempotency. `sessions.turn.send` applies plugin ownership; `sessions.message.send` deliberately reaches any startable session after the broader `session.message` grant. Its deadline bounds the caller's wait, not whether delivery may still complete. [session_api.rs](../repo/src/plugin/session_api.rs), lines 1–10, 39–95 and 791–915. This means a Wingman coordinator can be integrated, but must maintain its own message correlation, sender/recipient authorization, task semantics and retry reconciliation.

The daemon's MCP endpoint is much narrower than the plugin/HTTP control plane. Its inspected tools are session listing and `whoami`, with the latter returning `None` at this revision. [mcp.rs](../repo/src/server/mcp.rs), lines 37–95. Giving agents this endpoint does not by itself grant create/delegate/chat functionality.

## Major additional capabilities beyond Wingman's description

### Heterogeneous coding harnesses and an owned agent runtime

AoE normalizes many coding CLIs and ACP adapters, while Wingman explicitly starts from real Codex agents. It also ships the provider-backed AoE agent described above. The value is a common workspace and control surface across tools, models and execution styles. The integration consequence is capability negotiation: resume/fork/compaction/steering and permission modes are not universal, and a transcript fallback cannot promise exact native continuity. Wingman could retain Codex as its organizational standard while using AoE's adapter architecture as an execution seam. [AgentDef](../repo/src/agents.rs), lines 379–410; [ACP profiles](../repo/src/acp/agent_profiles.rs), lines 89–145; [AoE agent](../repo/acp-worker/aoe-agent/src/index.ts), lines 3–75.

### Owned branch, multi-repository and sandbox lifecycles

The workspace builder tracks owned resources and supports per-repository base choices. It can roll back newly provisioned resources. Trash and restore provide a reversible holding period before purge. These controls can reduce Wingman's concurrent-coding infrastructure work. Keep product knowledge and task identity outside disposable worker checkouts. Integration policy and shared context also need durable storage. See [builder.rs](../repo/src/session/builder.rs), lines 54–204; [trash.rs](../repo/src/session/trash.rs), lines 327–545; and [deletion.rs](../repo/src/session/deletion.rs), lines 20–87.

### A plugin automation platform with host-side limits

AoE supplies plugin workers, replayable topics, bounded plugin storage, metadata operations and UI contributions, plus capability-gated session creation and input. The automation policy limits creates, turns, messages and active plugin sessions, and distinguishes interactive, guarded and unattended modes. The inspected limits are 20 creates/hour, five active sessions, 120 turns/hour and 600 messages/hour per plugin. [host_api.rs](../repo/src/plugin/host_api.rs), lines 16–61 and 178 onward; [automation_policy.rs](../repo/src/plugin/automation_policy.rs), lines 17–32 and 102–179. This could host a Wingman integration, but default limits, capability boundaries and local storage sizes must be reconciled with a larger standing organization. They are execution guardrails, not task budgets or team policy.

The featured GitHub, cron and kanban plugins are meaningful adjacent products, but their manifests in [featured.toml](../repo/plugins/featured.toml), lines 1–19 and 28–49, are an index of externally fetched, hash-reviewed releases. Their scheduling, issue and board behavior was not verified here. The glossary's Board/Stage/Signal terminology in `CONTEXT.md` does not override that implementation boundary.

### Human summaries and background-work visibility

Conversation summaries use a fresh one-shot agent, incremental transcript deltas, a prior-summary budget and one process-wide concurrency slot. They trigger after sufficient new text or completed turns, and omit thinking, tool result bulk and synthesized resends. [conversation_summary.rs](../repo/src/session/conversation_summary.rs), lines 10–34 and 78–180. This supplies a useful human recap without pretending every raw event is an executive summary. Wingman could use it as evidence for briefings, while adding explicit task outcome/next-action fields and links.

AoE tracks native asynchronous subagents beyond the parent's turn. A transcript tailer reads host or container files and throttles previews. It marks a stall after 90 seconds. It stops tracking after five minutes without growth. A missing live transcript produces Error. A missing resumed transcript produces Detached. See [background_agent.rs](../repo/src/acp/background_agent.rs), lines 14–40 and 112–150. A supervisor must interpret and follow up on a stall. The signal alone does not recover the assigned product work.

### Remote development control and reproducible workspace provisioning

The browser/mobile client, remote daemon selection, tunnels and user-defined SSH agent commands make a remote development environment practical. CityHall bundles additionally describe sparse settings, reproducible repository remotes and per-user Git material for a hosted workspace. [cityhall_bundle.rs](../repo/src/session/cityhall_bundle.rs), lines 35–92 and 105–130. Wingman could use one AoE daemon per execution host and centralize organizational routing above them. The bundle is a provisioning document, not a federated scheduler or shared coordination record; CityHall's external service is outside this assessment. The [single-user daemon ADR](../repo/docs/adr/0002-single-user-daemon-multi-user-in-cityhall.md) is proposed, so future identity/authorization arrangements described there are not credited solely from the design text.

## Distinctive mechanisms and grounded innovation

These are concrete engineering mechanisms worth borrowing, without any claim of historical or industry-wide uniqueness.

**Conversation authority includes provenance and location.** An ID is qualified by agent/store/filesystem and whether it was actually observed, imported or asserted. Fork admission refuses to confuse preallocated or ambiguous IDs with proven parent conversations. This enables safer resume/fork across wrappers and containers, and suggests a sound base for Wingman's identity continuity. Its limit is that employee identity, assignments and cross-host shared records remain separate. [execution.rs](../repo/src/session/instance/execution.rs), lines 9–143; [fork.rs](../repo/src/session/fork.rs), lines 7–81.

**Execution survives presentation failure while destructive authority stays specific.** Tmux and detached ACP runners let work continue across UI or daemon loss. Leases, generations and process birth fingerprints prevent a stale controller from stopping or replacing the wrong incarnation, while teardown debt can block premature replacement. That combination is more useful than backgrounding a subprocess alone. For Wingman it reduces duplicated workers and misplaced cancellation during recovery. It does not decide whether a worker's business task succeeded. [runner.rs](../repo/src/acp/acp_client/runner.rs), lines 166 onward; [runner_lifecycle.rs](../repo/src/acp/runner_lifecycle.rs), lines 9–64 and 123–157; [supervisor/mod.rs](../repo/src/acp/supervisor/mod.rs), lines 67–106.

**Input arbitration is a server-domain operation.** All senders converge on session submission authority and a live-state decision among send, steer and queue. Persisted sender/attachment metadata and consume-after-acceptance semantics avoid losing or relabeling input when two clients or an automation race. This is directly relevant to Telegram plus dashboards steering one agent. Its boundary is routing: it safely sends to an already chosen session and does not choose the responsible product or role. [prompt.rs](../repo/src/server/api/acp/prompt.rs), lines 193–390; [dispatch.rs](../repo/src/acp/dispatch.rs), lines 51–95.

**Recovery and human comprehension use different summaries.** A context primer reconstructs bounded operational context when native load fails. The human conversation summary incrementally explains what happened. The former contains tools/plans with explicit truncation, while the latter filters noisy details and preserves open threads. This separation is useful for Wingman: a restart packet and an executive briefing serve different consumers. Neither should become the sole authoritative record of acceptance evidence. [context_primer.rs](../repo/src/acp/context_primer.rs), lines 1–87; [conversation_summary.rs](../repo/src/session/conversation_summary.rs), lines 78–180.

**Automation reuses execution invariants instead of bypassing them.** Plugin session RPCs pass through SessionService while the host applies capability grants, approval classification, limits and idempotency. That allows an organizational controller to automate the same operations the UI uses. The tradeoff is intentional constraint: broad cross-session messaging is a special grant, turns have ownership rules, and plugin storage/throughput are bounded. Wingman would need an explicit integration design rather than assuming plugins have unrestricted agent authority. [session_api.rs](../repo/src/plugin/session_api.rs), lines 1–10 and 39–135; [automation_policy.rs](../repo/src/plugin/automation_policy.rs), lines 17–32 and 102–179.

## Practical fit and remaining work

Use directly:

- Local session catalog and lifecycle controls.
- Real Codex CLI/ACP execution.
- Worktree/container provisioning.
- Terminal and structured per-session views.
- Prompt arbitration/queueing.
- Approval/elicitation UI.
- Durable conversation/event storage.
- Native resume/fork handling.
- Bounded crash and rate-limit recovery.
- Callback and plugin integration surfaces.

These mechanisms map most strongly to F14, F16, F20, and F21. Validate runtime suitability with the actual Codex toolchain and both hosts.

Adapt:

- Introduce a durable organizational agent ID above AoE session IDs.
- Map roles and projects to profile/instruction/skill configurations.
- Connect each task to an exact session and host.
- Use one daemon's API per host.
- Reconcile callbacks with durable state.
- Normalize adapter-specific controls.
- Expose role-aware summaries using actual tickets and verification evidence.

A coordinator plugin is possible. Its five-active-session limit requires capacity planning. Define plugin trust and ownership explicitly. Keep the shared tracker and rooms independent of disposable sandbox files and transient callbacks.

Build:

- Butler's Telegram ingress and correlated questions/answers.
- Portfolio intake/project registry semantics.
- ProjectMaster/ProductMaster/TechMaster responsibilities and team composition.
- Proportionate discovery and product specifications.
- A shared ticket and dependency model.
- Agent rooms and escalation.
- Durable DIRECTIVES consultation.
- Cross-host assignment and shared coordination.
- Proactive product/blocker supervision.
- Executive current/recent/next/blocker records and linked timelines.
- Integrated testing, acceptance, and delivery gates.

Role names can improve session presentation. They do not implement the required responsibilities.

The best architectural role is therefore an execution workbench underneath Wingman's organization, with clear boundaries between worker state and product state. Replacing the entire organization with AoE would move most of the coordination requirements into prompts, filesystem conventions and external plugins whose behavior is not established by this checkout.

## Verification scope and uncertainty

This was a fresh static source review. Git was queried for the commit. The full assessment guide and Wingman purpose, checkout root `AGENTS.md`, and `web/AGENTS.md` were read. No dependencies were installed, no build/test suite or agent was run, no service/browser was launched, and no alternative source was modified. Runtime behavior above is inferred from implementation and regression-test source, not described as exercised.

The implementation review covered these areas:

- CLI entry, agent definitions, configuration, and profiles.
- Instance identity, execution binding, resource builder, and shared spawn path.
- JSON storage and project registration.
- ACP supervisor, runner, leases, and reconciler.
- Prompt dispatch, queue, SessionService, event storage, and wakeups.
- Permissions, conversation summaries, context primers, and background transcripts.
- Fork, recovery, stop, deletion, trash, callbacks, and lifecycle feeds.
- MCP endpoint, plugin APIs, automation policy, and featured plugin index.
- CityHall bundles, skills, project MCP configuration, and web session views.

The local links and line ranges support the findings.

Regression tests read as evidence of intended invariants, **not executed validation**:

- [dispatch.rs](../repo/src/acp/dispatch.rs), L126–223: send/steer/queue decision cases, cancellation/compaction ordering and solo-command handling.
- [supervisor/drain.rs](../repo/src/acp/supervisor/drain.rs), L1194–1255: restart budget, deliberate-stop distinction and attached-worker recovery handoff.
- [event_store/wakeups.rs](../repo/src/acp/event_store/wakeups.rs), L199–250: latest schedule selection and once-claimed fired wakeups.
- [permissions.rs](../repo/src/acp/permissions.rs), L38–81: destructive classification, option preservation and fresh approval nonce.
- [stop.rs](../repo/src/session/stop.rs), L38–77: persistent stop for a session without tmux/sandbox resources.
- [session_spawn.rs](../repo/src/server/session_spawn.rs), L1018–1103 and L1170–1274: failed launch hook rollback and immediate purge while an ACP handshake is outstanding.
- [tests/e2e/acp_live_e2e.rs](../repo/tests/e2e/acp_live_e2e.rs), L1–120: full daemon/TUI tool rendering and approval interaction against a **fake ACP agent**. These tests establish the intended integration boundary, not real-provider reliability.

Negative-feature searches covered `src/session`, `src/server`, `src/daemon`, `src/plugin`, and `acp-worker/aoe-agent/src`. They also covered web components and plugin indexes. Terms included Telegram, Butler, leadership, tickets, assignees, dependencies, rooms, acceptance, hosts, federation, and scheduling.

The review traced apparent matches to their actual scope:

- The project registry stores repository metadata.
- Authentication tickets are scoped page-access credentials.
- Wakeups and monitors are native agent signals.
- Parent IDs and background transcripts link sessions and subagents.
- Remote flags and tunnels provide daemon access.
- Custom SSH commands permit remote launch.

These paths did not establish the missing core Wingman workflows or a shared organization model.

Uncertainty remains around external GitHub/cron/kanban plugins, CityHall services, third-party adapter behavior, actual provider/model availability, and successful operation on the user's machines. Their source/services were not fetched or exercised. This assessment therefore credits the inspected integration contracts and explicitly withholds claims about those external implementations.
