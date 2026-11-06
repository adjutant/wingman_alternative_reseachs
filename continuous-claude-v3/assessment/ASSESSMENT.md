# Continuous Claude v3 assessment

Assessment date: 2026-11-05. Product: Continuous Claude v3, a Claude Code workflow, hook, agent-profile and memory kit. Upstream: https://github.com/parcadei/Continuous-Claude-v3 . Local checkout: `researchs/continuous-claude-v3/repo`. Assessed commit: `d07ff4b06b62f43771bc0c927d0211b734d6149e`.

**Verdict:** useful material for Wingman's execution and continuity layer, with unusually substantial discovery instructions and context-management hooks. It does not implement Wingman's standing development organization. Its center of gravity is a human's Claude Code session, delegating bounded work and carrying context between sessions. Telegram intake, project leadership identities, a portfolio registry, organizational chat, the connected dashboards and multi-host agent placement would still need to be built. Several advanced coordination paths reference implementation absent from this checkout, so the architecture documentation substantially overstates what can be established locally.

This is a source assessment, not a runtime certification. No dependencies were installed, no services or agents were launched, and checkout files were not changed. All source citations below are relative to this report; stated line numbers refer to the assessed revision. The comparison target is [WINGMAN_PURPOSE.md](../../WINGMAN_PURPOSE.md), following [ASSESSMENT_GUIDE.md](../../generic/assessments/ASSESSMENT_GUIDE.md).

## Architecture and actual execution model

Claude Code and [.claude/settings.json][settings], lines 1–275, provide the entry point. Configuration registers a status command and hooks for session start, prompts, tools, compaction, stop, and session end. Most commands target the user's global `~/.claude` installation. This checkout therefore provides configuration and supporting code for an external harness. It does not supply its own durable-agent server.

[hook_launcher.py][launcher], lines 99–118 and 234–261, resolves project and global hook files. It prefers compiled JavaScript, then TypeScript, then Python. TypeScript inspection establishes source behavior. It does not prove that an installed compiled hook matches that source.

Agent execution has two paths. Markdown files define Claude Code roles. [maestro.md][maestro], lines 1–10, declares a model and tools and directs orchestration through the host's `Task` tool. [kraken.md][kraken], lines 1–12 and 57–89, defines implementation and TDD behavior. The external harness consumes those prompts.

[claude_spawn.py][spawn], lines 653–753, separately starts a local `claude -p` process. It assigns a UUID session ID, redirects output to `/tmp/claude-agents/<uuid>.json`, and passes hierarchy environment variables. It returns the PID. This is independent temporary task execution. It does not create an enduring employee with a mailbox and project appointment.

The Python subprocess path reads JSON profiles, not the Markdown definitions. [Profile loading][spawn], lines 276–328, searches the project, current directory and two user locations. [kraken.json][kraken-json], lines 1–10, has a compact TDD prompt and a different tool declaration from the much longer Markdown profile. A caller must deliberately choose the path and profile. `route_to_agent()` provides an ordered keyword classifier at [claude_spawn.py][spawn], lines 334–415, but `spawn_agent()` does not call it: it loads the explicit `perspective` argument. Searches found no active dispatcher calling that classifier. The checked-in `DISABLED-task-router-hook.json` is another reason not to infer transparent automatic delegation from the routing table.

Persistence is spread across several mechanisms, with different ownership and lifetimes:

* Project Markdown/YAML under `thoughts/shared/{specs,plans,research,handoffs}` and legacy `thoughts/ledgers` stores specifications, phase records and continuation context. [Build instructions][build], lines 281–321, describe writing an orchestration file; [pre-compact-continuity.ts][precompact], lines 17–94, implements transcript-derived handoffs when the required legacy ledger exists.
* A SQLite artifact index has handoffs, plans, continuity snapshots, queries and FTS5 indexes, including outcome annotations and trace IDs. See [artifact_schema.sql][artifact-schema], lines 13–125. It is a search and learning index, not a ticket registry or agent directory.
* PostgreSQL code implements core and archival memory, text/vector/hybrid retrieval and optional session/agent scoping. See [memory_service_pg.py][memory-pg], lines 74–142, 306–379 and 655–856. Hook helpers also implement session registration and advisory file claims directly with inline SQL in [db-utils-pg.ts][db], lines 390–445 and 532–575.
* Broader agent registration, blackboard and agent completion wrappers import `scripts.agentica_patterns.coordination_pg`. That package is absent locally. [claude_spawn.py][spawn], lines 787–829, catches that failure and appends a temporary registry record instead. The registration and file-claim SQL above does **not** depend on the missing package. Those narrower implementations should still receive credit.

Pattern modules implement swarm, pipeline, jury, hierarchy, and related functions. Active integration requires more than source presence. The [active settings][settings], lines 6–275, register neither `SubagentStart`, `SubagentStop`, nor a pattern dispatcher. [pipeline.ts][pipeline], lines 110–164 and 220–351, can start a detached next stage. It requires the correct environment/configuration and an existing SQLite database. This does not establish automatic scheduling in an ordinary installed `/build`. Its SQLite coordination also differs from the PostgreSQL wrappers.

The optional OPC runtime provides separate Python tool execution. [runtime.harness][harness], lines 133–180, initializes an MCP manager and executes scripts. [mcp_client.py][mcp], lines 421–556 and 598–703, supports local stdio and remote SSE/HTTP tools. Connections are lazy and retries are bounded. Remote tools do not establish remote coding-agent hosting.

## F01–F24 comparison

“Similar” credits substantial implemented or harness-consumable behavior while preserving its scope. Prompt workflows are explicitly identified; their successful model execution was not tested. “Absent” reflects the implementation searches described in the verification section, rather than a missing README claim.

| ID | Capability | Verdict | Evidence and concrete difference from Wingman |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | [Spawner][spawn], lines 653–753, starts separate Claude processes with UUIDs/PIDs; [Kraken][kraken], lines 1–12, supplies coding specialization. Multiple instances are possible. Instances are bounded executions and host subagents, without Wingman's persistent specialist appointments and independently maintained organizational conversations. |
| F02 | Extensible profiles, roles and team composition | **Similar** | [Profile loader][spawn], lines 276–328, accepts new JSON profiles; `spawn_lead()` passes loaded worker definitions through `--agents` at lines 580–650 and 877–969. Markdown profiles also extend the host catalog. There is no team registry, durable project membership model or automatic propagation into organizational views. |
| F03 | Agent directory and visible working relationships | **Resembles** | [Spawn environment and registry][spawn], lines 549–577 and 811–829, record parent, session, perspective and depth. [Session start][register], lines 43–68, prints active peer IDs. These are machine records and injected text, with no browsable directory showing teams, current assignments and persistent relationships. |
| F04 | Telegram and Butler routing | **Absent** | [Active hooks][settings], lines 1–275, are Claude Code event entry points; [harness][harness], lines 29–40, is a local CLI entry. Searches across application/runtime, hooks, profiles, skills and setup found no Telegram bot/client, update receiver, chat-to-project mapping or Butler service. |
| F05 | Cross-project registry, intake and new/existing routing | **Resembles** | [Session SQL][db], lines 390–445 and 453–518, records project directory strings and can filter sessions by project. [Build][build], lines 62–79, asks whether the code is new or existing. Neither is a durable portfolio registry or intake resolver that identifies the human's referenced product and creates its team. |
| F06 | Per-project product and technical leadership | **Resembles** | [Discovery interview][discovery], lines 8–21, acts as product discovery; [Maestro][maestro], lines 37–110, coordinates architecture/implementation/validation. They are invoked roles for a task, without durable ProductMaster/TechMaster pairs assigned to each product and available between worker turns. |
| F07 | Proportionate research, discovery and iterative clarification | **Similar** | [Build][build], lines 96–113, can skip discovery for clear requirements; [discovery][discovery], lines 23–53 and 131–178, has staged interviews, research loops and conflict resolution through `AskUserQuestion`. Strong reusable workflow, but conversation runs directly in Claude Code and is model-directed, without Butler routing, parallel pending-question records or an organizational discovery service. |
| F08 | Scope, specifications, acceptance scenarios and definition of done | **Similar** | [Discovery spec template][discovery], lines 187–294, defines success metrics, requirements with acceptance criteria, journey, out-of-scope work and research. [Atlas][atlas], lines 19–35, consumes explicit scenarios. These are useful documents/prompts. There is no enforced product-level definition-of-done entity aggregating all work and accepted delivery. |
| F09 | Decomposition, assignment and shared task tracking | **Resembles** | [Build][build], lines 264–321, instructs phase and pending-status storage in YAML. [implement_plan][implement], lines 32–39 and 90–112, updates plan checkboxes and todos. [observe_agents.py][observe], lines 121–154, reads a tasks table when present. Searches found no complete task-graph producer/service. These paths do not establish a cross-project tracker with durable assignees, comments, dependencies, and blockers. |
| F10 | Portfolio/project management dashboard | **Absent** | [Observer][observe], lines 195–208, collects data for CLI output; [status.py][status], lines 274–346, extracts a workflow checkpoint. Searches found no portfolio UI, project API, dashboard routes or task-management application. A token-statistics skill and textual summaries do not meet this capability. |
| F11 | Agent chat, rooms and direct collaboration | **Resembles** | [Broadcast hook][broadcast], lines 26–117, reads up to ten messages from a local SQLite swarm DB and injects them before tools. [Agent system prompt][system-prompt], lines 52–90, instructs PostgreSQL blackboard reads/writes through the absent coordination module. These are partial shared-state primitives; no room/chat app, persistent participants, threaded discussion or human-readable organizational chat interface was found. |
| F12 | Management escalation and human decisions/approvals | **Similar** | [Build][build], lines 409–419 and 520–582, specifies approve/change/abort, retry/skip and human phase checkpoints; [implement_plan][implement], lines 78–112, asks for mismatch decisions and manual verification. The substantial equivalent is local human decision gating. There is no worker → project leadership → management room → Butler routing or durable question ownership. |
| F13 | Durable project knowledge and reusable directives | **Similar** | [Artifact schema][artifact-schema], lines 13–125, indexes plans, handoffs, decisions and outcomes; [continuity loader][continuity], lines 323–428 and 433–540, restores project handoff/ledger content. Skills/rules supply reusable instructions. Organization is `thoughts/` plus `.claude`, rather than Wingman's `DIRECTIVES/{SCOPES,SPECS,HARNESS}`, and knowledge governance remains file/model-driven. |
| F14 | Identity, conversation and work continuity | **Similar** | [Spawner][spawn], lines 521–530 and 549–571, uses Claude session UUIDs and parent/session environment; [continuity][continuity], lines 323–428, restores work context. [Kraken][kraken], lines 14–33, instructs checkpoint resume. Durable context is substantial, but employment identity, host conversation and coordination identity are separate concepts with isolation caveats detailed below. |
| F15 | Proactive supervision and periodic blocker follow-up | **Resembles** | [Process monitor][spawn], lines 104–189, periodically checks local PID liveness; [StreamMonitor][stream], lines 54–113, tracks stuck state and callbacks. These monitor process/output health, not the portfolio and responsible leaders. No standing ProjectMaster wake scheduler, blocker outreach or escalation cycle was found. StreamMonitor is also not wired to the shown JSON-file spawning path. |
| F16 | Parallel products and concurrent specialists | **Similar** | [Spawner][spawn], lines 653–753 and 877–969, supports concurrent local executions; project-scoped [session SQL][db], lines 453–518, distinguishes directories. Separate human-started Claude sessions can work in separate products. There is no organization layer owning parallel product teams, priorities or integration boundaries; concurrency limits are process-local. |
| F17 | Real multi-host execution with shared coordination | **Absent** | [Popen execution][spawn], lines 724–729 and 940–945, is local and inherits the caller's working directory. [MCP transports][mcp], lines 421–556, connect tools remotely, not coding worker hosts. Searches found no host inventory, remote agent launcher, SSH worker routing, placement or shared cross-host workspace protocol. PostgreSQL connectivity alone does not supply these. |
| F18 | Executive overview of current/recent/next work and blockers | **Resembles** | [Status implementation][status], lines 246–346 and 349–370, renders goal/now from the latest workflow handoff; [observer][observe], lines 157–208, lists output files and other raw state. Neither produces one grounded briefing per durable agent, nor a portfolio overview with current, just-finished, next and attention-needed fields. |
| F19 | Per-agent summary timeline linked to underlying work | **Resembles** | [Artifact schema][artifact-schema], lines 20–40 and 61–79, stores task summaries, timestamps, trace IDs and continuity snapshots. [Stream events][stream], lines 34–50, carry raw activity timestamps. Those are potential inputs to a timeline, not an implemented per-agent summary feed with navigable task/conversation/artifact links. |
| F20 | Detailed individual coding workspace | **Resembles** | The parent runs in external Claude Code; [spawned runs][spawn], lines 690–729, expose an output file/PID, and [observer][observe], lines 157–192, lists Markdown outputs. No repository-owned agent workspace UI or summary-to-live-session drill-down is implemented. Native Claude Code capabilities cannot be credited as this project's integrated interface. |
| F21 | Live activity, lifecycle controls, steering and execution visibility | **Resembles** | [StreamMonitor][stream], lines 69–162, can consume streaming output and invoke callbacks; [status][status], lines 101–162, records session/context usage. But [spawn][spawn], lines 521–530 and 720–729, emits final JSON to a file, with no StreamMonitor connection, queued steering or complete stop/resume/fork/rename/archive API. Interactive controls depend on the external host. |
| F22 | Testing, integrated verification and acceptance/delivery | **Similar** | [Kraken][kraken], lines 57–89, instructs TDD; [Atlas][atlas], lines 10–17 and 38–100, instructs E2E/browser testing; [implement_plan][implement], lines 90–112, separates automated success from human-confirmed manual checks. [Build completion][build], lines 549–580, assembles artifacts. These are strong coding workflows, but no standing TestMaster or enforced product acceptance/stop-after-accepted-delivery controller exists. |
| F23 | Autonomous operation with human direction through organization | **Similar** | [Lead spawner][spawn], lines 877–969, gives a headless Claude workers and a task; [build][build], lines 308–321 and 570–592, chains work, checkpoints and continuation. Useful bounded autonomy exists, driven by a session and prompts. Persistent organizational self-supervision, organization-mediated human direction and multi-project lifecycle ownership are missing. |
| F24 | New profiles accommodated by chat, tracker and dashboards | **Resembles** | [Profile loader][spawn], lines 290–328, and generic [observer outputs][observe], lines 157–192, can handle new names. No equivalent chat/tracker/dashboard surfaces exist into which those roles are enrolled. Profile extensibility alone does not implement Wingman's connected extensible views. |

## Agent definition and complete lifecycle

### Definition, creation and identity

An agent profile is a role template, not a durable agent instance. Markdown frontmatter names the role, model and host tools; its body supplies instructions. JSON profiles for subprocess spawning additionally parse `permissions`, `blocked_patterns` and `inherit_blocks`. The [JSON loader][spawn], lines 276–328, only constructs configuration. The subprocess builder uses prompt, model, tools and the skip/queue choice. A search of the spawner found no enforcement of the parsed blocked-pattern or inheritance fields. This is a meaningful gap if treating those fields as a policy boundary.

Creation occurs through the external `Task` tool described by profiles/skills or by explicitly calling Python `spawn_agent()`/`spawn_lead()`. The latter assigns a fresh UUID unless a caller supplies one. `AGENT_ID` identifies this execution, `PARENT_AGENT_ID` its spawning relation, and `SESSION_ID` an inherited grouping that defaults to `default`. `PATTERN_TYPE` is optional. [Environment construction][spawn], lines 549–577, does not establish an employee identity, a product appointment or a persisted mailbox. `spawn_lead()` embeds selected JSON worker definitions using Claude's `--agents` flag, while its returned premise is simply `lead` ([lines 919–969][spawn]).

There is also a distinct coordination session identifier. [session-id.ts][session-id], lines 44–110, generates a short ID from a Braintrust span or timestamp and stores it in one user-global `~/.claude/.coordination-session-id` file. [Session registration][register], lines 33–44, sets an environment variable only in the hook process and writes that file. Later hook processes can therefore read the most recently written global ID unless a parent environment already supplied `COORDINATION_SESSION_ID`. Two terminals can overwrite that file. This is a source-visible isolation risk, not a reproduced runtime failure. The checked-in persistence tests actually assert overwriting behavior at [session-id-persistence.test.ts][identity-test], lines 107–112. Wingman should use canonical execution/session IDs throughout, with explicit project and host keys.

### Execution, tools and permissions

[Command construction][spawn], lines 488–546, runs `claude -p`, caps it at 100 turns and requests final JSON output. It injects persona text into the task. The optional system-context path deserves integration review: lines 543–544 pass a filesystem path string as the `--append-system-prompt` argument without reading that file. This code does not itself establish that the intended system-prompt contents are loaded. Model/tool declarations are forwarded to Claude. The project does not implement the model loop or tool authorization itself. By default it adds `--dangerously-skip-permissions`. A profile with `permissions: queue` merely suppresses that flag, delegating any approval behavior to Claude. No approval queue service is implemented here. Lead spawning always adds the skip-permissions flag ([lines 626–648][spawn]). These defaults would require deliberate integration with Wingman's human decisions and host execution policies.

Subprocesses inherit the calling environment and working directory. There is no per-task worktree creation, sandbox assignment or remote host placement in this path. Filesystem isolation is a coordination responsibility. [file-claims.ts][claims], lines 49–67, warns on an existing claim and allows the edit. It does not lock the file. Settings apply that hook to `Edit`, not `Write` or arbitrary Bash mutations. The check and claim are separate calls, and claims have no age filter in the inspected lookup. They should not be treated as serializable exclusive ownership.

The repository also has a separate Docker math-code sandbox runner ([sandbox_runner.py][sandbox], lines 1–42 and 77–150) with CPU/RAM limits, a timeout and reduced builtins. That does not sandbox the headless coding agent. Its existence should not be used to imply that skipped-permission coding runs execute inside containers.

### Routing and concurrency

Routing is distributed between keyword-triggered skill suggestions, model interpretation of workflow instructions, the optional routing function and explicit profile selection. The prompt hook [skill-activation-prompt.ts][activation], lines 53–79 and 87–130, reads rules and optionally invokes Python pattern inference. The inference file it checks for is absent here, so this branch returns no inference rather than proving autonomous pattern selection. The plain skill-matching machinery still exists; advanced pattern claims need separate evidence.

The Python spawner enforces depth below three at [lines 423–433][spawn], and a soft count of 50/hard count of 100 through [lines 26–34 and 436–453][spawn]. These are limits in a particular Python interpreter's global counter, not a distributed or even machine-wide quota. Checking the count and incrementing after `Popen` are separate operations, so concurrent callers could race. `resources_available()` samples CPU/RAM at [lines 382–395][spawn], but the shown `spawn_agent()` and `spawn_lead()` do not call it. A comment about resource-aware spawning therefore cannot establish actual admission control. Environment depth is also a convention propagated to child processes, not a security isolation boundary across all native `Task` executions.

### Persistence, resume and scheduling

The durable unit of continuity is mostly the work artifact. [Kraken's resume instructions][kraken], lines 14–33, direct a new/resumed agent to the last validated checkpoint. [implement_plan][implement], lines 124–130 onward, describes using a host agent ID for clarification. [Build][build], lines 584–592, instructs a resumed invocation to load `orchestration.yaml` and continue its incomplete phase. These are valuable protocols, but the Python spawner has no `--resume`/`--continue` operation and always normally creates a new session UUID. Reusing an ID is not an implemented conversation-resume controller.

Compaction continuity uses executable hooks. [pre-compact-continuity.ts][precompact], lines 21–63, finds a legacy ledger and creates a transcript-derived YAML handoff during automatic compaction. It directly reads the ledger directory. A missing directory therefore differs from an empty ledger list. Its final catch reports the error.

[session-start-continuity.ts][continuity], lines 323–428, first scans handoffs and loads embedded ledger/YAML content. Lines 433–540 provide legacy fallback. UUID-specific helpers exist at lines 16–85. The main handoff-first scan instead calls legacy session-name lookup. It selects the newest qualifying record across directories. UUID-helper tests alone cannot prove isolation in that main path.

Scheduling is session/event based. Hooks run when Claude triggers an event. A caller or model must begin the next work invocation. A conditional pipeline handler can advance a stage, and an in-process thread monitors PIDs. No long-lived organization scheduler starts idle project leaders, revisits unanswered product questions or periodically supervises multiple products.

The configured [auto-handoff-stop.py](../repo/.claude/hooks/auto-handoff-stop.py), lines 18–68, reads a context-percentage file written by the status command and blocks a first stop at 85% or higher with a request to run `/create_handoff`. Despite its name, that stop hook does not write the handoff itself. It relies on the model following the instruction. Missing percentage data and recursive stop-hook invocations are allowed through.

### Interruption, cancellation, failures and recovery

The native coding host owns interactive interruption. The spawner returns a PID, but exposes no corresponding managed cancel, task rollback, process-tree teardown or durable paused state. Its monitor is a daemon thread started on module import ([claude_spawn.py][spawn], lines 217–222), so a short-lived `python -c` caller can exit while the spawned agent continues. That loses the interpreter-local concurrency counter and completion monitor. The [agent system prompt][system-prompt], lines 21–30, itself suggests that short-lived invocation pattern. Wingman would need a persistent supervisor to own process handles and reconcile outcomes after restarts.

The monitor checks `os.kill(pid, 0)` once a second and, when the PID disappears, attempts to read JSON and write status/result summary ([lines 142–214][spawn]). It defaults to `completed` if the output file is absent and only classifies selected error subtypes as failed. It does not inspect an owned `Popen.returncode` or retry failed agent work. Its database update also uses a fixed development database target, unlike the environment-configurable hooks. This makes status consistency an integration concern. Registration falls back to append-only temporary JSONL, with no matching update of that fallback's `running` record in the monitor. A fallback registry is therefore an observation aid, not a reliable authoritative lifecycle ledger.

Workflow-level failure handling is more thoughtful but instructional: [build][build], lines 520–547, says to mark a blocked phase and present retry/skip/abort/manual-intervention options. [implement_plan][implement], lines 78–88, asks the human about mismatches. The MCP client separately retries tool-call exceptions ([mcp_client.py][mcp], lines 598–703), but tool retry is not agent/task recovery and could need idempotency controls for mutating calls. The harness has signal cleanup for its own execution ([harness.py][harness], lines 177 onward). It does not manage the independent coding-agent fleet.

### Completion, acceptance and retirement

Process completion, model-declared task completion and human acceptance are distinct. A JSON result or vanished PID is only execution termination. [Build][build], lines 549–580, asks the model to assemble specs, plans, validation, implementation handoffs and optional PR/commit details. [implement_plan][implement], lines 90–112, explicitly forbids marking manual checks complete before the human confirms them. This is a useful acceptance distinction, but there is no project-level transition that checks every ticket against an agreed product definition of done and retires the active team after accepted delivery.

[Session-end cleanup][cleanup], lines 68–120, updates the latest legacy ledger timestamp and removes an old `latest-output.md` from per-agent cache directories after seven days. Lines 123 onward optionally launch a Braintrust learning extractor with a user-global lock. The inspected hook does not deregister sessions, release file claims or kill spawned agents. The PID registry/output files under `/tmp/claude-agents` also have no corresponding retirement sweep in this spawner. An external harness may clean its own sessions, but that behavior is outside this checkout's demonstrated lifecycle.

## Coordination mechanics and concrete task traces

The closest coordination model is **orchestrator plus artifacts**. The main Claude session supplies tasks; specialists return files. The main session reads and synthesizes them. [Maestro][maestro], lines 88–117, explicitly follows that pattern. Skills can add a plan and human checkpoints, while file-claim hooks warn about concurrent editing. There is no durable organizational room where leadership and specialists retain membership, no common ticket lifecycle, and no implemented Butler to preserve question ownership across the human's conversations.

Blackboard code is mixed. The active pre-tool broadcast hook reads a project-local SQLite database when `SWARM_ID` is present ([broadcast][broadcast], lines 26–117). It repeatedly reads the latest ten messages from other senders; no unread cursor or acknowledgement is implemented in this hook. The PostgreSQL helper's blackboard API would read unread messages ([db-utils-pg.ts][db], lines 104–151), but depends on the absent `CoordinationDBPg` implementation. These are different paths, not one proven end-to-end chat system.

### Coding request: `/build greenfield Add user authentication with OAuth`

This concrete request is present in the repository's own [build example][build], lines 596–649. The following traces its actual configured/prompt implementation, not an executed historical run:

1. The user enters the request in Claude Code. `UserPromptSubmit` runs skill activation, memory awareness and other hooks ([settings][settings], lines 135–162). Skill activation can suggest relevant instructions. The host/model invokes the build skill. There is no Telegram update or project-registry lookup.
2. [Build's chain definition][build], lines 264–305, selects discovery → planning → plan validation → implementation → optional commit/PR and instructs creation of `thoughts/shared/handoffs/<session>/orchestration.yaml` with phase status. It is Markdown pseudocode/instructions, not a Python state-machine implementation.
3. [Discovery instructions][discovery], lines 23–53, 131–178 and 220–294, ask questions, research uncertain choices, confirm the understanding and write a spec with success/acceptance criteria. Answers remain in the host conversation and generated files. No cross-project pending-question router exists.
4. [Build][build], lines 387–419, passes the spec/research into a planning `Task`, records the plan path and asks for approval/change/abort. `Task` execution belongs to Claude Code. Separately, invoking `spawn_lead()` would use actual `Popen`, loaded workers and the environment/registry path described above. These are alternative entry paths, not a proven single automatic chain.
5. During implementation, [settings][settings], lines 46–79 and 164–225, can inject code/architecture context, check an `Edit` claim and run diagnostics. A conflict produces a warning, so two workers can still edit the same file. [implement_plan][implement], lines 90–112, tells the implementer to run checks, fix failures and await manual verification.
6. [Build][build], lines 520–592, instructs error recording, human retry decisions, artifact reporting and later continuation from YAML. Completion returns to the direct human session. It does not update a portfolio dashboard or notify Butler.

### Executable pipeline task: `async error handling python`

A narrower Python pipeline has explicit test configuration. [test_research_pipeline.py][pipeline-test], lines 38–44, supplies the topic. [research_implement_pipeline.py][research-pipeline], lines 95–115 and 501–530 onward, parses it and creates `PipelineContext`. It obtains the MCP manager and sequentially runs research, AST search, Morph search, quality checks, and Git status.

[Nia research][research-pipeline], lines 144–189, saves tool results. AST search uses a heuristic pattern (lines 192–226). [Morph][research-pipeline], lines 280–335, collects search matches. Steps return success, skipped, or failed and retain context/error lists. An unavailable configured tool can therefore produce an explicit skip.

The important boundary appears at [lines 402–436][research-pipeline]: despite the introductory “stage changes” language, the Git step only checks status and explicitly leaves `staged_files` empty. Likewise, the Morph step searches. It does not apply an implementation patch. This trace demonstrates functioning orchestration code structure and graceful degradation, not an autonomous research-to-delivery engine. The source test harness was inspected but not executed, and no external tool result or quality outcome is claimed.

## Major additional capabilities and integration consequences

**Intent-sensitive code context and token management.** The [TLDR read hook][tldr-read], lines 120–148 and 151–356, chooses structure, entry-point context or flow analysis based on the search context. It asks an external daemon for AST/call graph/CFG/DFG/PDG information. At lines 388–428 it permits explicitly bounded reads and falls back to normal reading when analysis is unavailable. [Task context injection][tldr-task], lines 50–121, recognizes data-flow, slicing, complexity and debugging intents. [daemon-client.ts][daemon], lines 20–103, resolves project paths, creates project-hashed lock/PID files, detects existing processes and bounds query time. This could reduce worker context consumption and improve targeted code understanding. The parser/indexer implementation is external; claimed savings/latency percentages in comments were not benchmarked. Porting to Codex requires adapting host events and tool input/output formats, with careful escape hatches so compressed structure does not hide necessary implementation detail.

**Searchable experience with explicit outcome labels.** [Artifact schema][artifact-schema], lines 20–40 and 81–125, distinguishes what worked, what failed, decisions, outcome confidence and query feedback, and links handoffs to traces. [PostgreSQL memory][memory-pg], lines 655–856, supports both weighted text/vector search and reciprocal-rank fusion. [memory-awareness.ts][memory-hook], lines 108–128, actually uses a fast text-only recall subprocess for automatic hints, despite its header's broader semantic-search description. The richer semantic interface is a separate capability. Wingman could reuse outcome-aware retrieval across projects, but must define sharing boundaries: memories scoped to session/agent are not automatically organization-wide institutional knowledge, and automatically extracted model judgments need provenance and confidence.

**Trace-derived learning and evaluation.** [braintrust_analyze.py][braintrust], lines 983–1052, evaluates plans against succeeded/failed precedent, and lines 1120–1475 implement learning extraction from session traces into cached files. [Session-end cleanup][cleanup], lines 123 onward, starts extraction only when Braintrust is configured and guards against duplicate extractors with a PID/timestamp lock. This extends beyond simple task tracking into improvement of later decisions. Integration would require an optional external tracing backend and LLM judge, explicit cost control, and stable mapping from traces to Wingman agents/tasks. Generated learnings and judge scores are evidence to review, not acceptance verdicts.

**Formal proof and numerical/symbolic tools.** [compiler-in-the-loop.ts][compiler], lines 71–109, invokes Lean/Lake and records errors/incomplete proofs; lines 129–150 check a local model endpoint for tactic assistance. The [stop hook][compiler-stop], lines 65–135, can ask Claude to repair unresolved errors while guarding recursive stop hooks and stale state. The repository also includes mathematical computation scripts and a restricted execution runner ([sandbox][sandbox], lines 33–42 and 77 onward). These could support verification-heavy products or specialist research. They bring separate toolchains and optional local-model infrastructure, and Lean proof correctness is not equivalent to whole-product acceptance. No proofs or compilers were run during this assessment.

**A library of coordination patterns.** [pipeline.ts][pipeline], lines 110–164 and 220–351, contains detached stage continuation and artifact passing; other source modules cover jury, generator/critic, adversarial and hierarchy. This is richer than Wingman's initially specified room/team structure and could provide reusable task execution strategies. Integration would first need to make dispatch explicit, reconcile SQLite/PostgreSQL state, enforce idempotent stage launch and define failure/acceptance criteria. The pipeline handler marks a stopped stage completed before considering any product-verification result, so its completion event is not a success gate. Advanced pattern inference/composition wrappers cannot be adopted as a working engine without supplying their missing Python implementations.

## Distinctive mechanisms and grounded innovation assessment

The strongest implemented design idea is **continuity as a generated, searchable work artifact** rather than merely retaining a chat transcript. The transcript parser feeds automatic handoffs before compaction. A later start hook can inject the handoff or embedded ledger; SQLite indexing attaches outcomes and trace provenance. This permits a fresh coding context to recover the goal, decisions and next steps without replaying the entire prior conversation. Its limitations are concrete: some paths require legacy ledgers, newest-record selection can cross work streams, status is a checkpoint rather than live activity, and outcome marking is not compulsory product acceptance.

Another worthwhile mechanism is **action-sensitive context selection**: a recent search result names an actual target, which the read hook uses to request relevant structure/flow context instead of blindly loading whole files. Explicit offsets/limits and failure fallback preserve a route to source. This is a practical execution-layer pattern Wingman could port independently of the rest of the project. It does not establish measured token savings in this assessment, and it depends on the external TLDR analysis service being accurate and available.

[composition-gate.ts][composition], lines 39–78, throws on invalid pattern compositions. [pattern-selector.ts][selector], lines 99–169, validates adjacent pairs. It exposes isolation, shared, federated, and handoff scopes with sequential, parallel, and additive operators.

[python-bridge.ts][bridge], lines 27–63 and 72–108, invokes two missing local scripts: `scripts/validate_composition.py` and `scripts/agentica_patterns/pattern_inference.py`. Failed validation returns an error. Failed inference falls back to a low-confidence hierarchy. Type contracts, wrappers, and tests do not establish a working algebraic scheduler. Pairwise checks also do not establish global properties of longer chains. This assessment makes no historical or industry-wide novelty claim.

Finally, the file-claim and peer-session hooks show a useful low-friction approach to concurrent sessions: make conflicts visible while letting coding continue. Its enabling tradeoff is advisory awareness with minimal central control. Wingman needs stronger identity isolation, freshness, cleanup and worktree/integration ownership before using it as protection for a standing organization. These mechanisms are useful seeds precisely when their boundaries remain explicit.

## Practical fit for Wingman

Reusable material includes discovery/specification templates, TDD, manual acceptance, handoff schemas, outcome-aware indexing, targeted context, and optional learning extraction. Wingman can adopt these protocols or libraries separately. The independent-process launcher can inform a host adapter. A production adapter still needs owned process handles, canonical IDs, streaming output, cancellation, and durable reconciliation. A temporary registry and short-lived caller cannot provide that full contract.

Adaptation is substantial because the system is Claude-specific: event names, `Task`, frontmatter, CLI flags, JSON/stream formats and installed global paths all assume Claude Code. Wingman's Codex agents require equivalent adapters with clearly separated profile, identity, conversation, task and execution records. A single profile source should replace divergent JSON and Markdown role definitions. Permissions should be enforced at execution, not inferred from unused profile fields. Durable shared state should choose one coordination contract and explicit project/host namespaces; file claims need expiry/release and stronger integration rules; lifecycle events need idempotency and reliable exit/success classification.

Wingman still needs these organization capabilities:

- Telegram Butler intake, answers, and escalation.
- Cross-project registry and continuing ProductMaster/TechMaster appointments.
- Shared tickets, dependencies, rooms, membership, and history.
- Project/executive dashboards, agent briefings, timelines, and linked coding workspaces.
- Multi-host placement, routing, and periodic blocker follow-up.

Product acceptance needs a durable transition tied to the definition of done. It must stop active development until new work arrives. Role names and hooks alone cannot implement these workflows.

## Verification scope and limits

The read-only review covered these areas:

- Active settings, hook launcher, Markdown/JSON profiles, process launcher, and system prompt.
- Process/stream monitoring and discovery/build/implementation instructions.
- Session/file-claim SQL, coordination wrappers, and continuity/compaction/cleanup/outcome hooks.
- Status line, artifact schema, memory service, recall, and hints.
- TLDR hooks/client, MCP harness/client, pipeline code/tests, and Lean feedback hooks.

Documentation located mechanisms. Implementation supported the findings. The review changed no checkout files and started no services, models, databases, containers, or browsers.

The review inspected these tests without running them:

- [session-id-persistence.test.ts][identity-test], lines 17–25 and 73–112, imports actual persistence helpers.
- [mainHandoffFirst.test.ts][handoff-test], lines 49–64 and 68–100, invokes a compiled hook with temporary fixtures.
- [session-affinity.test.ts][affinity-test], lines 14–20 and 80–117, contains inline logic and placeholder assertions.
- [composition-gate.test.ts][composition-test], lines 58–117, expects Python-backed inference.
- [tldr-hooks.test.ts][tldr-test], lines 40–68, recreates command-generation logic instead of exercising the current daemon hook.
- [test_research_pipeline.py][pipeline-test], lines 20–59, names pipeline scenarios.

Coverage is uneven. These sources do not establish passing tests. The configured `opc/tests` tree and coordination tests are missing locally. See [pyproject.toml][pyproject], lines 124–128 and 161–164.

Negative-feature searches included hidden files, `opc/src`, `opc/scripts`, `.claude/hooks/src`, `.claude/skills`, agents, and setup paths. Terms covered Telegram, dashboards, registry/intake, task graphs, scheduling, supervision, hosts, SSH, lifecycle controls, and coordination imports. Examples, backups, transcripts, generated bundles, and proof artifacts did not establish an active product service. The local checkout lacks `scripts/agentica_patterns` and `scripts/validate_composition.py`. An external package or prior global installation could supply more behavior. That possibility remains **unclear and unverified** for this revision.

Keep these verification boundaries separate:

- Present hooks and configured hooks.
- Source files and installed compiled code.
- Prompt instructions and enforced workflow transitions.
- Temporary process identity and enduring agents.
- Remote tools and remote workers.
- Raw logs/checkpoints and connected organizational views.

[settings]: ../repo/.claude/settings.json
[launcher]: ../repo/.claude/hooks/hook_launcher.py
[spawn]: ../repo/opc/scripts/claude_spawn.py
[maestro]: ../repo/.claude/agents/maestro.md
[kraken]: ../repo/.claude/agents/kraken.md
[kraken-json]: ../repo/.claude/agents/kraken.json
[atlas]: ../repo/.claude/agents/atlas.md
[build]: ../repo/.claude/skills/build/SKILL.md
[discovery]: ../repo/.claude/skills/discovery-interview/SKILL.md
[implement]: ../repo/.claude/skills/implement_plan/SKILL.md
[precompact]: ../repo/.claude/hooks/src/pre-compact-continuity.ts
[continuity]: ../repo/.claude/hooks/src/session-start-continuity.ts
[artifact-schema]: ../repo/opc/scripts/core/artifact_schema.sql
[memory-pg]: ../repo/opc/scripts/core/db/memory_service_pg.py
[db]: ../repo/.claude/hooks/src/shared/db-utils-pg.ts
[register]: ../repo/.claude/hooks/src/session-register.ts
[claims]: ../repo/.claude/hooks/src/file-claims.ts
[broadcast]: ../repo/.claude/hooks/src/pre-tool-use-broadcast.ts
[session-id]: ../repo/.claude/hooks/src/shared/session-id.ts
[pipeline]: ../repo/.claude/hooks/src/patterns/pipeline.ts
[harness]: ../repo/opc/src/runtime/harness.py
[mcp]: ../repo/opc/src/runtime/mcp_client.py
[observe]: ../repo/opc/scripts/observe_agents.py
[status]: ../repo/.claude/scripts/status.py
[stream]: ../repo/opc/scripts/stream_monitor.py
[system-prompt]: ../repo/opc/scripts/agent_system_prompt.md
[activation]: ../repo/.claude/hooks/src/skill-activation-prompt.ts
[cleanup]: ../repo/.claude/hooks/src/session-end-cleanup.ts
[research-pipeline]: ../repo/opc/scripts/research_implement_pipeline.py
[pipeline-test]: ../repo/opc/scripts/test_research_pipeline.py
[sandbox]: ../repo/opc/docker/sandbox_runner.py
[tldr-read]: ../repo/.claude/hooks/src/tldr-read-enforcer.ts
[tldr-task]: ../repo/.claude/hooks/src/tldr-context-inject.ts
[daemon]: ../repo/.claude/hooks/src/daemon-client.ts
[memory-hook]: ../repo/.claude/hooks/src/memory-awareness.ts
[braintrust]: ../repo/opc/scripts/braintrust_analyze.py
[compiler]: ../repo/.claude/hooks/src/compiler-in-the-loop.ts
[compiler-stop]: ../repo/.claude/hooks/src/compiler-in-the-loop-stop.ts
[composition]: ../repo/.claude/hooks/src/shared/composition-gate.ts
[selector]: ../repo/.claude/hooks/src/shared/pattern-selector.ts
[bridge]: ../repo/.claude/hooks/src/shared/python-bridge.ts
[identity-test]: ../repo/.claude/hooks/src/__tests__/session-id-persistence.test.ts
[handoff-test]: ../repo/.claude/hooks/src/__tests__/mainHandoffFirst.test.ts
[affinity-test]: ../repo/.claude/hooks/src/__tests__/session-affinity.test.ts
[composition-test]: ../repo/.claude/hooks/src/__tests__/composition-gate.test.ts
[tldr-test]: ../repo/.claude/hooks/src/__tests__/tldr-hooks.test.ts
[pyproject]: ../repo/opc/pyproject.toml
