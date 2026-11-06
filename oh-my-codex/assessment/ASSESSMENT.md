# oh-my-codex assessment against Wingman

## Identity and verdict

- **Repository:** https://github.com/Yeachan-Heo/oh-my-codex
- **Local checkout:** `research/oh-my-codex/repo`
- **Revision inspected:** `509a299d586b48f145c2c7a7baac8ce08d01a015`
- **Package version:** `0.21.46` ([package.json], lines 1–12).
- **Assessment date:** 2026-11-05.
- **Method:** read-only implementation and test inspection; no dependencies installed, services launched, Codex workers started, or runtime tests executed.

**Fit verdict: a substantial local execution/workflow substrate, not a replacement for Wingman's standing organization.** OMX actually launches independent coding CLI processes, gives them specialist instructions, maintains dependency-aware tasks and mailboxes, monitors workers, and has unusually concrete completion, delivery, and cleanup machinery. Discovery, consensus planning, durable goal execution, project memory, and Telegram notification replies also make it more relevant than a simple terminal multiplexer. Its durable unit is primarily a repository/session/team run, however. Butler, portfolio intake, persistent project leadership, cross-host execution, organizational rooms, and connected web/mobile management views would still have to be built.

A critical distinction at this revision is **workflow instruction versus runtime enforcement**. Autopilot's skill calls its interview → Ralplan → Ultragoal chain mandatory, but the generic transition validator records many missing-stage/evidence cases as advisories. Ultragoal's full independent-review/architecture quality cohort is enforced only in strict mode. Conversely, claim tokens, task dependency checks, and claim-bound completion reports are actual state-transition checks. Treating every documented gate as equally enforced would materially overstate this alternative ([autopilot skill], lines 8–78; [Autopilot gate], lines 165–220 and 367–490; [state operations], lines 937–944; [Ultragoal], lines 1693–1761).

## Architecture and actual execution model

### Entry points and layers

The npm `omx` executable is the compiled `dist/cli/omx.js`; its source delegates to compiled CLI `main`, and explicitly errors if the compiled entry is missing ([entry], lines 1–29). The CLI dispatches to distinct command implementations for setup, agent configuration, structured questions, ordinary Codex execution, mission batches, team runs, Autopilot, Ralph, Ralplan, Ultragoal, session inspection, and native helper binaries ([CLI], lines 5072–5300). Ordinary execution still runs the external Codex executable; OMX supplies configuration, instructions, hooks, lifecycle state, and wrappers. It does not implement its own LLM inference or an independent coding IDE.

There are two different forms of “agent”:

1. **Codex-native role configurations:** standalone TOML files in user or project `.codex/agents/`, built from role definitions and prompt files. An agent definition has a name, description, model/reasoning posture, routing role, and declared tool pattern. Creating a TOML is creating a reusable profile. It does not itself start a process. Native spawning/conversation behavior belongs to the installed Codex runtime ([definitions], lines 1–132; [native config], lines 1–19 and 139–169; [agents CLI], lines 12–34 and 99–190).
2. **OMX Team workers:** separate CLI processes in tmux panes, or supported prompt-mode child processes, with persisted `worker-N` identity, assigned tasks, role instructions, workspace, process/pane identifiers, and a shared team-state root. These are real concurrent workers, not merely a sequence of personas in one conversation ([runtime], lines 3562–3790 and 3875–4058; [worker types], lines 11–65).

For Codex specifically, the normal team path is **interactive tmux**. It requires tmux and the current leader-pane context. The code has a prompt-worker subprocess implementation, but production Codex prompt workers are rejected because they require a terminal. The non-TTY Codex allowance is explicitly a test escape hatch. Claude/Gemini can use that alternate path. This matters when considering a headless Wingman daemon: “prompt mode exists” is not evidence that one can run headless Codex teams unchanged ([runtime], lines 2223–2255, 3341–3381 and 3684–3698).

### Persistence and ownership

Team state lives below the canonical team-state root, normally repository `.omx/state`, with config/manifest, worker identity/status/heartbeat/inbox files, task JSON, approvals, dispatch state, and event history. Worktree workers are pointed back to the leader's canonical shared state root instead of each inventing a separate tracker. Config records include leader cwd, workspace mode, team creation time, tmux session, workers, and next task/worker identifiers. The manifest separates runtime policy, governance, and a permissions snapshot ([state], lines 1116–1250; [worker types], lines 11–49 and 157–248; [state root]). This is a file-backed team coordination store, not a portfolio database.

The persistence architecture is hybrid. TypeScript retains task/config/workspace semantics and exposes an aligned gateway through `team-ops.ts`; runtime and public CLI API import that gateway. Mailbox/dispatch/authority operations can be delegated through the TypeScript bridge to `omx-runtime`, whose Rust core has authority leases, dispatch and mailbox logs, event replay, duplicate-request tracking, and compatibility JSON projections. The bridge can be disabled; legacy/fallback JSON paths remain. Its command enum is a useful boundary: it contains authority, dispatch, replay, snapshots, and mailbox commands, **not** a Rust implementation of every team task or product workflow ([team operations], lines 1–13 and 58–146; [bridge], lines 1–8 and 81–121; [Rust engine], lines 90–180; [mailboxes], lines 1–6 and 130–166).

Workflow mode state is a separate surface. The canonical state writer handles session-scoped state, workflow transitions, handoff-carrier validation, terminal outcome normalization, and repair. Autopilot owns one supervised session state rather than allocating a standing department for each phase. Ultragoal keeps a repository-native brief, goal rows, and append ledger, reconciled with snapshots of native Codex goals ([state operations], lines 850–970; [Autopilot CLI], lines 9–20 and 87–99; [Ultragoal], lines 20–30 and 177–225).

### User surfaces

The main interface is terminal-based: leader/worker panes, a HUD roster, sidecar state/topology, CLI JSON, and session-history commands. The HUD renders worker name, state, current task, role, pane, and update age, and goal-level current/next progress. `team status` inspects dead/nonreporting workers, task counts, recommendations, and pane-tail detail. Those are useful operational views, but neither a portfolio dashboard nor executive prose summaries of every agent's recent/current/next work ([HUD rendering], lines 214–254; [HUD types], lines 12–41 and 113–135; [team CLI], lines 1504–1622). The native `omx api` gateway is a localhost text/image generation sidecar, not an organization management web UI ([API CLI], lines 22–39; [API Rust], lines 17–25 and 87–108).

## Feature matrix

Verdicts apply to the Wingman capability in each row, not to general product quality. “Similar” credits substantial equivalent behavior while retaining the boundary described.

| ID | Wingman capability | Verdict | Implementation evidence and concrete difference |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | Team startup prepares distinct worker workspaces, identity records, launch environments, and CLI processes; several workers can share a role ([runtime], lines 3875–4058; [worker types], lines 36–49). Real Codex team workers use tmux; prompt-mode Codex is explicitly disallowed outside tests (lines 2243–2255). Identities are team-run workers rather than permanently employed organizational agents. |
| F02 | Extensible agent profiles, roles and team composition | **Similar** | User/project TOML add/edit/remove and role-prompt directory lookup permit custom profiles; startup resolves task role and prompt per worker ([agents CLI], lines 12–34 and 99–190; [role router], lines 15–57; [runtime], lines 3885–3938). Manual scale-up/down code also exists behind an environment gate, but searches found no production caller in the inspected CLI/API command surface; do not count it as a finished staffing UI ([scaling], lines 1–10, 150–154, 580 onward and 1927 onward). |
| F03 | Agent directory and visible working relationships | **Resembles** | `agents list` lists reusable TOML profiles. The HUD/sidecar show current team roster and topology ([agents CLI], lines 145–173; [HUD rendering], lines 214–254; [sidecar types], lines 88–114). No organization-wide directory of persistent identities, projects, reporting relationships, histories, and linked personal workspaces was found. |
| F04 | Telegram main channel and Butler routing | **Resembles** | Telegram send/notification and reply polling are implemented. Replies must refer to a known notification in the configured chat and route through message-id → tmux-pane mapping ([notification dispatcher], lines 220–278; [reply listener], lines 712–845). This enables remote steering of an existing notified session, not arbitrary new Telegram product intake, project resolution, or Butler's management relationship. |
| F05 | Cross-project registry, intake and existing/new routing | **Absent** | Team and mode entry points resolve current cwd/session/team; mission records are local prompt-checklist runs ([team CLI], lines 1424–1437 and 1769–1813; [mission], lines 6–29 and 49–64). Searches across `src/` and Rust crates for portfolio/project registry/intake/routing found no corresponding registry/service. Repository roots and team names are not persistent product routing. |
| F06 | Per-project product and technical leadership | **Resembles** | Analyst/planner/architect/verifier role definitions and phase role recommendations cover parts of the responsibility ([definitions], lines 67–132; [orchestrator], lines 121–158). They are callable roles/stages and a leader session, without separate durable ProductMaster/TechMaster agents maintaining each project's remit across runs. |
| F07 | Proportionate research/discovery and iterative clarification | **Similar** | Deep-interview defines quick/standard/deep profiles, context intake, research/code grounding, one-question rounds, ambiguity thresholds, non-goals, and decision boundaries ([interview skill], lines 30–126 and 131–210). Actual question obligations are persisted and linked to same-session answered records ([interview questions], lines 24–37 and 93–168). Interview quality/scoring is model-led. It is not a standing ProductMaster or Telegram clarification router. |
| F08 | Scope/specifications/acceptance/definition of done | **Similar** | Interview produces durable `.omx/context` and spec handoffs; Autopilot and Ralplan carry artifact references. DAG nodes can carry acceptance statements and execution/verification lanes ([interview skill], lines 131–176; [Autopilot skill], lines 19–26 and 71–78; [repo decomposition], lines 106–118). Product definition is document/workflow-oriented rather than a project-owned SCOPES/SPECS/HARNESS registry; missing Autopilot handoff evidence can be advisory ([Autopilot gate], lines 395–429). |
| F09 | Decomposition, assignment and shared tracking | **Similar** | Team CLI builds repository-aware plans; tasks persist owners, dependency IDs, file/domain scope, lane and results. Claims enforce dependency readiness, versions and leases ([team CLI], lines 1769–1805; [repo decomposition], lines 18–50 and 121–147; [task state], lines 28–119). Substantial team tracker, but lacks Wingman's unified cross-project task records/comments/dashboard. |
| F10 | Human portfolio/project dashboard | **Absent** | CLI status/HUD/sidecar expose local team operations, not a navigable human project dashboard ([team CLI], lines 1504–1622; [HUD rendering], lines 214–254). Searches through source, UI-related paths and API crate found no project/portfolio web/mobile application. `omx api` serves generation, not tracker/dashboard pages ([API CLI], lines 22–39). |
| F11 | Agent chat app, rooms and direct collaboration | **Resembles** | Team direct messages, broadcasts, per-worker mailboxes, notification/delivery acknowledgements, and event APIs support actual agent communication ([team API], lines 105–144; [runtime], lines 7442–7528; [mailboxes], lines 8–22). No room-membership model, Room1/Room2 management discussions, or browsable chat application was found in messaging/sidecar/API paths. |
| F12 | Management escalation and human decisions/approvals | **Similar** | Worker bootstrap requires blocked-status/help reporting; leader monitoring surfaces stalled work; structured questions and task approval records exist ([worker bootstrap], lines 338–400; [runtime], lines 4680–4748; [approvals], lines 4–11 and 30–60; [interview questions], lines 93–168). This is worker → current leader → user, not a multi-level management/escalation graph; reviewer labels are not proof of authenticated human approval. |
| F13 | Durable project knowledge and reusable directives | **Similar** | Project memory/notepad tools add notes and directives; wiki pages store source links, categories, confidence and cross-links; lifecycle injects a bounded knowledge index ([memory], lines 41–94 and 188–268; [wiki types], lines 17–42; [wiki lifecycle], lines 43–97). Strong reusable primitives, but no prescribed Wingman DIRECTIVES hierarchy or portfolio-level knowledge ownership. |
| F14 | Persistent identity/conversation/work continuity | **Similar** | Worker identity, tasks, mailboxes, mode state, native Codex histories, and Ultragoal ledger persist ([worker types], lines 11–65; [Ultragoal], lines 177–225; [timeline CLI], lines 4–29). `resumeTeam` reuses live tmux sessions or prompt workers with retained process handles. It does not resurrect dead workers or guarantee prompt-mode resume after controller restart ([runtime], lines 5918–5979). Team cleanup can delete the coordination state. |
| F15 | Proactive supervision/periodic wake/blocker follow-up | **Similar** | Monitor implements liveness/heartbeat checks, expired-lease reclaim, rebalancing, verification and pending-mail delivery; normal start-summary/await invoke it, while status is read-only ([runtime], lines 4609–4890; [team CLI], lines 1400, 1515 and 1645). A standalone runtime helper has five-second polling, but no production auto-launch caller was found ([runtime CLI], lines 296–322 and 447–489). HUD authority and fallback hook watcher can continue maintenance/nudge checks while detached ([HUD loop], lines 330–359; [HUD authority], line 342 onward; [fallback watcher], lines 1850–1905). This is active-run local supervision, not a portfolio ProjectMaster scheduler. |
| F16 | Parallel products and concurrent specialists | **Similar** | Concurrent specialist processes and separate cwd/session/team state support multiple independent team runs; default governance permits one active team per leader session and disallows nested teams ([runtime], lines 3562–3698; [state], lines 543–555; [worker types], lines 385–386). Up to 20 workers is the explicit team ceiling. Parallel products remain separately launched repository workflows without portfolio allocation/leadership. |
| F17 | Real multi-host execution/shared coordination | **Absent** | Worker launch is local tmux or local `spawn`, state roots are filesystem paths, and liveness/cleanup use local pane/PID proofs ([runtime], lines 3341–3381 and 3684–3698; [tmux worker], lines 2038 onward). Searches for SSH, remote worker agents, fleet/host routing and shared network coordination in source/crates found no execution transport. Cross-platform binaries and notification web calls are not multi-host orchestration. |
| F18 | Executive agent overview: current/recent/next/blockers | **Resembles** | Worker roster reports current state/task/role/update age; team status adds dead/nonreporting workers and recommendations; goal HUD includes ongoing/next goals ([HUD types], lines 12–41 and 113–135; [HUD rendering], lines 214–254; [runtime], lines 4680–4782). No synthesized per-agent recent accomplishments/next assignment briefing linked across portfolio records. Goal-level next work is not each agent's next work. |
| F19 | Per-agent summary timeline linked to work | **Resembles** | Session timeline pairs tool calls/results with timestamps, source line numbers, turns, compactions and filters; team events record status/message activity ([timeline CLI], lines 4–29 and 108–149; [worker types], lines 257–274). This is detailed session metadata/event history, not a plain-language per-agent accomplishment/blocker feed connected to tasks, discussions and deliverables. |
| F20 | Detailed per-agent coding workspace drill-down | **Similar** | Worker tmux panes expose native coding sessions; `team status` captures pane state/tails and inspection hints; session timeline/search/export provide local forensic access ([team CLI], lines 705–843 and 1504–1622; [timeline CLI], lines 108–149). Useful terminal/native-session drill-down, without the unified web/mobile workspace and connected organizational navigation. |
| F21 | Live activity/lifecycle/steering/execution visibility | **Similar** | Start/status/await/resume/shutdown plus messaging and pane inspection are real controls; native session tools reveal tool/turn metadata; reply listener injects remote steering ([team CLI], lines 1424–1759; [runtime], lines 5068–5195 and 5918–5979; [reply listener], lines 782–828). Full fork/rename/compact/archive controls remain native-runtime concerns, not a complete OMX agent-management API. |
| F22 | Testing/integrated verification/product acceptance/delivery | **Similar** | Code-changing tasks cannot complete via normal transition without fresh claim-bound JSON evidence and structured verification. Monitoring holds a verification phase for missing evidence and integrates worktree commits ([task state], lines 206–265; [completion evidence], lines 13–48; [runtime], lines 4762–4815 and 1290–1656). Strict Ultragoal has independent reviewer/architect checks. Evidence is agent-supplied and product acceptance/delivery through Butler is not implemented. |
| F23 | Autonomous operation with human organizational direction | **Similar** | Autopilot chains discovery/planning/goals, continuation hooks nudge active workflows, team monitoring and durable goals support extended execution ([Autopilot skill], lines 8–49 and 83–112; [runtime], lines 4609–4890; [Ultragoal], lines 1763–1794). Autonomy is a recoverable workflow driven by current leader/native Codex session, not an always-on organization receiving all product direction through Butler. Advisory gates weaken any claim of enforced end-to-end acceptance. |
| F24 | Chat/tracker/dashboards accommodate new profiles | **Resembles** | Generic worker role strings, directory-loaded prompts, mailbox addresses and table rows accommodate new role names without a separate screen per role ([worker types], lines 36–49; [role router], lines 15–57; [HUD rendering], lines 214–254). This extensibility applies to the local team primitives. The Wingman chat, tracker and dashboards are not present as connected applications. |

## Agent definition and lifecycle

### Definition, profile creation, and identity

OMX's built-in definitions include analyst, planner, architect, executor, verifier, debugger, designers and specialist reviewers. Their model class/reasoning/tool-pattern metadata guides configuration and instruction composition. The native-config generator explicitly distinguishes the model written into TOML from richer informational role-model resolution; not every tier/default setting pins a native model. It also expresses a leaf-subagent rule in developer instructions and states that a runtime tool-capability gate would have to be added if TOML gains one. Thus role declarations and “read-only” labels should not be assumed to create an independent security boundary ([definitions], lines 7–30 and 55–132; [native config], lines 1–19 and 139–145).

The `agents` CLI scaffolds profile TOMLs, validates names, lists project/user definitions, launches an editor for edits, and deletes the selected definition on remove. It creates neither a permanent conversation nor a scheduled employee. Team startup separately loads project `.codex/prompts/<role>.md` before user prompts, composes model/role instructions, and persists `worker-N` identity. The leader has its own session/thread association and `leader-fixed` mailbox. A scoped internal team name derives from the leader identity to keep same display names from colliding; run identity and role identity are different concepts ([agents CLI], lines 39–57, 99–190 and 220–243; [runtime], lines 3590–3622 and 3885–3938; [worker types], lines 150–155).

### Creation and bootstrapping

`teamCommand` parses the request, builds a repo-aware execution plan or legacy text decomposition, computes effective worker count, and starts a team with the selected worktree mode and any approved planning binding. `startTeam` checks nesting/active-team policy, non-destructive startup, current plan bindings, worker provider compatibility, tmux requirements, and stale-state conditions. In worktree mode it requires a clean leader workspace and provisions per-worker Git worktrees. In shared-workspace mode it generates team-scoped instructions instead ([team CLI], lines 1769–1813; [runtime], lines 3562–3790).

It then initializes shared state, creates pending tasks, remaps symbolic DAG node dependencies to actual task IDs, writes role/root instructions and inboxes, and launches workers. Environment values identify canonical state root, leader cwd, instructions file, worktree, and worker identity. Startup is not considered successful solely because a pane exists: ready-prompt detection, a bootstrap ACK/status/task claim and dispatch receipt evidence are used, with bounded dispatch retries and recovery classification ([runtime], lines 3795–4058 and 4180–4320; [worker bootstrap], lines 338–400 and 884–920). Generated prompts instruct the worker to read its inbox, ACK first, claim a task, do the work and report through CLI APIs. The generated prompt is the worker protocol. The claim/transition functions provide the stronger persistence checks behind it.

### Execution, tools, permissions, and routing

Workers run the installed Codex/Claude/Gemini CLI with their native tools and provider credentials. OMX adds local MCP servers and CLI surfaces for state, memory, wiki, code intelligence and trace access, but it is not the underlying shell/editor permission engine. The launch policy code distinguishes an explicit approval/sandbox policy from bypass flags, propagates compatible Codex arguments, rejects explicit policy when switching to Claude/Gemini, and can grant execution roles Claude skip-permissions or Gemini YOLO arguments. A permissions snapshot records policy information. It is not itself enforcement ([tmux worker], lines 1784–1835 and 2017–2034; [state], lines 598–652). A Wingman integration must deliberately choose launch policy rather than infer restrictions from role titles.

Routing happens at several levels. CLI syntax chooses the workflow; role heuristics choose tasks' specialist roles; project/user prompt lookup supplies behavior; provider/model resolution selects the actual CLI/model. Native Codex subagents are a further layer inside the leader/worker runtime. Team bootstrap includes delegation plans but native leaf restrictions remain instruction-based. These nested concepts should not be counted as extra independently durable employees ([role router], lines 68–103 and 211 onward; [runtime], lines 3470–3516 and 3885–3938; [native config], lines 139–145).

### Concurrency and scheduling

A team has a declared worker count and default/absolute maximum of 20. Several workers can run simultaneously in separate panes/worktrees. A single worker can own several tasks; dependency readiness prevents claiming a task whose predecessors have not completed. Default governance disallows nested teams and allows only one team per leader session, so broader concurrency comes from separate leader sessions rather than a central portfolio scheduler ([worker types], lines 113–146 and 385–386; [task state], lines 28–119; [state], lines 543–555).

Repo-aware decomposition retains file paths, domains, lanes, dependencies and acceptance statements. It topologically sorts nodes, rejects cycles and estimates useful parallel lanes before allocation. This is stronger than blind worker fan-out, but file scopes are coordination metadata and prompt constraints, not filesystem locks preventing simultaneous edits ([repo decomposition], lines 18–77 and 106–170). Internal scaling code has monotonic worker indices, membership/task transactions, drain status, exact-pane proofs and cleanup debt. At this revision its exported functions have tests but no production caller found outside that module, so dynamic staffing should be treated as an internal/experimental capability requiring integration ([scaling], lines 1–10, 150–154 and 580 onward; [state], lines 892–1075).

Supervision is bounded to active execution. The normal team CLI invokes mutating `monitorTeam` in its start summary and once at the start of `team await`; `team status` explicitly uses read-only monitoring. A standalone runtime CLI contains a repeated polling loop, but the inspected production source has no auto-launch caller for that helper, so ordinary team startup should not be assumed to start that poller ([team CLI], lines 1400, 1515 and 1645). The normal terminal experience also uses hooks, a fallback watcher and HUD authority ticks. These have their own maintenance/nudge paths rather than implicitly calling the full monitor. Idle nudges have delay/count bounds; leader nudges remind the current leader to inspect inbox and worker state. None of this establishes a long-lived portfolio supervisor that wakes to discover new work across arbitrary products ([runtime CLI], lines 296–322 and 447–489; [idle nudges], lines 19–35; [fallback watcher], lines 1850–1905; [HUD authority], line 342 onward).

### Persistence and resume boundaries

Tasks, claims, messages, results, lifecycle phase, process/pane identity and project knowledge survive on disk. Native Codex sessions provide the coding conversation history. The session timeline reads active or archived local histories rather than inventing a second transcript store. Ultragoal's goals and ledger can continue planned work over interruptions, and workflow state identifies the supervised phase to resume ([timeline CLI], lines 4–29; [Ultragoal], lines 177–225; [Autopilot skill], lines 83–96).

`resumeTeam` is specifically **reconnection to existing workers**, not general resurrection. Interactive resume returns null when the named tmux session no longer exists. Prompt resume requires a live worker and a process-local handle; live PIDs without retained handles emit `prompt_resume_unavailable:missing_handle` and fail to resume. There is no demonstrated restoration of every worker's conversation, native subprocess, terminal and task claim after machine restart ([runtime], lines 5918–5979). The durable goal/work record could inform a newly launched run, but that is a distinct recovery procedure.

### Interruption, failure, retry, and recovery

Task claiming checks dependencies before and after acquiring a per-task lock, requires a real configured worker, rejects ownership/version conflicts, allocates a random claim token and a 15-minute lease, and increments task version. Terminal transitions require the current owner/token and a live lease. Expired claims can be reclaimed to pending; monitor can reassign eligible work and surface dead/nonreporting workers ([task state], lines 59–119, 206–247 and 339–369; [runtime], lines 4630–4750). Heartbeat is evidence of turns/liveness, not proof that semantic progress occurred. Nonreporting detection counts turns without task progress. It can recommend a reminder rather than solve the blocker itself.

Startup uses bounded ready/evidence waits and retries. Stale cleanup, process termination, scaling and shutdown all contain substantial exact-identity checking and durable cleanup journals. Missing config is explicitly **not** authority to kill a conventionally named tmux session. Teardown checks pane/PID/team ownership, and restartable receipts bridge crash windows where an effect may have occurred before its persistence was finalized ([runtime], lines 387–483, 2768–2900, 3105–3273 and 5068–5148). These are valuable operational safety measures for managing many local terminals, not network-wide distributed consensus.

Cancel/clear and recovery are intentionally available even when workflow evidence is missing or damaged. Runtime shutdown supports forced interruption, emits terminal epoch/reason, requests worker acknowledgements, then tears down exact owned resources. Forced shutdown is an execution control, not product completion. On terminal complete/failed/cancelled phases, the background runtime CLI preserves team state for inspection and explicitly asks for separate cleanup, rather than silently treating a failed run as success ([runtime], lines 5068–5195; [runtime CLI], lines 193–213; [Autopilot skill], lines 98–112).

### Completion, acceptance, and retirement

Normal task completion is guarded. A code-changing task must submit an `EVIDENCE_RECORDED` path inside `.omx/evidence`, without symlinks, containing a nonempty bounded JSON file fresh to the current claim. Team/task identifiers and a SHA-256 of the claim token must match. Every verification record requires command, passed result, output, and a summary/unverified list. The task result also needs a structured Verification section. Coordinated/delegated tasks can require textual coordination or delegation compliance evidence ([completion evidence], lines 13–48; [task state], lines 121–179 and 230–265). The validator validates the report, not the actual truth of commands reported by the worker; independent integration tests and human product acceptance remain separate responsibilities.

Monitor reconciles phases and task counts, blocks terminal success on missing structured verification, handles failed/dead-worker stalls, and may integrate worker commits into the leader worktree. Integration writes reports/events and handles conflicts/failures instead of assuming that separate passing tasks compose automatically ([runtime], lines 1290–1656 and 4762–4815). Team phase recommendations provide plan/PRD/exec/verify/fix roles, but are not evidence that each phase is executed by a separate autonomous department ([orchestrator], lines 121–158).

Ultragoal checkpoints reconcile native goal snapshots with the repository ledger. Final strict mode requires cleaner, passing verification, clean code review and independent code-reviewer/architect evidence plus architecture invariants. Ordinary mode accepts missing quality-gate input and treats cohort fields as advisory. Autopilot similarly records skipped gates; its status renderer explicitly labels `complete-with-skipped-gates`. A reliable Wingman delivery rule must consume those distinctions rather than trust a generic “complete” flag ([Ultragoal], lines 1693–1761 and 1796–2001; [Autopilot gate], lines 367–490; [Autopilot CLI], lines 72–87).

Retirement is per run/profile. Workers acknowledge a shutdown inbox, processes/panes are cleaned, worktree reports preserve merge information, instructions are restored/removed and explicit cleanup can remove team state. Removing a reusable native-agent TOML only removes the profile. Neither operation is an organization-wide agent archive preserving directory entry, responsibilities, chat history and a personal executive timeline ([worker bootstrap], lines 1029–1051; [runtime], lines 5068 onward; [agents CLI], lines 235–254).

## Coordination mechanics and traced request

The coordination model is **leader plus team-scoped tasks/mailboxes/events**, with direct worker collaboration. Task dependencies and claims determine eligible work; inbox files carry assignment instructions; mailbox messages carry peer/leader communication; dispatch requests carry the wake-up/transport lifecycle. A stored message, a notification that a message exists, and the receiver marking it delivered are distinct states. The public API exposes send/broadcast/list/mark-delivered, claim/transition/release, read-events/await-event and approval records. Rust-backed records include team scope, important because multiple teams reuse names like `worker-1` ([team API], lines 105–144; [mailboxes], lines 8–22 and 70–88; [worker types], lines 176–215).

Communication is adaptive rather than uniformly heavyweight. Task metadata/wording showing dependencies, shared files/domains, boundaries or handoffs activates a coordinated protocol; independent fan-out remains lightweight. The generated protocol asks for a shared understanding, ACK/readback handoffs, monitoring of boundary changes, backup/help requests and adaptation checkpoints. The completion transition can require a coordination evidence line, but this proves only that the worker recorded a statement, not that the collaborating agent understood or a handoff was correct ([coordination], lines 8–37 and 122 onward; [worker bootstrap], lines 689–710 and 768–783; [task state], lines 155–179 and 230–247).

The following traces an actual implemented command path for an illustrative request, **not an executed run**: `omx team 3:executor "Implement login throttling with API, UI and regression tests"`.

1. CLI `main` dispatches `team` to `teamCommand`. Argument parsing sets task/worker request and worktree mode. Repository-aware decomposition consults the available plan/DAG handoff; otherwise the legacy plan decomposes/classifies the task. The planner retains owner/role, dependencies, file scope, domains and lanes ([CLI], lines 5274–5276; [team CLI], lines 845–945 and 1769–1805; [repo decomposition], lines 18–77). There is no step resolving the phrase to an existing product in a portfolio.
2. `startTeam` resolves leader and internal team identity; validates current execution/Ultragoal binding when supplied; establishes workspaces and state; creates task rows, converts symbolic dependencies to concrete IDs and stores assignment metadata ([runtime], lines 3590–3675 and 3795–3866).
3. For each worker, startup resolves a specialist role/prompt, builds instructions and initial inbox, launches a local CLI pane, persists worker identity and waits for readiness/ACK evidence. A heuristic decomposition need not produce exactly the human's intended API/UI/test responsibilities. A reviewed DAG gives more explicit boundaries ([runtime], lines 3875–4058 and 4180–4320).
4. Worker follows its bootstrap instructions: ACK to `leader-fixed`, request `claim-task`, then implement. The API reaches `teamClaimTask`. The locked task code rejects a blocked dependency, unknown worker, version mismatch or live competing claim, and returns the new claim token ([worker bootstrap], lines 884–920; [team API], lines 105–144; [task state], lines 59–119).
5. If the UI worker needs the backend's error contract, it can send a direct message using `send-message`. The runtime persists the message before arranging a wake-up. The receiver reads mailbox and marks delivered. A shared-surface/handoff task activates the stronger coordination protocol; if blocked it records blocked status/reason and asks the leader for concrete help. This is a real team conversation channel, but not a room-based chat application ([runtime], lines 7232–7394 and 7442–7479; [worker bootstrap], lines 930–935; [coordination], lines 18–23).
6. A human-only policy choice can be asked through a structured question and recorded against the current session. Separately, if Telegram notification/reply is configured, a reply to that notification maps back to a pane. The daemon does not interpret an arbitrary unthreaded message as “start a new login-throttling project” ([interview questions], lines 93–168; [reply listener], lines 770–813).
7. Worker writes current-claim evidence and submits `transition-task-status`. The state code validates claim, lease, any compliance evidence and verification report before writing completed status/result/event. On a subsequent mutating monitor invocation, the monitor can assign dependency-ready work, detect blockers, attempt safe rebalance/integration, and update phase/recommendations ([task state], lines 206–292; [completion evidence], lines 13–48; [runtime], lines 4609–4890).
8. The leader verifies the integrated result and either continues repair or performs explicit shutdown. A background runtime preserves terminal state for inspection. Wingman would still need a product-level definition-of-done assessment, human acceptance record, delivery notification and continuation routing on top ([runtime], lines 5068–5195; [runtime CLI], lines 193–213).

## Major additional capabilities beyond Wingman's description

### Durable native-goal orchestration and bounded steering

Ultragoal adds brief/goals/append-ledger records, native Codex goal reconciliation, aggregate or per-story modes, retries, nonterminal blockers, review-blocker resolver goals and audited steering. Steering validates proposed mutations so they cannot simply weaken objectives, tests, reviews or quality gates; final aggregate receipts cannot be overwritten as if unfinished work were completed. This could give Wingman a useful execution ledger under each ticket or project milestone. Integration must preserve goal/thread ownership and handle native `get_goal` unavailability/foreign objectives rather than equate a repository row with the live native goal ([Ultragoal], lines 125–225, 1311–1374, 1472 onward and 1796–1878). Its strict versus ordinary quality modes must be chosen explicitly.

### Consensus/advisory planning and research validation

Deep-interview and Ralplan provide much more prescribed pre-execution reasoning than Wingman's broad purpose statement: explicit ambiguity dimensions, evidence provenance, pressure-testing questions, architect/critic review cycles, recoverable handoff artifacts and advisory planning lifecycle. These are reusable workflow practices, not automatic evidence that a product-manager agent exists. `$autoresearch` also has validation modes based on a mission-validator completion artifact or an output artifact plus architect approval, useful for bounded experimental/research work. The old `omx autoresearch` command is hard-deprecated and fails intentionally. It must not be cited as a current detached autonomous research launcher ([interview skill], lines 30–126 and 177–210; [Autopilot gate], lines 165–235; [research CLI], lines 4–30 and 104–111; [research validation], lines 133–178). Integration should retain machine-checkable validators where available and recognize that approval-shaped local JSON is not independently authenticated evaluation.

### Knowledge wiki with provenance and maintenance checks

The wiki is more structured than a plain shared notes file: source references, links, tags, confidence, categories, ingest/query/lint, bounded session-start context and session/compaction lifecycle hooks. The canonical `omx_wiki/` store and legacy read-only fallback are explicit. Lint can surface stale, orphan, broken-reference, low-confidence, oversized and structural-contradiction issues. This could augment Wingman's DIRECTIVES with retrieved working knowledge, but requires a decision about authoritative specs versus automatically captured notes, and about project boundaries. It does not make model-generated knowledge correct by construction ([wiki types], lines 17–42 and 85–118; [wiki API], lines 20–57; [wiki lifecycle], lines 43–97).

### Multi-provider teams and independent advisors

OMX can select Codex, Claude or Gemini workers and invoke Claude/Gemini advisor commands with a role prompt. Wingman describes autonomous Codex agents, so alternative-provider review is additional flexibility rather than a missing requirement. It could provide independent critique or specialized fallback. Integration would introduce credential/configuration ownership and permission-policy differences: translating a Codex launch policy to another CLI is intentionally restricted, and execution role defaults can request a provider's bypass mode ([runtime CLI], lines 216–232; [ask CLI], lines 9–15 and 169–201; [tmux worker], lines 1784–1835).

### Native shell-output evidence and session forensics

SparkShell executes commands, redacts output, returns raw output below a configurable line threshold and summarizes longer output; structured output can retain line counts, raw hash and pane/tail evidence. It can summarize a pane tail and compare cached output. This is useful for reducing the context cost of supervising many workers, but summaries remain lossy and commands remain real executions, not a sandbox. Its default threshold is 12 visible lines ([SparkShell], lines 88–155 and 910–961; [SparkShell threshold], lines 1–22). Session timeline adds filtered tool/turn/compaction forensics and clearly distinguishes recorded completion from proven success. Both would complement Wingman drill-down. Neither supplies executive semantic summaries by itself ([timeline CLI], lines 4–29 and 108–149).

### Local generation gateway and coding-analysis tools

The Rust API sidecar supports local text/image generation with mock and experimental private-backend modes and local bearer configuration. This could support artifacts outside an interactive coding session, but it is an optional integration dependency, not a management API or host fleet controller ([API CLI], lines 22–39; [API Rust], lines 56–108). Code-intelligence tools add TypeScript diagnostics, symbols/references/hover and AST-grep search/replacement. Some “LSP” functions use `tsc`, text patterns or command-backed implementations. They should be evaluated per language instead of assumed to be a general language-server platform ([code intelligence], lines 93–132, 143–149 and 332–450).

## Distinctive mechanisms and innovation assessment

The strongest ideas here concern **making a CLI agent team recoverable and inspectable**. These are implementation distinctions observed in this revision, not historical novelty claims.

1. **Claim-bound completion evidence.** A result file is tied to team, task, the current random claim token hash and claim freshness; unsafe/symlinked evidence paths are rejected. This prevents stale reports, bare “done” messages and another task's evidence from casually satisfying completion. The benefit is a much tighter relationship between task ownership and recorded verification. Its limit is that passed command/output fields are still written by the agent, not independently executed/attested by this validator ([completion evidence], lines 13–48; [completion tests], lines 335–407).
2. **Separate semantic message delivery from terminal nudging.** Mailbox creation, notified/delivered timestamps, dispatch requests, recovery journals and Rust event projections avoid equating “keys sent to pane” with “work received.” Team scoping matters when generic worker names repeat. This supports retries and post-crash reconciliation. It does not guarantee exactly-once model behavior or correct human-level understanding ([mailboxes], lines 70–88 and 130–166; [bridge], lines 81–121; [state tests], lines 594–816 and 2479–2523).
3. **Exact resource authority and cleanup debt.** Pane identifiers can be recycled, and process trees can outlive their parent. Runtime tracks exact pane/PID/owner evidence, journals incomplete effects and refuses to use a conventional session name as kill authority. That addresses concrete operational hazards in long-running multi-pane teams. It increases state-machine complexity and remains dependent on local tmux/process observation ([runtime], lines 2768–2900, 3105–3273 and 5068–5148; [scaling], lines 175–225).
4. **Dependency-aware coordination intensity.** The system synthesizes stronger collaboration requirements when tasks overlap or hand off work, while keeping independent sweeps lightweight. It connects task metadata, generated instructions and completion evidence rather than relying solely on a general “collaborate” prompt. The boundary is heuristic classification and textual compliance evidence. It is not a proof that shared contracts or merge order are correct ([coordination], lines 8–37 and 122 onward; [task state], lines 155–179 and 230–247).
5. **Durable steering and graded workflow truth.** Ultragoal can add/split/redirect bounded subgoals with audit records while protecting completion constraints; Autopilot records skipped gates and exposes qualified completion rather than hiding evidence gaps. That gives a future Wingman controller richer state than a Boolean done flag. The limitation is essential: ordinary workflow progress can remain advisory, so consumers must enforce their own acceptance policy where required ([Ultragoal], lines 1311–1374, 1472 onward and 1693–1761; [Autopilot CLI], lines 72–87).

The best reuse opportunity is these explicit coordination contracts and recovery patterns. The larger product idea—permanent human-facing organization spanning projects and hosts—is still outside the implementation observed.

## Practical Wingman fit

Use directly, subject to local runtime validation:

- Specialist prompt/config generation.
- Tmux Codex team launch.
- Per-team tasks/dependencies/claims.
- Mailboxes and events.
- Read-only status/pane inspection.
- Project memory/wiki.
- Claim-bound completion evidence.
- Goal/ledger records.
- Notification delivery and reply mapping. Together these can provide a capable local execution adapter beneath TechMaster. Reusing them also means accepting Node plus native-helper packaging, installed Codex CLI, tmux and Git/worktree operational assumptions ([package.json], lines 1–12 and 84–110; [runtime], lines 3684–3698).

Adapt before relying on organizational guarantees:

- Assign Wingman stable agent IDs independent of `worker-N` and team-run names.
- Bind every team/task/message/evidence record to durable project and agent identities.
- Wrap local execution behind an API that preserves exact ownership.
- Choose launch permissions explicitly.
- Make completion policy distinguish ordinary/advisory versus strict evidence.
- Expose mode/goal blockers and cleanup debt in the tracker.
- Define a durable restart procedure that launches replacement workers from saved context. Headless Codex and prompt-mode recovery cannot be assumed from test-only subprocess scaffolding. Internal scaling would need a supported command/service integration and runtime verification.

Still build:

- Butler Telegram intake and conversation routing.
- Organization-wide project registry and existing/new-product resolution.
- Standing ProjectMaster/ProductMaster/TechMaster instances and relationships.
- Project-owned scope/spec/harness structure and acceptance records.
- Room1/Room2 chat application and durable room membership.
- Integrated ProjectTracker with comments/decisions and portfolio views.
- Semantic per-agent accomplishment/current/next/blocker timelines.
- Connected web/mobile dashboards and per-agent workspaces.
- Persistent multi-host execution/placement/coordination.
- Portfolio scheduling and supervision that survives individual team/session retirement.

A sensible boundary is **Wingman owns organization, identity, projects, acceptance and host routing; OMX is an optional local execution engine**. Making OMX itself the whole organization would require extensive changes at both the data-model and interface layers. OMX can reduce the task and worker reliability code Wingman must build. Adoption requires checks against the exact Codex/tmux/version environment. Profile files do not establish durable agents. Advisory phase records do not enforce completion.

## Verification scope and limits

The assessment followed actual CLI dispatch, team planning/startup, workspaces, role instructions, task lifecycle, messaging, monitor/rebalance/integration, resume, shutdown and selected workflow state paths. It read source and representative tests; **no behavior was exercised**, and passing tests are not claimed.

Important implementation inspected includes:

- `src/cli/omx.ts`.
- relevant `src/cli/index.ts` dispatch/launch sections.
- `src/cli/team.ts`.
- `src/cli/agents.ts`.
- `src/agents/{definitions,native-config}.ts`.
- `src/team/{runtime,worker-bootstrap,role-router,repo-aware-decomposition,coordination-protocol,scaling,team-ops,api-interop}.ts`.
- `src/team/state.ts`.
- `src/team/state/{tasks,mailbox,approvals,types}.ts`.
- `src/team/completion-evidence.ts`.
- `src/runtime/bridge.ts`.
- Rust runtime engine.
- `src/state/operations.ts`.
- Autopilot FSM/gates/CLI/skill.
- Deep Interview skill/question obligations.
- Ultragoal artifacts.
- notification reply path.
- HUD and sidecar schemas/rendering.
- session timeline.
- wiki lifecycle/schema.
- research validation/deprecation.
- native API schema.
- code-intelligence surface and SparkShell execution/threshold sections.

Representative tests inspected:

- [Task/state tests], lines 1338–1698 and 2020–2216: dependency readiness, competing claims, stale locks, owner/version constraints, token/lease errors and reclaim behavior; lines 2479–2523: team-scoped mailboxes.
- [Completion tests], lines 106–155 and 271–407: generated implementation/test evidence, marker-only result rejection, current worker-directory selection and earlier-claim rejection; lines 408 onward enumerate unsafe/stale/mismatched/placeholder reports.
- [Worker identity tests], lines 125–200: fake prompt worker launch verifies roles remain distinct in outer identity/instructions. This test explicitly uses a mocked non-TTY Codex allowance. It is not evidence that production Codex supports that launch mode.
- [Autopilot advisory tests], lines 17–113 and following assertions: missing required stages/evidence become persisted advisory/qualified-completion cases. These tests are important counterevidence to a strict reading of the workflow skill.
- [Telegram tests], lines 763–835: mocked notification-reply mapping and acknowledgement; subsequent cases reject wrong-chat replies. No live Telegram delivery was attempted.
- [Ultragoal tests], starting line 160: artifact lifecycle and steering/checkpoint coverage were inspected by test cases and relevant implementation; full suite completeness and runtime performance were not established.

For negative findings, searches covered implementation `src/`, CLI/MCP/notification/team/HUD/sidecar paths and native crates, including portfolio/project-registry intake, Butler/room models, dashboards/web server responsibilities, SSH/remote hosts/fleet execution and caller paths for scaling. They found local team/workflow records and notification/generation networking, not the Wingman organizational applications or remote execution protocol. Native Codex itself is an external dependency. This checkout cannot establish all of its current lifecycle/permission guarantees. Documentation, skills, deprecated modules and executable runtime branches were distinguished wherever their behavior differed. No browser or external live documentation was needed for this local-revision assessment.

## Evidence links

Line numbers in the report refer to this exact checkout revision. Links are relative to the report directory.

[package.json]: ../repo/package.json
[entry]: ../repo/src/cli/omx.ts
[CLI]: ../repo/src/cli/index.ts
[team CLI]: ../repo/src/cli/team.ts
[agents CLI]: ../repo/src/cli/agents.ts
[definitions]: ../repo/src/agents/definitions.ts
[native config]: ../repo/src/agents/native-config.ts
[runtime]: ../repo/src/team/runtime.ts
[runtime CLI]: ../repo/src/team/runtime-cli.ts
[worker types]: ../repo/src/team/state/types.ts
[state]: ../repo/src/team/state.ts
[state root]: ../repo/src/team/state-root.ts
[task state]: ../repo/src/team/state/tasks.ts
[team operations]: ../repo/src/team/team-ops.ts
[team API]: ../repo/src/team/api-interop.ts
[mailboxes]: ../repo/src/team/state/mailbox.ts
[approvals]: ../repo/src/team/state/approvals.ts
[role router]: ../repo/src/team/role-router.ts
[worker bootstrap]: ../repo/src/team/worker-bootstrap.ts
[repo decomposition]: ../repo/src/team/repo-aware-decomposition.ts
[coordination]: ../repo/src/team/coordination-protocol.ts
[scaling]: ../repo/src/team/scaling.ts
[orchestrator]: ../repo/src/team/orchestrator.ts
[completion evidence]: ../repo/src/team/completion-evidence.ts
[bridge]: ../repo/src/runtime/bridge.ts
[Rust engine]: ../repo/crates/omx-runtime-core/src/engine.rs
[tmux worker]: ../repo/src/team/tmux-session.ts
[idle nudges]: ../repo/src/team/idle-nudge.ts
[fallback watcher]: ../repo/src/scripts/notify-fallback-watcher.ts
[HUD authority]: ../repo/src/hud/authority.ts
[HUD loop]: ../repo/src/hud/index.ts
[HUD rendering]: ../repo/src/hud/render.ts
[HUD types]: ../repo/src/hud/types.ts
[sidecar types]: ../repo/src/sidecar/types.ts
[state operations]: ../repo/src/state/operations.ts
[autopilot skill]: ../repo/skills/autopilot/SKILL.md
[Autopilot gate]: ../repo/src/autopilot/completion-gate.ts
[Autopilot CLI]: ../repo/src/cli/autopilot.ts
[interview skill]: ../repo/skills/deep-interview/SKILL.md
[interview questions]: ../repo/src/question/deep-interview.ts
[Ultragoal]: ../repo/src/ultragoal/artifacts.ts
[memory]: ../repo/src/mcp/memory-server.ts
[wiki types]: ../repo/src/wiki/types.ts
[wiki API]: ../repo/src/wiki/index.ts
[wiki lifecycle]: ../repo/src/wiki/lifecycle.ts
[notification dispatcher]: ../repo/src/notifications/dispatcher.ts
[reply listener]: ../repo/src/notifications/reply-listener.ts
[timeline CLI]: ../repo/src/cli/session-timeline.ts
[mission]: ../repo/src/cli/mission.ts
[research CLI]: ../repo/src/cli/autoresearch.ts
[research validation]: ../repo/src/autoresearch/skill-validation.ts
[ask CLI]: ../repo/src/cli/ask.ts
[API CLI]: ../repo/src/cli/api.ts
[API Rust]: ../repo/crates/omx-api/src/lib.rs
[code intelligence]: ../repo/src/mcp/code-intel-server.ts
[SparkShell]: ../repo/crates/omx-sparkshell/src/main.rs
[SparkShell threshold]: ../repo/crates/omx-sparkshell/src/threshold.rs
[Task/state tests]: ../repo/src/team/__tests__/state.test.ts
[state tests]: ../repo/src/team/__tests__/state.test.ts
[Completion tests]: ../repo/src/team/__tests__/completion-evidence.test.ts
[Worker identity tests]: ../repo/src/team/__tests__/worker-runtime-identity.test.ts
[Autopilot advisory tests]: ../repo/src/autopilot/__tests__/completion-gate-advisory.test.ts
[Telegram tests]: ../repo/src/notifications/__tests__/reply-listener.test.ts
[Ultragoal tests]: ../repo/src/ultragoal/__tests__/artifacts.test.ts
